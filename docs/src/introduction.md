# Kongming HV

> **[Download as PDF](kongming-hv.pdf)**

Kongming is a hyperdimensional computing library implementing sparse binary hypervectors for cognitive computing applications.

The core implementation is in **Go** with a parallel **Rust** implementation. Both strive to expose abstractions and features in parity and maintain wire-compatible protobuf serialization.

## What is Hyperdimensional Computing?

Hyperdimensional computing (HDC) represents concepts as high-dimensional vectors and manipulates them with simple algebraic operations (bind, bundle, and permutation). The key insight is that random vectors in high-dimensional spaces are nearly orthogonal, giving each concept a unique, robust and almost interference-free representation.

Kongming focuses on **sparse binary** hypervectors **only**: only a small fraction of dimensions are "on" (set to 1). This enables efficient storage and fast bitwise operations while preserving the algebraic properties of HDC.

## Key Abstractions

| Type | Purpose |
|------|---------|
| **SparseSegmented** | The building block for all sparse binary hypervectors |
| **Sparkle** | A seeded / deterministic hypervector |
| **Set** | An unordered collection of entities |
| **Sequence** | An ordered collection of entities |
| **Octopus** | A key-value structure (or equivalently attribute/value pairs) |
| **Knot** | Bound group of hypervectors |
| **Parcel** | Bundled group of hypervectors |
| **Cyclone** | Periodic permutation vector |
| **Learner** | Generic online learning with incremental bundling |

## Language Support

This documentation covers implementations in the following languages. API reference pages include both languages side by side.

- **Python**: bindings via the Rust implementation (public `kongming-rs-hv` on PyPI)
- **Go**: canonical implementation (proprietary package `github.com/kongming/core/kongming/hv`)
- **Rust**: parallel implementation, kept in feature parity (proprietary `kongming` crate)

## Reference

The work was initially outlined in [this arxiv paper](https://arxiv.org/abs/2310.18316), and here is the citation:

> Yang, Zhonghao (2023). Cognitive modeling and learning with sparse binary hypervectors. arXiv:2310.18316v1 [cs.AI]