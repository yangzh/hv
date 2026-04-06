# Operators

Kongming provides two core algebraic operations on hypervectors.

## Bind

**Binding** ($\otimes$) combines two vectors into a result that is dissimilar to both inputs. It is the multiplicative operation in the HDC algebra.

**Mathematically**

$$A \otimes B = B \otimes A \quad \text{(commutative)}$$

$$(A \otimes B) \otimes C = A \otimes (B \otimes C) \quad \text{(associative)}$$

$$A \otimes I = A \quad \text{(where I is an identity vector)}$$

$$A \otimes A^{-1} = I \quad \text{(inverse)}$$

$$O(A \otimes B, A) \approx O(A \otimes B, B) \approx \text{noise} \quad \text{(dissimilarity)}$$

**Implementation**: segment-wise offset addition modulo segment size: check out [original paper](../introduction.md#reference) for details.

Check out [code snippets](../api/hv/operators.md#bind) from the API reference.

### Release

Occasionally we use **release**, which is derived from **bind**, as the equivalent of division, as opposed to multiplication.

$$ A \oslash B = A \otimes B^{-1} $$

Note that release is anti-commutative:
$$ (A \oslash B)^{-1} = B \oslash A $$

Check out [code snippets](../api/hv/operators.md#release) from the API reference.

## Bundle

**Bundling** ($\oplus$) creates a superposition of vectors — the result is similar to all inputs. It is the additive operation within VSA algebra.

**Mathematically**

$$S = \sum_{i, \oplus} A_i$$

$$O(S, A_i) \gg O_{\text{random}} \quad \text{(similarity to each member)}$$

$$O(S, X) \approx O_{\text{random}} \quad \text{for } X \notin \{A_i\} \quad \text{(dissimilarity to non-members)}$$

Check out [original paper](../introduction.md#reference) for details on bundle operator.

Check out [code snippets](../api/hv/operators.md#bundle) from the API reference.