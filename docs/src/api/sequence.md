# Sequence

An ordered collection of hypervectors with positional encoding. See [Composites: Sequence](../concepts/composites.md#sequence) for the conceptual overview.

## Constructor

{{#tabs}}
{{#tab name="Python"}}
```python
seq = hv.Sequence(domain, pod, 0, [first, second, third])
```
{{#endtab}}
{{#tab name="Go"}}
```go
seq := hv.NewSequence(domain, pod, 0, first, second, third)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let seq = Sequence::new(domain, pod, 0, members);
```
{{#endtab}}
{{#endtabs}}

## Manipulation

{{#tabs}}
{{#tab name="Go"}}
```go
// Prepend a member (start decreases by 1)
seq2 := hv.PrependSequence(seq, newMember)

// Append a member
seq3 := hv.AppendSequence(seq, newMember)

// Reset to a new start position
seq4 := hv.ResetSequence(seq, 5)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let seq2 = seq.prepend(new_member);
let seq3 = seq.append(new_member);
let seq4 = seq.reset(5);
```
{{#endtab}}
{{#endtabs}}

## Key Methods

{{#tabs}}
{{#tab name="Go"}}
```go
seq.Start()       // int32 — starting index
seq.Model()       // api.Model
seq.Power(p)      // HyperBinary
seq.Core()        // SparseSegmented
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
seq.start()       // i32
seq.model()       // Model
seq.members()     // &UniformSet
seq.power(p)      // Sequence
seq.core()        // SparseSegmented
```
{{#endtab}}
{{#endtabs}}
