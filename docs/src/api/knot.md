# Knot

The result of binding (multiplicative composition) of hypervectors. Unlike `BindDirect`, Knot tracks its member parts for serialization and debugging. See [Composites: Knot](../concepts/composites.md#knot).

## Constructor

{{#tabs}}
{{#tab name="Go"}}
```go
k := hv.NewKnot(domain, pod, partA, partB)

// More commonly via the Bind operator:
k := hv.Bind(a, b)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let k = Knot::new(domain, pod, parts);
```
{{#endtab}}
{{#endtabs}}

## Key Methods

{{#tabs}}
{{#tab name="Go"}}
```go
k.Model()       // api.Model
k.Power(p)      // HyperBinary
k.Core()        // SparseSegmented
k.Clone()       // HyperBinary
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
k.model()       // Model
k.parts()       // &[HyperBinaryKind]
k.power(p)      // Knot
k.core()        // SparseSegmented
```
{{#endtab}}
{{#endtabs}}
