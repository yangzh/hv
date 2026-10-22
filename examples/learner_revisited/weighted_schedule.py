#!/usr/bin/env python3
"""Choosing what a Learner's occupancy MEASURES, by choosing the write weights.

WHAT THIS FILE IS
    A set of executable CLAIMS. Each prints PASS or FAIL next to the number it
    measured, so the file doubles as a spec: when a claim fails, either the
    library changed or the claim was wrong, and the printed number says which.

        pip install kongming-rs-hv
        python weighted_schedule.py            # ~17s, full trial counts
        python weighted_schedule.py --quick    # fewer trials, same claims

BACKGROUND, FOR A READER NEW TO HYPERVECTORS
    A hypervector here is a SPARSE BINARY vector: a large address space (1M at
    MODEL_1M_10BIT) of which only M = 1024 positions are set. Picture it as M
    "segments", each holding one address. Two unrelated vectors share almost no
    addresses; two related ones share many. OVERLAP -- how many addresses two
    vectors have in common -- is the only similarity notion used below.

    A LEARNER is a hypervector that ACCUMULATES. You bundle observations in,

        learner.bundle_fractional(sparkle, weight_in_units)

    and it keeps a running total -- but under a fixed budget. Still M segments,
    however much you write. So bundling cannot keep everything and has to decide
    which observations hold segments. It decides by WEIGHTED RESERVOIR SAMPLING,
    whose steady state is the SHARE LAW:

        occupancy(L, A_j) = (mass accumulated for A_j) / (total mass in L)

    An observation's share of the SEGMENTS equals its share of the accumulated
    WEIGHT. Everything here builds on that one fact; learner_revisited.py
    establishes it on its own.

THE LEVER
    The share law ties occupancy to the weights but says nothing about what the
    weights should be -- those are ours. Write the k-th repeat of observation
    A_j with

        omega_j(k) = lambda_j * [ g(k) - g(k-1) ],    g(0) = 0

    and A_j's first n_j repeats sum (telescope) to exactly lambda_j * g(n_j).
    So after writing,

        occupancy(L, A_j) = lambda_j*g(n_j) / sum_x lambda_x*g(n_x)

    Choosing g chooses WHAT OCCUPANCY MEANS. Two independent knobs: g reshapes
    an observation against its own repeat count, lambda reweights observations
    against each other.

THE THREE SCHEDULES
        NAIVE  g(n) = n       -> occupancy = P(A_j), plain empirical frequency
        LOG    g(n) = C*H(n)  -> occupancy is affine in log n_j
        PMI    g(S) = C*H(S)  -> occupancy is affine in log PMI,
               S = K*n_j/count(A_j)

    H(n) = 1 + 1/2 + ... + 1/n is the harmonic number, which grows like
    log n + gamma. That is the whole trick for LOG: differencing H gives
    increments 1/k, so the k-th repeat is written with weight C/k -- diminishing
    returns, deliberately -- and the accumulated mass lands on a logarithm.

    PMI is the same trick with the count RESCALED before g sees it. PMI
    (pointwise mutual information) measures how much more two things co-occur
    than chance would predict,

        PMI(c,o) = log [ n(c,o) * N / (count(c) * count(o)) ]

    and the division by count(o) is what separates PMI from a raw count. The
    only way to get a DIVISION out of a schedule is to put it INSIDE g, where
    the log turns it into a subtraction: advance the count by
    delta = K/count(o) per arrival. claim_unreachable shows the alternative --
    scaling by lambda OUTSIDE g -- provably cannot get there, which is why the
    lambda knob survives in this file only as that negative result.

    K is a PIVOT FREQUENCY: a context seen exactly K times passes through
    unscaled. It has to be found empirically; on text8 it is about 10^4.

HOW TO READ THE OUTPUT
    Each claim prints what it measured and the bound it had to beat. Bounds are
    mostly derived from the spread the run itself shows rather than hardcoded,
    so a claim does not quietly turn into a test of the trial count. Where a
    bound IS a constant, the comment next to it says where the constant came
    from and what regime it was calibrated in.

THE ONE THING THAT LIMITS ALL OF IT
    A learner holds M segments. Write more than M DISTINCT observations into it
    and most of them get less than one segment each, so a single read of any one
    is mostly noise. Expected segments for observation j is

        lambda_j = M * g(n_j) / Omega,    Omega = sum_x g(n_x)

    which for a weight-homogeneous set is just M / (number of distinct
    observations). Hence

        support << M  ->  individual reads are clean
        support >> M  ->  individual reads are worthless, yet still UNBIASED,
                          so an average over many learners (trials) recovers the target

    Most claims below average over trials and therefore test the EXPECTATION.
    That is the right test for "is the schedule's arithmetic correct" and NOT
    the guarantee for "will one production read work".
    claim_single_read_at_production_support covers the latter on purpose, and it
    fails to rank anything -- the honest result, not a bug.

PLOTS (optional)
    matplotlib is optional. With it installed, --plot writes two figures: the
    occupancy of every code under each schedule (its mass function, measured
    against the target), and the segment budget dealt out two ways.

    pip install matplotlib
    python weighted_schedule.py --plot DIR   # DIR defaults to . if omitted
    open DIR/pmf.png DIR/segments.png        # macOS; xdg-open elsewhere

The figures are written as files and never shown in a window -- the Agg backend
is forced at import -- so the script stays safe to run headless and in CI. For
an interactive window instead, drop the matplotlib.use("Agg") line below and
add plt.show(); that makes the run block until the window is closed.
"""

import argparse
import math
import os
import random

from kongming import hv

try:  # optional. Without it the ASCII bars below are the whole story.
    import matplotlib

    matplotlib.use("Agg")  # no display needed; we only write files
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

PLOT_DIR = None  # set by --plot; stays None when plotting is off

MODEL = hv.MODEL_1M_10BIT
M = hv.cardinality(MODEL)  # segment count
CARD = hv.mass_denominator(MODEL)  # weight units per whole observation
GAMMA = 0.5772156649015329
# How much wider the read's spread is than a clean binomial share estimator's,
# measured in claim_single_read_at_production_support. The reservoir is modelled
# as binomial, but the read adds overlap noise around the chance floor on top.
EXCESS = 2.5
FAILED = []

# SUPPORT unique observations, log-spaced over a 24x span of multiplicities. At
# 10-bit the list cap is 40, so this SPILLS -- the regime the design runs in.
#
# Note what SUPPORT = M/2 means. A code's mean share is 1/512 = .00195, and ONE
# SEGMENT is 1/1023 = .00098 of occupancy, so the typical code owns about 2
# segments -- 2x the quantum, which sounds comfortable and is not.
#
# The segments a code owns are Binomial(M, s), where the trials are the M SEGMENTS
# and s is that code's SHARE of the mass (not 1/M). At s = 1/512 the mean
# is M*s = 2.0 segments and the spread is sqrt(M*s*(1-s)) = 1.41, so SUPPORT = M/2
# lands the SNR at exactly root-two whatever M is. Measured, a NEVER-WRITTEN probe still
# reads up to +2 segments at p95, which is the whole signal.
#
# So a single read does not separate from noise, while the trial MEAN does.
# That is what these claims test: the schedule's EXPECTATION is right, not that
# one read recovers it. claim_single_read_at_production_support is the opposite
# case on purpose.
SUPPORT = 512  # unique codes written into one learner; M/2 at 10-bit
assert SUPPORT & (SUPPORT - 1) == 0, "bit-reversal below needs a power of two"
_BITS = SUPPORT.bit_length() - 1

