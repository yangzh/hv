# Operators

See [Concepts: Operators](../../concepts/operators.md) for the full overview.

## Bind

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
bound = hv.bind(a, b)
released = hv.release(bound, b)  # ≈ a
inv = hv.inverse(a)              # a.power(-1)
eq = hv.equal(a, b)              # hash equality
```
{{#endtab}}
{{#tab name="Go"}}
```go
k := hv.Bind(a, b)                       // → Knot
raw := hv.BindDirect(a.Core(), b.Core())  // → SparseSegmented
recovered := hv.Release(k, b)            // → Knot ≈ a
inv := hv.Inverse(a)                     // Power(-1)
eq := hv.Equal(a, b)                     // bool
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let k = bind_hb(&[a, b]);                // → Knot
let raw = bind_direct(&[a.core(), b.core()]); // → SparseSegmented
```
{{#endtab}}
{{#endtabs}}

## Bundle

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
p = hv.bundle(hv.Seed128(10, 1), a, b, c)
```
{{#endtab}}
{{#tab name="Go"}}
```go
p := hv.Bundle(seed, a, b, c)                    // → Parcel
raw := hv.BundleDirect(seed, a.Core(), b.Core())  // → SparseSegmented
p := hv.BundleSet(seed, hbs)                     // → Parcel from set
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let raw = bundle_direct(seed, &[a.core(), b.core()]);
```
{{#endtab}}
{{#endtabs}}

## BindDirect

Binds SparseSegmented instances directly, without wrapping in a Knot.

{{#tabs global="lang"}}
{{#tab name="Python"}}
Not directly exposed in Python.
{{#endtab}}
{{#tab name="Go"}}
```go
raw := hv.BindDirect(a.Core(), b.Core())  // → SparseSegmented
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let raw = bind_direct(&[a.core(), b.core()]); // → SparseSegmented
```
{{#endtab}}
{{#endtabs}}

## Similarity

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
hv.overlap(a, b)    # count of matching ON bits
hv.hamming(a, b)    # count of differing segments
hv.equal(a, b)      # hash equality
```
{{#endtab}}
{{#tab name="Go"}}
```go
hv.Overlap(a, b)         // uint32
hv.Hamming(a, b)         // uint32
hv.Equal(a, b)           // bool
hv.JaccardIndex(a, b)    // float64
hv.JaccardDistance(a, b)  // float64
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
overlap(&a.core(), &b.core())   // u32
```
{{#endtab}}
{{#endtabs}}
