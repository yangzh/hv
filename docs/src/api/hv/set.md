# Set 🫧

An unordered collection of hypervectors. See [Composites: Set](../../concepts/composites.md#set) for the conceptual overview.

## Constructor

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
s = hv.Set(hv.Seed128(0, 42), first, second, third)
```
{{#endtab}}
{{#endtabs}}

## Notable methods

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python

# All these will be approximately 1/3 of the total cardinality.
hv.overlap(s.unmasked(), first)
hv.overlap(s.unmasked(), second)
hv.overlap(s.unmasked(), third)
```
{{#endtab}}
{{#endtabs}}
