# Parcel 🎁

The result of bundling (additive composition) of hypervectors. Unlike `BundleDirect`, Parcel tracks its members and bundling seed for serialization and debugging. See [Composites: Parcel](../../concepts/composites.md#parcel).

## Constructors

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
p = hv.bundle(hv.Seed128(10, 1), a, b, c)
```
{{#endtab}}
{{#tab name="Go"}}
```go
p := hv.NewParcel(hv.NewSeed128(0, 42), partA, partB, partC)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let p = Parcel::new(Seed128::new(0, 42), parts);
```
{{#endtab}}
{{#endtabs}}
