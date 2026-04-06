# Pod

A `Pod` is a slot within a Domain, acting as the secondary identifier for a hypervector. It provides the low 64-bit half of a `Seed128`. The (Domain, Pod) pair uniquely identifies a Sparkle.

Pods can be seeded by a string word, a raw uint64, or a prewired enum value.

## Constructors

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
# From a word string (hashed to a 64-bit seed)
p = hv.Pod("cat")

# Same as above
p = hv.Pod.from_word("cat")

# From a raw 64-bit seed
p = hv.Pod.from_seed(42)

# From a prewired enum value
p = hv.Pod.from_prewired(hv.PREWIRED_SET_MARKER)
p = hv.Pod.from_prewired(hv.PREWIRED_STEP)

# Accessors
p.seed()       # u64
p.word()       # str (empty if constructed from seed or prewired)
p.prewired()   # int (0 if not prewired)
p.is_default() # True if seed == 0
```
{{#endtab}}
{{#tab name="Go"}}
```go
p := hv.NewPodByWord("cat")
p := hv.NewPodBySeed(42)
p := hv.NewPodByPrewired(api.Prewired_SET_MARKER)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let p = Pod::from_word("cat");
let p = Pod::from_seed(42);
let p = Pod::from_prewired(Prewired::SetMarker);
```
{{#endtab}}
{{#endtabs}}

## Prewired Constants

Prewired pods are infrastructure-level constants with fixed seeds:

| Constant | Value | Label |
|----------|-------|-------|
| `hv.PREWIRED_NIL` | 1 | ∅ |
| `hv.PREWIRED_FALSE` | 2 | ❎ |
| `hv.PREWIRED_TRUE` | 3 | ✅ |
| `hv.PREWIRED_BEGIN` | 4 | 🚀 |
| `hv.PREWIRED_END` | 5 | 🏁 |
| `hv.PREWIRED_LEFT` | 6 | ⬅️ |
| `hv.PREWIRED_RIGHT` | 7 | ➡️ |
| `hv.PREWIRED_UP` | 8 | ⬆️ |
| `hv.PREWIRED_DOWN` | 9 | ⬇️ |
| `hv.PREWIRED_MIDDLE` | 10 | ⏺️ |
| `hv.PREWIRED_STEP` | 11 | 𓊍 |
| `hv.PREWIRED_SET_MARKER` | 16 | 🫧 |
| `hv.PREWIRED_SEQUENCE_MARKER` | 17 | 📿 |
