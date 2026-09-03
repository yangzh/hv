# HyperBinary Types

All vector types conform to a common `HyperBinary` interface, kept at **feature parity** across the underlying engines.

{{#tabs global="lang"}}
{{#tab name="Python"}}
Python doesn't have the concept of interface/trait, but all `HyperBinary` derived types share a common set of methods.

```python
v.model()        # Model enum
v.width()
v.cardinality()
v.stable_hash()  # unique hash for this vector
v.seed128()
v.exponent()
```
{{#endtab}}
{{#endtabs}}

## Lazy materialization

Every type except `SparseSegmented` is defined by a **recipe** — much more compact than raw offsets.

The raw offsets will be computed and cached on first usage by APIs such as 
`core()`, `stable_hash()`, overlap and similarity, serialization of `SparseSegmented`, etc. Other API calls, such as `model()`, `domain()`, `pod()`, `exponent()`, never materialize anything.

This is invisible to callers: the vector holds the same semantic content whenever you ask, but it means constructing vectors you never observe is nearly free, which is the typical and common use case for hypervectors.

`compact()` releases the cached content again, recursively through members. The recipe is retained, so the next observation recomputes exactly the same bits.

## The tale of two equalities

Two levels are available, differing only in how hard they work:

- **`equal_lazy`** compares recipes (and already-known content hashes), so it
  never materializes anything. It is conservative: a `True` answer is always
  correct, while a `False` answer may mean "not provable this cheaply" — two
  vectors of different concrete types, for example, or a coincidence that only
  the actual offsets would reveal.
- **`equal`** starts with the
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
| [Knot 🪢](knot.md) | Results from bind operator |
| [Parcel 🎁](parcel.md) | Results from bundle operator |
| [Dart 🎯](dart.md) | Directed pair (tail → head) |
