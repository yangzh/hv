#!/usr/bin/env python3
"""What a Learner actually holds, measured rather than asserted.

A Learner is usually described as a bundle of observations.
More precisely, each of its M segments is an independent single-slot WEIGHTED RESERVOIR
over the stream of observations, and that one fact determines everything you can read back:

    P(a segment ends up owned by the write at position t) = omega_t / Omega

an observation owns a share of the vector equal to its share of the total weight
-- exactly, at every age, regardless of arrival order.
With every write carrying weight 1 this degenerates to the familiar case,
where the learner tracks the empirical frequency P(A_j) and `occupancy` produces
an unbiased estimate of it.

This script checks each of those statements against the library and prints
PASS/FAIL with the measured number beside the predicted one. Tolerances come
from the sampling spread, so they hold at any trial count rather than being
tuned to this run.

    pip install kongming-rs-hv
    python learner_revisited.py            # a few seconds
    python learner_revisited.py --quick    # fewer trials, same claims

See weighted_schedule.py for what happens once the weights are not all 1 — and
for `--plot`, which draws the resulting mass functions if matplotlib is
installed:

    pip install matplotlib
    python weighted_schedule.py --plot DIR   # DIR defaults to . if omitted
    open DIR/pmf.png DIR/segments.png        # macOS; xdg-open elsewhere
"""

import argparse
import math
import random

from kongming import hv

MODEL = hv.MODEL_64K_8BIT
M = hv.cardinality(MODEL)  # segment count; the doc's M
FAILED = []


def check(claim, ok, detail):
    print("  [%s] %-58s %s" % ("PASS" if ok else "FAIL", claim, detail))
    if not ok:
        FAILED.append(claim)


def sparkles(k, seed, domain="v"):
    so = hv.SparseOperation(MODEL, 0, seed)
    return [hv.Sparkle.random(domain, so) for _ in range(k)]


def learner(domain, pod):
    return hv.Learner(MODEL, hv.Seed128(domain, str(pod)))


# --------------------------------------------------------------------------
# "every model keeps M = q (so RandomOverlap == 1)"
# --------------------------------------------------------------------------
def claim_random_overlap():
    print("\nRandomOverlap == 1 for every model, because M = 1/sparsity")
    for name in ("MODEL_64K_8BIT", "MODEL_1M_10BIT", "MODEL_16M_12BIT", "MODEL_256M_14BIT", "MODEL_4G_16BIT"):
        m = getattr(hv, name)
        card, spars, ro = hv.cardinality(m), hv.sparsity(m), hv.random_overlap(m)
        check(
            "%s: M == 1/sparsity, RandomOverlap == 1" % name.replace("MODEL_", ""),
            abs(card * spars - 1.0) < 1e-12 and ro == 1,
            "M=%d  1/sparsity=%.0f  RandomOverlap=%d" % (card, 1.0 / spars, ro),
        )


# --------------------------------------------------------------------------
# "One segment, one owner, so the similarities to all its observations sum to M,
# up to chance collisions."
# --------------------------------------------------------------------------
def claim_overlaps_sum_to_M(trials):
    print("\nOverlaps over all observations sum to M (one segment, one owner)")
    K = 12
    tot = 0.0
    for trial in range(trials):
        sp = sparkles(K, 9100 + trial)
        L = learner("sum", trial)
        for i, s in enumerate(sp):
            for _ in range(i + 1):  # unequal multiplicities
                L.bundle(s)
        tot += sum(hv.overlap(L, s) for s in sp)
    mean = tot / trials
    # each of K members adds its own chance floor of RandomOverlap=1 on the
    # segments it does not own, so the sum overshoots M by at most K-1.
    check("sum_j O(L,A_j) in [M, M+K)", M <= mean < M + K, "measured %.2f, M=%d, K=%d" % (mean, M, K))


# --------------------------------------------------------------------------
# "For K of them equally weighted: E[O(L,A_j)] ~ M/K + 1"
# --------------------------------------------------------------------------
def claim_centroid(trials):
    print("\nE[O(L,A_j)] ~ M/K + 1 for K equally weighted observations")
    for K in (4, 16, 64, 256):
        tot = 0.0
        for trial in range(trials):
            sp = sparkles(K, 9200 + trial)
            L = learner("cent%d" % K, trial)
            for s in sp:
                L.bundle(s)
            tot += sum(hv.overlap(L, s) for s in sp) / float(K)
        mean, pred = tot / trials, M / float(K) + 1
        # sampling spread on a mean of K*trials reads; 3% covers it at every K
        check(
            "K=%-3d  E[O] ~ M/K+1" % K,
            abs(mean - pred) <= 0.03 * pred + 0.05,
            "predicted %.2f, measured %.2f" % (pred, mean),
        )


