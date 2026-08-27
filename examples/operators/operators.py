#!/usr/bin/env python3
"""Implementing bind and bundle operators from scratch using low-level offset API.

This script demonstrates the math behind the bind and bundle operators by
implementing them in pure Python, then verifying correctness against the
library's built-in implementations.

The only low-level API used:
  - hv.segment_size(model)             → bits per segment
  - hv.overlap(a, b)                   → count of shared ON bits (for verification)
  - a.cardinality()                    → number of segments
  - core().offset(seg)                 → ON-bit offset for a single segment
  - hv.SparseSegmented.from_offsets()  → construct from per-segment offsets
  - hv.SparseOperation.uint64()        → same PRNG as used internally

This script does NOT call hv.bind() or hv.bundle() for computation — it
reimplements them to show how they work.

NOTE on bundle verification: the library's bundle is a Learner underneath —
inputs fold in sequentially, each replacing a weight-proportional random
subset of segments. The per-segment SELECTION FREQUENCIES match the classic
per-segment draw implemented below, but the exact segment choices come from
internal state that is not part of the public contract. Bind/release verify
bit-for-bit; bundle verifies statistically.

Usage:
    python operators.py

See docs: https://yangzh.github.io/hv/examples/operators/index.html
"""

from kongming import hv


def pure_python_bind(model, a, b):
    """Bind two hypervectors: per-segment offset addition mod segment_size.

    For sparse binary vectors, each segment has exactly one ON bit.
    Binding adds the two ON-bit positions modulo the segment size.

    Returns a SparseSegmented with the result.

    Precondition:
    1. `a` and `b` are of the same model (and thus the same sparsity, dimension, etc);
    """
    core_a = a.core()
    core_b = b.core()
    cardinality = a.cardinality()
    seg_size = hv.segment_size(model)

    offsets = []
    for seg in range(cardinality):
        offsets.append((core_a.offset(seg) + core_b.offset(seg)) % seg_size)

    return hv.SparseSegmented.from_offsets(model, offsets)


def pure_python_release(model, composite, key):
    """Release (unbind) a key from a composite: per-segment offset subtraction.

    release(composite, key) = bind(composite, key.power(-1))

    Returns a SparseSegmented with the result.

    Precondition:
    1. `composite` and `key` are of the same model (and thus the same sparsity, dimension, etc);
    """
    core_c = composite.core()
    core_k = key.core()
    cardinality = composite.cardinality()
    seg_size = hv.segment_size(model)

    offsets = []
    for seg in range(cardinality):
        offsets.append((core_c.offset(seg) - core_k.offset(seg)) % seg_size)

    return hv.SparseSegmented.from_offsets(model, offsets)


def pure_python_bundle(model, so, vectors, weights=None):
    """Bundle multiple hypervectors using PRNG-based random selection.

    For each segment, use the PRNG to randomly select which input vector
    contributes its offset. The probability of selecting each input is
    proportional to its weight.

    Args:
        model: HV model constant.
        so: SparseOperation providing the PRNG.
        vectors: list of hypervectors to bundle.
        weights: list of floats (one per vector). Default: equal weights.

    Algorithm (per-segment draw):
      1. Compute cumulative weights, normalized to [0, 65535] (anchors)
      2. For each segment, draw a 16-bit random number from the PRNG
      3. Pick the input whose anchor range contains the random number
      4. Use that input's offset for the segment

    Each uint64() call provides randomness for 4 segments (4 × 16 bits).

    Returns a SparseSegmented with the result.

    Precondition:
    1. at least one vector in the input;
    2. vectors are all of the same model (and thus the same sparsity, dimension, etc);
    3. weights (if not None) are normalized to 1.0;
    """
    n = len(vectors)
    cardinality = vectors[0].cardinality()
    cores = [v.core() for v in vectors]

    if weights is None:
        weights = [1.0 / n] * n

    # Build cumulative anchor thresholds normalized to [0, 65535].
    cumulative = 0.0
    anchors = []
    for w in weights:
        cumulative += w
        anchors.append(int(cumulative * 0xFFFF))

    offsets = []
    for seg in range(0, cardinality, 4):
        r = so.uint64()  # get a 64-bit random number.
        for j in range(4):
            dial = (r >> (48 - 16 * j)) & 0xFFFF
            chosen = 0
            for k, anchor in enumerate(anchors):
                if dial <= anchor:
                    chosen = k
                    break
            offsets.append(cores[chosen].offset(seg + j))

    return hv.SparseSegmented.from_offsets(model, offsets)


