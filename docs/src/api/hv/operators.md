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

let eq = hyper_binary::equal(&a, &b);                              
```
{{#endtab}}
{{#endtabs}}

## Release

Extracts one component from a binding: $A \oslash B = A \otimes B^{-1}$

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
bound = hv.bind(role, filler)
recovered = hv.release(bound, role)  # ≈ filler
```
{{#endtab}}
{{#tab name="Go"}}
```go
bound := hv.Bind(role, filler)
recovered := hv.Release(bound, role)  // ≈ filler
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let bound = bind(&[role, filler]);
let recovered = release(&[bound, role]);
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