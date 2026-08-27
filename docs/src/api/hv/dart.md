# Dart 🎯

A one-directional reference between two hypervectors. A Dart is "thrown" from a `tail` to a `head`: 
$$ P = H \otimes T^{-1} = H \oslash T $$ 

See [Composites: Dart](../../concepts/composites.md#dart).

## Constructor

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
# Or via the release operator (note the order: release(head, tail)):
p = hv.release(head, tail)
```
{{#endtab}}
{{#tab name="Go"}}
```go
p := hv.NewDart(hv.NewSeed128(0, 42), tail, head)

// Or via the Release operator (note the order):
p := hv.Release(head, tail)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let p = Dart::new(Seed128::new(0, 42), tail, head);

// Or via the release operator (note the order):
let p = operators::release(&head, &tail);
```
{{#endtab}}
{{#endtabs}}

## Endpoints

A Dart retains references to its endpoints.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
p.tail()          # thrown from ...
p.head()          # ... to
```
{{#endtab}}
{{#tab name="Go"}}
```go
p.Tail()          // HyperBinary
p.Head()          // HyperBinary
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
p.tail()          // &HyperBinaryKind
p.head()          // &HyperBinaryKind
```
{{#endtab}}
{{#endtabs}}

## Recovering endpoints

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
p = hv.release(h, t)                    # the Dart thrown t → h
recovered_h = hv.bind(p, t)             # ≈ h
recovered_t = hv.bind(p.power(-1), h)   # ≈ t
```
{{#endtab}}
{{#tab name="Go"}}
```go
p := hv.Release(h, t)                   // the Dart thrown t → h
recoveredH := hv.Bind(p, t)             // ≈ h
recoveredT := hv.Bind(p.Power(-1), h)   // ≈ t
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let recovered_h = operators::bind_hb(vec![p.clone_hb(), t.clone()]);
let recovered_t = operators::bind_hb(vec![p.power(-1), h.clone()]);
```
{{#endtab}}
{{#endtabs}}

## Anti-commutativity

Dart (and the `release` operator that constructs it) is anti-commutative:

$$\text{Dart}(T, H) = \text{Dart}(H, T)^{-1}$$
