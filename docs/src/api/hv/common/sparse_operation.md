# SparseOperation

A Model wrapped with a seeded PCG-DXSM random number generator. Primary way to create random vectors deterministically.

The same (model, seed_high, seed_low) triple always produces the same sequence of random numbers, enabling reproducible vector generation across runs and languages.

## Constructor

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
so = hv.SparseOperation(model, seed_high, seed_low)
```
{{#endtab}}
{{#tab name="Go"}}
```go
so := hv.NewSparseOperation(model, seedHigh, seedLow)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let mut so = SparseOp::new(model, seed_high, seed_low);
```
{{#endtab}}
{{#endtabs}}

## Methods

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
so.model()        # Model enum
so.uint64()       # next random u64
so.width_bits()   # log2(width) for this model
```
{{#endtab}}
{{#tab name="Go"}}
```go
so.Model()        // api.Model
so.Width()        // uint32
so.Cardinality()  // uint32
so.Sparsity()     // float64
so.Uint64()       // uint64 — next random number
so.Seed()         // Seed128
so.RNG()          // *rand.Rand
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
so.model()        // Model
so.uint64()       // u64 — next random number
so.uint32()       // u32
```
{{#endtab}}
{{#endtabs}}

## Usage: Generating Random Vectors

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
so = hv.SparseOperation(model, seed_high, seed_low)
sparkle = hv.Sparkle.random("domain", so)
random_u64 = so.uint64()
```
{{#endtab}}
{{#tab name="Go"}}
```go
so := hv.NewSparseOperation(model, seedHigh, seedLow)
sparkle := hv.NewRandomSparkle(domain, so)
randomU64 := so.Uint64()
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let mut so = SparseOp::new(model, seed_high, seed_low);
let sparkle = Sparkle::random(&domain, &mut so);
let random_u64 = so.uint64();
```
{{#endtab}}
{{#endtabs}}
