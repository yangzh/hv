# HyperBinary Types

All vector types conform to a common interface. In Go this is the `HyperBinary` interface; in Rust it is the `HyperBinary` trait. The two implementations are kept at **feature parity**.

{{#tabs global="lang"}}
{{#tab name="Python"}}
Python doesn't have the concept of interface/trait, but all `HyperBinary` derived types share a common set of methods.

```python
v.model()        # Model enum
v.width()
v.cardinality()
v.hint()
v.stable_hash()  # int
v.seed128()
v.exponent()

v.core()         # SparseSegmented
v.power(p)       # HyperBinary
```
{{#endtab}}
{{#tab name="Go"}}
```go
type HyperBinary interface {
    Model() api.Model
    Width() uint32
    Cardinality() uint32
    Hint() api.HyperBinaryProto_Hint
    StableHash() uint64
    Seed128() Seed128
    Exponent() int32

    Core() SparseSegmented
    Power(p int32) HyperBinary
}
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
pub trait HyperBinary: std::fmt::Display {
    fn model(&self) -> Model;
    fn width(&self) -> u32;
    fn cardinality(&self) -> u32;
    fn hint(&self) -> HyperBinaryHint;
    fn stable_hash(&self) -> u64;
    fn seed128(&self) -> &Seed128;
    fn exponent(&self) -> i32;

    fn core(&self) -> SparseSegmented;
    fn power(&self, p: i32) -> HyperBinaryKind;
}
```

In Rust, concrete types are wrapped in `HyperBinaryKind` (an enum) for dynamic dispatch instead of Go's interface boxing.
{{#endtab}}
{{#endtabs}}

## Concrete Types

| Type | Description |
|------|-------------|
| [SparseSegmented 🍡](sparse_segmented.md) | Foundational vector — packed per-segment offsets |
| [Sparkle ✨](sparkle.md) | Seeded, deterministic hypervector |
| [Learner 💫](learner.md) | Online Hebbian learning |
| [Set 🫧](set.md) | Unordered collection |
| [Sequence 📿](sequence.md) | Ordered collection with positional encoding |
| [Octopus 🐙](octopus.md) | Key-value composite |
| [Knot 🪢](knot.md) | Bound (multiplied) group |
| [Parcel 🎁](parcel.md) | Bundled (added) group |