# --------------------------------------------------------------------------
# "E[O(L,A_j)] = P(A_j)(M-1) + 1" and "Occupancy = (O-1)/(M-1) = P(A_j)"
# --------------------------------------------------------------------------
def claim_occupancy(trials):
    print("\nE[O] = P(M-1)+1, and Occupancy inverts it to P(A_j)")
    counts = [50, 30, 10, 6, 4, 2, 1, 2, 2, 1, 1, 1]  # 12 distinct, sums to 111
    n = float(sum(counts))
    accO = [0.0] * len(counts)
    accB = [0.0] * len(counts)
    for trial in range(trials):
        sp = sparkles(len(counts), 9300 + trial)
        L = learner("bary", trial)
        for s, c in zip(sp, counts):
            L.bundle_multiple(s, c)
        for j, s in enumerate(sp):
            accO[j] += hv.overlap(L, s)
            accB[j] += L.occupancy(s)
    eO = eB = 0.0
    for j, c in enumerate(counts):
        p = c / n
        eO = max(eO, abs(accO[j] / trials - (p * (M - 1) + 1)))
        eB = max(eB, abs(accB[j] / trials - p))
    check("max |E[O] - (P(M-1)+1)| < 1 overlap", eO < 1.0, "max err %.3f overlaps" % eO)
    check("max |Occupancy - P| < 1/M", eB < 1.0 / M, "max err %.5f (1/M=%.5f)" % (eB, 1.0 / M))


# --------------------------------------------------------------------------
# "An observation owns a share of the vector equal to its share of the total
#  weight -- EXACTLY, at every age, with no dependence on arrival order."
# --------------------------------------------------------------------------
def stderr_bound(p, trials, sigmas=4.0):
    """Sampling bound on a mean occupancy over `trials` independent learners.

    Notation follows the design note: t indexes WRITE POSITIONS in the stream,
    j indexes DISTINCT codes, and k is one code's own repeat index.

    One learner reads an observation's share off M segments, so a single read
    has SD <= sqrt(p(1-p)/M) -- the binomial form, which the doc measures as
    conservative by ~2x (see "The write draws a shared count"). Averaging over
    trials divides that by sqrt(trials). This is the right yardstick for a mean;
    1/M is the resolution of ONE read and is not a bound on anything averaged.
    """
    return sigmas * math.sqrt(max(p * (1 - p), 1e-9) / (M * float(trials)))


def claim_occupancy_is_weight_share(trials):
    # occupancy of code j == omega_j / Omega, its share of the total weight
    print("\nAn observation's occupancy IS its share of the total weight")
    # every weight is kept above the 1/M resolution floor on purpose: a share of
    # less than one segment is indistinguishable from chance (see the floor claim
    # below), so the identity cannot be read off it whatever the estimator does.
    w = [40, 50, 60, 80, 100, 120, 150, 200, 260, 340, 450, 600]
    W = float(sum(w))
    acc = [0.0] * len(w)
    for trial in range(trials):
        sp = sparkles(len(w), 9400 + trial)
        L = learner("resv", trial)
        for s, wi in zip(sp, w):
            L.bundle_multiple(s, wi)
        for j, s in enumerate(sp):
            acc[j] += L.occupancy(s)
    worst = max((abs(acc[j] / trials - w[j] / W), w[j] / W) for j in range(len(w)))
    err, p = worst
    tol = stderr_bound(p, trials)
    check("max |occupancy - omega_j/W_n| within sampling bound", err < tol, "max err %.5f, 4*SE %.5f" % (err, tol))


def claim_order_independence(trials):
    print("\nNo dependence on arrival order")
    w = [40, 50, 60, 80, 100, 120, 150, 200, 260, 340, 450, 600]
    W = float(sum(w))
    rng = random.Random(7)
    # mean occupancy per arrival order; a single learner differs between orders
    # by sampling noise alone, so the claim is about the means, not one draw.
    means = [[0.0] * len(w) for _ in range(3)]
    for trial in range(trials):
        sp = sparkles(len(w), 9500 + trial)
        stream = [j for j, wi in enumerate(w) for _ in range(wi)]
        for v in range(3):
            order = list(stream)
            rng.shuffle(order)
            L = learner("ord%d" % v, trial)
            for j in order:
                L.bundle(sp[j])
            for j, s in enumerate(sp):
                means[v][j] += L.occupancy(s) / trials
    worst, at_p = 0.0, 0.0
    for j in range(len(w)):
        col = [means[v][j] for v in range(3)]
        if max(col) - min(col) > worst:
            worst, at_p = max(col) - min(col), w[j] / W
    tol = stderr_bound(at_p, trials) * math.sqrt(2)  # difference of two means
    check("spread of per-order means within sampling bound", worst < tol, "max spread %.5f, bound %.5f" % (worst, tol))


def claim_age_counts_observations():
    print("\nAge counts OBSERVATIONS, not weight (it is the stream length)")
    sp = sparkles(1, 9550)
    a = learner("agea", 0)
    a.bundle_multiple(sp[0], 5)
    b = learner("ageb", 0)
    for _ in range(5):
        b.bundle(sp[0])
    check(
        "one observation of weight 5 -> age 1; five of weight 1 -> age 5",
        a.age() == 1 and b.age() == 5,
        "ages %d and %d; both hold %d units of mass" % (a.age(), b.age(), a.mass_units(sp[0])),
    )
    check(
        "both routes accumulate the same mass",
        a.mass_units(sp[0]) == b.mass_units(sp[0]),
        "mass_units %d == %d" % (a.mass_units(sp[0]), b.mass_units(sp[0])),
    )


