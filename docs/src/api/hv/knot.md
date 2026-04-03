# Knot 🪢

The result of binding (multiplicative composition) of hypervectors. Unlike `BindDirect`, Knot tracks its member parts for serialization and debugging. See [Composites: Knot](../../concepts/composites.md#knot).

## Constructor

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
# Not directly constructed in Python. Use hv.bind() instead.
k = hv.bind(a, b)
```
{{#endtab}}
{{#tab name="Go"}}
```go
k := hv.NewKnot(hv.NewSeed128(0, 42), partA, partB)

// More commonly via the Bind operator:
k := hv.Bind(a, b)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let k = Knot::new(Seed128::new(0, 42), parts);
```
{{#endtab}}
{{#endtabs}}

