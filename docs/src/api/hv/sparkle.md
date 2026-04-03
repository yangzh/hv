# Sparkle ✨

A seeded hypervector — a [SparseSegmented](sparse_segmented.md) with an associated Domain, Pod (seed source), and exponent. Sparkle is the atomic building block for higher-level constructs: given the same (model, domain, pod), it always produces the same vector deterministically.

## Constructors

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
# From a word string
s = hv.Sparkle.with_word(model, "animals", "cat")

# From a numeric seed
s = hv.Sparkle.with_seed(model, "animals", 42)

# From a prewired enum
s = hv.Sparkle.with_prewired(model, "animals", hv.PREWIRED_SET_MARKER)

# Identity vector
s = hv.Sparkle.identity(model)

# Random (from SparseOperation)
s = hv.Sparkle.random("animals", so)
```
{{#endtab}}
{{#tab name="Go"}}
```go
// From a word string
s := hv.NewSparkleWithWord(model, domain, "cat")

// From a numeric seed
s := hv.NewSparkleWithSeed(model, domain, 42)

// From a prewired enum
s := hv.NewSparkleWithPrewired(model, domain, api.Prewired_SET_MARKER)

// Identity vector
s := hv.NewSparkleIdentity(model)

// Random (from SparseOperation)
s := hv.NewRandomSparkle(domain, so)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
// From a word string
let s = Sparkle::with_word(model, domain, "cat");

// From a numeric seed
let s = Sparkle::with_seed(model, domain, 42);

// From a prewired enum
let s = Sparkle::with_prewired(model, domain, Prewired::SetMarker);

// Identity vector
let s = Sparkle::identity(model);
```
{{#endtab}}
{{#endtabs}}

## Key Methods

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
s.model()         # Model enum
s.stable_hash()   # Deterministic hash
s.exponent()      # Current exponent (1 for base vector)
s.power(p)        # Returns p-th power (new Sparkle)
s.core()          # Returns underlying SparseSegmented
```
{{#endtab}}
{{#tab name="Go"}}
```go
s.Model()         // api.Model
s.Domain()        // Domain
s.Pod()           // Pod
s.StableHash()    // uint64
s.Exponent()      // int32
s.Power(p)        // HyperBinary (cast to Sparkle)
s.Core()          // SparseSegmented
s.Clone()         // HyperBinary
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
s.model()         // Model
s.domain()        // &Domain
s.pod()           // &Pod
s.stable_hash()   // u64
s.exponent()      // i32
s.power(p)        // Sparkle
s.core()          // SparseSegmented
```
{{#endtab}}
{{#endtabs}}

## Domain & Pod Accessors

Sparkle is the **only** HyperBinary type that exposes `Domain()` and `Pod()` directly. All other types expose `Seed128()` / `seed128()` which wraps both.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
s.domain()        # Domain
s.pod()           # Pod
```
{{#endtab}}
{{#tab name="Go"}}
```go
s.Domain()        // Domain
s.Pod()           // Pod
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
s.domain()        // &Domain
s.pod()           // &Pod
```
{{#endtab}}
{{#endtabs}}

## Display Labels

In the compact emoji representation, Domain and Pod are shown with these labels:

| Emoji | Field | Meaning | Format |
|-------|-------|---------|--------|
| 🔗 | Domain (named) | Semantic namespace | `🔗animals` or `🔗PREFIX.name` |
| 🌐 | Domain (id) | Numeric domain ID | `🌐0x..c862` (lower 16 bits hex) |
| 🫛 | Pod (seed) | Numeric seed | `🫛0x..80e4` (lower 16 bits hex) |
| 🌱 | Pod (named) | Word-seeded pod | `🌱cat` |
| 🍀 | Pod (prewired) | Prewired constant | `🍀SET_MARKER` |
| 💪 | Exponent | Non-trivial exponent | `💪3` or `💪-1` |

**Identity vectors** display as `IDENT` (e.g., `✨IDENT`).

## Notes

- Sparkle is **deterministic**: the same (model, domain, pod) triple always produces the same offsets.
- The underlying offsets are generated lazily from a seeded PRNG (PCG-DXSM). Only the seeds are stored, which is a significant saving; offsets are recomputed during serialization.
- `Power(0)` returns the identity sparkle. `Power(-1)` returns the inverse.
- Serialization / deserialization is designed to work across language / system boundaries.
