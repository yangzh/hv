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
let bound = operators::bind_hb(vec![role.clone(), filler.clone()]);
let recovered = operators::release(&bound, &role);
```
{{#endtab}}
{{#endtabs}}

### Bind more

Extends an existing [Knot](knot.md) with additional operands without
re-binding from scratch. `bind_more(bind(a, b), c)` produces the same
result as `bind(a, b, c)`.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
bound = hv.bind(a, b)
expanded = hv.bind_more(bound, c)       # Knot — ≡ hv.bind(a, b, c)
# The input `bound` is unchanged; a new Knot is returned.
```
{{#endtab}}
{{#tab name="Go"}}
```go
bound := hv.Bind(a, b)
expanded := hv.BindMore(bound, c)       // ≡ hv.Bind(a, b, c)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let bound = operators::bind_hb(vec![a.clone(), b.clone()]);
let expanded = operators::bind_more(bound.clone(), vec![c]); // ≡ bind_hb(vec![a, b, c])
// `bind_more` consumes the Knot — clone first if you still need `bound`.
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
