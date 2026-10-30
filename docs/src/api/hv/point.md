# Point 📍

A position in the space a **frame** of basis vectors spans. Given bases
$b_0 \ldots b_{n-1}$ and coordinates $c_0 \ldots c_{n-1}$:

$$\text{Point} = b_0^{c_0} \otimes b_1^{c_1} \otimes \cdots \otimes b_{n-1}^{c_{n-1}}$$

The coordinates are **exponents**, so a Point is the fractional-power encoding of
an $n$-tuple on one shared frame. Two Points on the same frame are comparable;
the same offsets under a different frame mean a different position.

## Why the coordinates are kept

A Point carries its coordinates rather than folding them into the vector,
because **bind is not additive on these codes**:

$$K^x \otimes K^y \neq K^{x+y}$$

The two disagree on about half the segments, because
$\lfloor u \rfloor + \lfloor v \rfloor$ loses 1 against
$\lfloor u + v \rfloor$. So coordinate
arithmetic has to happen on the rationals and truncate **once**, at
materialization. A Point that keeps its coordinates can do that; a bare
`SparseSegmented` has already spent its exponent into the offsets and cannot.

## Constructors

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
frame = [hv.Sparkle(model, d, hv.Pod("b0")), hv.Sparkle(model, d, hv.Pod("b1"))]

p = hv.Point(frame, [5, 9])                      # integer coordinates

# Fractional: each coordinate an int or a (numerator, denominator) pair.
p = hv.Point(frame, [(4100, 4096), (4096, 4096)])

# A short list pads with zeros — the origin on the remaining axes.
p = hv.Point(frame, [5])

p = hv.Point(frame, [5, 9], keep_frame=False)    # the STORAGE shape, below
```
{{#endtab}}
{{#endtabs}}

The frame must share a model and be pairwise distinct and non-identity.

## Inspection

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
p.rank()        # axis count — len(coords), whether or not the frame is held
p.coords()      # [(numerator, denominator), ...] in lowest terms
p.frame()       # the basis vectors, empty when not retained
p.is_ready()    # bool: whether the frame is held
```
{{#endtab}}
{{#endtabs}}

## The storage shape: a Point without its frame

Many Points usually share one frame, and storing a copy per record is waste.
`keep_frame=False` keeps the coordinates and drops the frame:

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
stored = hv.Point(frame, [5, 9], keep_frame=False)
stored.is_ready()           # False
stored.rank()               # 2 — the coordinates are still there

live = stored.attach_frame(frame)   # a NEW Point; Points are immutable
live.is_ready()                     # True

stored = live.detach_frame()        # the same thing from an existing Point
```
{{#endtab}}
{{#endtabs}}

The frame argument is **still required and validated** when `keep_frame=False`
— it supplies the model, the axis count, and the seed `attach_frame` later
checks, so a mismatched frame is caught rather than silently decoding a
different position.

A non-ready Point's content reads as the **identity**, not the position: it is
for writing, not computing. Comparing one against a genuine origin Point is the
one place to be careful — they are different things that both read as identity.

## Recovering coordinates from raw offsets

Given a frame and a bare `SparseSegmented`, the coordinates can be solved for.
Three functions, in increasing cost and tolerance:

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
hv.recover_point(frame, raw)                    # integer, an exact solve
hv.recover_point_fractional(frame, raw, 12)     # on the 1 / 2**12 grid

# Integer, tolerating up to max_bad corrupted segments. Returns the Point AND
# how many segments disagreed; max_bad=0 is exactly recover_point.
point, bad = hv.recover_point_noisy(frame, raw, 8)
```
{{#endtab}}
{{#endtabs}}

| | method | tolerates corruption | practical rank |
|---|---|---|---|
| `recover_point` | exact modular solve | no | any |
| `recover_point_fractional` | lattice reduction (LLL + Babai), then polish | no | 10-bit and up: through 10; 8-bit: about 4 |
| `recover_point_noisy` | consensus over random segment subsets (RANSAC) | yes, up to `max_bad` | tolerance falls with rank — see below |

**The fractional grid has a floor.** A power *truncates*, so a coordinate delta
below $2^{\text{level}} / M$ moves no segment at all. Inside that plateau the
position is genuinely indistinguishable from the origin — the information is not
in the vector, so no solver recovers it. At level 12 and $M = 1024$ that is a
delta under 4.

**Noise tolerance costs rank.** A random subset of $n$ segments is usable only
when its pivot rows are all clean, which has probability $(1-f)^n$ — so the
corruption a solve survives shrinks as the rank grows. Measured, exact recovery
holds to roughly **59%** corrupted segments at rank 3, **39%** at rank 5 and
**20%** at rank 10.

`recover_point` cannot tolerate even one bad segment: the coordinates live in a
modular group with no notion of "close", so a single wrong offset among the ones
the solve pivots on randomizes the answer outright. A vector that is not on the
frame at all still raises, rather than passing as heavily corrupted.

> Resolving a Point is NOT a resonator network. That was measured and does not
> work here: the cleanup scores an exact-offset match, so a wrong power sits at
> chance with no slope toward the right answer. A resonator needs the score to
> degrade smoothly as it approaches the solution, and it also discards the very
> structure that makes the solve possible — FPE offsets are
> $\lfloor o \cdot a \rfloor$, *linear* in the exponent.

## Comparing Points

A Point is the type where [Lee distance](common/utilities.md#similarity) earns
its keep. Because the offsets are fractional powers, they carry an **ordinal**
meaning: nearby positions have nearby offsets, and Lee reads that gradation
where overlap only reports agreement and collapses into noise as positions
separate.

The gradation has the same floor as recovery, though — a coordinate delta inside
the plateau reads Lee 0, because no segment moved.

## Hazards

Both inherited from fractional-power encoding, and both easy to trip:

1. **Keep fractional exponents at or above 1.** Below 1 the encoding
   degenerates, for an exact reason: $x < 1$ contracts every offset into
   $[0,\ x \cdot W)$, so two *different* base vectors stop being orthogonal —
   they are both crushed into the same narrow band. At the limit $K^{1/W}$
   measures as the identity outright.

   So distinct codes raised to the same small power retain spurious overlap
   (one measured pair: 18 segments at $x = 1/16$ and 8 at $x = 1/4$, against
   near-chance once $x \ge 1$ — single draws, so read the trend and not the
   counts).

   The fix is in how you encode: put a continuous value $A$ on a $2^l$ grid as
   the numerator $2^l + A$ over $2^l$. That keeps $x$ in $[1,\ W+1)$, where
   cross-vector orthogonality is clean. **Nothing enforces this** — it is the
   caller's to get right.
2. **Bind is not additive** on fractional powers — the reason the coordinates
   are kept at all. Do arithmetic on `coords()`, build a new Point, and let it
   truncate once.

## See also

- [Utilities](common/utilities.md#similarity) — `lee_distance`, the graded read.
- [Operators](operators.md) — `power`, and what fractional exponents mean.
- [HyperPhaser & Phasers 🧭](phasers.md) — the other type whose offsets are
  ordinal rather than labels.
