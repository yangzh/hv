#!/usr/bin/env python3
"""A Point in 3-D: why the coordinates are kept, and the three ways to read them.

Rank 3 is where the design decision behind `Point` becomes visible. The vector
itself is just a bind of powers,

    Point = b0**c0  (x)  b1**c1  (x)  b2**c2

but the object also CARRIES its coordinates as exact rationals, and that is not
redundancy. Bind is not additive on fractional powers: `K**u (x) K**v` agrees
with `K**(u+v)` on only about half the segments, because flooring each factor
separately loses what flooring the sum keeps. So arithmetic on an encoded value
cannot be done on the vector — it has to happen on the rationals and truncate
ONCE, at materialization. A Point can do that. A bare `SparseSegmented`, having
already spent its exponents into its offsets, cannot.

Reading coordinates back off a raw vector has three routines, one per regime,
and this script exercises each separately:

    recover_point            integer coordinates    exact solve, mod W
    recover_point_fractional a 1/2**level grid       LLL lattice + polish
    recover_point_noisy      corrupted offsets       RANSAC over the solve

    pip install kongming-rs-hv
    python point_3d.py

See point_2d.py for the fundamentals: what a frame is, why the surplus
equations matter, and why coordinates are only ever modulo W.

NOTE: `Point` and the `recover_point*` functions are newer than the published
kongming-rs-hv release. If `hv.Point` raises AttributeError, your installed
wheel predates them.
"""

import random

from kongming import hv

MODEL = hv.MODEL_1M_10BIT
W = hv.cardinality(MODEL)  # 1024 segments, and the modulus coordinates live in
RANK = 3
FAILED = []


def check(claim, ok, detail):
    print("  [%s] %-58s %s" % ("PASS" if ok else "FAIL", claim, detail))
    if not ok:
        FAILED.append(claim)


def axes(n=RANK, tag="ax", model=MODEL):
    return [hv.Sparkle(model, hv.d0(), "%s%d" % (tag, i)) for i in range(n)]


def corrupt(raw, bad, rng, model=MODEL):
    """Shift `bad` distinct offsets by 3, chosen at random."""
    o = list(raw.offsets())
    size = hv.cardinality(model)
    for seg in rng.sample(range(size), bad):
        o[seg] = (o[seg] + 3) % size
    return hv.SparseSegmented.from_offsets(model, o)


# --------------------------------------------------------------------------
# "Point = b0**c0 (x) b1**c1 (x) b2**c2 — three factors, one bind."
# --------------------------------------------------------------------------
def claim_is_the_bind():
    print("\nA rank-3 Point is the bind of three powers")
    a, b, c = axes()

    p = hv.Point([a, b, c], [11, 28, 45])
    by_hand = hv.bind(hv.bind(a.power(11), b.power(28)), c.power(45))
    check(
        "Point(frame,[11,28,45]) == bind of the three powers",
        p.stable_hash() == by_hand.stable_hash(),
        "rank=%d  hash 0x%016x" % (p.rank(), p.stable_hash()),
    )

    # The frame is reachable from the Point, because a Point is meaningless
    # without it — the same offsets denote different positions under different
    # bases, which is also why the frame travels on the wire.
    check(
        "the Point carries its own frame",
        [x.stable_hash() for x in p.frame()] == [a.stable_hash(), b.stable_hash(), c.stable_hash()],
        "%d axes recoverable from the Point" % len(p.frame()),
    )


# --------------------------------------------------------------------------
# "recover_point: integer coordinates come back EXACTLY, on every model."
# --------------------------------------------------------------------------
def claim_recover_point():
    print("\nrecover_point — the exact solve, rank 3")
    a, b, c = axes()

    # An integer power scales offsets without truncating (floor(o*k) == o*k),
    # so each segment gives one exact linear equation mod W. 1024 equations,
    # 3 unknowns: Gaussian elimination solves it, the surplus verifies.
    for coords in ([11, 28, 45], [0, 0, 1], [1, 0, 0], [W - 1, 1, W - 2], [512, 512, 512]):
        p = hv.Point([a, b, c], coords)
        got = hv.recover_point([a, b, c], p.core())
        check(
            "coords %-18s recovered exactly" % (coords,),
            got.coords() == p.coords() and hv.equal(got, p),
            "%s" % (got.coords(),),
        )

    # The solve is model-independent: it only needs offsets and the modulus, so
    # it is exact from 8-bit through 16-bit.
    print("  -- and on every model --")
    for name in ("MODEL_64K_8BIT", "MODEL_1M_10BIT", "MODEL_16M_12BIT", "MODEL_256M_14BIT", "MODEL_4G_16BIT"):
        m = getattr(hv, name)
        f = axes(RANK, "m", m)
        want = [3, 7, 11]
        p = hv.Point(f, want)
        got = hv.recover_point(f, p.core())
        check(
            "%-14s exact at rank 3" % name.replace("MODEL_", ""),
            got.coords() == p.coords(),
            "M=%d" % hv.cardinality(m),
        )


