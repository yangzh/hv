# Operators

Kongming provides three core algebraic operations on hypervectors, plus convenience functions.

## Bind

**Binding** combines two vectors into a result that is dissimilar to both inputs. It is the multiplicative operation in the HDC algebra.

- Implemented as segment-wise offset addition modulo segment size
- Associative and commutative
- Reversible: `Bind(Bind(a, b), Inverse(b)) = a`
- Binding with identity is a no-op

{{#tabs}}
{{#tab name="Python"}}
```python
bound = hv.bind(a, b)
recovered = hv.bind(bound, hv.inverse(b))
hv.equal(recovered, a)

## Or equivalently..
released = hv.release(bound, b)
hv.equal(released, a)
```
{{#endtab}}
{{#tab name="Go"}}
```go
bound := hv.Bind(a, b)
recovered := hv.Bind(bound, hv.Inverse(bound))

// Or equivalently...
released = hv.Release(bound, b)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let bound = bind(&[a, b]);
let recovered = bind(&[bound, inverse(b)]);

// Or equivalently...
let released = release(&[bound, b]);
```
{{#endtab}}
{{#endtabs}}

## Bundle

**Bundling** creates a superposition of vectors — the result is similar to all inputs. It is the additive operation within VSA algebra.

- Not reversible — individual members cannot be recovered without extra help
- The result has above-random overlap with each input
- Weights can be applied to emphasize certain members

{{#tabs}}
{{#tab name="Go"}}
```go
p := hv.Bundle(seed, a, b, c)                 // → Parcel
raw := hv.BundleDirect(seed, a.Core(), b.Core()) // → SparseSegmented
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let raw = bundle_direct(seed, &[a.core(), b.core()]);
```
{{#endtab}}
{{#endtabs}}

## Permute (Power)

**Permutation** rotates a vector's offsets, creating a new vector dissimilar to the original. Used to encode positional information (e.g., in Sequences).

- `Power(1)` is the base vector
- `Power(0)` is the identity
- `Power(-1)` is the inverse
- `Power(n) = Power(1)` applied $n$ times

{{#tabs}}
{{#tab name="Python"}}
```python
v2 = sparkle.power(3)
inv = sparkle.power(-1)  # inverse
```
{{#endtab}}
{{#tab name="Go"}}
```go
v2 := sparkle.Power(3).(hv.Sparkle)
inv := hv.Inverse(sparkle)  // shorthand for Power(-1)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let v2 = sparkle.power(3);
```
{{#endtab}}
{{#endtabs}}

## Derived Operations

### Release

Extracts one component from a binding by binding with the inverse of the other.

```go
// Go
recovered := hv.Release(knot, role) // = Bind(knot, Inverse(role))
```

Note: `Release(a, b) == Inverse(Release(b, a))` — it is anti-commutative.

### Replace

Substitutes a filler in a template without unbundling.

```go
// Go
result := hv.ReplaceSingle(template, oldFiller, newFiller)
result := hv.Replace(template, seed, hv.Replacement{Old: a, New: b}, ...)
```

### Template

Creates a reusable structure from roles (binds each role with itself).

```go
// Go
tmpl := hv.NewTemplate(seed, roleA, roleB)
```

## Similarity Metrics

| Function | Description |
|----------|-------------|
| `Overlap` / `overlap` | Count of matching ON bits (inner product) |
| `Equal` | True if stable hashes match |
| `Hamming` | Count of differing segments |
| `JaccardIndex` | $\frac{\text{overlap}}{2k - \text{overlap}}$ |
| `JaccardDistance` | $1 - \text{JaccardIndex}$ |
