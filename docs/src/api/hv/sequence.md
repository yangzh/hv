# Sequence 📿

An ordered collection of hypervectors with positional encoding. See [Composites: Sequence](../../concepts/composites.md#sequence) for the conceptual overview.

## Constructor

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
# Constructing a sequence, with logical index start at 1 (default to 0).
seq = hv.Sequence(hv.Seed128(0, 42), [first, second, third], start=1)
```
{{#endtab}}
{{#tab name="Go"}}
```go
seq := hv.NewSequence(hv.NewSeed128(0, 42), 1, first, second, third)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let seq = Sequence::new(Seed128::new(0, 42), 1, members);
```
{{#endtab}}
{{#endtabs}}
