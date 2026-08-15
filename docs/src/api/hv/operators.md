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

`release` returns a [Dart](dart.md) — a directional reference from `composite` to `role` that retains both endpoints for inspection and serialization. The bit-level value is identical to `bind(composite, inverse(role))`.

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

### BindDirect

Like `Bind`, but returns a raw [SparseSegmented](sparse_segmented.md) instead of a
[Knot](knot.md) — no operand tracking. Cheaper for intermediate computations
where you don't need to reverse the bind or inspect the operand list.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
# domain/pod default to the zero Domain/Pod
ss = hv.bind_direct(a, b, c)

# Or supply an explicit seed (annotates the resulting SparseSegmented):
ss = hv.bind_direct(a, b, domain=d, pod=p)
```
{{#endtab}}
{{#tab name="Go"}}
```go
ss := hv.BindDirect(domain, pod, a, b, c)  // SparseSegmented
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let ss = operators::bind(domain, pod, &[a, b, c]);         // SparseSegmented
let ss0 = operators::bind_direct(&[a, b, c]);              // no seed (default Domain/Pod)
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
