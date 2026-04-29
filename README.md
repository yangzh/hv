# hv

[![Docs](https://img.shields.io/badge/docs-yangzh.github.io%2Fhv-blue)](https://yangzh.github.io/hv/)
[![PyPI](https://img.shields.io/pypi/v/kongming-rs-hv)](https://pypi.org/project/kongming-rs-hv/)
[![Python](https://img.shields.io/pypi/pyversions/kongming-rs-hv)](https://pypi.org/project/kongming-rs-hv/)
[![License](https://img.shields.io/github/license/yangzh/hv)](LICENSE)

Public release of sparse binary hypervectors and associated learners, powered by the Rust-backed `kongming-rs-hv` package.

## Installation

```bash
pip install kongming-rs-hv
```

Supports Linux, macOS, and Windows on Python 3.10–3.14.

## Documentation

Full documentation is available at **[yangzh.github.io/hv](https://yangzh.github.io/hv/)**, including:

- [Concepts](https://yangzh.github.io/hv/concepts/hypervectors.html) — hypervectors, models, composites, operators, constant-time near-neighbor search
- [API Reference](https://yangzh.github.io/hv/api/sparkle.html) — Python, Go, and Rust side by side
- [Python Quick Start](https://yangzh.github.io/hv/guides/python/quick-start.html) — installation, examples, and notebooks
- [Notebook Quick Start](https://yangzh.github.io/hv/guides/notebook/quick-start.html) — cell-by-cell Jupyter walkthrough
- [PDF download](https://yangzh.github.io/hv/kongming-hv.pdf)

> The published site is deployed from release tags (`v*`) and tracks the
> latest `kongming-rs-hv` release on PyPI. The `main` branch of this repo is
> the working head — it may describe APIs or examples that haven't been
> released yet.

## Try Online

| Platform | Link |
|----------|------|
| Colab — tutorial walkthrough | <a href="https://colab.research.google.com/github/yangzh/hv/blob/main/notebook/first.ipynb?flush_cache=true" target="_blank"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"></a> |
| Colab — hypervector storage | <a href="https://colab.research.google.com/github/yangzh/hv/blob/main/notebook/memory.ipynb?flush_cache=true" target="_blank"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"></a> |
| Binder | <a href="https://mybinder.org/v2/gh/yangzh/hv/main?labpath=notebook/first.ipynb" target="_blank"><img src="https://mybinder.org/badge_logo.svg" alt="Binder"></a> |

## Applications

Runnable scripts under [`examples/`](examples/) including:
* [Mexican Dollar](https://yangzh.github.io/hv/examples/mexican_dollar/index.html): analogical reasoning;
* [Word Indexer](https://yangzh.github.io/hv/examples/word_indexer/index.html): suffix-queryable word indexing;
* [Bulk Storage](https://yangzh.github.io/hv/examples/bulk_storage/index.html): storage benchmarks;
* [Operators from Scratch](https://yangzh.github.io/hv/examples/operators/index.html): the math underneath the library;
* [LISP Interpreter](https://yangzh.github.io/hv/examples/pylisp/index.html): where every value is a hypervector.

See the [examples index](https://yangzh.github.io/hv/examples/index.html) for walkthroughs.

## Community

Questions, ideas, or feedback? Visit [GitHub Discussions](https://github.com/yangzh/hv/discussions) for announcements, Q&A, and general conversation. For bugs, please use [Issues](https://github.com/yangzh/hv/issues). 

For private inquiries, use the [contact form](https://docs.google.com/forms/d/e/1FAIpQLSeAPEzqIgcf1CYJZJepN2jtNy1QTPKtpQYkdBBs1-rNeIuoGQ/viewform).

## References

> Yang, Zhonghao (2023). Cognitive modeling and learning with sparse binary hypervectors. [arXiv:2310.18316](https://arxiv.org/abs/2310.18316) [cs.AI]

## License

The Python source code, examples, and documentation in this repository are licensed under the [MIT License](LICENSE). 

The underlying engine distributed via PyPI (`kongming-rs-hv`), however, is proprietary.
