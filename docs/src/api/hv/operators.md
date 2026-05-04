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

`release` returns a [Pointer](pointer.md) — a directional reference from `composite` to `role` that retains both endpoints for inspection and serialization. The bit-level value is identical to `bind(composite, inverse(role))`.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
bound = hv.bind(role, filler)
recovered = hv.release(bound, role)  # Pointer; ≈ filler at the bit level
```
{{#endtab}}
{{#tab name="Go"}}
```go
bound := hv.Bind(role, filler)
recovered := hv.Release(bound, role)  // Pointer; ≈ filler at the bit level
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let bound = operators::bind_hb(vec![role.clone(), filler.clone()]);
let recovered = operators::release(&bound, &role);  // Pointer
```
{{#endtab}}
{{#endtabs}}

### Expand (extend a Knot)

Extends an existing [Knot](knot.md) with additional operands without
re-binding from scratch. `k.expand(c)` on `k = bind(a, b)` gives the
same result as `bind(a, b, c)` — but **mutates `k` in place**, so clone
first if you need the original.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
import copy

k = hv.bind(a, b)
k.expand(c)                 # k is now equivalent to hv.bind(a, b, c)

# To preserve the original, clone first:
base = hv.bind(a, b)
k1 = copy.copy(base)
k1.expand(c)                # base is untouched
```
{{#endtab}}
{{#tab name="Go"}}
```go
k := hv.Bind(a, b)
k.Expand(c)                 // k is now equivalent to hv.Bind(a, b, c)

// To preserve the original, clone first (Clone returns HyperBinary):
base := hv.Bind(a, b)
k1 := base.Clone().(hv.Knot)
k1.Expand(c)                // base is untouched
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let mut k = operators::bind_hb(vec![a.clone(), b.clone()]);
k.expand(vec![c.clone()]);   // k is now equivalent to bind_hb(vec![a, b, c])

// To preserve the original, clone first:
let base = operators::bind_hb(vec![a.clone(), b.clone()]);
let mut k1 = base.clone();
k1.expand(vec![c]);           // base is untouched
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
let ss = operators::bind_direct(domain, pod, &[a, b, c]);  // SparseSegmented
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
