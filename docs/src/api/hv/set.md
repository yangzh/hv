# Set 🫧

An unordered collection of hypervectors. See [Composites: Set](../../concepts/composites.md#set) for the conceptual overview.

## Constructor

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
s = hv.Set(hv.Seed128(0, 42), [member_a, member_b, member_c])
```
{{#endtab}}
{{#tab name="Go"}}
```go
s := hv.NewSet(hv.NewSeed128(0, 42), memberA, memberB, memberC)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let s = Set::new(Seed128::new(0, 42), members);
```
{{#endtab}}
{{#endtabs}}
