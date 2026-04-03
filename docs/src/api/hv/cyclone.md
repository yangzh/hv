# Cyclone 🌀

A periodic permutation vector where `power(v, period) == identity`. See [Composites: Cyclone](../../concepts/composites.md#cyclone).

Constraint: `segment_size(model)` must be divisible by `period`.

## Constructor

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
c = hv.Cyclone(model, hv.Seed128(0, 42), period=16)
```
{{#endtab}}
{{#tab name="Go"}}
```go
c, err := hv.NewCyclone(model, hv.NewSeed128(0, 42), 16)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let c = Cyclone::new(model, Seed128::new(0, 42), 16)?;
```
{{#endtab}}
{{#endtabs}}
