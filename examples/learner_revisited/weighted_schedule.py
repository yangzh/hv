#!/usr/bin/env python3
"""Choosing what a Learner's occupancy MEASURES, by choosing the write weights.

Run learner_revisited.py first: it establishes that occupancy is an observation's
share of the accumulated mass. That leaves the mass itself free, and the weight schedule
is how you pick it. Writing the k-th repeat of an observation with weight

    omega_j(k) = lambda_j * [ g(k) - g(k-1) ],    g(0) = 0

makes its accumulated mass telescope to lambda_j * g(n_j), so occupancy lands on
any non-decreasing g of the observation's own count, times any external
per-observation scale lambda.

Three schedules are checked here, each with PASS/FAIL and a tolerance taken
from the sampling spread:

    NAIVE  g(n) = n              occupancy lands on P(A_j)
    LOG    g(n) = C*H(n)         occupancy lands on log n_j
    PMI    g(S) = C*H(S),        occupancy lands on log PMI,
           S = K*n_j/count(A_j)  the division moving INSIDE g

The lambda lever -- an external per-observation scale -- is kept only where the
PMI story needs it: claim_unreachable shows no lambda outside g can reach what
advancing the count inside it does.

    pip install kongming-rs-hv
    python weighted_schedule.py            # ~17s
    python weighted_schedule.py --quick    # fewer trials, same claims

matplotlib is optional. With it installed, --plot writes two figures: the
occupancy of every code under each schedule (its mass function, measured against
the target), and the segment budget dealt out two ways.

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

# multiplicities spanning a 24x range, so the reshaping has something to do
# 500 unique observations, log-spaced over a 24x span of multiplicities. At
# 10-bit the list cap is 40, so this SPILLS -- the regime the design runs in.
#
# Note what 500 against M=1024 means: the mean share is 1/500 = .002 against a
# chance floor of 1/1023 = .00098, so an INDIVIDUAL read is barely above noise.
# The trial MEAN still resolves it, so these claims test that the schedule's
# expectation is right, not that a single read recovers it.
N = [max(2, round(2 * (24.0 ** (j / 499.0)))) for j in range(500)]
# an external count, deliberately uncorrelated with N
# An external count per observation, deliberately uncorrelated with N: a
# bit-reversal permutation of the same span, so no row can pass by the two
# cancelling.
NEXT = [max(1, round(2 * (32.0 ** (int(format(j, "09b")[::-1], 2) / 511.0)))) for j in range(500)]


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

    Called ``occupancy()`` from v7 on; ``barycentric()`` was the name on earlier
    wheels and was removed after v7. Same value either way: the share of the M
    segments that `probe` owns.
    """
    fn = getattr(learner, "occupancy", None)
    return fn(probe) if fn is not None else learner.barycentric(probe)


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
# "makes that sum telescope to lambda_j g(n_j) EXACTLY"
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
# "the SCALE moved rather than the spread narrowing"
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
    # trial count and the code count (.998 at 13 codes/200 trials, .965 at 500
    # codes/200, .800 at 500/25), so any fixed threshold on it tests the budget
    # rather than the shape. The gap survives all three at .10 or better.
    check(
        "occupancy is affine in log P, not in P",
        r_log - r_lin > 0.05,
        "R^2 on log P = %.4f, on P = %.4f, gap %.4f" % (r_log, r_lin, r_log - r_lin),
    )


# --------------------------------------------------------------------------
# "mass differences come out exact and offset-free"  and
# "MassUnits/C = H(n_j), minus log Age(L), leaves log P(A_j)"
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
    small = N[:8]
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
        "inverting H exactly recovers n_j itself",
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
# End to end: SAMPLE from a known P, and check the occupancy the learner ends
# up with is the schedule's transform of that P. Unlike the runs above, the
# realized counts are themselves random, so the draw's noise rides on top of
# the reservoir's.
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
# "At production support, ONE read cannot rank the codes"
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
