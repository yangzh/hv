# HyperBinary Types

All vector types conform to a common interface. In Go this is the `HyperBinary` interface; in Rust it is the `HyperBinary` trait. The two implementations are kept at **feature parity**.

{{#tabs global="lang"}}
{{#tab name="Python"}}
Python doesn't have the concept of interface/trait, but all `HyperBinary` derived types share a common set of methods.

```python
v.model()        # Model enum
v.width()
v.cardinality()
v.stable_hash()  # int
v.seed128()
v.exponent()

v.core()         # SparseSegmented
v.power(p)       # HyperBinary; p=0 (identity) only for SparseSegmented/Sparkle

v.equal_lazy(w)  # bool: provable equality, never materializes
v.equal(w)       # bool: accurate equality (materializes when needed)
v.compact()      # drop cached materializations
```
{{#endtab}}
{{#tab name="Go"}}
```go
type HyperBinary interface {
    Model() api.Model
    Width() int
    Cardinality() int32
    StableHash() uint64
    Seed128() Seed128
    Domain() Domain
    Pod() Pod
    Exponent() int32

    Core() SparseSegmented
    Power(p int) HyperBinary
    Clone() HyperBinary

    EqualLazy(other HyperBinary) bool
    Compact()
}
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
pub trait HyperBinary: std::fmt::Display {
    fn model(&self) -> Model;
    fn width(&self) -> usize;
    fn cardinality(&self) -> usize;
    fn stable_hash(&self) -> u64;
    fn seed128(&self) -> Seed128;
    fn domain(&self) -> &Domain;
    fn pod(&self) -> &Pod;
    fn exponent(&self) -> i32;

    fn core(&self) -> SparseSegmented;
    fn power(&self, p: isize) -> HyperBinaryKind;
    fn clone_hb(&self) -> HyperBinaryKind;

    fn equal_lazy(&self, other: &HyperBinaryKind) -> bool;
    fn compact(&self);
}
```

In Rust, concrete types are wrapped in `HyperBinaryKind` (an enum) for dynamic dispatch instead of Go's interface boxing.
{{#endtab}}
{{#endtabs}}

## Lazy materialization

Every type except `SparseSegmented` is defined by a **recipe** — its model, seed
and members — rather than by raw bits. Constructing one stores the recipe;
the offsets are computed on first observation and cached from then on.
Observations are the operations that genuinely need content: `core()`,
`stable_hash()`, overlap and similarity, serialization of `SparseSegmented`.
Identity questions (`model()`, `domain()`, `pod()`, `exponent()`) never
materialize anything.

This is invisible to results — a vector holds the same content whenever you ask
— but it means constructing vectors you never observe is nearly free, which is
the common case when a search mints many candidates and keeps few.

`compact()` releases the cached content again, recursively through members. The
recipe is retained, so the next observation recomputes exactly the same bits;
the content hash is kept, so equality against a compacted vector stays free.
Use it on subtrees you know are cold — it is advisory, and a no-op when there is
nothing cached.

## Equality

Two levels are available, differing only in how hard they work:

- **`equal_lazy`** compares recipes (and already-known content hashes), so it
  never materializes anything. It is conservative: a `True` answer is always
  correct, while a `False` answer may mean "not provable this cheaply" — two
  vectors of different concrete types, for example, or a coincidence that only
  the bits would reveal.
- **`equal`** (Go: `hv.Equal`, Rust: `HyperBinaryKind::equal`) starts with the
  lazy check and falls back to comparing content hashes, materializing if it
  must. Use it when the answer must be exact.

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
| [Dart 🎯](dart.md) | Directed pair (tail → head) |
