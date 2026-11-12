# SparseSegmented 🍡

The most foundational vector type — a sparse binary hypervector where each segment has exactly one ON bit at the recorded offset location. All other types (Sparkle, Set, Sequence, etc.) ultimately contain a `SparseSegmented` in memory for processing, whenever necessary.

## Structure

| Field | Description |
|-------|-------------|
| `model` | Sparsity configuration ([Model](common/models.md)) |
| `offsets` | Packed bit array of per-segment ON offsets. `nil`/`None` = identity vector |
| `hash` | Lazy-computed stable hash for equality checks |
| `domain` / `pod` | The identifier for these offsets; serialized, so it survives a round trip |
| `exponent` | The accumulated power, 1 if unpowered. See below |

The offsets are bit-packed according to the model's sparsity bits — they do **not** align to byte boundaries. This trades a small CPU cost for compact, uniform storage that works both in memory and on disk.

**Identity vector**: when `offsets` is blank (zero storage), the vector is the identity vector where all offsets are 0.

## Constructors

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
# Identity
ss = hv.SparseSegmented.identity(model)
```
{{#endtab}}
{{#endtabs}}

## Key Methods

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
ss.is_identity()  # True if identity vector

ss2 = ss.power(2)
inv = ss.power(-1)
half = ss.power(1, 2)   # fractional: ss^(1/2)

# Similarity
hv.overlap(a, b)   # Count of matching ON bits
hv.hamming(a, b)   # Count of differing segments

ss.offsets()   # returns all offsets
ss.on(idx)     # True if global bit index is ON
ss.offset(seg) # the ON offset within one segment
```
{{#endtab}}
{{#endtabs}}

## Bulk export to numpy

`offsets()` builds one Python `int` per segment, which is the wrong shape for
an array library. `hv.code_to_np()` hands back the same offsets as a numpy
array, and `hv.codes_to_np` does a whole batch in one call — about **27x
faster** than iterating, and close to a memory copy.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
a = hv.code_to_np(v0)                     # (M,), uint8 or <u2

# One call for a whole codebook: row i is vectors[i].
codes = hv.codes_to_np([v0, v1, v2])      # (3, M)

# And back. An array carries no identity, so (domain, pod) come from you.
ss = hv.code_from_np(model, domain, pod, a)
vs = hv.codes_from_np(model, domain, pod, codes)
```
{{#endtab}}
{{#endtabs}}

The dtype is `uint8` at 8-bit and `<u2` for every wider model — one element per
segment, since every model's offset fits 16 bits. The export is zero-copy,
reading over immutable `bytes`; an offset wider than the segment is masked into
it on the way back, as every write path does.

The byte order is **fixed little-endian**, not the host's, so the same vector
exports to the same bytes everywhere.

### Offsets are ring angles, so lift before you compute

An exported offset is an **angle on the segment's ring**, not a coordinate.
Euclidean array math on it is meaningless, and silently so: two vectors each
exactly one ring step from a base read $L_2$ distances of **32.0** and
**32736.0** at 10-bit, for the identical true relation, because one of them
wraps. Nothing in numpy or torch will stop you.

`hv.phasor_table(model)` is the lift. It returns the ring's
`segment_size(model)` **unit phasors** as `complex64`, so turning offsets into
something you can do linear algebra on is a gather:

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
O = hv.codes_to_np(vectors)         # (n, M) ring offsets
Z = hv.phasor_table(model)[O]       # (n, M) complex64 — one gather

# All-pairs similarity is then one matmul, and it IS hv.alignment.
S = (Z @ Z.conj().T).real / hv.cardinality(model)

# For torch layers that reject complex dtypes: (W, 2) float32 instead.
table = hv.phasor_table(model, real=True)
```
{{#endtab}}
{{#endtabs}}

Measured **10x faster** than `exp(2j*pi*O/W)` per element at (512, 1024), and
bit-identical — the table holds every value that exponential can take, so there
is nothing to approximate. The matmul reproduces `hv.alignment` to better than
1e-5. The table itself is built once per model inside the library and handed out
zero-copy.

<div class="callout callout-note">
<div class="callout-title">Which dtype a network wants</div>

`complex64` is the compute dtype: torch accepts it with no conversion. The raw
offsets are `uint16`, which torch will convert to a tensor and then refuse to do
arithmetic on — but that only matters if you meant to do the algebra there.
Bind, release and power belong in `kongming`; the array boundary is for the
numbers a network consumes, and those want the lift.

</div>

<div class="callout callout-warning">
<div class="callout-title">The buffer is a snapshot, not a view</div>

The export copies, so the array freezes the content at the moment of the call.
For an immutable vector that never matters. For a **`Learner`** it does:
bundling after an export does not reach the array you already hold, and nothing
warns you — re-export after every change you need reflected.

A view is not an option. The offsets are bit-packed below 16-bit, the buffer
mutates and can move underneath an alias, and an identity vector holds no
buffer at all.

</div>

Composites are accepted and materialized to their core first, so they
contribute only their offsets: a `Point`'s coordinates and frame, or a
`Learner`'s weight distribution, do **not** survive the trip.

## Chained powers are exact

`power()` reports the exponent you asked for, and `core()` folds it into the
offsets:

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
ss = hv.Sparkle.from_word(model, "pos", "step").core()

ss.exponent()                  # (1, 1) — unpowered
ss.power(3).exponent()         # (3, 1)
ss.power(3).core().exponent()  # (1, 1) — core() folds it in
```
{{#endtab}}
{{#endtabs}}

Chaining composes on the rational, so a chain of powers agrees exactly with the
single equivalent power — scaling truncates only once however long the chain:

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
hv.equal(ss.power(5, 4).power(7, 3), ss.power(35, 12))   # True
hv.equal(ss.power(1, 2).power(2, 1), ss)                 # True
```
{{#endtab}}
{{#endtabs}}

That matters for EXPANDING exponents, which is what
[fractional-power encoding](point.md) uses: scaling step by step instead would
disagree as soon as an intermediate wraps past the ring — measured 70 Lee steps
apart for `5/4` then `7/3` at 10-bit. Contracting chains agree either way,
since `floor(floor(x/a)/b)` really is `floor(x/(a*b))` and nothing wraps on the
way down.

A powered vector survives the wire with that exactness intact, and domain and
pod are written too — they identify the offsets rather than transform them.

## `core()` returns eagerly-applied offsets

`core()` on any type crosses from recipe to materialized, which means it
**computes** the offsets and folds in every pending exponent:

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
half = hv.Set(seed, a, b).power(1, 2)

half.exponent()          # (1, 2) — the composite still describes itself
half.core().exponent()   # (1, 1) — the returned offsets already include the 1/2
```
{{#endtab}}
{{#endtabs}}

So `core()` is the boundary where a lazy vector becomes concrete bits. Reading
it forces the computation, and the result is self-contained: no exponent left to
apply, nothing further to resolve.

<div class="callout callout-note">
<div class="callout-title">Fractional powers still truncate — once</div>

Scaling truncates toward zero, so once a fractional power is applied the
scaled offsets have lost that information for good. What the retained base buys
is that the loss is never compounded: a chain re-scales from the base, so
`ss.power(1, 2).power(2, 1)` **does** recover `ss` exactly, and a three-deep
chain truncates no more than a one-step one.

A lazy `Sparkle` reaches the same place by a different route — the exponents
cancel in the recipe before anything is computed. See
[Sparkle](sparkle.md#fractional-powers).
</div>

