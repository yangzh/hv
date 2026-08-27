# Operators

See [Concepts: Operators](../../concepts/operators.md) for the full overview.

## Bind

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
bound = hv.bind(a, b)
released = hv.release(bound, b)  # this will recover `a`

hv.equal(a, b)                   # hash equality
```
{{#endtab}}
{{#tab name="Go"}}
```go
bound := hv.Bind(a, b)                       
recovered := hv.Release(bound, b)        // this will recover `a`

eq := hv.Equal(a, b)                     // bool
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let bound = operators::bind_hb(vec![a.clone(), b.clone()]); // Knot
let recovered = operators::release(&bound, &b);             // this will recover `a`

let eq = hyper_binary::equal(&a, &b);                       // bool
```
{{#endtab}}
{{#endtabs}}

### Release

Extracts one component from a binding: $A \oslash B = A \otimes B^{-1}$

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
bound = hv.bind(role, filler)
recovered = hv.release(bound, role)  # Dart; ≈ filler at the bit level
```
{{#endtab}}
{{#tab name="Go"}}
```go
bound := hv.Bind(role, filler)
recovered := hv.Release(bound, role)  // Dart; ≈ filler at the bit level
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let bound = operators::bind_hb(vec![role.clone(), filler.clone()]);
let recovered = operators::release(&bound, &role);  // Dart
```
{{#endtab}}
{{#endtabs}}

### Expand (extend a Knot)

Extends an existing [Knot](knot.md) with additional operands without
re-binding from scratch. `k.expand(c)` on `k = bind(a, b)` **returns a
new Knot** equal to `bind(a, b, c)` — a Knot is an immutable value, so
`k` itself never changes.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
k = hv.bind(a, b)
k2 = k.expand(c)            # k2 is equivalent to hv.bind(a, b, c); k unchanged
```
{{#endtab}}
{{#tab name="Go"}}
```go
k := hv.Bind(a, b)
k2 := k.Expand(c)           // k2 is equivalent to hv.Bind(a, b, c); k unchanged
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let k = operators::bind_hb(vec![a.clone(), b.clone()]);
let k2 = k.expand(vec![c.clone()]); // equivalent to bind_hb(vec![a, b, c]); consumes k

// Deriving several Knots from one base: clone first.
let base = operators::bind_hb(vec![a.clone(), b.clone()]);
let k1 = base.clone().expand(vec![c]); // base still usable
```
{{#endtab}}
{{#endtabs}}

## Bundle

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
p = hv.bundle(hv.Seed128(10, 1), a, b, c)
```
{{#endtab}}
{{#tab name="Go"}}
```go
p := hv.Bundle(hv.NewSeed128(10, 1), a, b, c)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let p = operators::bundle(Seed128::new(10, 1), vec![a, b]);
```
{{#endtab}}
{{#endtabs}}
