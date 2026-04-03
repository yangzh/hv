# Sparkle ✨


Sparkles are the atomic building block for higher-level constructs: essentially [SparseSegmented](sparse_segmented.md) annotated with domain and pod. 

Domain is a logical namespace that groups related Sparkle instances. Pod acts as the secondary identifier for a Sparkle instance.

Sparkle is **deterministic**: the same (domain, pod) pair always produces the same offsets. For this reason, the (model, pod) pair uniquely identifies a Sparkle.

## Sparkle Constructors

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
s.StableHash()    // uint64
s.Exponent()      // int32

s.Power(p)        // HyperBinary (cast to Sparkle)
s.Core()          // SparseSegmented
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
s.model()         // Model
s.stable_hash()   // u64
s.exponent()      // i32

s.power(p)        // Sparkle
s.core()          // SparseSegmented
```
{{#endtab}}
{{#endtabs}}

## Pretty-printing

{{#tabs global="lang"}}
{{#tab name="Python"}}
```Python
# Pretty-printing, or s.__str__()
print(s)

# More detailed information, or s.__repr__()
s
```
{{#endtab}}
{{#endtabs}}

During pretty-printing of Sparkle instances, you may notice special emoji for domain / pods.

<div class="callout callout-tip">
<div class="callout-title">emojis for domain / pod</div>

| Emoji | Variant | Example |
|-------|---------|---------|
| 🔗 | Named | `🔗animals`, `🔗PREFIX.name` |
| 🌐 | Numeric ID | `🌐0x..c862` |
| 🌱 | Word-seeded | `🌱cat` |
| 🫛 | Numeric seed | `🫛0x..80e4` |
| 🍀 | Prewired | `🍀SET_MARKER` |
| 💪 | Exponent / Power | `💪3`, `💪-1` |

**Identity vectors** display as `IDENT` (e.g., `✨IDENT`).

</div>

## Notes
- The underlying offsets are generated lazily from a seeded PRNG. Only the seeds are stored, which is a significant saving; offsets are recomputed during serialization.
- `Power(0)` alwsys returns the identity sparkle. `Power(-1)` returns the inverse.
- Serialization / deserialization is designed to work across language / system boundaries.
