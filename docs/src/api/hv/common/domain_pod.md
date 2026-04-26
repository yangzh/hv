# Domain & Pod

A `Domain` models the semantic grouping for hypervectors, providing the high 64-bit half of a `Seed128`. A `Pod` is a slot within a Domain, providing the low 64-bit half. The (Domain, Pod) pair uniquely identifies a Sparkle.

## Domain Constructors

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
# From a name string (hashed to a 64-bit id)
d = hv.Domain("animals")

# Same as above
d = hv.Domain.from_name("animals")

# From a raw 64-bit id
d = hv.Domain.from_id(0x1234567890abcdef)

# From a domain prefix enum and a name suffix
# The id is computed as xxhash(prefix_label + "." + name)
d = hv.Domain.from_prefix_and_name(hv.DOMAIN_PREFIX_NLP, "concept")

# Accessors
d.id()              # u64
d.name()            # str (empty if constructed from id)
d.domain_prefix()   # int (0 = UNKNOWN if no prefix was set)
d.is_default()      # True if id == 0
```
{{#endtab}}
{{#tab name="Go"}}
```go
d := hv.NewDomain("animals")
d := hv.NewDomainByID(0x1234567890abcdef)
d := hv.NewDomainWithPrefix(api.DomainPrefix_NLP, "concept")
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let d = Domain::from_name("animals");
let d = Domain::from_id(0x1234567890abcdef);
let d = Domain::with_prefix(DomainPrefix::Nlp, "concept");
```
{{#endtab}}
{{#endtabs}}

### Domain Prefix Constants

| Constant | Label |
|----------|-------|
| `hv.DOMAIN_PREFIX_USER` | 🎭 |
| `hv.DOMAIN_PREFIX_NLP` | 💬 |

Domain prefixes provide namespacing for domains. When a prefix is set, the domain id is derived from the prefix label (and optional name), ensuring consistent hashing across languages.

## Pod Constructors

Pods can be seeded by a string word, a raw uint64, or a prewired enum value.

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

### Prewired Constants

Prewired pods are infrastructure-level constants with fixed seeds:

| Constant | Label |
|----------|-------|
| `hv.PREWIRED_NIL` | ∅ |
| `hv.PREWIRED_FALSE` | ❎ |
| `hv.PREWIRED_TRUE` | ✅ |
| `hv.PREWIRED_BEGIN` | 🚀 |
| `hv.PREWIRED_END` | 🏁 |
| `hv.PREWIRED_LEFT` | ⬅️ |
| `hv.PREWIRED_RIGHT` | ➡️ |
| `hv.PREWIRED_UP` | ⬆️ |
| `hv.PREWIRED_DOWN` | ⬇️ |
| `hv.PREWIRED_MIDDLE` | ⏺️ |
| `hv.PREWIRED_STEP` | 𓊍 |
| `hv.PREWIRED_SET_MARKER` | 🫧 |
| `hv.PREWIRED_SEQUENCE_MARKER` | 📿 |

## Polymorphic arguments (Python)

Most Python factories that take a `Domain`, `Pod`, or `Seed128` accept
the underlying primitives directly — you rarely need to wrap them
explicitly:

| Parameter type | Accepted Python forms |
|----------------|-----------------------|
| `Domain` | `Domain` instance, `str` (→ `Domain.from_name`), `int` (→ `Domain.from_id`), `(DomainPrefix, str)` tuple (→ `Domain.with_prefix`) |
| `Pod` | `Pod` instance, `Prewired` enum (→ `Pod.from_prewired`), `str` (→ `Pod.from_word`), `int` (→ `Pod.from_seed`) |
| `Seed128` | `Seed128` instance, or a `(domain, pod)` tuple — each side polymorphic per the rows above (so the tuple can nest) |

```python
# Domain — four equivalent forms in any factory expecting a Domain:
memory.by_item_key("animals", "cat")
memory.by_item_key(hv.Domain.from_name("animals"), "cat")
memory.by_item_key(0x1234, "cat")                           # from numeric id
memory.by_item_key((hv.DOMAIN_PREFIX_NLP, "concept"), "p")  # from (prefix, name)

# Pod — Prewired enum is recognized:
memory.new_terminal("internal", hv.PREWIRED_STEP)           # Pod from Prewired
memory.new_terminal("animals", "cat")                       # Pod from word
memory.new_terminal("animals", 0xCAFE_BABE)                 # Pod from raw seed

# Seed128 — (domain, pod) tuple:
seq = hv.Sequence(("words", "hi"), m1, m2)
seq = hv.Sequence(hv.Seed128("words", "hi"), m1, m2)        # equivalent

# Tuple forms compose — Seed128 with a prefixed Domain:
seq = hv.Sequence(((hv.DOMAIN_PREFIX_NLP, "concept"), "myseq"), m1, m2)
```

Disambiguation rules (order-sensitive in the extractor):

- `Pod` checks the `Prewired` enum **before** `int` so `hv.PREWIRED_STEP`
  (which is also an `IntEnum` member, hence also an `int`) routes to
  `Pod.from_prewired`, not `Pod.from_seed`.
- `Domain` checks the `(DomainPrefix, str)` tuple **before** the `int`
  branch for the same reason — `DomainPrefix` members extract as ints.

Applies to `memory.*` producers/selectors (`new_terminal`,
`new_learner`, `from_set_members`, `from_sequence_members`,
`from_key_values`, `by_item_key`, `by_item_domain`, `with_sparkle`,
`only_domain`, `set_attractor`, `sequence_attractor`), storage
convenience methods (`storage.get/exists/delete/note/names`,
`view.read_chunk/chunk_exists`), and `hv.*` composite constructors
(`Set`, `Sequence`, `Octopus`, `Dart`, `Cyclone`, `Learner`,
`Knot`, `Parcel`, `bundle`, `bind_direct`).
