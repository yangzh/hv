# Parcel 🎁

Parcel 🎁 contains the result of bundling (additive composition) of hypervectors, while tracking its members and bundling seed for serialization and debugging. See [Composites: Parcel](../../concepts/composites.md#parcel).

## Constructors

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
# Direct, with optional per-member weights:
p = hv.Parcel(hv.Seed128(10, 1), a, b, c, weights=[0.6, 0.2, 0.2])
```
{{#endtab}}
{{#endtabs}}

## Key Methods

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
p.count()      # member count
p.members()    # the tracked members
```
{{#endtab}}
{{#endtabs}}
