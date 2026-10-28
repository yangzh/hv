#!/usr/bin/env python3
"""A Point in 2-D, and how to read its coordinates back off a raw vector.

A `Point` is a position in the space spanned by a FRAME of basis hypervectors.
Given bases b0, b1 and coordinates c0, c1 it is exactly this bind:

    Point = b0**c0  (x)  b1**c1                     (x) = bind

Nothing is stored "beside" the vector to make that readable. `.core()` hands
back a bare `SparseSegmented` — 1024 integer offsets, no coordinates in sight —
and the coordinates are still fully determined by it, GIVEN the frame. Reading
them back is not a search over candidate positions. It is a linear solve:

    raw_i = (b0_i * c0 + b1_i * c1)  mod W          one equation per segment

which is 1024 equations in 2 unknowns. Two pin the answer; the surplus 1022
VERIFY it, which is what lets recovery REFUSE a vector instead of returning a
meaningless best fit.

This script checks each claim against the library and prints PASS/FAIL with the
measured number beside the predicted one.

    pip install kongming-rs-hv
    python point_2d.py

See point_3d.py for rank 3, for why the coordinates have to be kept as
rationals, and for recovery from a CORRUPTED vector.

NOTE: `Point` and the `recover_point*` functions are newer than the published
kongming-rs-hv release. If `hv.Point` raises AttributeError, your installed
wheel predates them.
"""

from kongming import hv

MODEL = hv.MODEL_1M_10BIT
W = hv.cardinality(MODEL)  # 1024 segments, and the modulus coordinates live in
FAILED = []


def check(claim, ok, detail):
    print("  [%s] %-58s %s" % ("PASS" if ok else "FAIL", claim, detail))
    if not ok:
        FAILED.append(claim)


def axes(*words):
    """A frame is just a list of basis vectors — nothing marks them as axes."""
    return [hv.Sparkle(MODEL, hv.d0(), w) for w in words]


# --------------------------------------------------------------------------
# "A frame must be READABLE: shared model, pairwise distinct, no identity."
# --------------------------------------------------------------------------
def claim_frame_rules():
    print("\nThe constructor rejects frames whose coordinates could not be read")
    a, b = axes("x-axis", "y-axis")

    # Two EQUAL bases would give one position many spellings, so a recovered
    # coordinate would be arbitrary between them. An IDENTITY basis is worse:
    # I**c == I for every c, so that axis has one spelling for ALL positions
    # and its coordinate is not ambiguous but absent.
    identity = hv.SparseSegmented.identity(MODEL)
    cases = [
        ("empty frame", lambda: hv.Point([], [1]), "empty frame"),
        ("duplicate basis", lambda: hv.Point([a, a], [1, 2]), "same basis"),
        ("identity basis", lambda: hv.Point([a, identity], [1, 2]), "is the identity"),
        ("more coords than axes", lambda: hv.Point([a, b], [1, 2, 3]), "coordinates for a"),
    ]
    for name, build, want in cases:
        try:
            build()
            check(name + " rejected", False, "constructed anyway")
        except ValueError as e:
            check(name + " rejected", want in str(e), str(e).split(":")[-1].strip()[:34])


# --------------------------------------------------------------------------
# "Point IS b0**c0 (x) b1**c1, and the all-origin Point is the identity."
# --------------------------------------------------------------------------
def claim_is_the_bind():
    print("\nA Point is exactly the bind of its bases raised to its coordinates")
    a, b = axes("x-axis", "y-axis")

    p = hv.Point([a, b], [3, 7])
    # Build the same thing by hand: raise each basis, bind the results.
    by_hand = hv.bind(a.power(3), b.power(7))
    check(
        "Point(frame,[3,7]) == bind(b0**3, b1**7)",
        p.stable_hash() == by_hand.stable_hash(),
        "hash 0x%016x" % p.stable_hash(),
    )

    # Coordinates are EXPONENTS, not weights. Integers read back as (n, 1).
    check("integer coords read back as (n,1)", p.coords() == [(3, 1), (7, 1)], "%s" % p.coords())

    # A short list pads with zeros, and 0 means the origin on that axis:
    # b**0 is the identity, which contributes nothing to the bind.
    check(
        "a short coord list pads with the origin",
        hv.Point([a, b], [3]).coords() == [(3, 1), (0, 1)],
        "%s" % hv.Point([a, b], [3]).coords(),
    )

    # Every coordinate at the origin means every factor is the identity, so the
    # whole Point is the identity. It is represented as such, not as a buffer
    # that happens to be zero.
    origin = hv.Point([a, b])
    check("the all-origin Point is the identity", origin.core().is_identity(), "%s" % origin.coords())


