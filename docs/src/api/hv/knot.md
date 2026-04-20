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

An existing Knot can be extended with additional parts via the
[`bind_more`](operators.md#bind-more) operator (`Knot::expand` in Rust),
which is equivalent to re-binding all parts together but avoids
recomputing the base.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
k = hv.bind(a, b)
k2 = hv.bind_more(k, c)   # ≡ hv.bind(a, b, c); `k` unchanged
```
{{#endtab}}
{{#tab name="Go"}}
```go
k := hv.Bind(a, b)
k2 := hv.BindMore(k, c)   // ≡ hv.Bind(a, b, c)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let k = operators::bind_hb(vec![a.clone(), b.clone()]);
let k2 = k.clone().expand(vec![c]);   // or: operators::bind_more(k.clone(), vec![c])
```
{{#endtab}}
{{#endtabs}}
