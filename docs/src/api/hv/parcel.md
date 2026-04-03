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
// Uniform weights
p := hv.NewParcel(seed, partA, partB, partC)

// From a HyperBinarySet
p := hv.NewParcelWithParts(seed, hbs)

// Via the Bundle operator
p := hv.Bundle(seed, a, b, c)

// Weighted
p := hv.NewWeightedParcel(seed, []float64{0.7, 0.3}, a, b)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
// Uniform weights
let p = Parcel::new(seed, parts);

// Weighted
let p = Parcel::weighted(seed, weights, parts);

// From a HyperBinarySet
let p = Parcel::with_parts(seed, hbs);
```
{{#endtab}}
{{#endtabs}}

## Key Methods

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
p.model()       # Model
p.power(p_)     # HyperBinary
p.core()        # SparseSegmented
p.stable_hash() # int
```
{{#endtab}}
{{#tab name="Go"}}
```go
p.Model()       // api.Model
p.Power(p_)     // HyperBinary
p.Core()        // SparseSegmented
p.Clone()       // HyperBinary
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
p.model()       // Model
p.parts()       // &HyperBinarySetKind
p.power(p_)     // Parcel
p.core()        // SparseSegmented
```
{{#endtab}}
{{#endtabs}}