def claim_no_drift(trials):
    print("\nNo drift toward the dominant observation (the doc's drift table)")
    counts = [50, 30, 10, 6, 4, 2, 1]
    extra = [2, 2, 1, 1, 1]  # 12 distinct observations in total
    n = float(sum(counts) + sum(extra))
    rng = random.Random(11)
    rows, ages = {}, {}
    for mult in (1, 100):
        acc = [0.0] * len(counts)
        for trial in range(trials):
            sp = sparkles(len(counts) + len(extra), 9600 + trial)
            L = learner("drift%d" % mult, trial)
            # iid shuffled unit-weight writes, as the doc's run describes: this
            # is what makes Age() the stream length rather than a call count
            stream = [j for j, c in enumerate(counts + extra) for _ in range(c * mult)]
            rng.shuffle(stream)
            for j in stream:
                L.bundle(sp[j])
            ages[mult] = L.age()
            for j in range(len(counts)):
                acc[j] += hv.overlap(L, sp[j])
        rows[mult] = [a / trials for a in acc]
        print("    O at age %-6d %s" % (ages[mult], " ".join("%7.2f" % v for v in rows[mult])))
    pred = [c / n * (M - 1) + 1 for c in counts]
    print("    %-14s %s" % ("P(M-1)+1", " ".join("%7.2f" % v for v in pred)))
    check(
        "Age() == stream length under unit writes",
        ages[1] == int(n) and ages[100] == int(n) * 100,
        "ages %d and %d for streams of %d and %d" % (ages[1], ages[100], n, n * 100),
    )

    # same bound as elsewhere, in overlap units: SD of one read is
    # sqrt(M p(1-p)), a mean over trials divides by sqrt(trials)
    def olap_bound(p, sigmas=4.0, pairs=1.0):
        return sigmas * math.sqrt(M * max(p * (1 - p), 1e-9) / trials) * math.sqrt(pairs)

    worst = max(((abs(a - b), c / n) for a, b, c in zip(rows[1], rows[100], counts)))
    moved, p_at = worst
    tol = olap_bound(p_at, pairs=2.0)
    check(
        "100x longer stream does not move O beyond sampling noise",
        moved < tol,
        "max move %.2f overlaps, bound %.2f" % (moved, tol),
    )
    worst = max(((abs(m - q), c / n) for m, q, c in zip(rows[100], pred, counts)))
    err, p_at = worst
    tol = olap_bound(p_at)
    check(
        "matches P(M-1)+1 (collapse onto the head would read M=%d)" % M,
        err < tol,
        "max err %.2f overlaps, bound %.2f" % (err, tol),
    )


# --------------------------------------------------------------------------
# "the resolution floor is 1/M: an observation accounting for less than 1/256
#  of a learner's writes is indistinguishable from chance"
# --------------------------------------------------------------------------
def claim_resolution_floor(trials):
    print("\nResolution floor 1/M, independent of stream length")
    # one observation at just under 1/M of the stream, one at 4x that
    for share, expect_sep in ((0.6 / M, False), (4.0 / M, True)):
        for total in (4000, 40000):
            rare = max(1, int(round(share * total)))
            bulk = (total - rare) // 20
            hits, nulls = [], []
            for trial in range(trials):
                sp = sparkles(21, 9700 + trial)
                nl = sparkles(20, 9700 + trial, domain="null")
                L = learner("floor%d" % total, trial)
                L.bundle_multiple(sp[0], rare)
                for s in sp[1:]:
                    L.bundle_multiple(s, bulk)
                hits.append(hv.overlap(L, sp[0]))
                nulls.extend(hv.overlap(L, d) for d in nl)
            th = sorted(nulls)[int(0.95 * len(nulls))]
            rate = sum(1 for o in hits if o > th) / float(len(hits))
            sep = rate > 0.5
            check(
                "share=%.2f/M, n=%-5d  %s" % (share * M, total, "separable" if expect_sep else "at chance"),
                sep == expect_sep,
                "detected %.0f%% of the time (theta=%d)" % (100 * rate, th),
            )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true", help="fewer trials")
    a = ap.parse_args()
    t = 20 if a.quick else 200

    print(
        "model=64K/8BIT  M=cardinality=%d  segment_size=%d  width=%d  trials=%d"
        % (M, hv.segment_size(MODEL), hv.width(MODEL), t)
    )

    claim_random_overlap()
    claim_overlaps_sum_to_M(t)
    claim_centroid(max(40, t // 5))
    claim_occupancy(t)
    claim_occupancy_is_weight_share(t)
    claim_order_independence(max(20, t // 4))
    claim_age_counts_observations()
    claim_no_drift(max(40, t // 2))
    claim_resolution_floor(max(40, t // 2))

    print("\n%s" % ("ALL CLAIMS PASS" if not FAILED else "FAILED: %s" % "; ".join(FAILED)))
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
