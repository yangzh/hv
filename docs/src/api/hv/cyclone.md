# Cyclone 🌀

A periodic permutation vector where `power(v, period) == identity`. See [Composites: Cyclone](../../concepts/composites.md#cyclone).

Constraint: `segment_size(model)` must be divisible by `period`.

## Constructor

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
c = hv.Cyclone(model, domain, pod, 16)  # period=16
```
{{#endtab}}
{{#tab name="Go"}}
```go
c, err := hv.NewCyclone(model, seed, 16)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let c = Cyclone::new(model, seed, 16)?;
```
{{#endtab}}
{{#endtabs}}

## Key Methods

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
c.period()      # int
c.power(p)      # HyperBinary
c.model()       # Model
c.core()        # SparseSegmented
```
{{#endtab}}
{{#tab name="Go"}}
```go
c.Period()      // uint32
c.Power(p)      // HyperBinary — wraps around at period
c.Model()       // api.Model
c.Core()        // SparseSegmented
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
c.period()      // u32
c.power(p)      // Cyclone
c.model()       // Model
c.core()        // SparseSegmented
```
{{#endtab}}
{{#endtabs}}
