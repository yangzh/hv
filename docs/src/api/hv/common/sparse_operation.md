# SparseOperation

A SparseOperation instance wraps a Model, a random number generator, and potentially other information related to the sparse operation in general.

## Constructor

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
so = hv.SparseOperation(hv.MODEL_1M_10BIT, 0, 42)

# Explicit RNG backend (keyword-only; omit for the KONGMING_RNG default, hv.RNG_PHILOX_4X64)
# Constants: hv.RNG_PHILOX_4X64, hv.RNG_XOSHIRO_256PP, hv.RNG_PCG_DXSM, hv.RNG_XOROSHIRO_128PP.
so2 = hv.SparseOperation(hv.MODEL_1M_10BIT, 0, 42, rng_hint=hv.RNG_XOSHIRO_256PP)
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

so.rng_hint()     # RNG backend (an hv.RNG_* constant)

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
