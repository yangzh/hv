# Kongming HV

[![PDF](https://img.shields.io/badge/PDF-download-red)](kongming-hv.pdf)

Kongming is a hyperdimensional computing library implementing sparse binary hypervectors for cognitive computing applications.

The core implementation is in **Go** with a parallel **Rust** implementation. Both strive to expose abstractions and features in parity and maintain wire-compatible protobuf serialization.

See [Hypervectors](concepts/hypervectors.md) for an introduction to hyperdimensional computing and the sparse binary representation.

## Install

```bash
pip install kongming-rs-hv
```

See [Installation](guides/python/installation.md) for supported platforms and verification steps.

## Published notebooks

See [Notebook Platforms](guides/notebook/platforms.md) for all available notebooks and platform details. 

## Guides

| Guide | Description |
|-------|-------------|
| [Notebook Quick Start](guides/notebook/quick-start.md) | Platform setup, interactive notebooks, cell-by-cell walkthrough |
| [Python Quick Start](guides/python/quick-start.md) | Installation, examples, and walkthrough |

## Language Support

This documentation covers implementations in the following languages. API reference pages include both languages side by side.

- **Python**: bindings via the Rust implementation (public `kongming-rs-hv` on PyPI)
- **Go**: canonical implementation (proprietary package `github.com/kongming/core/kongming/hv`)
- **Rust**: parallel implementation, kept in feature parity (proprietary `kongming` crate)

## Reference

The work was initially outlined in [this arxiv paper](https://arxiv.org/abs/2310.18316), built on top of the work from many others, and here is the citation:

> Yang, Zhonghao (2023). Cognitive modeling and learning with sparse binary hypervectors. arXiv:2310.18316v1 [cs.AI]