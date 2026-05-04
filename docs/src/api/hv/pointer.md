# Pointer 👉

A one-directional reference between two hypervectors. A Pointer encodes a directed link from a `source` to a `destination` via `P = source ⊗ Inv(destination)`. Given the pointer and either endpoint, the other endpoint can be recovered. See [Composites: Pointer](../../concepts/composites.md#pointer).

## Constructor

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
p = hv.Pointer(hv.Seed128(0, 42), source, destination)

# Or via the release operator:
p = hv.release(source, destination)
```
{{#endtab}}
{{#tab name="Go"}}
```go
p := hv.NewPointer(hv.NewSeed128(0, 42), source, destination)

// Or via the Release operator:
p := hv.Release(source, destination)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let p = Pointer::new(Seed128::new(0, 42), source, destination);

// Or via the release operator:
let p = operators::release(&source, &destination);
```
{{#endtab}}
{{#endtabs}}

## Endpoints

A Pointer retains references to its source (`A`) and destination (`B`).

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
p.source()        # → A
p.destination()   # → B
```
{{#endtab}}
{{#tab name="Go"}}
```go
p.Source()        // HyperBinary — A
p.Destination()   // HyperBinary — B
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
p.source()        // &HyperBinaryKind — A
p.destination()   // &HyperBinaryKind — B
```
{{#endtab}}
{{#endtabs}}

## Recovering endpoints

Given the pointer and one endpoint, the other can be recovered:

- `RDeref(B) = A` — recover the source given the destination, via `P ⊗ B`.
- `Deref(A) = B` — recover the destination given the source, via `A ⊗ Inv(P)`.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
p = hv.Pointer(seed, a, b)
recovered_a = p.rderef(b)   # ≈ a
recovered_b = p.deref(a)    # ≈ b
```
{{#endtab}}
{{#tab name="Go"}}
```go
p := hv.NewPointer(seed, a, b)
recoveredA := p.RDeref(b)   // ≈ a
recoveredB := p.Deref(a)    // ≈ b
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let recovered_a = p.rderef(&b);  // ≈ a
let recovered_b = p.deref(&a);   // ≈ b
```
{{#endtab}}
{{#endtabs}}

## Anti-commutativity

Pointer (and the `release` operator that constructs it) is anti-commutative:

$$P(A, B) = P(B, A)^{-1}$$
