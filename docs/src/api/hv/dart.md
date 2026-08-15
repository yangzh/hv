# Dart 🎯

A one-directional reference between two hypervectors. A Dart encodes a directed link from a `source` to a `destination` via `P = source ⊗ Inv(destination)`. Given the Dart and either endpoint, the other endpoint can be recovered. See [Composites: Dart](../../concepts/composites.md#dart).

## Constructor

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
p = hv.Dart(hv.Seed128(0, 42), source, destination)

# Or via the release operator:
p = hv.release(source, destination)
```
{{#endtab}}
{{#tab name="Go"}}
```go
p := hv.NewDart(hv.NewSeed128(0, 42), source, destination)

// Or via the Release operator:
p := hv.Release(source, destination)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let p = Dart::new(Seed128::new(0, 42), source, destination);

// Or via the release operator:
let p = operators::release(&source, &destination);
```
{{#endtab}}
{{#endtabs}}

## Endpoints

A Dart retains references to its source (`A`) and destination (`B`).

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

Given the Dart and one endpoint, the other can be recovered:

- `RDeref(B) = A` — recover the source given the destination, via `P ⊗ B`.
- `Deref(A) = B` — recover the destination given the source, via `A ⊗ Inv(P)`.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
p = hv.Dart(seed, a, b)
recovered_a = p.rderef(b)   # ≈ a
recovered_b = p.deref(a)    # ≈ b
```
{{#endtab}}
{{#tab name="Go"}}
```go
p := hv.NewDart(seed, a, b)
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

Dart (and the `release` operator that constructs it) is anti-commutative:

$$P(A, B) = P(B, A)^{-1}$$