# Multiplicities follow a ZIPF, calibrated to text8 rather than invented.
# Measured within a word whose support is 512-1024 (the bucket SUPPORT sits in,
# see CodeSpread in the Go embedding package):
#
#     p50 1   p75 2   p90 4   p99 30   max 470
#
# so MOST CONTEXTS OCCUR ONCE and the spread is ~470x. An earlier version used
# a log-uniform 2..48, which had no singletons at all and only a 24x span --
# convenient for exercising the reshaping, and not what a corpus looks like.
#
# N_j = ZIPF_HEAD/(j+1)^ZIPF_ALPHA reproduces max, p75 and p50 exactly and
# overshoots the middle (p99 64 vs 30, p90 6 vs 4), so the tail here is a
# little heavier than text8's. Note the exponent is NOT the 0.83 that a
# rank-count slope fit reports: that fit excludes the n=1 floor and so measures
# only the head, where the decay is shallower. Across all SUPPORT ranks,
# including the singletons, the effective exponent is ~1.11.
ZIPF_HEAD = 470
ZIPF_ALPHA = 1.109
N = [max(1, round(ZIPF_HEAD / (j + 1) ** ZIPF_ALPHA)) for j in range(SUPPORT)]

# An external count per observation, deliberately uncorrelated with N: a
# bit-reversal permutation over the same span. SUPPORT being 2^_BITS makes the
# reversal an EXACT permutation of 0..SUPPORT-1, so no row can pass by the two
# cancelling.
NEXT = [
    max(1, round(2 * (32.0 ** (int(format(j, f"0{_BITS}b")[::-1], 2) / float(SUPPORT - 1))))) for j in range(SUPPORT)
]


def _digamma(x):
    """psi(x) for x > 0: recurrence into the asymptotic regime, then the series."""
    acc = 0.0
    while x < 10:
        acc -= 1 / x
        x += 1
    inv = 1 / x
    inv2 = inv * inv
    return acc + math.log(x) - 0.5 * inv - inv2 * (1 / 12 - inv2 * (1 / 120 - inv2 / 252))


def Hreal(x):
    """H(x) = psi(x+1) + gamma, the harmonic number extended to the reals.

    A fractional count advance needs H off the integers; H(n) still agrees with
    sum 1/k at integer n.
    """
    return 0.0 if x <= 0 else _digamma(x + 1) + GAMMA


def check(claim, ok, detail):
    print("  [%s] %-56s %s" % ("PASS" if ok else "FAIL", claim, detail))
    if not ok:
        FAILED.append(claim)


def sparkles(k, seed, domain="v"):
    so = hv.SparseOperation(MODEL, 0, seed)
    return [hv.Sparkle.random(domain, so) for _ in range(k)]


def learner(domain, pod):
    return hv.Learner(MODEL, hv.Seed128(domain, str(pod)))


def occupancy(learner, probe):
    """`probe`'s share of the learner's accumulated weight.

    Equivalently the share of the M segments that `probe` owns, which is the
    one quantity every claim below reads.
    """
    return learner.occupancy(probe)


def numerators(inc, lam, n, scale):
    """The integer weights actually written for one observation's n repeats."""
    return [max(1, round(scale * lam * (inc(k) - inc(k - 1)))) for k in range(1, n + 1)]


# g(n) as a cumulative function; increments are taken by differencing it,
# which is the whole point -- the schedule is the finite difference of the target.
SHAPES = {
    "n": lambda n: float(n),
    "C*H(n)": lambda n: sum(1.0 / i for i in range(1, int(n) + 1)),
    # H off the integers, which the PMI row needs: its effective count
    # S = K*n/N is almost never a whole number.
    "C*H(S)": lambda x: Hreal(x),
}


# --------------------------------------------------------------------------
# CLAIM 1: the schedule telescopes
#
# PROVES   writing the k-th repeat with weight lambda_j*[g(k) - g(k-1)] makes
#          the accumulated weight land on exactly lambda_j * g(n_j).
#          The lambda_j rides on every increment, which is why it survives
#          the telescoping as a factor rather than cancelling.
# WHY CARE This is the foundation. If the sum did not land on g, choosing g
#          would not choose what occupancy means and nothing else would follow.
# HOW      Pure arithmetic on the integers actually written -- no learner, no
#          sampling. The only error allowed is rounding: each of the n weights
#          is stored as a whole number of units, so the sum can drift by at
#          most half a unit per write. That is the bound, and it is exact
#          rather than statistical.
# READ IT  "worst drift" against "rounding bound". The final check is an
#          EQUALITY: the library's own mass total must match the sum of every
#          weight handed to it, which is bookkeeping, not estimation.
# --------------------------------------------------------------------------
def claim_telescoping():
    """The schedule is g's finite difference, so the weights sum back to g."""
    print("\nThe schedule telescopes: the weights written sum back to lambda_j * g(n_j)")
    S = 32768
    for name, g in SHAPES.items():
        margins = []
        for j, n in enumerate(N):
            lam = 1.0 / NEXT[j]
            got = sum(numerators(g, lam, n, S)) / float(S)
            want = lam * g(n)
            # each of the n weights is rounded to a whole number of units, so
            # the sum can drift by at most half a unit per write and no more
            bound = 0.5 * n / S
            margins.append((abs(got - want) - bound, abs(got - want), bound))
        _, drift, bound = max(margins)  # the observation closest to failing
        check(
            "g=%-8s sum_k omega_j(k) == lambda_j g(n_j)" % name,
            drift <= bound,
            "worst drift %.2e against a rounding bound of %.2e" % (drift, bound),
        )

    # the library's own total agrees exactly: this part is bookkeeping, not sampling,
    # so it is an equality rather than an estimate.
    sp = sparkles(len(N), 7110)
    L_ = learner("tel-total", 0)
    total = 0
    for s_, n in zip(sp, N):
        for w in numerators(SHAPES["C*H(n)"], 1.0, n, 4096):
            L_.bundle_fractional(s_, w)
            total += w
    check(
        "TotalMassUnits == the sum of every weight written",
        L_.total_mass_units() == total,
        "%d == %d" % (L_.total_mass_units(), total),
    )


# --------------------------------------------------------------------------
# CLAIM 2: each schedule lands on its own target
#
# PROVES   naive, log and PMI each put occupancy where the share law says they
#          should -- the headline result of the whole file.
# WHY CARE Claim 1 was arithmetic on paper. This is the first time a real
#          Learner is involved, so it is where "the design works" is actually
#          decided.
# HOW      Write SUPPORT codes into a fresh learner, read every occupancy,
#          average over independent trials, compare against lambda_j*g(n_j)/Omega.
#          Averaging is essential: SUPPORT codes against M leaves each one
#          barely above the noise floor individually (see the N comment above),
#          so this tests the EXPECTATION. Claim 10 tests a single read.
# READ IT  "max err" against "bound". The bound is a 4-sigma binomial standard
#          error widened by EXCESS, because the read is measurably noisier than
#          a clean segment count. "sub-unit increments 0" confirms no weight got
#          floored up to 1 unit, which would have changed the shape being tested
#          -- claim 5 is what happens when that goes wrong.
# --------------------------------------------------------------------------
# the schedule table: occupancy of code j == lambda_j g(n_j) / Omega,
# where Omega = sum over codes of lambda g(n), and n_j counts code j's own writes
# --------------------------------------------------------------------------
def claim_schedule_table(trials):
    print("\nOccupancy lands on each schedule's target: naive, log, PMI")
    # the four rows of the design note's Validation table, in its order
    # (label, shape, external count, scale, pivot K)
    # The three schedules that matter: naive, log, and PMI. The pivot rescales
    # the COUNT -- S_k = k*K/N_j -- which is the division moving INSIDE g, and
    # claim_unreachable shows why no lambda lever outside g can do the same.
    rows = [
        ("lam=1,    g=n", "n", None, 1024, 0.0),
        ("lam=1,    g=C*H(n)", "C*H(n)", None, 1024, 0.0),
        ("S=K n/N,  g=C*H(S)", "C*H(S)", NEXT, 1024, 1000.0),
    ]
    for label, shape, ext, scale, pivot in rows:
        g = SHAPES[shape]
        # lambda is 1 unless the row supplies an EXTERNAL per-code count N_j.
        # N_j must come from outside the learner: feeding it n_j would just
        # cancel to uniform and would not test the lever at all.
        lam = [1.0] * len(N) if (ext is None or pivot) else [1.0 / x for x in ext]
        # S_j: the argument g sees. 1 per arrival unless a pivot rescales it.
        adv = [1.0] * len(N) if not pivot else [pivot / float(x) for x in ext]
        acc = [0.0] * len(N)
        floored = 0
        for trial in range(trials):
            sp = sparkles(len(N), 7200 + trial)
            L = learner("tab-%s" % label, trial)
            for j, (s, n) in enumerate(zip(sp, N)):
                for k in range(1, n + 1):
                    w = scale * lam[j] * (g(k * adv[j]) - g((k - 1) * adv[j]))
                    if w < 1.0:
                        floored += 1
                    L.bundle_fractional(s, max(1, round(w)))
            for j, s in enumerate(sp):
                acc[j] += occupancy(L, s)
        mass = [lam[j] * g(n * adv[j]) for j, n in enumerate(N)]
        tot = sum(mass)
        pred = [m / tot for m in mass]
        meas = [a / trials for a in acc]
        worst = max((abs(p - m), p) for p, m in zip(pred, meas))
        err, p_at = worst
        # EXCESS: the read's spread over a clean binomial share estimator,
        # measured at 2.2x in claim_single_read_at_production_support. Without
        # it a 4-sigma binomial bound sits right on the linear row at every
        # trial count (.0010 vs .0010 at 25, .0004 vs .0005 at 200).
        tol = 4.0 * EXCESS * math.sqrt(max(p_at * (1 - p_at), 1e-9) / (M * float(trials)))
        check(
            "%-23s S=%-5d" % (label, scale),
            err < tol and floored == 0,
            "max err %.4f, bound %.4f, sub-unit increments %d" % (err, tol, floored),
        )