# --------------------------------------------------------------------------
# "recover_point_fractional: a 1/2**level grid, via lattice reduction."
# --------------------------------------------------------------------------
def claim_recover_point_fractional():
    print("\nrecover_point_fractional — LLL + polish, rank 3")
    a, b, c = axes()

    # Now the power TRUNCATES, so the equations hold only up to a small unknown
    # error and the problem stops being a solve. Undoing the floor leaves a
    # linear system mod 2**level * W with bounded error — a closest-vector
    # problem. LLL reduces a lattice over 4*rank segments to place the answer
    # globally, then a polish pass scores it against all 1024 to pin it.
    #
    # Exponents stay at or above 1: below 1 the encoding degenerates and
    # different bases stop being orthogonal, so a value A rides as 2**level + A.
    for level in (8, 10, 12):
        den = 1 << level
        vals = [137 % den, 901 % den, 55 % den]
        p = hv.Point([a, b, c], [(den + v, den) for v in vals])
        got = hv.recover_point_fractional([a, b, c], p.core(), level)
        check(
            "level=%-2d  A=%-16s recovered" % (level, vals),
            hv.equal(got, p),
            "%s" % (got.coords(),),
        )

    # Reliability is governed by rank/W, so it follows the MODEL rather than the
    # level. At 10-bit (W=1024) rank 3 is far inside the comfortable region; on
    # 8-bit (W=256) the same rank is near the edge.
    check(
        "rank 3 of W=%d is well inside rank << W" % W,
        RANK * 8 < W,
        "noise/modulus = rank/W = %.4f" % (RANK / float(W)),
    )

    # The lattice runs in 64-bit integers, so level + the model's sparsity bits
    # is capped at 28. Past that it refuses rather than overflowing silently.
    try:
        hv.recover_point_fractional([a, b, c], hv.Point([a, b, c], [1, 1, 1]).core(), 19)
        check("level past the 28-bit lattice budget is refused", False, "accepted anyway")
    except ValueError as e:
        check(
            "level past the 28-bit lattice budget is refused",
            "past the 28" in str(e),
            "level 19 + 10 sparsity bits = 29",
        )


