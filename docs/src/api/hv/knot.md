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

## Extending a Knot

An existing Knot can be extended with additional parts via
[`expand`](operators.md#expand-extend-a-knot). This **mutates the Knot
in place** — equivalent to re-binding all parts from scratch but
without reconstructing the base.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
k = hv.bind(a, b)
k.expand(c)       # k is now equivalent to hv.bind(a, b, c)
```
{{#endtab}}
{{#tab name="Go"}}
```go
k := hv.Bind(a, b)
k.Expand(c)       // k is now equivalent to hv.Bind(a, b, c)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let mut k = operators::bind_hb(vec![a.clone(), b.clone()]);
k.expand(vec![c]);  // k is now equivalent to bind_hb(vec![a, b, c])
```
{{#endtab}}
{{#endtabs}}

If you need to preserve the original, clone before expanding — see the
[Expand operator](operators.md#expand-extend-a-knot) section for full
examples including clone-first patterns.
