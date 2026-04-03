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

## Key Methods

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
s.model()         # Model
s.stable_hash()   # int
s.power(p)        # HyperBinary
s.core()          # SparseSegmented
```
{{#endtab}}
{{#tab name="Go"}}
```go
s.Model()         // api.Model
s.Seed128()       // Seed128
s.StableHash()    // uint64
s.Power(p)        // HyperBinary
s.Core()          // SparseSegmented
s.Clone()         // HyperBinary
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
s.model()         // Model
s.members()       // &UniformSet
s.power(p)        // Set
s.core()          // SparseSegmented
```
{{#endtab}}
{{#endtabs}}
