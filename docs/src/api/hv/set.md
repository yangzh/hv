# Set

An unordered collection of hypervectors. See [Composites: Set](../../concepts/composites.md#set) for the conceptual overview.

## Constructor

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
s = hv.Set(domain, pod, [member_a, member_b, member_c])
```
{{#endtab}}
{{#tab name="Go"}}
```go
s := hv.NewSet(domain, pod, memberA, memberB, memberC)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let s = Set::new(domain, pod, members);
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
s.Domain()        // Domain
s.Pod()           // Pod
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
