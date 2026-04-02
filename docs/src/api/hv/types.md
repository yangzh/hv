# HyperBinary Types

All vector types conform to a common interface. In Go this is the `HyperBinary` interface; in Rust it is the `HyperBinary` trait. The two implementations are kept at **feature parity**.

{{#tabs global="lang"}}
{{#tab name="Python"}}
In Python, there is no explicit interface. All types expose the same methods (`model()`, `stable_hash()`, `core()`, `power()`, etc.) by convention.

```python
v.model()        # Model enum
v.stable_hash()  # int
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
    Core() SparseSegmented
    Domain() Domain
    Pod() Pod
    Exponent() int32
    Power(p int32) HyperBinary
    Clone() HyperBinary

    // Display: String() returns compact emoji form;
    // Repr() returns detailed YAML/proto form.
    // Both are part of the interface in Go.
    fmt.Stringer
    Repr() string

    // Serialization is part of the interface in Go.
    ToProto(ctx context.Context) (*api.HyperBinaryProto, error)
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
    fn core(&self) -> SparseSegmented;
    fn domain(&self) -> &Domain;
    fn pod(&self) -> &Pod;
    fn exponent(&self) -> i32;
    fn power(&self, p: i32) -> HyperBinaryKind;
    fn clone_hb(&self) -> HyperBinaryKind;

    // Display: via the std::fmt::Display supertrait (shown above).
    // No separate Repr(); use Debug derive or per-type formatting.

    // Serialization: to_proto() / from_proto() are inherent methods
    // on each concrete type, not part of the trait.
}
```

In Rust, concrete types are wrapped in `HyperBinaryKind` (an enum) for dynamic dispatch instead of Go's interface boxing.
{{#endtab}}
{{#endtabs}}

## Type Symbols

| Emoji | Type |
|-------|------|
| ✨ | Sparkle |
| 🍡 | SparseSegmented |
| 💫 | Learner |
| 🫧 | Set |
| 📿 | Sequence |
| 🐙 | Octopus |
| 🪢 | Knot |
| 🎁 | Parcel |
| 🌀 | Cyclone |
| 🎯 | Dart |

See [Display & Emoji](display.md) for the full field label reference.

## Concrete Types

| Type | Description |
|------|-------------|
| [SparseSegmented 🍡](sparse_segmented.md) | Foundational vector — packed per-segment offsets |
| [Sparkle ✨](sparkle.md) | Seeded, deterministic hypervector |
| [Set 🫧](set.md) | Unordered collection |
| [Sequence 📿](sequence.md) | Ordered collection with positional encoding |
| [Octopus 🐙](octopus.md) | Key-value composite |
| [Knot 🪢](knot.md) | Bound (multiplied) group |
| [Parcel 🎁](parcel.md) | Bundled (added) group |
| [Cyclone 🌀](cyclone.md) | Periodic permutation vector |
| [Learner 💫](learner.md) | Online Hebbian learning |
