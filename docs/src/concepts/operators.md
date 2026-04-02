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

Occasionally we use **releae**, which derived from **bind**, as the equivalent of division, as opposed of multiplication.

$$ A \oslash B = A \otimes B^{-1} $$



Note that release is anti-commutative:
$$ (A \oslash B)^{-1} = B \oslash A $$


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