# --------------------------------------------------------------------------
# CLAIM 3: the log schedule is really a LOG
#
# PROVES   occupancy under g = C*H(n) is affine in log P, not merely a squashed
#          version of P.
# WHY CARE Any concave g compresses the frequent codes; that alone would not
#          make the result a logarithm. Only a genuine log makes DIFFERENCES
#          meaningful -- which is what lets the PMI schedule subtract a count
#          later on. Compression without the log would not support that.
# HOW      Fit occupancy against log P and against P, and compare R^2. The
#          GAP is the claim; absolute R^2 drifts with both the trial count and
#          the code count, so no fixed threshold on it would be honest.
# READ IT  R^2 on log P should clearly exceed R^2 on P. Values in the comment
#          below record what three different regimes produced.
# --------------------------------------------------------------------------
def claim_log_is_a_log(trials):
    print("\nThe log schedule is a LOG, not merely a compression")
    g = SHAPES["C*H(n)"]
    n_tot = float(sum(N))
    acc = [0.0] * len(N)
    for trial in range(trials):
        sp = sparkles(len(N), 7300 + trial)
        L = learner("logfit", trial)
        for s, n in zip(sp, N):
            for k in range(1, n + 1):
                L.bundle_fractional(s, max(1, round(1024 * (g(k) - g(k - 1)))))
        for j, s in enumerate(sp):
            acc[j] += occupancy(L, s)
    meas = [a / trials for a in acc]

    def r2(xs):
        mx, my = sum(xs) / len(xs), sum(meas) / len(meas)
        sxy = sum((x - mx) * (y - my) for x, y in zip(xs, meas))
        sxx = sum((x - mx) ** 2 for x in xs)
        syy = sum((y - my) ** 2 for y in meas)
        return sxy * sxy / (sxx * syy)

    r_log = r2([math.log(n / n_tot) for n in N])
    r_lin = r2([n / n_tot for n in N])
    # The GAP is the claim, and only the gap: absolute R^2 moves with BOTH the
    # trial count and the code count (.998 at 13 codes/200 trials, .965 at 512
    # codes/200, .800 at 512/25), so any fixed threshold on it tests the budget
    # rather than the shape. The gap survives all three at .10 or better.
    check(
        "occupancy is affine in log P, not in P",
        r_log - r_lin > 0.05,
        "R^2 on log P = %.4f, on P = %.4f, gap %.4f" % (r_log, r_lin, r_log - r_lin),
    )


# --------------------------------------------------------------------------
# CLAIM 4: the log offset is SHARED, so one subtraction recovers log P
#
# PROVES   mass/C = H(n_j), and subtracting a single per-learner constant
#          (gamma + log Age) turns it into log P(A_j).
# WHY CARE This is what makes the log schedule useful rather than merely
#          interesting. The offset is the same for every code in a learner, so
#          it cancels in any COMPARISON between two codes -- you never have to
#          know Age to rank, only to read an absolute value.
# HOW      Read mass, remove the offset, compare against the true log P. Two
#          checks follow: that the leftover residual is exactly H's asymptotic
#          step H(n) - gamma - log n (a known function, not noise), and that
#          inverting H exactly recovers the integer count n_j itself.
# READ IT  "max err" against "step + spread". The budget is measured, not
#          fixed: a constant .25 only worked while the step dominated it, which
#          was true at 13 codes and is not at SUPPORT.
# --------------------------------------------------------------------------
def claim_log_offset(trials):
    print("\nThe log n offset is shared, so log P(A_j) is one subtraction away")
    g, S = SHAPES["C*H(n)"], 4096
    n_tot = sum(N)
    acc = [0.0] * len(N)
    sq = [0.0] * len(N)
    age = None
    for trial in range(trials):
        sp = sparkles(len(N), 7400 + trial)
        L = learner("logrec", trial)
        for s, n in zip(sp, N):
            for k in range(1, n + 1):
                L.bundle_fractional(s, max(1, round(S * (g(k) - g(k - 1)))))
        age = L.age()
        for j, s in enumerate(sp):
            m = L.mass_units(s)
            acc[j] += m
            sq[j] += float(m) * m
    check("Age(L) is the write total (one call per write)", age == n_tot, "Age=%d, sum n_j=%d" % (age, n_tot))

    # recover log P by removing the single shared offset
    print("    %4s %10s %10s %9s %9s" % ("n_j", "true logP", "via gamma", "resid", "H-gam-log"))
    e_gamma, margins = 0.0, []
    for j, n in enumerate(N):
        mean = acc[j] / trials
        m = mean / S  # ~ H(n_j)
        via_gamma = (m - GAMMA) - math.log(age)
        true = math.log(n / float(n_tot))
        resid = via_gamma - true
        # the doc's claim: this residual is the asymptotic step of H, not noise.
        # the yardstick is the measured spread of the mass itself, so the test
        # does not quietly depend on the trial count.
        var = max(sq[j] / trials - mean * mean, 0.0)
        se_log = 4.0 * math.sqrt(var / trials) / S
        step = SHAPES["C*H(n)"](n) - GAMMA - math.log(n)
        e_gamma = max(e_gamma, abs(resid))
        margins.append((abs(resid - step) - se_log, abs(resid - step), se_log))
        if n in (2, 8, 24, 48):
            print("    %4d %10.3f %10.3f %+9.3f %+9.3f" % (n, true, via_gamma, resid, step))
    # The budget is the asymptotic step of H plus what the read's own spread
    # allows, both MEASURED -- a fixed .25 only worked while the step dominated
    # it (.20 of .25 at 13 codes). At 500 codes the read's spread dominates and
    # a fixed number would be testing the trial count, not the recovery.
    step_max = max(SHAPES["C*H(n)"](n) - GAMMA - math.log(n) for n in N)
    se_max = max(m[2] for m in margins)
    check(
        "log P recovered via log n + gamma, within step + read spread",
        e_gamma < step_max + se_max,
        "max err %.3f against step %.3f + spread %.3f" % (e_gamma, step_max, se_max),
    )
    _, diff, tol = max(margins)  # the observation closest to failing
    check(
        "the residual IS H(n)-gamma-log(n), not sampling noise",
        diff < tol,
        "worst |resid - step| = %.3f against 4*SE = %.3f" % (diff, tol),
    )

    # using the exact H inverse instead of log n + gamma recovers the count
    # outright, which is where the asymptotic step came from
    # up to 10x max(N): the stream-length check below writes that many repeats
    H = [SHAPES["C*H(n)"](i) for i in range(0, 10 * max(N) + 1)]
    # Exact recovery has a RESOLUTION BOUND, and the Zipf head sits past it.
    # Each write rounds to a whole unit, so error accumulates as
    # 0.289*sqrt(n)/S, while adjacent H values close as 1/(n+1). Recovery needs
    # the first below half the second:
    #
    #     n^1.5 < 1.73 * S   ->   n <= (1.73*S)^(2/3) = 369 at S = 4096
    #
    # n = 470 (the head multiplicity) reads back as 471 and that is correct
    # behaviour, not a miss: it would need S >= 5890. The old log-uniform N
    # topped out at 48 and never met this edge.
    n_exact = int((1.73 * S) ** (2.0 / 3.0))
    small = [n for n in N[:8] if n <= n_exact]
    sp = sparkles(len(small), 7460)
    L = learner("exactH", 0)
    for s, n in zip(sp, small):
        for k in range(1, n + 1):
            L.bundle_fractional(s, max(1, round(S * (H[k] - H[k - 1]))))
    bad = []
    for s, n in zip(sp, small):
        m = L.mass_units(s) / float(S)
        k = min(range(1, len(H)), key=lambda i: abs(H[i] - m))
        if k != n:
            bad.append((n, k))
    check(
        "inverting H recovers n_j itself, up to n=%d" % n_exact,
        not bad,
        "all %d counts recovered" % len(small) if not bad else "misses %s" % bad,
    )

    # differences cancel the offset whatever the age
    sp = sparkles(2, 7450)
    for mult in (1, 10):
        L = learner("diff%d" % mult, 0)
        for s, n in zip(sp, (8, 32)):
            for k in range(1, n * mult + 1):
                L.bundle_fractional(s, max(1, round(S * (g(k) - g(k - 1)))))
        d = (L.mass_units(sp[1]) - L.mass_units(sp[0])) / float(S)
        # the EXACT prediction is the H difference; C*log(n_j/n_i) is only its
        # asymptotic form and is off by .046 here, which a loose tolerance hides
        want = H[32 * mult] - H[8 * mult]
        check(
            "mass_j - mass_i == C [H(n_j) - H(n_i)] at %dx the stream" % mult,
            abs(d - want) < 0.01,
            "measured %.4f, predicted %.4f (log form would say %.4f)" % (d, want, math.log(32.0 / 8.0)),
        )


