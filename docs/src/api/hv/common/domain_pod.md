# Domain & Pod

## Domain

A logical namespace that groups related hypervectors. Different domains produce orthogonal marker vectors, so composites (Set, Sequence, Octopus) built in different domains are distinguishable.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
d = hv.Domain("animals")            # from name (hashed to 64-bit id)
d = hv.Domain.from_name("animals")  # same as above
d = hv.Domain.from_id(12345)        # from numeric id
d = hv.d0()                         # default domain (id=0)

d.id()       # uint64
d.name()     # str (empty if created from id)
```
{{#endtab}}
{{#tab name="Go"}}
```go
d := hv.NewDomain("animals")                        // from name
d := hv.NewDomainWithPrefix(api.DomainPrefix_LANG, "en") // prefix + name
d := hv.NewDomainByID(12345)                         // from numeric id
d := hv.D0()                                         // default domain

d.ID()       // uint64
d.Name()     // string
d.Prefix()   // api.DomainPrefix_E
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let d = Domain::from_name("animals");     // from name
let d = Domain::from_id(12345);           // from numeric id
let d = Domain::default_domain();         // D0

d.id()       // u64
d.name()     // &str
```
{{#endtab}}
{{#endtabs}}

## Pod

A slot within a Domain, acting as the secondary identifier for a hypervector. The (Domain, Pod) pair uniquely identifies a Sparkle.

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
