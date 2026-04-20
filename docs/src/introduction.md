# Kongming HV

[![PDF](https://img.shields.io/badge/PDF-download-red)](kongming-hv.pdf)

Kongming is a hyperdimensional computing library implementing sparse binary hypervectors for cognitive computing applications.

The core engine is implemented in **Rust** for maximum efficiency, while ergonomic APIs are open-sourced in **Python** for better usability.

See [Hypervectors](concepts/hypervectors.md) for an introduction to hyperdimensional computing and the sparse binary representation.

## License

The Python source code, examples, and documentation in this repository are licensed under the [MIT License](https://github.com/yangzh/hv/blob/main/LICENSE). 

The compiled engine distributed via PyPI (`kongming-rs-hv`) is proprietary.

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

## Docs versioning

The documentation on **[yangzh.github.io/hv](https://yangzh.github.io/hv/)** is
deployed from release tags (`v*`) and stays in lockstep with the latest
`kongming-rs-hv` release on PyPI. Whatever you read there matches what
`pip install kongming-rs-hv` gives you.

The [`main` branch](https://github.com/yangzh/hv/tree/main/docs/src) of this
repository is the working head — it may describe APIs or examples that haven't
been released yet. If you browse the raw markdown on GitHub, expect it to
occasionally be ahead of the published site.

## Reference

The work was initially outlined in [this arxiv paper](https://arxiv.org/abs/2310.18316), built on top of the work from many others, and here is the citation:

> Yang, Zhonghao (2023). Cognitive modeling and learning with sparse binary hypervectors. arXiv:2310.18316v1 [cs.AI]

## Feedback

Found a bug, have a question, or want to suggest an improvement? [Open an issue on GitHub](https://github.com/yangzh/hv/issues).