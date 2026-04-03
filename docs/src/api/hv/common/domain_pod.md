# Seed128

A `Seed128` is a 128-bit seed that embeds a [Domain](#domain) and a [Pod](#pod). It is the primary parameter for all composite constructors (Set, Sequence, Octopus, Knot, Parcel, Cyclone, Learner) and for the Learner.

The `HyperBinary` trait exposes `Seed128()` (Go) / `seed128()` (Rust). Only [Sparkle](../sparkle.md) retains separate `Domain()` / `Pod()` accessors.

## Constructors

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
seed = hv.Seed128(high, low)       # from two u64 values (domain id, pod seed)
seed = hv.Seed128.zero()           # zero seed

seed.high()                        # u64 (domain id)
seed.low()                         # u64 (pod seed)
```
{{#endtab}}
{{#tab name="Go"}}
```go
seed := hv.NewSeed128(domain, pod)    // from Domain + Pod
seed := hv.Seed128Zero()              // zero seed
seed := hv.NewRandomSeed128(so)       // random from SparseOperation

seed.Domain   // Domain
seed.Pod      // Pod
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let seed = Seed128::new(domain, pod);  // from Domain + Pod
let seed = Seed128::zero();            // zero seed

seed.domain   // Domain (pub field)
seed.pod      // Pod (pub field)
```
{{#endtab}}
{{#endtabs}}

## Usage

All composite constructors take a `Seed128`:

```python
# Python — composites accept (domain, pod, ...) and wrap internally
s = hv.Set(domain, pod, a, b, c)
seq = hv.Sequence(domain, pod, a, b, c)
```

```go
// Go — composites take Seed128 directly
s := hv.NewSet(hv.NewSeed128(domain, pod), a, b, c)
seq := hv.NewSequence(hv.NewSeed128(domain, pod), 0, a, b, c)
```

```rust
// Rust — composites take Seed128 directly
let s = Set::new(Seed128::new(domain, pod), vec![a, b, c]);
let seq = Sequence::new(Seed128::new(domain, pod), 0, vec![a, b, c]);
```

## Domain

A logical namespace that groups related hypervectors. Different domains produce orthogonal marker vectors, so composites (Set, Sequence, Octopus) built in different domains are distinguishable.

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
