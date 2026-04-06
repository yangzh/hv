# Sparkle ✨


Sparkles are the atomic building block for higher-level constructs: essentially [SparseSegmented](sparse_segmented.md) annotated with domain and pod. 

Domain is a logical namespace that groups related Sparkle instances. Pod acts as the secondary identifier for a Sparkle instance.

Sparkle is **deterministic**: the same (domain, pod) pair always produces the same offsets. For this reason, the (model, pod) pair uniquely identifies a Sparkle.

## Sparkle Constructors

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
# From a word string
s0 = hv.Sparkle.from_word(model, "animals", "cat")

# From a numeric seed
s1 = hv.Sparkle.from_seed(model, "animals", 42)

# From a prewired enum
s2 = hv.Sparkle.from_prewired(model, "animals", hv.PREWIRED_SET_MARKER)

# Identity vector
s3 = hv.Sparkle.identity(model)

# Random (from SparseOperation)
so=hv.SparseOperation(hv.MODEL_1M_10BIT, "domain", "pod")
s4 = hv.Sparkle.random("animals", so)
```
{{#endtab}}
{{#tab name="Go"}}
```go
// From a word string
s0 := hv.NewSparkleWithWord(model, domain, "cat")

// From a numeric seed
s1 := hv.NewSparkleWithSeed(model, domain, 42)

// From a prewired enum
s2 := hv.NewSparkleWithPrewired(model, domain, api.Prewired_SET_MARKER)

// Identity vector
s3 := hv.NewSparkleIdentity(model)

// Random (from SparseOperation)
s4 := hv.NewRandomSparkle(domain, so)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
// From a word string
let s0 = Sparkle::with_word(model, domain, "cat");

// From a numeric seed
let s1 = Sparkle::with_seed(model, domain, 42);

// From a prewired enum
let s2 = Sparkle::with_prewired(model, domain, Prewired::SetMarker);

// Identity vector
let s3 = Sparkle::identity(model);

// Random (from SparseOperation)
let s4 = Sparkle::from_random(domain, &mut so);
```
{{#endtab}}
{{#endtabs}}

## Key Methods

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
s0.model()         # Model enum
s0.stable_hash()   # Deterministic hash
s0.exponent()      # Current exponent (1 for base vector)

s0_square=s0.power(2)     # Returns p-th power (new Sparkle)
hv.equal(s0, s0_square)   # s0_square = s0^2, different from original s0.
       
core0=s0.core()     # Returns underlying SparseSegmented
core0.offsets()    # The raw offsets for each segment.
```
{{#endtab}}
{{#tab name="Go"}}
```go
s0.Model()         // api.Model
s0.StableHash()    // uint64
s0.Exponent()      // int32

s0Square := s0.Power(2)  // HyperBinary (cast to Sparkle)
s0Square.Core()          // SparseSegmented
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
s0.model()         // Model
s0.stable_hash()   // u64
s0.exponent()      // i32

let s0_square = s0.power(2)        // Sparkle
s0.core()          // SparseSegmented
```
{{#endtab}}
{{#endtabs}}

<div class="callout callout-note">
<div class="callout-title">Note</div>

`power(0)` always returns the identity sparkle. `power(-1)` returns the inverse.
</div>

## Pretty-printing

{{#tabs global="lang"}}
{{#tab name="Python"}}
```Python
# Pretty-printing, or s.__str__()
print(s0)
# ✨:🔗animals,🌱cat

# More detailed information, or s.__repr__()
s
# hint: SPARKLE
# model: MODEL_1M_10BIT
# stable_hash: 9725717137035622833
# domain:
#   name: animals
# pod:
#   word: cat
```
{{#endtab}}
{{#endtabs}}

During pretty-printing of Sparkle instances, you may notice special emoji for domain / pods.

<div class="callout callout-tip">
<div class="callout-title">emojis for domain / pod</div>

| Emoji | Variant | Example |
|-------|---------|---------|
| 🔗 | named domain| `🔗animals`, `🔗PREFIX.name` |
| 🌐 | numeric domain | `🌐0x..c862` |
| 🌱 | named pod | `🌱cat` |
| 🫛 | numeric pod | `🫛0x..80e4` |
| 🍀 | pre-defined pod | `🍀SET_MARKER` |
| 💪 | Exponent / Power | `💪3`, `💪-1` |

**Identity vectors** display as `IDENT` (e.g., `✨IDENT`).

</div>

<div class="callout callout-note">
<div class="callout-title">Note</div>

The underlying offsets are lazily generated from a seeded PRNG. Only the seeds are stored in serialization, which is a significant storage saving; offsets are recomputed during de-serialization.

</div>