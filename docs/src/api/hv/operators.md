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
{{#endtabs}}

## Bundle

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
p = hv.bundle(hv.Seed128(10, 1), a, b, c)
```
{{#endtab}}
{{#endtabs}}