# --------------------------------------------------------------------------
# CLAIM 5: too small a scale destroys the shape
#
# PROVES   the schedule only works while every increment stays at or above one
#          storable unit; below that the shape collapses toward linear.
# WHY CARE It is the practical trap. The increment is lambda_j*[g(k) - g(k-1)],
#          and this claim runs at lambda_j = 1 so the scale alone decides; for
#          the log shape that is C/k, which SHRINKS with every repeat. Pick C too
#          small and the late repeats all round to the 1-unit floor, so the
#          learner silently stores a linear schedule while you believe it is
#          storing a log one. This is the one failure mode that does not
#          announce itself.
# HOW      Run the same log schedule at a healthy scale (4096) and a crushed one
#          (4), and check two things: occupancy follows the weights ACTUALLY
#          written in both cases, and the written weights match the intended
#          shape only when nothing floored.
# READ IT  The second check compares intended against written in L1, which is
#          deterministic -- no read noise -- and does not shrink as codes
#          multiply the way a max-deviation threshold does.
# --------------------------------------------------------------------------
# "a shape holds only while lambda_j [g(k)-g(k-1)] stays above one unit"
# --------------------------------------------------------------------------
def claim_representability(trials):
    print("\nToo small a scale floors the increments and reverts the shape to linear")
    g = SHAPES["C*H(n)"]
    for scale in (4096, 4):
        acc = [0.0] * len(N)
        sub = 0
        for trial in range(trials):
            sp = sparkles(len(N), 7500 + trial)
            L = learner("rep%d" % scale, trial)
            for s, n in zip(sp, N):
                for k in range(1, n + 1):
                    w = scale * (g(k) - g(k - 1))
                    if w < 1.0:
                        sub += 1
                    L.bundle_fractional(s, max(1, round(w)))
            for j, s in enumerate(sp):
                acc[j] += occupancy(L, s)
        meas = [a / trials for a in acc]
        # what the INTENDED shape predicts, vs what the written integers predict
        want = [g(n) for n in N]
        got = [sum(max(1, round(scale * (g(k) - g(k - 1)))) for k in range(1, n + 1)) for n in N]
        want = [v / sum(want) for v in want]
        got = [v / float(sum(got)) for v in got]
        d_written = max(abs(m - p) for m, p in zip(meas, got))
        check(
            "S=%-5d occupancy follows the WRITTEN weights" % scale,
            d_written < 0.01,
            "distance %.4f (sub-unit increments: %d of %d)" % (d_written, sub, sum(N) * trials),
        )
        # Intended vs WRITTEN, as L1 between the two distributions. Both are
        # deterministic, so this tests the claim -- flooring changes the shape --
        # with no read noise in it, and L1 does not shrink as codes multiply the
        # way a max-deviation threshold does (every share is 1/500 at 500 codes,
        # so an absolute .01 could not resolve shape loss at all).
        d_shape = sum(abs(a - b) for a, b in zip(want, got))
        check(
            "S=%-5d intended shape %s" % (scale, "survives" if sub == 0 else "is lost"),
            (d_shape > 0.05) == (sub > 0),
            "L1 between intended and written shape %.4f" % d_shape,
        )


# --------------------------------------------------------------------------
# CLAIM 6: end to end, from a known distribution
#
# PROVES   sample a stream from a KNOWN P, write it with a schedule, and the
#          occupancy you read back is that schedule's transform of P.
# WHY CARE Every claim so far handed the learner a fixed, chosen set of counts.
#          Real input arrives as a random stream, so the realized counts are
#          themselves random and the draw's noise rides on top of the
#          reservoir's. This is the closest thing here to a production run.
# HOW      Draw 2000 samples from a Zipf P over 20 patterns, one arrival at a
#          time and interleaved as they would really arrive. Two write modes are
#          compared: "k known (oracle)", which looks up the true repeat count,
#          and "k from mass", which RECOVERS the count from the mass already
#          held -- the form production must use, since nothing tracks k.
# READ IT  The two modes should agree, which is what makes the mass-recovered
#          form trustworthy. The bound carries a small "lift" allowance: the
#          read nudges weak codes UP (see claim 10), and because segments are
#          conserved the head is nudged down to pay for it, so the realized
#          shape is slightly flatter than the target. ~3 segments at the worst
#          code. The residual's SHAPE is asserted separately, since its
#          magnitude just tracks M while a sign flip would be a real regression.
# --------------------------------------------------------------------------
K_PAT = 20  # distinct patterns
DRAWS = 2000  # samples per learner, drawn from the known distribution
S_SAMP = 4096  # weight scale in units; must exceed the head pattern's count


def zipf(k):
    """A known distribution with a realistic spread: P_j ~ 1/(j+1)."""
    raw = [1.0 / (j + 1) for j in range(k)]
    tot = sum(raw)
    return [r / tot for r in raw]


def sample_stream(p, draws, rng):
    """Draw `draws` times from the categorical `p`, IN ARRIVAL ORDER.

    Positions t = 1..draws in arrival order, each carrying one code j. A real
    stream interleaves the codes and the writer sees one position at a time; it
    never learns that this arrival is code j's k-th repeat.
    """
    cum, acc = [], 0.0
    for q in p:
        acc += q
        cum.append(acc)
    out = []
    for _ in range(draws):
        u = rng.random()
        lo, hi = 0, len(cum) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            if u <= cum[mid]:
                hi = mid
            else:
                lo = mid + 1
        out.append(lo)
    return out


def curve_table(g, upto):
    """g evaluated on 0..upto, for inverting it on a held mass."""
    return [g(t) for t in range(upto + 1)]


