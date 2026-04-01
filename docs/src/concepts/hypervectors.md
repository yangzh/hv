# Hypervectors

## What is Hyperdimensional Computing?

Hyperdimensional computing (HDC) represents concepts as high-dimensional vectors and manipulates them with simple algebraic operations. The key insight is that random vectors in high-dimensional spaces are **nearly orthogonal** — giving each concept a unique, robust representation that tolerates potential interference from other entities.

## Sparse Binary Representation

Kongming uses **sparse binary** hypervectors. Each vector has a fixed, large number of dimensions (e.g., 65,536 or 16 million), but only a small fraction of them are "on" (set to 1). This sparsity is controlled by the [Model](models.md) configuration.

We don't linger at generic **sparse binary** hypervectors. Instead, the base type we are focusing is **SparseSegmented**: the vector is divided into equal-sized *segments*, and exactly one bit is "on" per segment. 

Conceptually you can image this as a list of phasers, where the offset of ON bit (within a host segment) represents the discretized phase.

Implementation-wise, this unique constraint enables:

- **Compact storage**: only the offset of ON bit within its host segment needs to be stored
- **Efficient operations**: each phaser can be operated locally, independent of other phasers, even from the same **sparse binary** hypervector

## Core Properties

Every hypervector in kongming carries:

| Property | Description |
|----------|-------------|
| **Model** | Sparsity configuration — determines vector's cardinality and width |
| **Domain** | Semantic namespace (e.g., "language", "color"), for grouping |
| **Pod** | An identifier for a random vector within a Domain |
| **Exponent** | Exponent applied to the base vector. Particularly, exponent of 0 implies an identity vector |
| **StableHash** | Deterministic hash for equality checks and indexing, consistent across serializations, even across different implementations and storage systems |

## Identity and Inverses

- The **identity** vector has all offsets set to 0. Binding with identity is a no-op. Actually as a special case, there is no storage cost. 
- The **inverse** of a vector `v` is `v.Power(-1)`. Binding `v` with its inverse yields the identity.

## Similarity and distance measure

Two vectors are compared via **overlap** — the count of segments where both have the same ON bit. This is equivalent to a bitwise AND operation, which can be performed very efficiently in modern CPU.

For a model with cardinality $k$ and segment size $s$, the expected overlap between two random vectors $A$ and $B$ is:

$$\text{E}[O(A, B)] = Ns$$

Given the model setup, this is typically 1 or 2.

Semantically-related vectors have significantly higher overlap. A vector's overlap with itself equals its cardinality $M$.

The commonly-used distance measure (dis-similar measure) for binary vectors is Hamming Distance, equivalent to a bitwise XOR operation. As we discussed (and proved) in the paper, the **overlap** and **Hamming distance** between **sparse binary** hypervectors  are two sides of the same coin, with the following equation:

$$2 \times O(A, B) + H(A, B) = 2M$$
