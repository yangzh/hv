# Knot 🪢

Knot 🪢 contains the result of binding (multiplicative composition) of hypervectors, while tracking its member parts for serialization and introspection. See [Composites: Knot](../../concepts/composites.md#knot).

## Constructor

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
# More commonly via the bind operator:
k = hv.bind(a, b)
```
{{#endtab}}
{{#endtabs}}

## Extending a Knot

An existing Knot can be extended with additional parts via
[`expand`](operators.md#expand-extend-a-knot). This **returns a new
Knot** (as a Knot is an immutable value) — equivalent to re-binding all
parts from scratch but without reconstructing the base.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
k = hv.bind(a, b)
k2 = k.expand(c)  # k2 is equivalent to hv.bind(a, b, c); k is unchanged
```
{{#endtab}}
{{#tab name="Go"}}
```go
k := hv.Bind(a, b)
k2 := k.Expand(c) // k2 is equivalent to hv.Bind(a, b, c); k is unchanged
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let k = operators::bind_hb(vec![a.clone(), b.clone()]);
let k2 = k.expand(vec![c]); // equivalent to bind_hb(vec![a, b, c]); consumes k
// To keep the original: k.clone().expand(vec![c])
```
{{#endtab}}
{{#endtabs}}
