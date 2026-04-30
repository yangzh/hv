# Octopus 🐙

A key-value composite where each value is bound with its key's Sparkle. See [Composites: Octopus](../../concepts/composites.md#octopus) for the conceptual overview.

## Constructor

Keys are `Pod`s. In Python, strings (and any value polymorphically convertible to `Pod`) are accepted and auto-converted.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
oct = hv.Octopus(hv.Seed128(0, 42), ["color", "shape"], red, circle)
```
{{#endtab}}
{{#tab name="Go"}}
```go
keys := []hv.Pod{hv.NewPod("color"), hv.NewPod("shape")}
oct := hv.NewOctopus(hv.NewSeed128(0, 42), keys, red, circle)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let keys = vec![Pod::from_word("color"), Pod::from_word("shape")];
let oct = Octopus::new(Seed128::new(0, 42), keys, values);
```
{{#endtab}}
{{#endtabs}}

## Key Methods

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
oct.value_by_key("color")  # accepts Pod | str | int | Prewired
```
{{#endtab}}
{{#tab name="Go"}}
```go
oct.ValueByKey(hv.NewPod("color"))  // HyperBinary — lookup by Pod
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
oct.value_by_key(&Pod::from_word("color"))  // Option<&HyperBinaryKind>
```
{{#endtab}}
{{#endtabs}}
