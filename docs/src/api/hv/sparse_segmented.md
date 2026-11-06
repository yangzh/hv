# SparseSegmented 🍡

The most foundational vector type — a sparse binary hypervector where each segment has exactly one ON bit at the recorded offset location. All other types (Sparkle, Set, Sequence, etc.) ultimately contain a `SparseSegmented` in memory for processing, whenever necessary.

## Structure

| Field | Description |
|-------|-------------|
| `model` | Sparsity configuration ([Model](common/models.md)) |
| `offsets` | Packed bit array of per-segment ON offsets. `nil`/`None` = identity vector |
| `hash` | Lazy-computed stable hash for equality checks |
| `domain` / `pod` | The identifier for these offsets; serialized, so it survives a round trip |
| `exponent` | **Always 1.** See below |

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
an array library. `offsets_buffer()` returns the same offsets as a single
little-endian buffer, and `codes_buffer` does a whole batch in one call —
about **27x faster** than iterating, and close to a memory copy.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
import numpy as np

a = np.frombuffer(ss.offsets_buffer(), dtype=ss.offsets_dtype())   # (M,)

# One call for a whole codebook, row-major.
buf = hv.codes_buffer([v0, v1, v2])
codes = np.frombuffer(buf, dtype=hv.offsets_dtype(model)).reshape(3, -1)
```
{{#endtab}}
{{#endtabs}}

`offsets_dtype` is `"uint8"` at 8-bit and `"<u2"` for every wider model — one
element per segment, since every model's offset fits 16 bits. `frombuffer` is
zero-copy, because the returned `bytes` is immutable.

The byte order is **fixed little-endian**, not the host's, so the same vector
exports to the same bytes everywhere.

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

## The exponent is always 1

A `SparseSegmented` **never carries an exponent other than 1**, and this is
structural rather than a convention you could accidentally violate.

Every other type is defined by a *recipe*, and an exponent there is a pending
instruction: "when you compute these offsets, scale them by this much". A
`SparseSegmented` holds no recipe — the offsets *are* the value. So `power()`
scales them on the spot and leaves the exponent at 1; there is nothing left
pending.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
s = hv.Sparkle.from_word(model, "pos", "step")

s.power(3).exponent()          # (3, 1) — lazy, the exponent is pending
s.core().power(3).exponent()   # (1, 1) — materialized, already spent

ss = s.core()
ss.power(1, 2).exponent()      # (1, 1) — the offsets were scaled instead
```
{{#endtab}}
{{#endtabs}}

That is also why the exponent never appears on the wire for this type: writing
it alongside offsets that already carry it would apply the scaling a second
time on read. Domain and pod *are* written — they identify the offsets rather
than transform them.

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

<div class="callout callout-warning">
<div class="callout-title">Which is why fractional powers truncate here</div>

Because `power()` rewrites the offsets immediately, a fractional power
truncates toward zero and the loss is permanent —
`ss.power(1, 2).power(2, 1)` does **not** recover `ss`. On a lazy `Sparkle` the
same pair of calls cancels in the exponent *before* anything is computed, so it
is exact. Compose on the lazy value and call `core()` once at the end. See
[Sparkle](sparkle.md#fractional-powers).
</div>

