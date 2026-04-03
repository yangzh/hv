# Sequence 📿

An ordered collection of hypervectors with positional encoding. See [Composites: Sequence](../../concepts/composites.md#sequence) for the conceptual overview.

## Constructor

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
seq = hv.Sequence(hv.Seed128(0, 42), [first, second, third])
```
{{#endtab}}
{{#tab name="Go"}}
```go
seq := hv.NewSequence(hv.NewSeed128(0, 42), 0, first, second, third)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let seq = Sequence::new(Seed128::new(0, 42), 0, members);
```
{{#endtab}}
{{#endtabs}}

## Manipulation

{{#tabs global="lang"}}
{{#tab name="Python"}}
Not directly exposed in Python.
{{#endtab}}
{{#tab name="Go"}}
```go
// Append a member
seq3 := hv.AppendSequence(seq, newMember)

// Reset to a new start position
seq4 := hv.ResetSequence(seq, 5)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let seq3 = seq.append(new_member);
let seq4 = seq.reset(5);
```
{{#endtab}}
{{#endtabs}}
