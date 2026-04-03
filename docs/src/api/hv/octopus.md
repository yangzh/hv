# Octopus 🐙

A key-value composite where each value is bound with its key's Sparkle. See [Composites: Octopus](../../concepts/composites.md#octopus) for the conceptual overview.

## Constructor

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
oct = hv.Octopus(hv.Seed128(0, 42), ["color", "shape"], red, circle)
```
{{#endtab}}
{{#tab name="Go"}}
```go
oct := hv.NewOctopus(hv.NewSeed128(0, 42), []string{"color", "shape"}, red, circle)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let oct = Octopus::new(Seed128::new(0, 42), keys, values);
```
{{#endtab}}
{{#endtabs}}

## Key Methods

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
oct.value_by_key("color") // returns the value, or raises ValueError
```
{{#endtab}}
{{#tab name="Go"}}
```go
oct.ValueByKey("color")  // HyperBinary — lookup by key
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
oct.value_by_key("color")  // Option<&HyperBinaryKind>
```
{{#endtab}}
{{#endtabs}}
