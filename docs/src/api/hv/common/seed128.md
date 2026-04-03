# Seed128

A `Seed128` is a 128-bit seed to drive a random number generator. 

The current random number generator expects 2 64-bit seeds (total 128bit): the same (seed_high, seed_low) pair always produces the same sequence of random numbers, enabling reproducible vector generation across runs and languages.

## Constructors

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
seed = hv.Seed128(0, 42)           # from two u64 values (domain id, pod seed)
seedZero = hv.Seed128.zero()       # zero seed

seed.high()                        # u64 (domain id)
seed.low()                         # u64 (pod seed)
```
{{#endtab}}
{{#tab name="Go"}}
```go
seed := hv.NewSeed128(0, 42)          // from raw uint64 values
seedZero := hv.Seed128Zero()          // zero seed
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

All composite constructors take a `Seed128`:

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
seed = hv.Seed128(0, 42)

s = hv.Set(seed, a, b, c)
seq = hv.Sequence(seed, a, b, c)
```
{{#endtab}}
{{#tab name="Go"}}
```go
seed := hv.NewSeed(0, 42)

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
