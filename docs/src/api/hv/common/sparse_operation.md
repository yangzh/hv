# SparseOperation

A SparseOperation instance wraps a Model, and a random number generator. It can be used to create random vectors deterministically.

The current random number generator expects 2 64-bit seeds (total 128bit): the same (model, seed_high, seed_low) triple always produces the same sequence of random numbers, enabling reproducible vector generation across runs and languages.

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
so.width()        # width for this model
so.cardinality()  # cardinality for this model
so.sparsity()     # sparsity for this model
so.uint64()       # next random number

```
{{#endtab}}
{{#tab name="Go"}}
```go
so.Model()        // api.Model
so.Width()        // width for this model
so.Cardinality()  // cardinality for this model
so.Sparsity()     // sparsity for this model
so.Uint64()       // next random number
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
so.model()        // Model
so.width()        // width for this model
so.cardinality()  // cardinality for this model
so.sparsity()     // sparsity for this model
so.uint64()       // next random number
```
{{#endtab}}
{{#endtabs}}

## Usage: Generating Random Vectors

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
so = hv.SparseOperation(model, seed_high, seed_low)
sparkle = hv.Sparkle.random("domain", so)
```
{{#endtab}}
{{#tab name="Go"}}
```go
so := hv.NewSparseOperation(model, seedHigh, seedLow)
sparkle := hv.NewRandomSparkle(domain, so)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let mut so = SparseOp::new(model, seed_high, seed_low);
let sparkle = Sparkle::random(&domain, &mut so);
```
{{#endtab}}
{{#endtabs}}
