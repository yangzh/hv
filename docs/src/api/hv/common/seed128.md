# Seed128

A `Seed128` is a 128-bit seed to drive a random number generator. 

The current random number generator expects 2 64-bit seeds: the same (seed_high, seed_low) pair always produces the same sequence of random numbers, enabling reproducible and deterministic vector generation across runs and languages.

## Constructors

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
# From Domain and Pod arguments (each accepts Domain/Pod, int, or str)
seed = hv.Seed128("animals", "cat")                # domain name + pod word
seed = hv.Seed128(0, 42)                           # default domain + raw pod seed
seed = hv.Seed128("animals", 42)                   # domain name + raw pod seed
seed = hv.Seed128(hv.Domain("animals"), hv.Pod("cat"))  # explicit Domain/Pod objects

# Zero seed
seed_zero = hv.Seed128.zero()                      # (0, 0)

# Random seed from a SparseOperation
seed_rand = hv.Seed128.random(so)                  # consumes two u64 from the RNG

# Accessors
seed.domain()                                      # Domain object
seed.pod()                                         # Pod object
seed.high()                                        # u64 (domain id)
seed.low()                                         # u64 (pod seed)
```
{{#endtab}}
{{#tab name="Go"}}
```go
seed := hv.NewSeed128(0, 42)          // from raw uint64 values
seedZero := hv.Seed128Zero()          // zero seed
seed1 := hv.NewSeed128FromDP(hv.NewDomain("domain"), hv.NewPod("pod"))
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let seed = Seed128::new(0, 42);     // from raw u64 values
let seedZero = Seed128::zero();         // zero seed
```
{{#endtab}}
{{#endtabs}}

## Usage

All composite constructors take a `Seed128`, as seed for the bundle operator:

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
seed = hv.Seed128("fruits", "fruit_set")

s = hv.Set(seed, a, b, c)
seq = hv.Sequence(seed, a, b, c)
```
{{#endtab}}
{{#tab name="Go"}}
```go
seed := hv.NewSeed128(0, 42)

s := hv.NewSet(seed, a, b, c)
seq := hv.NewSequence(seed, 0, a, b, c)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let seed = Seed128::new(0, 42);

let s = Set::new(seed, vec![a, b, c]);
let seq = Sequence::new(seed, 0, vec![a, b, c]);
```
{{#endtab}}
{{#endtabs}}

## Polymorphic arguments (Python-only)

Anywhere a Python factory expects a `Seed128` (composite constructors
like `hv.Set` / `hv.Sequence` / `hv.Octopus`, the `hv.bundle` operator,
etc.) you can pass either a `Seed128` instance or a `(domain, pod)`
tuple — the binding extracts and constructs the seed for you.

| Parameter type | Accepted Python forms |
|----------------|-----------------------|
| `Seed128` | `Seed128` instance, or a `(domain, pod)` tuple |

The tuple **composes** with the polymorphic forms accepted by Domain
and Pod (see
[Domain & Pod → Polymorphic arguments](domain_pod.md#polymorphic-arguments-python-only)),
so each side can itself be a string / int / Prewired enum / `(prefix, name)`
tuple — letting you skip the `hv.Seed128(...)` wrap entirely:

```python
# Equivalent to hv.Sequence(hv.Seed128("words", "hi"), m1, m2):
seq = hv.Sequence(("words", "hi"), m1, m2)

# Tuple form composes with Domain's (DomainPrefix, str) tuple:
seq = hv.Sequence(((hv.DOMAIN_PREFIX_NLP, "concept"), "myseq"), m1, m2)

# And with Pod's Prewired enum:
seq = hv.Sequence(("internal", hv.PREWIRED_STEP), m1, m2)
```
