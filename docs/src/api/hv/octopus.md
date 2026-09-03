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
{{#endtabs}}

## Key Methods

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
oct.value_by_key("color")  # accepts Pod | str | int | Prewired
```
{{#endtab}}
{{#endtabs}}
