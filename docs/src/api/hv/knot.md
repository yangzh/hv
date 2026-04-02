# Knot

The result of binding (multiplicative composition) of hypervectors. Unlike `BindDirect`, Knot tracks its member parts for serialization and debugging. See [Composites: Knot](../../concepts/composites.md#knot).

## Constructor

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
# Not directly constructed in Python. Use hv.bind() instead.
k = hv.bind(a, b)
```
{{#endtab}}
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

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
k.model()       # Model
k.power(p)      # HyperBinary
k.core()        # SparseSegmented
k.stable_hash() # int
```
{{#endtab}}
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
