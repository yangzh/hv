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
ph.angle(seg)       # accumulated phase in radians, [0, 2*pi)
ph.magnitude(seg)   # resultant length r_i
ph.offset(seg)      # the phase quantized to the ring — what export() writes
```
{{#endtab}}
{{#endtabs}}

`magnitude()` is a **per-segment confidence, not a length**. Within one vector it
varies by roughly 8x, and it says how much the contributing phases cancelled
there — a near-zero resultant means the stored angle is decided by rounding
residuals and carries no information. A segment with a large resultant also
resists new observations, which makes it per-segment plasticity where a Learner
has only a scalar age.

A cancelled segment reports angle `0.0`, which is indistinguishable from a
genuine zero phase: read `magnitude()` to tell them apart.

## Exporting

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
v = ph.export()                   # angle only: a true hypervector
v = ph.export_with_magnitudes()   # plus one 4-bit magnitude per segment
```
{{#endtab}}
{{#endtabs}}

`export()` gives one quantized phase per segment — the same bytes, packing and
footprint as any `SparseSegmented`, exactly $\sqrt{M}$ long. Dropping the
magnitudes costs roughly 10% on similarity and all of *distributional* analogy
(`b - a + c`), which needs the radial component; it buys a vector that composes
under bind and permute like any other.

`export_with_magnitudes()` keeps a 4-bit normalized magnitude per segment, two
per byte. They are normalized by the vector's **own** rms onto a fixed grid, and
the scale is not stored — a global per-vector factor cancels in both Lee and
cosine, so no read needs it.

> The magnitude-carrying form cannot be serialized yet: `proto_bytes()` on it
> raises rather than quietly publishing unit magnitudes in place of real ones.

## Comparing

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
v.lee(other)              # the metric this type exists for
hv.lee_distance(v, other) # same reading, via the free function

v.has_magnitudes()
v.magnitude(seg)          # normalized, in units of the vector's own rms
v.offset(seg)             # the stored phase
v.offsets()               # every phase, in segment order
v.equal(other)            # phases AND magnitudes

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

`stable_hash()` covers the **phases alone**, so two exports of one accumulator —
one with magnitudes, one without — hash alike and sit at Lee distance 0. Only
`equal()` separates them, and it accepts another `Phasers` only: a
`SparseSegmented` holding identical bytes is *not* equal, because those offsets
are labels rather than phases.

## See also

- [Learner 💫](learner.md) — the reservoir alternative. Retrieval of members
  from a mixture favours the Learner (its exact-match index, and L1
  normalization that keeps a small member's few clean segments); comparison of
  two bundles at large support favours the phasor.
- [Utilities](common/utilities.md#similarity) — `lee_distance` and when to
  reach for it.
- [Hypervector concepts](../../concepts/hypervectors.md) — the phasor framing
  and the Lee/Hamming split.