def main():
    model = hv.MODEL_1M_10BIT
    so = hv.SparseOperation(model, 0, 42)

    a = hv.Sparkle.random("test", so)
    b = hv.Sparkle.random("test", so)
    c = hv.Sparkle.random("test", so)

    cardinality = hv.cardinality(model)
    seg_size = hv.segment_size(model)
    MODEL_NAMES = {
        1: "MODEL_64K_8BIT",
        2: "MODEL_1M_10BIT",
        3: "MODEL_16M_12BIT",
        4: "MODEL_256M_14BIT",
        5: "MODEL_4G_16BIT",
    }
    print(f"Model: {MODEL_NAMES.get(model, model)} ({a.width()} bits, {cardinality} segments, {seg_size} bits/segment)")
    print()

    # ── Bind ──────────────────────────────────────────────────────────
    print("=" * 60)
    print("BIND: per-segment offset addition mod segment_size")
    print("=" * 60)

    our_bind = pure_python_bind(model, a, b)
    lib_bind = hv.bind(a, b)

    overlap = hv.overlap(our_bind, lib_bind)
    print(f"  overlap(ours, library) = {overlap}/{cardinality}")
    assert overlap == cardinality, "bind mismatch!"
    print("  PASS: pure Python bind matches library exactly")
    print()

    # ── Release ───────────────────────────────────────────────────────
    print("=" * 60)
    print("RELEASE: per-segment offset subtraction mod segment_size")
    print("=" * 60)

    our_release = pure_python_release(model, lib_bind, b)
    overlap = hv.overlap(our_release, a)
    print(f"  overlap(release(bind(a,b), b), a) = {overlap}/{cardinality}")
    assert overlap == cardinality
    print("  PASS: pure Python release recovers a exactly")
    print()

    # ── Multi-way bind ────────────────────────────────────────────────
    print("=" * 60)
    print("MULTI-WAY BIND: bind(a, b, c) = bind(bind(a, b), c)")
    print("=" * 60)

    our_ab = pure_python_bind(model, a, b)
    our_abc = pure_python_bind(model, our_ab, c)
    lib_abc = hv.bind(a, b, c)

    overlap = hv.overlap(our_abc, lib_abc)
    print(f"  overlap(ours, library) = {overlap}/{cardinality}")
    assert overlap == cardinality
    print("  PASS: step-by-step bind matches library multi-bind")
    print()

    # ── Bundle ────────────────────────────────────────────────────────
    print("=" * 60)
    print("BUNDLE: PRNG-based random selection among inputs")
    print("=" * 60)

    # The library's bundle folds inputs into a Learner sequentially,
    # each replacing a weight-proportional random subset of segments;
    # the exact segment choices are internal state, so the check here
    # is STATISTICAL instead of bit-identical:
    # every segment must come from one input, and each input's share must
    # sit within ~6σ of its weight (Binomial(cardinality, w)).
    bundle_seed = hv.Seed128(0, 99)
    bundle_so = hv.SparseOperation(model, bundle_seed.high(), bundle_seed.low())

    our_bundle = pure_python_bundle(model, bundle_so, [a, b, c])
    lib_bundle = hv.bundle(bundle_seed, a, b, c)

    third = cardinality // 3
    tol = 6 * int((cardinality * (1 / 3) * (2 / 3)) ** 0.5)
    print(f"  Equal weights [1, 1, 1]  (expected ~{third} ± {tol} per input):")
    for name, v in (("ours", our_bundle), ("library", lib_bundle)):
        shares = [hv.overlap(v, x) for x in (a, b, c)]
        print(f"    {name:7s} overlap with a/b/c = {shares[0]:3d}/{shares[1]:3d}/{shares[2]:3d}")
        # Segment-offset collisions between inputs (~1/seg_size each) can
        # double-count a few segments, so the sum may slightly exceed.
        assert cardinality <= sum(shares) <= cardinality + 16, "segments must come from the inputs"
        assert all(abs(s - third) <= tol for s in shares), "selection frequencies off"
    print("    PASS: both draw each input equally (statistically)")
    print()

    # Weighted bundle: a gets 60% weight, b and c 20% each
    bundle_seed2 = hv.Seed128(0, 200)
    bundle_so2 = hv.SparseOperation(model, bundle_seed2.high(), bundle_seed2.low())

    our_weighted = pure_python_bundle(model, bundle_so2, [a, b, c], weights=[0.6, 0.2, 0.2])
    print("  Weighted [0.6, 0.2, 0.2]:")
    for x, w in ((a, 0.6), (b, 0.2), (c, 0.2)):
        o = hv.overlap(our_weighted, x)
        sd = (cardinality * w * (1 - w)) ** 0.5
        print(f"    overlap(ours, {'abc'[[a, b, c].index(x)]}) = {o:3d}  (expected ~{int(cardinality * w)})")
        assert abs(o - cardinality * w) <= 6 * sd, "weighted share off"
    print("    PASS: weighted shares match (statistically)")
    print()

    print("All checks passed.")


if __name__ == "__main__":
    main()
