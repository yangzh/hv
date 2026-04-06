# Domain

A `Domain` models the semantic grouping for hypervectors. It provides the high 64-bit half of a `Seed128`. The (Domain, Pod) pair uniquely identifies a Sparkle.

## Constructors

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

## Domain Prefix Constants

| Constant | Value | Label |
|----------|-------|-------|
| `hv.DOMAIN_PREFIX_UNKNOWN` | 0 | (none) |
| `hv.DOMAIN_PREFIX_INTERNAL` | 1 | ⚙️ |
| `hv.DOMAIN_PREFIX_USER` | 2 | 🎭 |
| `hv.DOMAIN_PREFIX_NLP` | 3 | 💬 |
| `hv.DOMAIN_PREFIX_LISP` | 4 | λ |

Domain prefixes provide namespacing for domains. When a prefix is set, the domain id is derived from the prefix label (and optional name), ensuring consistent hashing across languages.
