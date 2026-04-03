# Sparkle ✨

A seeded hypervector — a [SparseSegmented](sparse_segmented.md) with an associated Domain, Pod (seed source), and exponent. Sparkle is the atomic building block for higher-level constructs: given the same (model, domain, pod), it always produces the same vector deterministically.

## Domain

A logical namespace that groups related Sparkle instances. Sparkle is the **only** HyperBinary type that exposes `Domain()` / `Pod()` directly — all other types expose [Seed128](common/seed128.md).

> **Tip:** Domain display labels in the compact emoji representation:
>
> | Emoji | Variant | Example |
> |-------|---------|---------|
> | 🔗 | Named | `🔗animals`, `🔗PREFIX.name` |
> | 🌐 | Numeric ID | `🌐0x..c862` |

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
d = hv.Domain("animals")            # from name (hashed to 64-bit id)
d = hv.Domain.from_name("animals")  # same as above
d = hv.Domain.from_id(12345)        # from numeric id
d = hv.Domain.with_prefix(hv.DOMAIN_PREFIX_NLP, "sentiment")  # prefixed
d = hv.d0()                         # default domain (id=0)

d.id()       # uint64
d.name()     # str (empty if created from id)

s.domain()   # access the Domain of a Sparkle
```
{{#endtab}}
{{#tab name="Go"}}
```go
d := hv.NewDomain("animals")                             // from name
d := hv.NewDomainWithPrefix(api.DomainPrefix_LANG, "en") // prefix + name
d := hv.NewDomainByID(12345)                              // from numeric id
d := hv.D0()                                              // default domain

d.ID()       // uint64
d.Name()     // string
d.Prefix()   // api.DomainPrefix_E

s.Domain()   // access the Domain of a Sparkle
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let d = Domain::from_name("animals");     // from name
let d = Domain::from_id(12345);           // from numeric id
let d = Domain::default_domain();         // D0

d.id()       // u64
d.name()     // &str

s.domain()   // access the Domain of a Sparkle
```
{{#endtab}}
{{#endtabs}}

## Pod

A slot within a Domain, acting as the secondary identifier for a Sparkle instance. The (Domain, Pod) pair uniquely identifies a Sparkle.

> **Tip:** Pod and exponent display labels:
>
> | Emoji | Variant | Example |
> |-------|---------|---------|
> | 🌱 | Word-seeded | `🌱cat` |
> | 🫛 | Numeric seed | `🫛0x..80e4` |
> | 🍀 | Prewired | `🍀SET_MARKER` |
> | 💪 | Exponent | `💪3`, `💪-1` |
>
> **Identity vectors** display as `IDENT` (e.g., `✨IDENT`).

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
p = hv.Pod("cat")                   # from word (hashed to seed)
p = hv.Pod.from_word("cat")         # same as above
p = hv.Pod.from_seed(42)            # from numeric seed
p = hv.Pod.from_prewired(hv.PREWIRED_SET_MARKER)  # prewired constant
p = hv.p0()                         # default pod (seed=0)

p.seed()      # uint64
p.word()      # str (empty if seed-based)
p.prewired()  # int (0 if not prewired)

s.pod()       # access the Pod of a Sparkle
```
{{#endtab}}
{{#tab name="Go"}}
```go
p := hv.NewPodByWord("cat")                         // from word
p := hv.NewPodBySeed(42)                             // from numeric seed
p := hv.NewPodByPrewired(api.Prewired_SET_MARKER)   // prewired constant
p := hv.P0()                                         // default pod

p.Seed()      // uint64
p.Word()      // string

s.Pod()       // access the Pod of a Sparkle
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let p = Pod::from_word("cat");             // from word
let p = Pod::from_seed(42);                // from numeric seed
let p = Pod::from_prewired(Prewired::SetMarker);  // prewired
let p = Pod::default_pod();                // P0

p.seed()      // u64
p.word()      // &str

s.pod()       // access the Pod of a Sparkle
```
{{#endtab}}
{{#endtabs}}

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

## Notes

- Sparkle is **deterministic**: the same (model, domain, pod) triple always produces the same offsets.
- The underlying offsets are generated lazily from a seeded PRNG. Only the seeds are stored, which is a significant saving; offsets are recomputed during serialization.
- `Power(0)` returns the identity sparkle. `Power(-1)` returns the inverse.
- Serialization / deserialization is designed to work across language / system boundaries.