# --------------------------------------------------------------------------
# "The raw SparseSegmented holds no coordinates, yet determines them exactly."
# --------------------------------------------------------------------------
def claim_recover_from_raw():
    print("\nrecover_point solves the coordinates back out of a bare vector")
    a, b = axes("x-axis", "y-axis")

    for c0, c1 in ((3, 7), (0, 1), (1, 0), (512, 999), (W - 1, W - 2)):
        p = hv.Point([a, b], [c0, c1])

        # .core() materializes the recipe into offsets. The coordinates were
        # SPENT into them when the vector was built — there is no field to read.
        raw = p.core()
        got = hv.recover_point([a, b], raw)

        # Exact, because an integer power never truncates: floor(o*c) == o*c,
        # so the equations hold with no error term at all.
        check(
            "coords (%d,%d) recovered exactly" % (c0, c1),
            got.coords() == p.coords() and hv.equal(got, p),
            "raw=%d offsets -> %s" % (len(raw.offsets()), got.coords()),
        )


# --------------------------------------------------------------------------
# "The surplus equations VERIFY, so a vector off the frame is refused."
# --------------------------------------------------------------------------
def claim_surplus_equations_verify():
    print("\nOnly 2 of 1024 equations are needed; the rest reject impostors")
    a, b = axes("x-axis", "y-axis")
    raw = hv.Point([a, b], [3, 7]).core()

    # A vector that is simply not a point on this frame. The solve would still
    # return SOMETHING from any 2 equations, so it is the other 1022 that catch
    # it.
    try:
        hv.recover_point([a, b], hv.Sparkle(MODEL, hv.d0(), "not-on-this-frame"))
        check("a foreign vector is rejected", False, "recovered anyway")
    except ValueError as e:
        check("a foreign vector is rejected", "not a point" in str(e), str(e).split("—")[-1].strip()[:34])

    # The SAME raw vector read against a DIFFERENT frame is also rejected. This
    # is the precise sense in which a Point is meaningless without its frame:
    # identical offsets denote different positions under different bases, which
    # is also why the frame travels on the wire.
    try:
        hv.recover_point(axes("u", "v"), raw)
        check("the same raw under another frame is rejected", False, "recovered anyway")
    except ValueError:
        check("the same raw under another frame is rejected", True, "same offsets, other bases")


# --------------------------------------------------------------------------
# "Coordinates are determined only MODULO W."
# --------------------------------------------------------------------------
def claim_modulo_w():
    print("\nc and c+W are the same vector, so recovery folds into [0, W)")
    a, b = axes("x-axis", "y-axis")
    p = hv.Point([a, b], [3, 7])

    # Offsets are taken mod W, so scaling by c and by c+W lands on the same
    # offsets. The two Points are one vector, and "which did you mean" is not a
    # question the vector can answer. The window IS the whole answer.
    wrapped = hv.Point([a, b], [3 + W, 7])
    check("Point[3+W,7] is the same vector as Point[3,7]", hv.equal(wrapped, p), "W=%d" % W)
    check(
        "recovery returns the representative in [0,W)",
        hv.recover_point([a, b], wrapped.core()).coords() == [(3, 1), (7, 1)],
        "%s" % hv.recover_point([a, b], wrapped.core()).coords(),
    )


# --------------------------------------------------------------------------
# "Fractional coordinates on a 1/2**level grid recover too, via a lattice."
# --------------------------------------------------------------------------
def claim_fractional():
    print("\nrecover_point_fractional reads a continuous coordinate back")
    a, b = axes("x-axis", "y-axis")

    # Keep fractional exponents at or ABOVE 1. Below 1 the encoding degenerates:
    # offsets contract toward zero and different bases stop being orthogonal
    # (K**(1/1024) measures as the identity outright). So encode a value A as
    # the numerator 2**level + A, keeping the exponent in [1, 2).
    for level in (8, 10, 12):
        den = 1 << level
        a0, a1 = 137 % den, 901 % den
        p = hv.Point([a, b], [(den + a0, den), (den + a1, den)])

        # A fractional power TRUNCATES, so the equations now hold only up to a
        # small unknown error and this is no longer a solve but a closest-vector
        # problem: LLL reduces a lattice over a few segments to place the
        # answer, then a polish pass scores it against all 1024.
        got = hv.recover_point_fractional([a, b], p.core(), level)
        check(
            "level=%-2d  A=(%d,%d) recovered" % (level, a0, a1),
            hv.equal(got, p),
            "coords %s" % (got.coords(),),
        )

    # level=0 means the integer grid, which routes to the exact solve.
    q = hv.Point([a, b], [5, 9])
    check(
        "level=0 is the integer grid",
        hv.recover_point_fractional([a, b], q.core(), 0).coords() == [(5, 1), (9, 1)],
        "exact path, no lattice",
    )