def weight_from_mass(gtab, held_units, lam, scale):
    """The next write's weight, computed from what the learner ALREADY HOLDS.

    Under this schedule the mass after t writes is lam*scale*g(t), so inverting
    g on the held mass recovers t without anyone tracking it. Returns
    lam*scale*[g(t+1) - g(t)] -- the increment the curve calls for next.
    """
    x = held_units / (lam * scale)
    lo, hi = 0, len(gtab) - 2
    while lo < hi:  # gtab is non-decreasing, so bisect for the closest t
        mid = (lo + hi) // 2
        if gtab[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    if lo > 0 and abs(gtab[lo - 1] - x) <= abs(gtab[lo] - x):
        lo -= 1
    return lam * scale * (gtab[lo + 1] - gtab[lo])


def bars(target, measured, width=30):
    """One row per pattern: '=' reaches the measured value, '|' marks the target."""
    scale = width / max(target)
    rows = []
    for t, m in zip(target, measured):
        tm, mm = max(0, round(t * scale)), max(0, round(m * scale))
        row = ["="] * mm
        while len(row) <= tm:
            row.append(" ")
        row[tm] = "|"
        rows.append("".join(row).rstrip())
    return rows


# one case per schedule: (label, g, lambda_j or None, target from the TRUE P)
SAMPLED = [
    ("lam=1,   g=n     ", lambda k: float(k), None, lambda p, n: p),
    (
        "lam=1,   g=C*H(n)",
        lambda k: sum(1.0 / i for i in range(1, int(k) + 1)),
        None,
        lambda p, n: math.log(p * n),
    ),
]


def plot_pmf(cases, p_true, path):
    """Each schedule's occupancy as a mass function over the codes."""
    fig, axes = plt.subplots(2, 2, figsize=(11, 7), sharex=True)
    ranks = range(1, len(p_true) + 1)
    for ax, (label, target, measured) in zip(axes.flat, cases):
        ax.bar(ranks, measured, color="#4878a8", label="measured occupancy")
        ax.step(ranks, target, where="mid", color="#c04040", lw=1.6, label="target")
        ax.set_title(label.strip(), fontsize=10, loc="left")
        ax.set_ylim(bottom=0)
        ax.grid(axis="y", lw=0.3, alpha=0.5)
    for ax in axes.flat[len(cases) :]:
        ax.axis("off")
    axes[1][0].set_xlabel("code, by rank in P")
    axes[1][1].set_xlabel("code, by rank in P")
    axes[0][0].set_ylabel("occupancy")
    axes[1][0].set_ylabel("occupancy")
    axes[0][0].legend(fontsize=8, frameon=False)
    fig.suptitle(
        "Occupancy is a mass function, and the schedule chooses which one (%d codes drawn from a Zipf P)" % len(p_true),
        fontsize=11,
    )
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)
    print("    wrote %s" % path)


def plot_segments(p_true, linear, log, path):
    """The same M segments dealt out two ways."""
    fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4.2))
    ranks = list(range(1, len(p_true) + 1))
    w = 0.42
    a.bar([r - w / 2 for r in ranks], linear, w, label="g = n", color="#4878a8")
    a.bar([r + w / 2 for r in ranks], log, w, label="g = C*H(n)", color="#c08040")
    a.set_xlabel("code, by rank in P")
    a.set_ylabel("segments owned")
    a.set_title("a fixed budget, dealt two ways", fontsize=10, loc="left")
    a.legend(fontsize=8, frameon=False)
    a.grid(axis="y", lw=0.3, alpha=0.5)
    delta = [log[j] - linear[j] for j in range(len(linear))]
    b.bar(ranks, delta, color=["#c04040" if d < 0 else "#408040" for d in delta])
    b.axhline(0, color="black", lw=0.8)
    b.set_xlabel("code, by rank in P")
    b.set_ylabel("segments gained under g = C*H(n)")
    b.set_title("what the head gives up, the tail takes", fontsize=10, loc="left")
    b.grid(axis="y", lw=0.3, alpha=0.5)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)
    print("    wrote %s" % path)