# --------------------------------------------------------------------------
# "recover_point_noisy: consensus survives corruption the solve cannot."
# --------------------------------------------------------------------------
def claim_recover_point_noisy():
    print("\nrecover_point_noisy — RANSAC over the solve, rank 3")
    rng = random.Random(11)
    a, b, c = axes()
    p = hv.Point([a, b, c], [11, 28, 45])
    raw = p.core()

    # The exact solve is brittle on purpose. Coordinates live in a modular
    # group with no notion of "close", so a corrupted offset among the three
    # the elimination pivots on does not perturb the answer — it randomizes it.
    try:
        hv.recover_point([a, b, c], corrupt(raw, 1, rng))
        check("one bad offset defeats recover_point", False, "recovered anyway")
    except ValueError:
        check("one bad offset defeats recover_point", True, "1 of %d segments is enough" % W)

    # The repair introduces no new mathematics: repeat the SAME solve on random
    # subsets and score each candidate against all 1024 segments, keeping the
    # best. A draw is usable when its pivot rows are clean — probability
    # (1-f)**rank for a corrupted fraction f.
    for bad in (1, 50, 200, 400):
        got, reported = hv.recover_point_noisy([a, b, c], corrupt(raw, bad, rng), bad)
        check(
            "%3d/%d (%2d%%) corrupted: exact" % (bad, W, 100 * bad // W),
            got.coords() == p.coords() and reported == bad,
            "reported %d bad segment(s)" % reported,
        )

    # The reported count is a free diagnostic: on success the score IS the
    # number of agreeing segments, so W minus it is the corruption count.
    # Which also means a foreign vector cannot pass as "merely very corrupted":
    # its best score sits at chance, about W/segment_size = 1 segment.
    try:
        hv.recover_point_noisy([a, b, c], hv.Sparkle(MODEL, hv.d0(), "stranger"), 600)
        check("a foreign vector is not mistaken for corruption", False, "recovered anyway")
    except ValueError as e:
        check(
            "a foreign vector is not mistaken for corruption",
            "not a point" in str(e),
            "best score stays at chance",
        )

    # Rank COSTS tolerance, and (1-f)**rank says how: at 60% corruption a rank-3
    # draw is clean 6.4% of the time, a rank-10 draw only 0.01% of the time. So
    # the same budget that rank 3 absorbs comfortably starts failing at rank 10.
    print("  -- rank costs tolerance: (1-f)**rank --")
    frac, trials = 0.6, 5
    bad = int(frac * W)
    wins = {}
    for rank in (RANK, 10):
        f = axes(rank, "t%d_" % rank)
        ok = 0
        for _ in range(trials):
            coords = [rng.randrange(1, W) for _ in range(rank)]
            q = hv.Point(f, coords)
            try:
                got, _ = hv.recover_point_noisy(f, corrupt(q.core(), bad, rng), bad)
                ok += got.coords() == q.coords()
            except ValueError:
                pass
        wins[rank] = ok
        print(
            "       rank %-2d at %d%% corrupted: %d/%d exact   (clean draw p=%.4f)"
            % (rank, int(frac * 100), ok, trials, (1 - frac) ** rank)
        )
    check(
        "rank %d tolerates at least as much as rank 10" % RANK,
        wins[RANK] >= wins[10],
        "%d/%d vs %d/%d at %d%%" % (wins[RANK], trials, wins[10], trials, int(frac * 100)),
    )


# --------------------------------------------------------------------------
# "Bind is additive on INTEGER powers and NOT on fractional ones — which is
#  exactly why a Point keeps its coordinates as rationals."
# --------------------------------------------------------------------------
def claim_why_coords_are_kept():
    print("\nWhy the coordinates are kept: bind is not additive on these codes")
    k = hv.Sparkle(MODEL, hv.d0(), "ax0")

    # Integer exponents never truncate, so composing powers IS adding them.
    for x, y in ((3, 7), (11, 28), (100, 200)):
        check(
            "K**%d (x) K**%d == K**%d" % (x, y, x + y),
            hv.equal(hv.bind(k.power(x), k.power(y)), k.power(x + y)),
            "integer powers compose exactly",
        )

    # Fractional exponents DO truncate, and flooring each factor separately
    # loses 1 against flooring the sum on about half the segments. So the two
    # vectors agree at roughly chance-plus-half and are NOT the same point.
    level = 12
    den = 1 << level
    for x, y in ((den + 300, den + 500), (den + 100, den + 100), (den + 2000, den + 1000)):
        lhs = hv.bind(k.power(x, den), k.power(y, den))
        rhs = k.power(x + y, den)
        ov = hv.overlap(lhs, rhs)
        # ~50% of segments, nowhere near the 1024 that equality would need.
        check(
            "bind(K**%.3f, K**%.3f) != K**(sum)" % (x / den, y / den),
            0.40 * W < ov < 0.60 * W,
            "overlap %d of %d (%.0f%%)" % (ov, W, 100.0 * ov / W),
        )

    # Hence the rule: arithmetic on an encoded value belongs on the rational
    # exponents, with a single truncation at materialization. A Point holds
    # those rationals; a materialized vector has already spent them.
    #
    # "Exact" means the VALUE, not the spelling: exponents are always stored in
    # lowest terms, so 4396/4096 comes back as 1099/1024. Same rational, no
    # rounding — compare by cross-multiplying rather than by the digits.
    a, b, c = axes()
    p = hv.Point([a, b, c], [(den + 300, den), 1, 2])
    num, d = p.coords()[0]
    check(
        "a Point stores the exact rational (reduced, not rounded)",
        num * den == (den + 300) * d,
        "%d/%d stored as %d/%d" % (den + 300, den, num, d),
    )


# --------------------------------------------------------------------------
# "Power scales the COORDINATES, exactly, and stays on the same frame."
# --------------------------------------------------------------------------
def claim_power_scales_coordinates():
    print("\nPoint.power scales every coordinate exactly — (b**c)**k == b**(ck)")
    a, b, c = axes()
    p = hv.Point([a, b, c], [11, 28, 45])

    # Folding k into the materialized vector's exponent would truncate a SECOND
    # time. Scaling the rational coordinates instead is exact, and the result
    # is still a Point on the same frame — so it can be recovered again.
    doubled = p.power(2)
    check(
        "power(2) doubles each coordinate",
        doubled.coords() == [(22, 1), (56, 1), (90, 1)],
        "%s" % (doubled.coords(),),
    )
    check("the result is still a Point", isinstance(doubled, hv.Point), "rank=%d" % doubled.rank())
    check(
        "and recovers on the same frame",
        hv.recover_point([a, b, c], doubled.core()).coords() == doubled.coords(),
        "round trip holds after scaling",
    )

    # A fractional scale keeps exact rationals: 28/2 reduces to 14, while 11/2
    # and 45/2 stay fractions rather than rounding.
    halved = p.power(1, 2)
    check(
        "power(1,2) halves exactly, keeping fractions",
        halved.coords() == [(11, 2), (14, 1), (45, 2)],
        "%s" % (halved.coords(),),
    )

    # power(0) is the typed identity — every coordinate at the origin.
    check(
        "power(0) is the origin",
        p.power(0).core().is_identity(),
        "all coordinates zero",
    )


def main():
    print(
        "model=1M/10BIT  M=cardinality=%d  segment_size=%d  width=%d  rank=%d"
        % (W, hv.segment_size(MODEL), hv.width(MODEL), RANK)
    )

    claim_is_the_bind()
    # The three ways to read coordinates back, each on its own.
    claim_recover_point()  # exact solve
    claim_recover_point_fractional()  # lattice
    claim_recover_point_noisy()  # RANSAC
    claim_why_coords_are_kept()
    claim_power_scales_coordinates()

    print("\n%s" % ("ALL CLAIMS PASS" if not FAILED else "FAILED: %s" % "; ".join(FAILED)))
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
