# Seed128

A `Seed128` is a 128-bit seed to drive a random number generator. A deterministic random sequence can be used for probablistic bundling, for example.

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
seed := hv.NewSeed128(high, low)      // from raw uint64 values
seed := hv.Seed128Zero()              // zero seed
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let seed = Seed128::new(high, low);     // from raw u64 values
let seed = Seed128::zero();             // zero seed
```
{{#endtab}}
{{#endtabs}}

## Usage

All composite constructors take a `Seed128`:

```python
# Python — composites take Seed128 directly
s = hv.Set(hv.Seed128(0, 42), a, b, c)
seq = hv.Sequence(hv.Seed128(0, 42), a, b, c)
```

```go
// Go — composites take Seed128 directly
s := hv.NewSet(hv.NewSeed128(0, 42), a, b, c)
seq := hv.NewSequence(hv.NewSeed128FromDP(domain, pod), 0, a, b, c)
```

```rust
// Rust — composites take Seed128 directly
let s = Set::new(Seed128::new(0, 42), vec![a, b, c]);
let seq = Sequence::new(Seed128::from_dp(domain, pod), 0, vec![a, b, c]);
```
