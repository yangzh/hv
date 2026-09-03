# Dart 🎯

A one-directional reference between two hypervectors. A Dart is "thrown" from a `tail` to a `head`: 
$$ P = H \otimes T^{-1} = H \oslash T $$ 

See [Composites: Dart](../../concepts/composites.md#dart).

## Constructor

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
# Or via the release operator (note the order: release(head, tail)):
p = hv.release(head, tail)
```
{{#endtab}}
{{#endtabs}}

## Endpoints

A Dart retains references to its endpoints.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
p.tail()          # thrown from ...
p.head()          # ... to
```
{{#endtab}}
{{#endtabs}}

## Recovering endpoints

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
p = hv.release(h, t)                    # the Dart thrown t → h
recovered_h = hv.bind(p, t)             # ≈ h
recovered_t = hv.bind(p.power(-1), h)   # ≈ t
```
{{#endtab}}
{{#endtabs}}

## Anti-commutativity

Dart (and the `release` operator that constructs it) is anti-commutative:

$$\text{Dart}(T, H) = \text{Dart}(H, T)^{-1}$$
