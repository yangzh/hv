# Hypervectors

## What is Hyperdimensional Computing?

Hyperdimensional computing (HDC) represents concepts as high-dimensional vectors and manipulates them with simple algebraic operations. Motivated readers should perform their own background research on this topic.

The key insight is that random vectors in high-dimensional spaces are **nearly orthogonal** — giving each concept a unique, robust representation that tolerates potential interference from other entities. 

In that sense, the traditional notion of curse of dimensionality becomes the bless of dimensionality.

## Sparse Binary Representation

Kongming uses **sparse binary** hypervectors. Each vector has a fixed, large number of dimensions (e.g., 65,536 or 16 million), but only a very small fraction of them are "on" (set to 1). This sparsity is controlled by the [Model](../api/hv/common/models.md) configuration.

We don't linger at generic sparse binary hypervectors. Instead, the base type we are focusing is **SparseSegmented**: each such vector is divided into equal-sized *segments*, and exactly one ON bit is "on" per segment. 

Conceptually you can image this as a list of phasers, where the offset of ON bit (within a host segment) represents the discretized phase.

Implementation-wise, this unique constraint enables:

- **Compact storage**: only the offset of ON bit within its host segment needs to be stored
- **Efficient operations**: Unlike neural nets, where weights are recorded in float numbers, binary operations can be performed very efficiently with modern CPUs.

## Core Properties

Every hypervector in kongming carries:

| Property | Description |
|----------|-------------|
| **Model** | Sparsity configuration — determines vector's cardinality and width |
| **StableHash** | Deterministic hash for equality and integrity checks |
| **Exponent** | Exponent applied to the base vector. Particularly, exponent of 0 implies an identity vector |
| **Seed128** | A 128-bit seed for probablistic operations |

## Identity and Inverses

- The **identity** vector has all offsets set to 0. Binding with identity is a no-op. Actually as a special case, there is no storage cost. 
- The **inverse** of a vector `v` is `v.Power(-1)`. Binding `v` with its inverse yields the identity.

## Similarity and distance measure

Two vectors are compared via **overlap** — the count of segments where both have the same ON bit. This is equivalent to a bitwise AND operation, which can be performed very efficiently in modern CPU.

For a model with cardinality $k$ and segment size $s$, the expected overlap between two random vectors $A$ and $B$ is:

$$\text{E}[O(A, B)] = Ns$$

Given the model setup, this is typically 1 or 2.

Semantically-related vectors have significantly higher overlap. A vector's overlap with itself equals its cardinality $M$.

The commonly-used distance measure (dis-similar measure) for binary vectors is Hamming Distance, equivalent to a bitwise XOR operation. As we discussed (and proved) in [the paper](https://arxiv.org/abs/2310.18316), the **overlap** and **Hamming distance** between **sparse binary** hypervectors  are two sides of the same coin, with the following equation:

$$2 \times O(A, B) + H(A, B) = 2M$$

## Supported Models

A **Model** defines the sparsity configuration for all hypervectors in a system. It determines the total number of dimensions (width), how those dimensions are divided into segments, and therefore the storage and compute characteristics.

| Model | Width | Sparsity Bits | Segment Size | Cardinality (ON bits) |
|-------|-------|---------------|-------------|----------------------|
| `MODEL_64K_8BIT` | 65,536 | 8 | 256 | 256 |
| `MODEL_1M_10BIT` | 1,048,576 | 10 | 1,024 | 1,024 |
| `MODEL_16M_12BIT` | 16,777,216 | 12 | 4,096 | 4,096 |
| `MODEL_256M_14BIT` | 268,435,456 | 14 | 16,384 | 16,384 |
| `MODEL_4G_16BIT` | 4,294,967,296 | 16 | 65,536 | 65,536 |

### Model properties

All model functions take a Model enum value and return the derived property:

<div class="callout callout-note">
<div class="callout-title">Note</div>

For simplicity, we use function names from Python. The counterparts from Go / Rust can be found by consulting their respective references.

</div>

| Function | Description |
|----------|-------------|
| `width` | Total dimension count (`2^width_bits`) |
| `sparsity` | Fraction of ON bits (`1 / segment_size`) |
| `cardinality` | Number of ON bits (= number of segments) |
| `segment_size` | Dimensions per segment |

### How to Choose a Model

- **`MODEL_64K_8BIT`**: Fast prototyping, tiny memory footprint. Good for tests and small-scale experiments.
- **`MODEL_1M_10BIT`**: General-purpose, balances performance and storage.
- **`MODEL_16M_12BIT`**: General-purpose, for the adventurous.
- **`MODEL_256M_14BIT` / `MODEL_4G_16BIT`**: Very high capacity, not there yet.

Larger models provide more orthogonal space (lower collision probability) at the cost of more memory per vector.

Also note that the storage per hypervector estimation only applies to **SparseSegmented** (and a few other types) where raw offsets are neede. **Sparkle**, for example, only stores the random seeds so that the offsets can be recovered on-the-fly at serialization time. Composite types (such as **Set**, **Sequence**) typically contain reference to member **Sparkle** instances, and typically cost much less storage than a **SparseSegmented** instance.