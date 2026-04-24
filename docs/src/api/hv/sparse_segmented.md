# SparseSegmented 🍡

The most foundational vector type — a sparse binary hypervector where each segment has exactly one ON bit at the recorded offset location. All other types (Sparkle, Set, Sequence, etc.) ultimately contain a `SparseSegmented` in memory for processing.

## Structure

| Field | Description |
|-------|-------------|
| `model` | Sparsity configuration ([Model](common/models.md)) |
| `offsets` | Packed bit array of per-segment ON offsets. `nil`/`None` = identity vector |
| `hash` | Lazy-computed stable hash for equality checks |

The offsets are bit-packed according to the model's sparsity bits — they do **not** align to byte boundaries. This trades a small CPU cost for compact, uniform storage that works both in memory and on disk.

**Identity vector**: when `offsets` is blank, the vector is the identity vector where all offsets are 0. Binding with identity is a no-op, and identity requires zero storage for offsets.

## Constructors

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
# Identity
ss = hv.SparseSegmented.identity(model)

# From per-segment offsets, typically discouraged...
ss = hv.SparseSegmented.from_offsets(model, [off0, off1, ...])
```
{{#endtab}}
{{#tab name="Go"}}
```go
// Identity
ss := hv.NewSparseSegmentedIdentity(model)

// With explicit domain/pod and packed offsets (takes ownership of slice)
ss := hv.NewSparseSegmented(model, domain, pod, offsets)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
// Identity
let ss = SparseSegmented::identity(model);

// With explicit domain/pod and packed offsets (takes ownership)
let ss = SparseSegmented::new(model, domain, pod, Some(offsets));
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

# Similarity
hv.overlap(a, b)   # Count of matching ON bits
hv.hamming(a, b)   # Count of differing segments

ss.offsets()   # returns all offsets
```
{{#endtab}}
{{#tab name="Go"}}
```go
ss.IsIdentity()   // bool

ss2 := ss.Power(2).(hv.SparseSegmented)
inv := ss.Power(-1).(hv.SparseSegmented)

// Similarity
a.Overlap(b)   // uint32
a.Hamming(b)   // uint32

// offset access.
ss.On(idx)         // Check if a specific global index is ON
ss.Offset(seg)     // Get the offset within a segment

// Iterate over all (segment, offset) pairs
for seg, offset := range ss.OffsetIter() {
    // ...
}
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
ss.is_identity()  // bool

let ss2 = ss.power(2);
let inv = ss.power(-1);

// Similarity
a.overlap(&b)   // u32
a.hamming(&b)   // u32

// offset access.
ss.on(idx)          // bool
ss.offset(seg)      // u32

for (seg, offset) in ss.offset_iter() {
    // ...
}
```
{{#endtab}}
{{#endtabs}}

## Serialization

SparseSegmented serializes to `HyperBinaryProto` with hint `SPARSE_SEGMENTED`. The `offsets` field carries the raw packed bytes. Identity vectors serialize with empty offsets.