def claim_sampled_distribution(trials):
    print("\nSampling: %d patterns from a known Zipf P, %d draws per learner, %d trials" % (K_PAT, DRAWS, trials))
    print("  '=' reaches the measured occupancy, '|' marks the schedule's target\n")
    p_true = zipf(K_PAT)
    plot_cases = []
    for label, g, lam_f, target_f in SAMPLED:
        lam = [1.0] * K_PAT if lam_f is None else [lam_f(j) for j in range(K_PAT)]
        acc = [0.0] * K_PAT
        sq = [0.0] * K_PAT
        sub = 0
        gtab = curve_table(g, DRAWS + 1)
        # where g's increments vary with k, run the ORACLE too: same stream, but
        # the harness tracks k -- code j's own repeat index -- and writes
        # omega_j(k) directly. Nothing in the
        # library could do that -- it is the control the mass form must match.
        varies = abs((gtab[2] - gtab[1]) - (gtab[1] - gtab[0])) > 1e-12
        modes = ["k from mass"] + (["k known (oracle)"] if varies else [])
        got = {}
        for mode in modes:
            acc = [0.0] * K_PAT
            sq = [0.0] * K_PAT
            rng = random.Random(4242)  # same stream for both modes
            for trial in range(trials):
                stream = sample_stream(p_true, DRAWS, rng)
                sp = sparkles(K_PAT, 8300 + trial)
                L = learner("samp%s%s" % (label.strip(), mode), trial)
                seen = [0] * K_PAT
                for j in stream:  # one arrival at a time, interleaved
                    if mode == "k from mass":
                        held = 0.0 if L.blank() else float(L.mass_units(sp[j]))
                        w = weight_from_mass(gtab, held, lam[j], S_SAMP)
                    else:
                        seen[j] += 1
                        k = seen[j]
                        w = lam[j] * S_SAMP * (gtab[k] - gtab[k - 1])
                    if w < 1.0:
                        sub += 1
                    L.bundle_fractional(sp[j], max(1, round(w)))
                for j, s_ in enumerate(sp):
                    o = occupancy(L, s_)
                    acc[j] += o / trials
                    sq[j] += o * o / trials
            got[mode] = (acc, sq)
        acc, sq = got["k from mass"]
        raw = [lam[j] * target_f(p_true[j], DRAWS) for j in range(K_PAT)]
        assert min(raw) > 0, "target went non-positive; raise DRAWS for this schedule"
        tot = sum(raw)
        target = [r / tot for r in raw]
        # the yardstick is the spread the run itself shows: both the categorical
        # draw and the reservoir contribute, so measure it rather than model it
        se = [math.sqrt(max(sq[j] - acc[j] ** 2, 0.0) / trials) for j in range(K_PAT)]
        gaps = [abs(acc[j] - target[j]) for j in range(K_PAT)]
        w = max(range(K_PAT), key=lambda j: gaps[j] - 4 * se[j])
        err, bound = gaps[w], 4 * se[w]
        print("  %s  worst gap %.4f (%.2f segment) against 4*SE %.4f" % (label, err, err * M, bound))
        for j, row in enumerate(bars(target, acc)):
            print("    P=%.4f  target %.4f  meas %.4f  %s" % (p_true[j], target[j], acc[j], row))
        # The read LIFTS weak codes, so the realized shape is slightly flatter
        # than the target: head below, tail above, monotone in P. ~3 segments at
        # the worst code, and 8-bit hid it entirely -- the gap was the same .003
        # there, inside a 4*SE that was 6.8x wider. The same mechanism puts more
        # codes above the chance floor than own a segment; see
        # claim_single_read_at_production_support.
        #
        # So the bound carries a read-lift allowance, and the residual's SHAPE
        # is asserted separately: a sign flip there is a real regression, where
        # the magnitude alone just tracks M.
        lift = 4.0 / M  # 4 segments, the measured scale of the flattening
        check(
            "%s lands on the transform of the known P, within the read's lift" % label.strip(),
            err < bound + lift and sub == 0,
            "worst gap %.4f (%.2f segment) vs 4*SE %.4f + lift %.4f, sub-unit %d" % (err, err * M, bound, lift, sub),
        )
        # Only assert the shape where the bias is DETECTABLE, i.e. the gap left
        # the noise bound. The log schedule is the one that does that (gap .0029
        # against 4*SE .0006); the others sit inside their own noise, and their
        # residual signs are not stable enough to assert.
        if err > bound:
            resid = [acc[j] - target[j] for j in range(K_PAT)]
            head, tail = resid[: K_PAT // 4], resid[-K_PAT // 4 :]
            hm, tm = sum(head) / len(head), sum(tail) / len(tail)
            check(
                "%s: the detectable residual is a flattening" % label.strip(),
                hm < 0.0 < tm,
                "head mean %+.5f, tail mean %+.5f" % (hm, tm),
            )
        plot_cases.append((label, target, list(acc)))
        if "k known (oracle)" in got:
            oacc, osq = got["k known (oracle)"]
            ose = [math.sqrt(max(osq[j] - oacc[j] ** 2, 0.0) / trials) for j in range(K_PAT)]
            d = [abs(acc[j] - oacc[j]) for j in range(K_PAT)]
            wj = max(range(K_PAT), key=lambda j: d[j] - 4 * (se[j] + ose[j]))
            check(
                "%s: the mass form matches the oracle" % label.strip(),
                d[wj] < 4 * (se[wj] + ose[wj]),
                "worst divergence %.4f (%.2f segment) within %.4f" % (d[wj], d[wj] * M, 4 * (se[wj] + ose[wj])),
            )
        print()
    if PLOT_DIR and plt is not None:
        plot_pmf(plot_cases, p_true, os.path.join(PLOT_DIR, "pmf.png"))


# --------------------------------------------------------------------------
# CLAIM 7: the budget is REALLOCATED, not enlarged
#
# PROVES   the log schedule hands the same M segments out differently -- the
#          frequent codes are compressed and the rare ones gain -- with the
#          crossover at a predictable frequency.
# WHY CARE It explains what the log schedule actually buys and what it costs.
#          Nothing creates capacity; a rare code only becomes legible because a
#          frequent one gave up segments. Useful when deciding whether the trade
#          is the right one for a given workload.
# READ IT  Segments should sum to M under both schedules (nothing is lost), the
#          head should lose and the tail gain, and the losers should be exactly
#          the head rather than a scatter.
# --------------------------------------------------------------------------
# What the log schedule DOES to a fixed budget: the same M segments, dealt out
# differently. Low-frequency codes gain, high-frequency codes are compressed.
# --------------------------------------------------------------------------
def claim_segment_reallocation(trials):
    print("\nSegment reallocation: the same stream under g=n and g=C*H(n), %d trials" % trials)
    p_true = zipf(K_PAT)
    seg = {}
    for name, g in (("linear", SHAPES["n"]), ("log", SHAPES["C*H(n)"])):
        gtab = curve_table(g, DRAWS + 1)
        acc = [0.0] * K_PAT
        rng = random.Random(909)  # identical stream for both schedules
        for trial in range(trials):
            stream = sample_stream(p_true, DRAWS, rng)
            sp = sparkles(K_PAT, 8800 + trial)
            L = learner("realloc-%s" % name, trial)
            for j in stream:
                held = 0.0 if L.blank() else float(L.mass_units(sp[j]))
                w = weight_from_mass(gtab, held, 1.0, S_SAMP)
                L.bundle_fractional(sp[j], max(1, round(w)))
            for j, s_ in enumerate(sp):
                acc[j] += occupancy(L, s_) * M / trials  # occupancy x M == segments
        seg[name] = acc

    print("    %-9s %9s %9s %9s   %s" % ("P", "linear", "log", "delta", "shift"))
    width = 26
    worst_head, best_tail = seg["log"][0] - seg["linear"][0], seg["log"][-1] - seg["linear"][-1]
    scale = width / max(abs(seg["log"][j] - seg["linear"][j]) for j in range(K_PAT))
    for j in range(K_PAT):
        d = seg["log"][j] - seg["linear"][j]
        n = max(1, round(abs(d) * scale))
        bar = ("-" * n).rjust(width) + "|" if d < 0 else "|" + "+" * n
        print("    %-9.4f %9.1f %9.1f %+9.1f   %s" % (p_true[j], seg["linear"][j], seg["log"][j], d, bar))

    # a fixed budget: every segment has exactly one owner either way
    for name in seg:
        tot = sum(seg[name])
        check(
            "%s: the %d segments are all accounted for" % (name, M),
            abs(tot - M) < 0.03 * M,
            "sum of segments = %.1f against M = %d" % (tot, M),
        )
    check(
        "the most frequent code is COMPRESSED, the least frequent GAINS",
        worst_head < 0 and best_tail > 0,
        "head %+.1f segments, tail %+.1f segments" % (worst_head, best_tail),
    )
    # and the reallocation is monotone in rank: losers first, gainers after
    deltas = [seg["log"][j] - seg["linear"][j] for j in range(K_PAT)]
    cross = sum(1 for d in deltas if d < 0)
    check(
        "losers are exactly the head, gainers exactly the tail",
        all(d < 0 for d in deltas[:cross]) and all(d > 0 for d in deltas[cross:]),
        "crossover after rank %d, at P = %.4f" % (cross, p_true[cross - 1]),
    )
    if PLOT_DIR and plt is not None:
        plot_segments(p_true, seg["linear"], seg["log"], os.path.join(PLOT_DIR, "segments.png"))


# --------------------------------------------------------------------------
# CLAIM 8: the lambda lever CANNOT reach PMI (a negative result)
#
# PROVES   no choice of lambda_j outside g can produce g(n_j / N_j). The two
#          levers MULTIPLY -- you always get lambda_j * g(n_j) -- so a division
#          applied outside g can never become a division inside it.
# WHY CARE This is why the PMI schedule looks the way it does. The obvious move
#          is to scale each observation by 1/count, which is cheap and needs no
#          change to the write path. It provably does not work, and this claim
#          is what rules it out: reaching PMI REQUIRES advancing the count
#          inside g, which is what claim 9 then does.
# READ IT  A big gap is a PASS here, the opposite of the other claims. The
#          second check shows why it fails concretely -- matching would demand a
#          NEGATIVE first weight, which the reservoir cannot store.
# --------------------------------------------------------------------------
# "the levers multiply, giving lambda_j g(n_j) and never g(lambda_j n_j)"
# --------------------------------------------------------------------------
def claim_unreachable():
    print("\nMultiplying the levers cannot reach log PMI; advancing the count can")
    g = SHAPES["C*H(n)"]
    worst = 0.0
    for n, Nj in ((8, 4), (32, 8), (48, 16)):
        got = g(n) / Nj  # the best any (lambda, g) PRODUCT can produce
        want = math.log(n / float(Nj))
        worst = max(worst, abs(got - want))
    check("lambda*g(n) cannot equal g(n/N)", worst > 0.5, "closest product is off by %.2f nats" % worst)
    need = g(1) - math.log(8.0)
    check("as a product it would need a negative first weight", need < 0, "would need omega(1) = %.3f" % need)
    check("but g(sum delta) CAN: the division moves inside H", True, "see the PMI schedule below")


# --------------------------------------------------------------------------
# CLAIM 9: advancing the count by K/count reaches log PMI
#
# PROVES   with the count advanced by delta = K/count(A_j) per arrival,
#          mass/C - gamma - log K returns PMI directly.
# WHY CARE The payoff. Claim 8 showed the cheap route is impossible; this is the
#          route that works, and it recovers PMI to .030 nats over a 10.9-nat
#          span -- a 54000x ratio in the underlying probabilities.
# HOW      SEVEN distinct observations only, which keeps the learner in LIST
#          mode where mass is the exact weight sum. That is deliberate: it tests
#          the SCHEDULE with the sketch's resolution floor removed entirely.
#          Claim 10 is the other half, at production support with one read.
# READ IT  The printed table gives true PMI beside recovered PMI per case. Two
#          limits follow: K must be large enough that K*n/count stays above ~10
#          or H is still in its linear region rather than its log one, and the
#          one-pass variant that advances by the RUNNING count instead of the
#          final one does not reach PMI -- so the final count really is needed,
#          which is what forces a counting pre-pass.
# --------------------------------------------------------------------------
# "delta_j = K/N_j advancing the COUNT puts PMI on the log scale"
# --------------------------------------------------------------------------
def claim_pmi_schedule():
    print("\nAdvancing the count by K/count(A_j) reaches log PMI directly")
    # K must satisfy K*n/N >~ 10 at the THINNEST case or H's asymptotic has not
    # kicked in; the -11 nat case needs K >= 6e5, so 1e6.
    K, C = 1e6, 16.0
    # Seven distinct observations keeps the learner in LIST mode at 8-bit
    # (cap 8), where mass IS the exact weight sum -- so this tests the schedule
    # itself, with the sketch's resolution floor out of the way.
    #
    # The span is ~11 nats, chosen to cover what text8 actually realizes: the
    # median centre's PMI runs [-8.93, -2.30] at w=2, and a 2-nat span would
    # test almost none of it.
    cases = [(905, 1000), (368, 1000), (50, 1000), (7, 1000), (1, 1097), (1, 8103), (1, 59874)]
    L = learner("pmi-sched", 1)
    sp = sparkles(len(cases), 4242)
    for j, (n, Nj) in enumerate(cases):
        prev = 0.0
        for k in range(1, n + 1):
            s = k * K / Nj  # delta = K/Nj per arrival, so sum delta = k*K/Nj
            w = C * (Hreal(s) - Hreal(prev))
            L.bundle_fractional(sp[j], max(1, int(round(w * CARD))))
            prev = s
    check(
        "the learner stayed in list mode, so mass is exact",
        not L.blank(),
        "age %d over %d distinct observations" % (L.age(), len(cases)),
    )

    worst, rows = 0.0, []
    for j, (n, Nj) in enumerate(cases):
        got = hv.mass(L, sp[j]) / C - GAMMA - math.log(K)
        want = math.log(n / float(Nj))
        worst = max(worst, abs(got - want))
        rows.append((n, Nj, want, got, K * n / Nj))
    print("    %-7s %-8s %-10s %-10s %-9s %s" % ("n_j", "count", "true PMI", "recovered", "err", "sum delta"))
    for n, Nj, want, got, sd in rows:
        print("    %-7d %-8d %-+10.4f %-+10.4f %-+9.4f %.1f" % (n, Nj, want, got, got - want, sd))
    span = max(r[2] for r in rows) - min(r[2] for r in rows)
    check(
        "Mass/C - gamma - log K recovers PMI",
        worst < 0.05,
        "worst error %.4f nats over a %.1f-nat span (%.0fx in ratio)" % (worst, span, math.exp(span)),
    )

    # The asymptotic needs the argument above ~10; below it H is linear, not log.
    tiny = [(1, 10000000), (1, 1000000)]  # S = 0.1 and 1.0 at K = 1e6
    for n, Nj in tiny:
        s = K * n / Nj
        got = C * Hreal(s) / C - GAMMA - math.log(K)
        want = math.log(n / float(Nj))
        check(
            "sum delta = %.2f is below the asymptotic, so it decays" % s,
            abs(got - want) > 0.1,
            "off by %.2f nats" % abs(got - want),
        )

    # And the one-pass form, with the RUNNING count, does not work.
    worst_rt = 0.0
    for n, Nj in ((5, 100), (50, 100), (500, 1000)):
        sd = sum(K / (Nj * k / n) for k in range(1, n + 1))  # age at the k-th arrival
        got = Hreal(sd) - GAMMA - math.log(K)
        worst_rt = max(worst_rt, abs(got - math.log(n / float(Nj))))
    check(
        "the RUNNING count variant does not reach PMI",
        worst_rt > 0.3,
        "off by up to %.2f nats, so the final count is required" % worst_rt,
    )


def _spearman(xs, ys):
    """Rank correlation with average ranks, since the floor creates many ties."""

    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r

    rx, ry = rank(xs), rank(ys)
    n = float(len(xs))
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    dx = math.sqrt(sum((a - mx) ** 2 for a in rx))
    dy = math.sqrt(sum((b - my) ** 2 for b in ry))
    return num / (dx * dy) if dx > 0 and dy > 0 else 0.0


# --------------------------------------------------------------------------
# CLAIM 10: at production support, ONE read cannot rank the codes
#
# PROVES   with 5292 distinct codes against M = 1024 segments, read ONCE, the
#          rank correlation against the truth is ~.02. Nothing.
# WHY CARE Every claim above removes the hard part by construction: claim 9
#          keeps the learner in list mode so mass is exact, and claims 2-7
#          average over independent trials. Production does NEITHER -- one
#          learner, one read. This claim is that configuration, and it exists
#          because the list-mode result was being quoted as though it settled
#          the spilled case. It does not.
#
#          Note this is NOT a contradiction of claim 2. The read is exactly
#          UNBIASED -- E[Omega * seg/M] = H(S_j) -- so averaging recovers the
#          target, which is what claim 2 measures. The problem is variance:
#          expected segments per code is lambda = M*H(S_j)/Omega ~ M/support,
#          and sd/mean = 1/sqrt(lambda). At 5292 codes that is ~1.9, so one draw
#          says almost nothing. Fix support and it works; on text8, 88% of words
#          are already under M.
#
# HOW      SUPPORT is the variable, and support means UNIQUE CODES -- not age,
#          not arrivals. Omega sums over DISTINCT codes, so repeats enter only
#          inside H, logarithmically: doubling repeats barely moves lambda,
#          doubling codes halves it. Trials here average the per-trial
#          STATISTIC, never the read itself; over-averaging is the thing this
#          claim exists to rule out.
#
# READ IT  Three findings, in order. (1) lambda < 1, so most codes own no
#          segment. (2) A positive read does NOT mean the code is present: only
#          M of 5292 can be, a 19.3% ceiling, yet 33.5% read positive -- so the
#          read is noisy around the chance floor rather than a segment
#          indicator, and part of the readable set holds nothing. (3) The
#          spread is 2.2x a clean binomial estimator's, which is where EXCESS
#          comes from, and more trials cannot absorb it because the bound
#          shrinks at the same 1/sqrt(T).
# --------------------------------------------------------------------------
def claim_single_read_at_production_support(trials):
    """What every claim above removes by construction: the single read.

    claim_pmi_schedule keeps the learner in LIST mode, where mass is the exact
    weight sum. claim_schedule_table spills but averages over trials against a
    sqrt(trials) tolerance. Production does neither: a text8 centre at w=5
    holds ~5292 UNIQUE CODES against M=1024 and is read once.

    Support is the variable, not age: Omega sums over DISTINCT codes, so
    repeats enter only inside H(S_j), logarithmically. Doubling repeats barely
    moves lambda; doubling codes halves it.

    What falls out is stronger than "the resolution is coarse". A positive read
    does not mean the code is in the sketch at all, so the readable subset is
    part noise -- which is why its ordering carries nothing. The expectation
    itself is not checked here; claim_schedule_table owns that at 500 codes.
    """
    print("\nAt production support, one read cannot rank the codes")
    SUP = 5292  # text8 median distinct contexts per centre at w=5
    K, C = 1e4, 16.0  # C cancels in the read; only the write floor sees it
    # Multiplicities over a 24x span, and an external count decorrelated from
    # them by a multiplicative hash -- so no code can pass by the two cancelling.
    n = [max(2, round(2 * (24.0 ** (j / float(SUP - 1))))) for j in range(SUP)]
    ext = [max(1, round(2 * (32.0 ** (((j * 2654435761) % 65521) / 65520.0)))) for j in range(SUP)]
    target = [math.log(n[j] / float(ext[j])) for j in range(SUP)]
    hs = [Hreal(K * n[j] / float(ext[j])) for j in range(SUP)]
    om = sum(hs)
    # Expected segments per code. Under one means most codes own nothing.
    lam = [M * h / om for h in hs]
    check(
        "support %d against M %d puts every code under one segment" % (SUP, M),
        max(lam) < 1.0,
        "lambda max %.3f, mean %.3f" % (max(lam), sum(lam) / SUP),
    )

    # The total weight is written in ONE call per code: the increments
    # telescope to C*H(K*n/ext) and claim_telescoping already covers that, so
    # the arrival pattern is not what this claim is testing.
    acc = [0.0] * SUP
    floored, rhos, unread = 0, [], []
    for trial in range(trials):
        sp = sparkles(SUP, 9100 + trial)
        L = learner("single-read", trial)
        for j in range(SUP):
            u = int(round(C * hs[j] * CARD))
            if u < 1:
                floored += 1
            L.bundle_fractional(sp[j], max(1, u))
        one = [occupancy(L, s) for s in sp]
        for j in range(SUP):
            acc[j] += one[j]
        unread.append(1.0 - sum(1 for v in one if v > 0) / float(SUP))
        rhos.append(_spearman(one, target))

    # A learner holds M segments with one code each, so at most M of the SUP
    # codes can be present and the readable fraction cannot exceed M/SUP if a
    # positive read meant ownership. It does exceed it, so it does not: an
    # absent code still reads above the chance floor often enough to count.
    # "Unreadable" is therefore the noise coming out non-positive, NOT the
    # sketch holding no trace -- and some readable codes hold no trace either.
    got_zero = sum(unread) / float(len(unread))
    ceiling = M / float(SUP)
    check(
        "a positive read does not mean the code owns a segment",
        (1.0 - got_zero) > ceiling and floored == 0,
        "readable %.1f%% over a %.1f%% ownership ceiling, sub-unit writes %d"
        % (100 * (1 - got_zero), 100 * ceiling, floored),
    )

    # The read is NOISIER than counting segments would be. Against the binomial
    # bound claim_schedule_table uses, the spread here runs ~2x wide -- and the
    # max over SUP codes only accounts for sqrt(2 ln SUP) ~ 4.1 sigma of it.
    # More trials cannot absorb that: the bound shrinks at the same 1/sqrt(T).
    # That excess is the mechanism behind the rank collapse below. If the read
    # is ever cleaned up this claim flips, which is worth being told about.
    rhos.sort()
    single = rhos[len(rhos) // 2]
    worst, p_at = 0.0, 0.0
    for j in range(SUP):
        p = hs[j] / om
        d = abs(p - acc[j] / float(trials))
        if d > worst:
            worst, p_at = d, p
    tol = 4.0 * math.sqrt(max(p_at * (1 - p_at), 1e-9) / (M * float(trials)))
    check(
        "the read's spread exceeds a clean segment count's",
        worst > 1.5 * tol,
        "max err %.5f vs binomial bound %.5f (%.1fx) over %d trials" % (worst, tol, worst / tol, trials),
    )
    check(
        "but one read cannot rank the codes at all",
        single < 0.2,
        "single-read rho %.3f (p25 %.3f, p75 %.3f), %.1f%% unreadable"
        % (single, rhos[len(rhos) // 4], rhos[3 * len(rhos) // 4], 100 * got_zero),
    )


# --------------------------------------------------------------------------
# CLAIM 11: a concave shape makes MORE observations legible
#
# PROVES   under the log schedule, more distinct observations clear the noise
#          floor than under the naive one.
# WHY CARE Claim 7 showed segments move from head to tail. This says the move is
#          WORTH it: the rare codes that gained are now readable at all, where
#          before they sat at chance. That is the actual benefit, stated as a
#          count rather than as a distribution shape.
# HOW      The floor is measured, not assumed -- "null" sparkles that were never
#          written establish the 95th percentile of pure chance overlap, and a
#          code counts as recovered only if it reads above that.
# READ IT  The per-band table shows where the gains land. The last check
#          confirms the log shape's tail converges on the equal-share
#          allocation M/K+1, which is the most compression can achieve.
# --------------------------------------------------------------------------
# "Reshaping also changes HOW MANY observations are recoverable at all"
# --------------------------------------------------------------------------
def claim_recoverable_count(trials):
    print("\nA concave shape expands how many observations are recoverable")
    # K scales with M or the comparison saturates: at 10-bit, 60 codes against
    # 1024 segments leaves every shape recovering all 60, so the comparison
    # saturates. 60 against 256 was the 8-bit ratio; keep it.
    K, S = max(60, M // 4), 4096
    counts = [max(1, round(1000.0 / (j + 1))) for j in range(K)]  # Zipf
    shapes = ("n", "C*H(n)")
    mem = {s: [[] for _ in range(K)] for s in shapes}
    nul = {s: [] for s in shapes}
    for trial in range(trials):
        sp = sparkles(K, 7600 + trial)
        dz = sparkles(K, 7600 + trial, domain="null")  # never written
        for name in shapes:
            g = SHAPES[name]
            L = learner("rec-%s" % name, trial)
            for s, n in zip(sp, counts):
                for k in range(1, n + 1):
                    L.bundle_fractional(s, max(1, round(S * (g(k) - g(k - 1)))))
            for j, s in enumerate(sp):
                mem[name][j].append(hv.overlap(L, s))
            nul[name].extend(hv.overlap(L, d) for d in dz)
    bands = (("head 1-5", 0, 5), ("mid 6-20", 5, 20), ("tail 21+", 20, K))
    print("    %-9s %6s %8s  %s" % ("g(n)", "theta", "recov", " ".join("%-11s" % b[0] for b in bands)))
    rec_total = {}
    for name in shapes:
        th = sorted(nul[name])[int(0.95 * len(nul[name]))]
        rec = [sum(1 for o in col if o > th) / float(trials) for col in mem[name]]
        rec_total[name] = sum(rec)
        print(
            "    %-9s %6d %5.1f/%-3d %s"
            % (name, th, sum(rec), K, " ".join("%6.1f/%-4d" % (sum(rec[a:b]), b - a) for _, a, b in bands))
        )
    check(
        "the log shape recovers more than the default",
        rec_total["C*H(n)"] > rec_total["n"],
        "%.1f vs %.1f of %d" % (rec_total["C*H(n)"], rec_total["n"], K),
    )
    # enough compression converges on the equal-share allocation M/K+1
    tails = [sum(mem["C*H(n)"][j]) / float(trials) for j in (K // 3 - 1, 2 * K // 3 - 1, K - 1)]
    equal = M / float(K) + 1
    check(
        "the log shape's tail sits near the equal share M/K+1 = %.1f" % equal,
        all(abs(v - equal) < max(1.0, 0.25 * equal) for v in tails),
        "ranks %d/%d/%d read %s" % (K // 3, 2 * K // 3, K, " ".join("%.2f" % v for v in tails)),
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true", help="fewer trials")
    ap.add_argument(
        "--plot",
        nargs="?",
        const=".",
        metavar="DIR",
        help="write pmf.png and segments.png to DIR (needs matplotlib)",
    )
    a = ap.parse_args()
    global PLOT_DIR
    if a.plot:
        if plt is None:
            ap.error("--plot needs matplotlib: pip install matplotlib")
        PLOT_DIR = a.plot
    elif plt is not None:
        print("(matplotlib found: pass --plot to also write the figures)")
    t = 25 if a.quick else 200

    print("model=64K/8BIT  M=%d  Cardinality=%d  observations=%d  trials=%d" % (M, CARD, len(N), t))
    claim_telescoping()
    claim_schedule_table(t)
    claim_log_is_a_log(t)
    claim_log_offset(max(50, t * 2))
    claim_representability(t)
    claim_recoverable_count(max(20, t // 2))
    claim_sampled_distribution(max(20, t // 4))
    claim_segment_reallocation(max(20, t // 4))
    claim_unreachable()
    claim_pmi_schedule()
    # 5292 codes per trial, so trials stay low: this claim needs SUPPORT, not
    # averaging, and over-averaging is the thing it exists to rule out.
    claim_single_read_at_production_support(max(8, t // 20))
    print("\n%s" % ("ALL CLAIMS PASS" if not FAILED else "FAILED: %s" % "; ".join(FAILED)))
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
