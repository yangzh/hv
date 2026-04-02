# Operators

Kongming provides three core algebraic operations on hypervectors, plus convenience functions.

## Bind

**Binding** ($\otimes$) combines two vectors into a result that is dissimilar to both inputs. It is the multiplicative operation in the HDC algebra.

**Mathematical properties:**

$$A \otimes B = B \otimes A \quad \text{(commutative)}$$

$$(A \otimes B) \otimes C = A \otimes (B \otimes C) \quad \text{(associative)}$$

$$A \otimes I = A \quad \text{(where I is an identity vector)}$$

$$A \otimes A^{-1} = I \quad \text{(inverse)}$$

$$O(A \otimes B, A) \approx O(A \otimes B, B) \approx \text{noise} \quad \text{(dissimilarity)}$$

Implementation: segment-wise offset addition modulo segment size.

{{#tabs global="lang"}}
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

### Release

Occasionally we use **releae**, which derived from **bind**, by binding $A$ with the inverse of $B$: the equivalent of division, as opposed of multiplication.

Note: `Release(a, b) == Inverse(Release(b, a))` — it is anti-commutative.

## Bundle

**Bundling** ($\oplus$) creates a superposition of vectors — the result is similar to all inputs. It is the additive operation within VSA algebra.

**Mathematical properties:**

$$S = \sum_{i, \oplus} A_i$$

$$O(S, A_i) \gg O_{\text{random}} \quad \text{(similarity to each member)}$$

$$O(S, X) \approx O_{\text{random}} \quad \text{for } X \notin \{A_i\} \quad \text{(dissimilarity to non-members)}$$

Bundling is **not reversible** — individual members cannot be recovered from the bundle without extra help (e.g., [near-neighbor search](near_neighbor_search.md)). Weights can be applied to emphasize certain members.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
p = hv.bundle(hv.Seed128(10, 1), a, b, c)
```
{{#endtab}}
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

**Permutation** ($\pi$) rotates a vector's offsets, creating a new vector dissimilar to the original. Used to encode positional information (e.g., in Sequences).

**Mathematical properties:**

$$\pi^0(A) = I \quad \text{(identity)}$$

$$\pi^1(A) = A \quad \text{(base vector)}$$

$$\pi^{-1}(A) = A^{-1} \quad \text{(inverse)}$$

$$\pi^n(A) = \pi^1(A) \text{ applied } n \text{ times}$$

$$O(\pi^i(A), \pi^j(A)) \approx O_{\text{random}} \quad \text{for } i \neq j \quad \text{(different powers are near-orthogonal)}$$

{{#tabs global="lang"}}
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



## Similarity Metrics

| Function | Description |
|----------|-------------|
| `Overlap` / `overlap` | Count of matching ON bits (inner product) |
| `Equal` | True if stable hashes match |
| `Hamming` | Count of differing segments |
| `JaccardIndex` | $\frac{\text{overlap}}{2k - \text{overlap}}$ |
| `JaccardDistance` | $1 - \text{JaccardIndex}$ |
