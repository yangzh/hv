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

Code snippets are available [here](../api/hv/operators.md#bind).

### Release

Occasionally we use **releae**, which derived from **bind**, as the equivalent of division, as opposed of multiplication.

$$ A \oslash B = A \otimes B^{-1} $$

Note that release is anti-commutative:
$$ (A \oslash B)^{-1} = B \oslash A $$

Code snippets are availale [here](../api/hv/operators.md#release)

## Bundle

**Bundling** ($\oplus$) creates a superposition of vectors — the result is similar to all inputs. It is the additive operation within VSA algebra.

**Mathematical properties:**

$$S = \sum_{i, \oplus} A_i$$

$$O(S, A_i) \gg O_{\text{random}} \quad \text{(similarity to each member)}$$

$$O(S, X) \approx O_{\text{random}} \quad \text{for } X \notin \{A_i\} \quad \text{(dissimilarity to non-members)}$$

<div class="callout callout-warning">
<div class="callout-title">Not Reversible</div>
Individual members cannot be recovered from the bundle without extra help (e.g., <a href="near_neighbor_search.html">near-neighbor search</a>). Weights can be applied to emphasize certain members.
</div>

Code snippets are available [here](../api/hv/operators.md#bundle)