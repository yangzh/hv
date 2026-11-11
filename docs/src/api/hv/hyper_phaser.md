# HyperPhaser 🧭

A second way to bundle a stream of observations. A [Learner 💫](learner.md) reads
each offset as a **label** and compares by overlap; a phasor bundle reads it as a
**phase** and compares by [Lee distance](common/utilities.md#similarity) or
[alignment](common/utilities.md#similarity).

Recall from [concepts](../../concepts/hypervectors.md) that a SparseSegmented
vector is already a list of phasors — the ON bit's offset within its segment is
a discretized phase. A `HyperPhaser` takes that literally: it superposes unit
phasors and keeps the resulting angle, which is FHRR's bundle operator living
inside kongming's existing representation.

So there is no separate "phasor vector" type: **every hypervector already is
one.** What a `HyperPhaser` adds is the accumulator — the one form that is NOT a
hypervector:

| | `HyperPhaser` | any `HyperBinary` |
|---|---|---|
| state | dense complex, $M$ components | one offset per segment |
| is a `HyperBinary`? | **no** — no wire form | **yes** |
| role | accumulate | compare, store |
| magnitudes | kept, per segment | dropped — angle only |

`HyperPhaser.quantize()` crosses from the accumulator to a
[SparseSegmented 🎞️](sparse_segmented.md), one way — the name says the cost: it
rounds each phase to the ring and drops the magnitudes.

## What it estimates

Comparing two phasor bundles estimates the **cosine between the underlying
weight vectors**:

$$\cos(z_A, z_B) \approx \frac{\langle w_A, w_B \rangle}{\|w_A\|_2 \|w_B\|_2}$$

with standard error $\sim 1/\sqrt{M}$ — it is a random projection, whose basis is
the codebook you feed it. That single fact sets expectations: the readout is
**scale-free** (re-presenting the same data changes nothing but magnitude), flat
in the number of distinct observations, and sharper at larger $M$ because $M$
buys ranking resolution rather than fidelity.

## Accumulating

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
ph = hv.HyperPhaser(model, hv.d0(), hv.p0())

ph.bundle(a, 1.0)       # one whole observation

# Any signed float: 1.0 is one whole observation, so a quarter is 0.25.
ph.bundle(b, 0.25)

# NEGATIVE SUBTRACTS, which is what makes match-and-subtract work in place.
ph.bundle(b, -0.25)

ph.dimension()          # how many phasors: one per segment
ph.magnitude_squared()  # 0.0 iff nothing is accumulated
ph.clone_phaser()       # deep copy; the accumulator IS the storage
```
{{#endtab}}
{{#endtabs}}

Unlike a Learner's, these writes are **deterministic and linear**. No RNG is
drawn, so:

- **order never matters** — the same observations in any order give the same
  bytes, where reservoir sampling gives an order-dependent realization;
- **duplicates are harmless** — bundling something twice equals bundling it once
  at double weight, which only rescales and leaves every angle fixed;
- **shares below $1/M$ survive** — a Learner is a *sample*, so a member owning
  less than one segment is invisible; a phasor accumulates, so small weights
  still move every segment.

The cost is resumability. A Learner resumes from its offsets plus one age
scalar; a phasor needs all $M$ magnitudes, because accumulated mass is
per-segment. There is deliberately **no counter of any kind** — neither a call
count nor an accumulated-mass total. Nothing on the write path consults one, and
the L2 mass is already recoverable from the state as $\sqrt{M} \cdot \mathrm{rms}(r_i)$.

> A counter would also have been the wrong emptiness test. A blank accumulator
> simply *is* zero in every segment, so `magnitude_squared() == 0` is the whole
> question — and unlike a call count it stays honest for an accumulator that was
> bundled and then subtracted back to **exactly** zero.

## Reading the accumulator

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
ph.angle(seg)            # accumulated phase in radians, [0, 2*pi)
ph.magnitude_at(seg)     # resultant length r_i, one segment

ph.magnitude_squared()   # the whole vector: sum_i |z_i|**2
```
{{#endtab}}
{{#endtabs}}

`magnitude_at()` is a **per-segment confidence, not a length**. Within one vector
it varies by roughly 8x, and it says how much the contributing phases cancelled
there — a near-zero resultant means the stored angle is decided by rounding
residuals and carries no information. A segment with a large resultant also
resists new observations, which makes it per-segment plasticity where a Learner
has only a scalar age.

A cancelled segment reports angle `0.0`, which is indistinguishable from a
genuine zero phase: read `magnitude_at()` to tell them apart.

`magnitude_squared()` is the whole-vector reading, and it is **squared** rather
than a norm on purpose: that is the moment with an exact law. The cross terms
vanish for independent phases, so $E[|z_i|^2] = \|w\|_2^2$ per segment and the
sum estimates $M \|w\|_2^2$ — linear in the accumulated mass. The norm itself
carries a per-segment Rayleigh factor (0.886) that the second moment does not,
which is why rms derives from here rather than from averaging `magnitude_at()`.

It has exact values worth checking against: one unit observation gives
`magnitude_squared() == M`, and the same observation `n` times gives `n**2 * M`.

## Reading back what went in

`alignment()` scores a candidate against the accumulator and returns **the weight it
was bundled at** — not a similarity:

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
ph.bundle(cat); ph.bundle(cat); ph.bundle(dog)

ph.alignment(cat)        # ~2.0  — bundled twice
ph.alignment(dog)        # ~1.0  — bundled once
ph.alignment(fish)       # ~0.0  — never bundled
```
{{#endtab}}
{{#endtabs}}

It works because the scoring rule gives **partial credit**. Compare the two:

| | rule |
|---|---|
| overlap | count the segments where the two offsets are **equal** |
| `alignment()` | add up $\cos(\text{angle difference})$ over the segments, then divide by $M$ |

Overlap is all-or-nothing per segment. `alignment()` scores two offsets one ring
step apart at $\cos(2\pi/W)$, just under 1, where overlap scores them **0** —
and scores a half-turn at $-1$, which overlap cannot express at all.

That is also why the weight comes back. A member's own phases line up, each
contributing $\cos(0) = 1$, so $n$ copies sum to $n$; every other member sits at
an unrelated angle, and cosines of scattered angles average to **zero**. The
estimate is unbiased, with the usual $\sim\!\|w\|_2/\sqrt{M}$ wobble from that
cancellation being imperfect — so a non-member reads *near* 0, not exactly 0.

`alignment()` reads its argument as unit phasors, exactly as `bundle()` does, so a
quantized vector works too and costs only the magnitudes it dropped.

### It scores; it does not search

`alignment()` needs you to name a candidate, which raises the obvious question: how
do you find one without trying the whole codebook? The answer is that **the
search is ordinary [near-neighbor search](../memory/selectors/near_neighbor.md)**,
and it needs nothing new:

| the question | HyperBinary | HyperPhaser |
|---|---|---|
| how close are **these two**? | `hv.overlap(a, b)` | `ph.alignment(c)` |
| which stored vector is **my probe**? | NNS over the index | **the same NNS** |
| what is **inside** this bundle? | NNS over the index | no index — enumerate |

Row 2 is the one that surprises. A noisy probe is a corrupted *code*, not a
superposition, so most of its segments still carry exact offsets and the
overlap-keyed index finds it — measured correct at rank 1 through **95%**
corrupted segments. So retrieval is two steps, neither of them a scan: let the
**probe** drive NNS over the codebook, then let `alignment()` say whether the
accumulator has actually seen the winner, and how often.

Row 3 is the real gap. A `Learner`'s offsets *are* member offsets — reservoir
sampling copies them, so exact matches survive and the index can see them. Every
offset in a phasor bundle is a vector *sum*, so no member's offset survives
intact and the index is blind to it. Asking "what is in this bundle" with no
probe to narrow it therefore costs one `alignment()` per candidate.

## Binding and releasing

`bind()` multiplies the accumulator segment by segment, and `release()` divides
back. The pair is what lets you put a **key** on a bundle and take it off again:

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
ph.bundle(cat, 2.0)
ph.bundle(dog, 1.0)

ph.bind(key)            # every term now carries the key
ph.release(key)         # and back: alignment() reads 2.0 and 1.0 again
```
{{#endtab}}
{{#endtabs}}

**It distributes over `bundle()`**, which is the whole reason it is useful on an
accumulator: binding a sum binds every term in it. So the interesting direction
is the other one — release a key off a superposition and `alignment()` reads what
that key was bound to, without ever enumerating the bundle:

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
ph = hv.HyperPhaser(model, hv.d0(), hv.p0())
ph.bundle(hv.bind(role, filler), 1.0)

ph.release(role)
ph.alignment(filler)        # ~1.0 — the filler, recovered
```
{{#endtab}}
{{#endtabs}}

### The operand picks the arithmetic

| operand | contributes | magnitudes |
|---|---|---|
| a `HyperPhaser` | its **exact** phase *and* its magnitude | **multiply** |
| any `HyperBinary` | a phase off the model's ring, read as a **unit** phasor | untouched |

A hypervector operand is therefore a pure rotation: it moves the accumulator
around the torus without changing how much evidence any segment carries. An
accumulator operand is the full complex product, so a half-weight key halves the
magnitudes it touches.

`release()` is a true inverse in both cases: it divides, computing
$z_i / w_i = z_i \overline{w_i} / |w_i|^2$, so whatever magnitude `bind()`
multiplied in divides back out. Two consequences worth knowing:

- **A segment whose operand is exactly zero stays zero.** `bind()` took its
  content to zero and there is nothing left to restore, so `release()` leaves it
  alone rather than returning a `NaN` that `angle()`, `magnitude_squared()` and
  `alignment()` would all then spread silently.
- **Small operands amplify.** That is the correct inverse of an attenuating
  `bind()`, not a bug, and it is deliberately not clamped — clamping would make
  `release()` quietly stop being an inverse in exactly the regime where you would
  not notice.

> **Python alone is polymorphic here.** Go and Rust split the two arithmetics
> into `Bind`/`BindQuantized` and `Release`/`ReleaseQuantized`, because they are
> genuinely different operations and the choice is a compile-time one there.
> Python picks the arm from the operand's type, and raises `TypeError` for
> anything that is neither.

## Exporting

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
v = ph.quantize()                # a SparseSegmented: ANGLES ONLY

block = ph.quantized_magnitudes()   # the confidences, to keep yourself

# LOSSLESS, unlike quantize(): the accumulator as complex64, and back.
z = hv.hyper_phaser_to_np(ph)                       # (M,) complex64
ph2 = hv.hyper_phaser_from_np(model, hv.d0(), hv.p0(), z)
```
{{#endtab}}
{{#endtabs}}

`quantize()` gives one phase per segment — the same bytes, packing and
footprint as any `SparseSegmented`, exactly $\sqrt{M}$ long. That makes it a
vector which composes under bind and permute like any other.

**The quantized form carries angles only.** Reading it as unit phasors costs roughly
10% on similarity and all of *distributional* analogy (`b - a + c`), which needs
the radial component. The magnitudes stay on the accumulator, where
`quantized_magnitudes()` packs them onto a fixed 4-bit grid, two per byte — so a
caller who wants the per-segment confidences keeps that block beside the quantized form
themselves.

They are normalized by the accumulator's **own** rms, and the scale is not
included: a global per-vector factor cancels in both Lee and cosine, so no
comparison needs it, and what survives is the confidence *ordering*. Four bits
is the knee — measured, it matches fp32 on both similarity and analogy, and the
grid is a compile-time constant because the normalized magnitude's distribution
depends on neither the word, its support, nor the model.

## Raising to a power

Both forms answer `power(num, den)`, and they mean different things because the
two representations differ.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
ph.power(2)         # the accumulator: the FULL complex power
ph.power(1, 2)      # a root
ph.power(-1)        # the true inverse, 1/z

v = ph.quantize()
v.power(5, 4)       # the quantized form: the phases, scaled — DEFERRED
```
{{#endtab}}
{{#endtabs}}

### On the accumulator: the full complex power

`HyperPhaser.power` is `z**a = r**a * exp(i*a*theta)` — the **magnitude is
raised alongside the phase**.

A materialized vector's `power` scales only offsets because every one of its
segments is unit; there is no magnitude to raise. An accumulator's are not
unit, so stopping at the phase would be a *different operation* that merely
coincides with the power when `r == 1`. Which is also why `power(-1)` here is
the genuine `1/z` rather than only a conjugation.

Raising the magnitude **reshapes the per-segment confidence**: above 1 sharpens,
so already-confident segments pull further ahead, and below 1 flattens. That is
what the power means rather than a side effect — but note the consequence: the
result is no longer the accumulator of any weight vector, so the cosine estimate
described above no longer applies to it. Phase-only scaling would not preserve
it either.

Two edges worth knowing: a cancelled segment (`magnitude == 0`) stays zero
rather than taking `0**a`, which would be infinite for a negative exponent; and
`z**0` is 1, so `power(0)` gives the unit phasor in every live segment, not the
all-zero vector.

### On the quantized form: deferred, so chains compose

`SparseSegmented.power` scales the phases, which are the offsets. What differs
from a step-by-step scaling is *when*: the vector keeps the **unscaled** offsets
plus the exponent applied to them, so a chain of powers composes on the rational
and the scaling is applied **once**, from the base.

That is not cosmetic. Scaling step by step disagrees with the single equivalent
power once an intermediate **wraps past `W`** — wrapping then scaling is not
scaling then wrapping:

| chain | step by step | deferred |
|---|---|---|
| `1/2` then `1/2` | agrees with `1/4` | agrees |
| `3/7` then `2/5` | agrees with `6/35` | agrees |
| **`5/4` then `7/3`** | **tens of ring steps off `35/12`** | **agrees** |

The size of that gap depends on the vector — it is wherever the wrapped
segments happen to land, measured in the 60–80 range on two different
codebooks — but the deferred column is exactly zero every time, which is the
part that is a property of the operation rather than of the instance.

Contracting exponents agree either way, because `floor(floor(x/a)/b)` really is
`floor(x/(a*b))` and nothing wraps on the way down. Expanding ones are the
regime fractional-power encoding actually uses — [Point](point.md) keeps its
exponents at or above 1 — so this is the common case, not an exotic one.

An **unpowered** vector carries no base and pays nothing: its offsets *are* the
base, and only a `power()` call that leaves a non-unit exponent records one. A
chain that scales back to unit — `power(2)` then `power(1, 2)` — hands back the
base itself and drops the recipe again.

Note the asymmetry between the two forms. The accumulator's power reshapes the
confidences, since raising `r` is part of what `z**a` means. The quantized form
has no confidences to reshape, so its power is purely a rotation of the phases.

## Comparing

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
hv.lee_distance(v, other) # how far around the ring, per segment
hv.alignment(v, other)    # the true cosine, in angle space
hv.overlap(v, other)      # exact-offset agreement — see the warning below

v.offset(seg)             # the stored phase
v.offsets()               # every phase, in segment order
hv.equal(v, other)        # content equality
```
{{#endtab}}
{{#endtabs}}

Lower Lee is closer; chance is `W/4` and the maximum `W/2`, per segment.

**Every metric answers, and the choice is yours.** A quantized vector is an
ordinary hypervector, so nothing raises — which means the hazard is now a fact
about the *question* rather than about the type. Two vectors one ring step apart
in every segment are nearly identical as phasors and share no exact offset at
all, so the three metrics disagree completely (measured at $M = 1024$, ring
$W = 1024$):

| reading | one step apart | unrelated pair | range |
|---|---|---|---|
| `hv.overlap` | **0** | 0 | 0 … 1024, higher is closer |
| `hamming()` | **2048** — the maximum | 2048 | 0 … 2048, lower is closer |
| `hv.lee_distance` | **1** | 253 | 0 … 512, lower is closer |
| `hv.alignment` | **0.99998** | 0.012 | −1 … 1, higher is closer |

Read that top-left column as the warning it is: the label metrics call the
closest possible pair the *furthest*, because they ask whether the offsets are
**equal** and nothing more. That is exactly right for exact-match retrieval and
useless for a near-miss.

So a vector you intend to compare as phases **must not** be fed to the
overlap-keyed [near-neighbor index](../memory/selectors/near_neighbor.md). The
bytes are indistinguishable from any other hypervector's, so nothing can warn
you at the call — pick `lee_distance` or `alignment` deliberately.

### Lee or alignment?

Both read the same per-segment quantity — the ring gap $\theta_i = 2\pi
\cdot \text{lee}_i / W$ — and then **aggregate it differently**:

- `lee_distance` averages the gaps. It is a true metric, it is integer, and it
  is what the near-neighbor machinery can be made to bound.
- `alignment` averages their cosines and is therefore the exact cosine
  similarity: every segment is a unit phasor, so both norms are exactly
  $\sqrt{M}$ and the $1/M$ *is* the normalization. Use it when you want an
  inner product rather than a distance.

Neither determines the other — a mean of angles and a mean of cosines are
different statistics — so they can rank a pair differently, and that is not a
bug in either.

## See also

- [Learner 💫](learner.md) — the reservoir alternative. Retrieval of members
  from a mixture favours the Learner (its exact-match index, and L1
  normalization that keeps a small member's few clean segments); comparison of
  two bundles at large support favours the phasor.
- [Utilities](common/utilities.md#similarity) — `lee_distance` and when to
  reach for it.
- [Hypervector concepts](../../concepts/hypervectors.md) — the phasor framing
  and the Lee/Hamming split.
