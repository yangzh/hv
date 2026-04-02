# SparseSegmented

The foundational vector type — a sparse binary hypervector where each segment has exactly one ON bit at a recorded offset. All other types (Sparkle, Set, Sequence, etc.) ultimately stores a `SparseSegmented` in memory and can be accessed via `.Core()`.

## Structure

| Field | Description |
|-------|-------------|
| `model` | Sparsity configuration ([Model](model.md)) |
| `offsets` | Packed bit array of per-segment ON offsets. `nil`/`None` = identity vector |
| `hash` | Lazy-computed stable hash for equality checks |

The offsets are bit-packed according to the model's sparsity bits — they do **not** align to byte boundaries. This trades a small CPU cost for compact, uniform storage that works both in memory and on disk.

**Identity vector**: when `offsets` is nil/None, the vector is the identity (all offsets = 0). Binding with identity is a no-op, and identity requires zero storage for offsets.

## Constructors

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
# From raw offsets, typically discouraged...
ss = hv.SparseSegmented(model, offsets_bytes)

# Identity
ss = hv.SparseSegmented.identity(model)

# Random
so = hv.SparseOperation(model, seed_high, seed_low)
ss = hv.SparseSegmented.random(so)
```
{{#endtab}}
{{#tab name="Go"}}
```go
// From raw offsets (takes ownership of slice)
ss := hv.NewSparseSegmented(model, offsets)

// Identity
ss := hv.NewSparseSegmentedIdentity(model)

// Random
ss := hv.NewRandomSparseSegmented(so)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
// From raw offsets (takes ownership)
let ss = SparseSegmented::new(model, Some(offsets));

// Identity
let ss = SparseSegmented::identity(model);

// Random
let ss = SparseSegmented::from_random(model, seed_high, seed_low);
```
{{#endtab}}
{{#endtabs}}

## Key Methods

### Model Properties

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
ss.model()        # Model enum
ss.width()        # Total dimensions
ss.cardinality()  # Number of ON bits (= segments)
ss.stable_hash()  # Deterministic hash
ss.is_identity()  # True if identity vector
```
{{#endtab}}
{{#tab name="Go"}}
```go
ss.Model()        // api.Model
ss.Width()        // uint32
ss.Cardinality()  // uint32
ss.StableHash()   // uint64
ss.IsIdentity()   // bool
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
ss.model()        // Model
ss.width()        // u32
ss.cardinality()  // u32
ss.stable_hash()  // u64
ss.is_identity()  // bool
```
{{#endtab}}
{{#endtabs}}

### Similarity

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
hv.overlap(a, b)   # Count of matching ON bits
hv.hamming(a, b)   # Count of differing segments
```
{{#endtab}}
{{#tab name="Go"}}
```go
a.Overlap(b)   // uint32
a.Hamming(b)   // uint32
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
a.overlap(&b)   // u32
a.hamming(&b)   // u32
```
{{#endtab}}
{{#endtabs}}

### Power (Permutation)

Returns the $p$-th power of the vector. `Power(0)` returns identity, `Power(-1)` returns the inverse.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
ss2 = ss.power(3)
inv = ss.power(-1)
```
{{#endtab}}
{{#tab name="Go"}}
```go
ss2 := ss.Power(3).(hv.SparseSegmented)
inv := ss.Power(-1).(hv.SparseSegmented)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let ss2 = ss.power(3);
let inv = ss.power(-1);
```
{{#endtab}}
{{#endtabs}}

### Bit Access

{{#tabs global="lang"}}
{{#tab name="Python"}}
Not directly exposed in Python.
{{#endtab}}
{{#tab name="Go"}}
```go
// Check if a specific global index is ON
ss.On(idx)         // bool

// Get the offset within a segment
ss.Offset(seg)     // uint32

// Iterate over all (segment, offset) pairs
for seg, offset := range ss.OffsetIter() {
    // ...
}
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
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
