# Octopus

A key-value composite where each value is bound with its key's Sparkle. See [Composites: Octopus](../../concepts/composites.md#octopus) for the conceptual overview.

## Constructor

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
oct = hv.Octopus(domain, pod, ["color", "shape"], [red, circle])
```
{{#endtab}}
{{#tab name="Go"}}
```go
oct := hv.NewOctopus(domain, pod, []string{"color", "shape"}, red, circle)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let oct = Octopus::new(domain, pod, keys, values);
```
{{#endtab}}
{{#endtabs}}

## Key Methods

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
oct.model()              # Model
oct.power(p)             # HyperBinary
oct.core()               # SparseSegmented
oct.stable_hash()        # int
```
{{#endtab}}
{{#tab name="Go"}}
```go
oct.ValueByKey("color")  // HyperBinary — lookup by key
oct.Model()              // api.Model
oct.Power(p)             // HyperBinary
oct.Core()               // SparseSegmented
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
oct.value_by_key("color")  // Option<&HyperBinaryKind>
oct.keys()                 // &[String]
oct.values()               // &[HyperBinaryKind]
oct.power(p)               // Octopus
oct.core()                 // SparseSegmented
```
{{#endtab}}
{{#endtabs}}
