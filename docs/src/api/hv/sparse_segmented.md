# SparseSegmented 🍡

The most foundational vector type — a sparse binary hypervector where each segment has exactly one ON bit at the recorded offset location. All other types (Sparkle, Set, Sequence, etc.) ultimately contain a `SparseSegmented` in memory for processing, whenever necessary.

## Structure

| Field | Description |
|-------|-------------|
| `model` | Sparsity configuration ([Model](common/models.md)) |
| `offsets` | Packed bit array of per-segment ON offsets. `nil`/`None` = identity vector |
| `hash` | Lazy-computed stable hash for equality checks |

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

<div class="callout callout-warning">
<div class="callout-title">Fractional powers truncate here</div>

`SparseSegmented` is materialized, so `power()` rewrites the offsets
immediately. A fractional power truncates toward zero and the loss is
permanent — `ss.power(1, 2).power(2, 1)` does **not** recover `ss`. On a lazy
`Sparkle` the same pair of calls cancels in the exponent before computing, and
is exact. See [Sparkle](sparkle.md#fractional-powers).
</div>

