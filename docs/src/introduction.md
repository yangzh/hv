# Kongming HV

[![PDF](https://img.shields.io/badge/PDF-download-red)](kongming-hv.pdf)

Kongming is a hyperdimensional computing library implementing sparse binary hypervectors for cognitive computing applications.

The Python package of `kongming-rs-hv` is released under MIT license, essentially no limitation (and assumes no liability) to any use, personal or commercial.

The core engine is implemented in **Go** / **Rust** for maximum efficiency, while ergonomic APIs are open-sourced in **Python**, for better usability. 

We do have an internal Go/Rust APIs that interacts directly with the core engine: overall all APIs maintains minimalistic abstractions and wire-identical serialization.

See [Hypervectors](concepts/hypervectors.md) for an introduction to hyperdimensional computing and the sparse binary representation.

## License

[MIT License](https://github.com/yangzh/hv/blob/main/LICENSE)

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
| [Python Quick Start](guides/python/quick-start.md) | Installation, examples, and walkthrough |
| [Notebook Quick Start](guides/notebook/quick-start.md) | Platform setup, interactive notebooks, cell-by-cell walkthrough |

## Language Support

This documentation covers code snippets in multiple languages (if available) side by side.

- **Python**: bindings to the underlying Rust implementation (public `kongming-rs-hv` on PyPI);
- **Go**: canonical / reference implementation in proprietary package;
- **Rust**: parallel implementation, carefully maintained in feature parity;

## Reference

The work was initially outlined in [this arxiv paper](https://arxiv.org/abs/2310.18316), built on top of the work from many others, and here is the citation:

> Yang, Zhonghao (2023). Cognitive modeling and learning with sparse binary hypervectors. arXiv:2310.18316v1 [cs.AI]

## Feedback

Found a bug, have a question, or want to suggest an improvement? [Open an issue on GitHub](https://github.com/yangzh/hv/issues).