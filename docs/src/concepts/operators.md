# Operators

`kongming` provides two core algebraic operations on sparse binary hypervectors.

## Bind

**Binding** ($\otimes$) combines two vectors into a result that is dissimilar to both inputs. It is the multiplicative operation in the VSA algebra.

**Definition**

For $K$ codes $C_0, C_1, \ldots, C_{K-1}$, bind is **segment-wise modular addition** of the ON offsets:

$$B = C_0 \otimes C_1 \otimes \cdots \otimes C_{K-1}$$

$$B_i = \Big( \sum_k C_{k,i} \Big) \bmod M \qquad (0 \le i < M)$$

where $C_{k,i}$ is the offset of the ON bit in the $i$-th segment of $C_k$. Each
segment is handled independently, so the result keeps exactly one ON bit per
segment — binding never leaves the segmented space.

**Mathematically**

$$A \otimes B = B \otimes A \quad \text{(commutative)}$$

$$(A \otimes B) \otimes C = A \otimes (B \otimes C) \quad \text{(associative)}$$

$$A \otimes I = A \quad \text{(where I is an identity vector)}$$

$$A \otimes A^{-1} = I \quad \text{(inverse)}$$

$$O(A \otimes B, A) \approx O(A \otimes B, B) \approx \text{noise} \quad \text{(dissimilarity)}$$

**Implementation**: segment-wise offset addition modulo segment size.

Check out [original paper](../introduction.md#reference) for details.

Check out [code snippets](../api/hv/operators.md#bind) from the API reference.

### Release

Occasionally we use **release**, as the equivalent of division.

$$ A \oslash B = A \otimes B^{-1} $$

Note that release is anti-commutative:

$$ (A \oslash B)^{-1} = B \oslash A $$

Check out [code snippets](../api/hv/operators.md#release) from the API reference.

## Bundle

**Bundling** ($\oplus$) creates a superposition of vectors, which is similar to all inputs. It is the additive operation in the VSA algebra.

**Definition**

For $K$ codes with normalized weights $w_k$ (where $\sum_k w_k = 1$):

$$B = (w_0 \cdot C_0) \oplus (w_1 \cdot C_1) \oplus \cdots \oplus (w_{K-1} \cdot C_{K-1})$$

Bundling is **not** arithmetic addition. Each segment of the result takes its
offset from exactly **one** operand, chosen with probability $w_k$:

$$B_i = C_{k,i} \quad \text{with probability } w_k \qquad (0 \le i < M)$$

So every segment still holds exactly one ON bit, and the result stays in the
segmented space. Think of it as a lossy compression: $B$ retains each operand's
segment-wise offsets in proportion to that operand's weight, which gives the
similarity directly:

$$O(B, C_k) \approx w_k N s = w_k M$$

With uniform weights $w_k = 1/K$, the notation simplifies to the plain sum and
each member keeps a $1/K$ share:

$$B = C_0 \oplus C_1 \oplus \cdots \oplus C_{K-1} \qquad O(B, C_k) \approx \frac{M}{K}$$

This is the capacity limit in one line: bundle $K$ members and each survives at
overlap $M/K$, so a member stops being recoverable once $M/K$ approaches the
noise floor.

**Mathematically**

$$O(B, C_k) \gg O_{\text{random}} \quad \text{(similarity to each member)}$$

$$O(B, X) \approx O_{\text{random}} \quad \text{for } X \notin \{C_k\} \quad \text{(dissimilarity to non-members)}$$

$$A \oplus B = B \oplus A \quad \text{(commutative)}$$

Check out [original paper](../introduction.md#reference) for details on bundle operator.

Check out [code snippets](../api/hv/operators.md#bundle) from the API reference.