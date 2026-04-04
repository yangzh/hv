# SparseOperation

A SparseOperation instance wraps a Model, a random number generator, and potentially other information related to the sparse operation in general.

## Constructor

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
so = hv.SparseOperation(hv.MODEL_1M_10BIT, 0, 42)
so1 = hv.SparseOperation(hv.MODEL_1M_10BIT, "domain", "pod")
```
{{#endtab}}
{{#tab name="Go"}}
```go
so := hv.NewSparseOperation(api.Model_MODEL_1M_10BIT, 0, 42)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let mut so = SparseOp::new(Model::Model1m10bit, 0, 42);
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
so = hv.SparseOperation(hv.MODEL_1M_10BIT, 0, 42)
sparkle = hv.Sparkle.random(hv.Domain("domain"), so)
```
{{#endtab}}
{{#tab name="Go"}}
```go
so := hv.NewSparseOperation(api.Model_MODEL_1M_10BIT, 0, 42)
sparkle := hv.NewRandomSparkle(domain, so)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let mut so = SparseOp::new(Model::Model1m10bit, 0, 42);
let sparkle = Sparkle::random(&domain, &mut so);
```
{{#endtab}}
{{#endtabs}}
