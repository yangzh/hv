# HyperPhaser 🧭 & Phasers 🧭

A second way to bundle a stream of observations. A [Learner 💫](learner.md) reads
each offset as a **label** and compares by overlap; a phasor bundle reads it as a
**phase** and compares by [Lee distance](common/utilities.md#similarity).

Recall from [concepts](../../concepts/hypervectors.md) that a SparseSegmented
vector is already a list of phasors — the ON bit's offset within its segment is
a discretized phase. A `HyperPhaser` takes that literally: it superposes unit
phasors and keeps the resulting angle, which is FHRR's bundle operator living
inside kongming's existing representation.

There are two types because the trainable and published forms differ:

| | `HyperPhaser` | `Phasers` |
|---|---|---|
| state | dense complex, $M$ components | one offset per segment |
| is a `HyperBinary`? | **no** — no wire form | **yes**, hint `HINT_PHASERS` |
| role | accumulate | compare, store |
| metric | — | **Lee**, never overlap |

`HyperPhaser.export()` crosses from one to the other, one way.

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

ph.bundle(a)            # one whole observation

# Below one observation: weights are numerators over cardinality, so a
# quarter-observation is that count // 4.
ph.bundle_fractional(b, ph.cardinality() // 4)

ph.age()                # how many bundle calls, whatever weight they carried
ph.blank()              # bool: nothing bundled yet
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
per-segment. There is deliberately **no accumulated-mass counter** beside
`age()` — nothing on the write path consults one, and the L2 mass is already
recoverable from the state as $\sqrt{M} \cdot \mathrm{rms}(r_i)$.

> Note `age()` counts *calls*, so with fractional writes it is not a weight
> total: eight quarter-weight calls read as age 8, like eight whole ones.

## Reading the accumulator

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
ph.angle(seg)            # accumulated phase in radians, [0, 2*pi)
ph.magnitude_at(seg)     # resultant length r_i, one segment
ph.offset(seg)           # the phase quantized to the ring — what export() writes

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

## Exporting

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
v = ph.export()                  # a Phasers: ANGLES ONLY

block = ph.quantized_magnitudes()   # the confidences, to keep yourself
```
{{#endtab}}
{{#endtabs}}

`export()` gives one quantized phase per segment — the same bytes, packing and
footprint as any `SparseSegmented`, exactly $\sqrt{M}$ long. That makes it a
vector which composes under bind and permute like any other.

**A `Phasers` carries angles only.** Reading it as unit phasors costs roughly
10% on similarity and all of *distributional* analogy (`b - a + c`), which needs
the radial component. The magnitudes stay on the accumulator, where
`quantized_magnitudes()` packs them onto a fixed 4-bit grid, two per byte — so a
caller who wants the per-segment confidences keeps that block beside the export
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

v = ph.export()
v.power(5, 4)       # the export: the phases, scaled — DEFERRED
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

### On the export: deferred, so chains compose

`Phasers.power` scales the phases exactly as it would any `SparseSegmented`'s
offsets. What differs is *when*: the exponent is **recorded** and applied when
the vector is next read, so a chain of powers composes on the rational and is
applied once.

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

Deferral is also why `Phasers` is recipe-backed: the cell holds the unscaled
angles plus the exponent, and the fill applies it. `compact()` drops the
materialized angles and keeps the base and the hash, recomputing identically on
the next read.

Note the asymmetry between the two forms. The accumulator's power reshapes the
confidences, since raising `r` is part of what `z**a` means. The export has no
confidences to reshape, so its power is purely a rotation of the phases.

## Comparing

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
v.lee(other)              # the metric this type exists for
hv.lee_distance(v, other) # same reading, via the free function

v.offset(seg)             # the stored phase
v.offsets()               # every phase, in segment order
v.equal(other)            # content equality, Phasers against Phasers

v.overlap(other)          # raises
v.hamming(other)          # raises
```
{{#endtab}}
{{#endtabs}}

Lower Lee is closer; chance is `W/4` and the maximum `W/2`, per segment.

**The label metric is refused, not merely discouraged.** Two phasors one ring
step apart are maximally similar yet share no exact offset, so overlap reads
them as unrelated — which is why `overlap()` and `hamming()` raise rather than
return a plausible-looking number, and why a `Phasers` must not be fed to the
overlap-keyed [near-neighbor index](../memory/selectors/near_neighbor.md).

That hazard is the whole reason `PHASERS` is its own hint: the bytes are
indistinguishable from any other hypervector's, so nothing but the type can warn
you. Note `core()` deliberately hands back a plain `SparseSegmented`, which has
**lost** that warning — overlap on it answers quietly and wrongly. Prefer `lee()`.

### `equal()` is deliberately strict

It accepts another `Phasers` only. A `SparseSegmented` holding byte-identical
offsets is **not** equal, because those offsets are labels rather than phases —
and since both carry the same `stable_hash()`, nothing but the type
distinguishes them.

So the method and the free function disagree, on purpose:

```python
v.equal(v.core())        # False — only this method separates the metrics
hv.equal(v, v.core())    # True  — the free function compares content hashes
```

`hv.equal` is documented as "identical ON bits", and by that definition it is
right: the bytes *are* identical. It just cannot see that one side reads them as
phases. Treat `Phasers.equal()` as the authoritative check for a phasor.

## See also

- [Learner 💫](learner.md) — the reservoir alternative. Retrieval of members
  from a mixture favours the Learner (its exact-match index, and L1
  normalization that keeps a small member's few clean segments); comparison of
  two bundles at large support favours the phasor.
- [Utilities](common/utilities.md#similarity) — `lee_distance` and when to
  reach for it.
- [Hypervector concepts](../../concepts/hypervectors.md) — the phasor framing
  and the Lee/Hamming split.