# --------------------------------------------------------------------------
# "A larger level buys more CODES, not finer resolution."
# --------------------------------------------------------------------------
def claim_level_buys_codes_not_resolution():
    print("\nRaising level packs codes closer together; it does not separate them")
    a, b = axes("x-axis", "y-axis")

    # Adjacent numerators stay DISTINCT vectors at every level -- so recovery
    # keeps returning the exact numerator. What changes is how far apart they
    # sit: the Hamming distance between neighbours collapses as level grows,
    # because each step of the numerator moves a smaller fraction of the
    # offsets. Codes get denser, not better separated.
    prev = None
    for level in (10, 13, 16):
        den = 1 << level
        base = hv.Point([a, b], [(den + 137, den), (den + 901, den)])
        nb = hv.Point([a, b], [(den + 138, den), (den + 901, den)])
        ham = hv.hamming(nb, base)

        distinct = not hv.equal(nb, base)
        closer = prev is None or ham < prev
        check(
            "level=%-2d  neighbours distinct, and closer than before" % level,
            distinct and closer,
            "hamming(n, n+1) = %-5d %s" % (ham, "" if prev is None else "(was %d)" % prev),
        )
        prev = ham

    # The practical reading: level is a codebook-size dial. Past log2(W) it adds
    # addressable positions without making any of them easier to tell apart.
    check(
        "so level is a code-count dial, not a precision dial",
        prev is not None and prev < W // 32,
        "neighbours only %d bits apart at level 16" % prev,
    )


# --------------------------------------------------------------------------
# "recover_point breaks on ONE bad offset; recover_point_noisy does not."
# --------------------------------------------------------------------------
def claim_noisy():
    print("\nrecover_point_noisy: consensus over the exact solve (RANSAC)")
    a, b = axes("x-axis", "y-axis")
    p = hv.Point([a, b], [3, 7])
    clean = p.core().offsets()

    def corrupt(n):
        """Shift n offsets by 3 — a small, local perturbation of the vector."""
        o = list(clean)
        for i in range(n):
            seg = (i * 37) % W
            o[seg] = (o[seg] + 3) % W
        return hv.SparseSegmented.from_offsets(MODEL, o)

    # The exact solve is BRITTLE, and deliberately so. Coordinates live in a
    # modular group, where there is no notion of "close": if a corrupted
    # segment happens to be one the elimination pivots on, the answer is not
    # perturbed, it is randomized. And the all-segments check then rejects even
    # a clean solve. So one bad offset out of 1024 is fatal.
    try:
        hv.recover_point([a, b], corrupt(1))
        check("one bad offset defeats recover_point", False, "recovered anyway")
    except ValueError:
        check("one bad offset defeats recover_point", True, "1 of 1024 segments is enough")

    # The repair needs no new mathematics: run the SAME solve on random subsets
    # of segments and score each candidate against all 1024, keeping the best.
    # A draw is usable whenever its pivot rows happen to be clean, which has
    # probability (1-f)**rank for a corrupted fraction f — so low rank tolerates
    # a lot. At rank 2 that is (1-f)**2, and it holds up remarkably far.
    for bad in (1, 5, 50, 200, 500):
        got, reported = hv.recover_point_noisy([a, b], corrupt(bad), bad)
        check(
            "%3d/%d corrupted: coords recovered exactly" % (bad, W),
            got.coords() == p.coords() and reported == bad,
            "reported %d bad segment(s)" % reported,
        )

    # The count it returns is a free diagnostic: on success the score is
    # exactly "segments that agree", so M minus it IS the corruption count.
    # That also means a foreign vector cannot sneak through as "very
    # corrupted": its best score sits at chance (about M/W = 1 segment), miles
    # below any budget a caller would grant.
    try:
        hv.recover_point_noisy([a, b], hv.Sparkle(MODEL, hv.d0(), "stranger"), 500)
        check("a foreign vector is not mistaken for corruption", False, "recovered anyway")
    except ValueError as e:
        check(
            "a foreign vector is not mistaken for corruption",
            "not a point" in str(e),
            "best score stays at chance",
        )

    # A zero budget is exactly recover_point, brittleness included.
    got, reported = hv.recover_point_noisy([a, b], p.core(), 0)
    check("max_bad=0 is the plain exact solve", reported == 0 and hv.equal(got, p), "reported 0 bad")


def main():
    print("model=1M/10BIT  M=cardinality=%d  segment_size=%d  width=%d" % (W, hv.segment_size(MODEL), hv.width(MODEL)))

    claim_frame_rules()
    claim_is_the_bind()
    # The three ways to read coordinates back, each on its own.
    claim_recover_from_raw()  # recover_point            — exact solve
    claim_fractional()  # recover_point_fractional — lattice
    claim_noisy()  # recover_point_noisy      — RANSAC
    claim_surplus_equations_verify()
    claim_modulo_w()
    claim_level_buys_codes_not_resolution()

    print("\n%s" % ("ALL CLAIMS PASS" if not FAILED else "FAILED: %s" % "; ".join(FAILED)))
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
