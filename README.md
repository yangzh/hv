# hv

[![Docs](https://img.shields.io/badge/docs-yangzh.github.io%2Fhv-blue)](https://yangzh.github.io/hv/)

Public release of sparse binary hypervectors and associated learners,
powered by the Rust-backed `kongming-rs-hv` package.

## Installation

```bash
pip install kongming-rs-hv
```

**Supported platforms:**
- Linux (x86_64) - Python 3.10-3.14
- macOS (Apple Silicon & Intel) - Python 3.10-3.14
- Windows (x86_64) - Python 3.10-3.14

## Try Online

For quick experimentation without installation:

| Platform | Link | Notes |
|----------|------|-------|
| Google Colab (tutorial) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yangzh/hv/blob/main/notebook/first.ipynb?flush_cache=true) | Faster startup, requires Google account |
| Colab (Memory) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yangzh/hv/blob/main/notebook/memory.ipynb?flush_cache=true) | In-memory storage, NNS, and persistent export |
| Colab (LISP) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yangzh/hv/blob/main/notebook/lisp.ipynb?flush_cache=true) | VSA-based LISP interpreter demo |
| Binder (tutorial) | [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/yangzh/hv/main?labpath=notebook/first.ipynb) | No account needed, slower startup |

**Colab**: Click the badge, then run the first cell to install `kongming-rs-hv`. Restart the runtime when prompted (Runtime → Restart runtime), then run all cells.

**Binder**: Click the badge and wait for the environment to build (first launch takes 2-5 minutes). Dependencies are pre-installed via `requirements.txt`.

## Getting Started

See the [notebooks](notebook/) for tutorials:

- [`first.ipynb`](notebook/first.ipynb) - Introduction to hypervectors, bind/bundle operations, and composites;
- [`memory.ipynb`](notebook/memory.ipynb) - In-memory and persistent storage, near-neighbor search with attractors, and export to disk;
- [`lisp.ipynb`](notebook/lisp.ipynb) - VSA-based LISP interpreter where every data structure is a hypervector, inspired by this ArXiv paper [Hey, Pentti, We Did it!: A fully Vector-Symbolic Lisp](https://arxiv.org/abs/2510.17889);

## Quick Example

```python
from kongming_rs.api import v1 as apiv1
from kongming_rs import hv

# Create hypervectors
a = hv.Sparkle.from_word(apiv1.MODEL_64K_8BIT, hv.d0(), "hello")
b = hv.Sparkle.from_word(apiv1.MODEL_64K_8BIT, hv.d0(), "world")
print(f'{a=}\n{hv.to_message(a)=}')
print(f'{b=}\n{hv.to_message(b)=}')
print(f'Overlap: {hv.overlap(a, b)}')  # Near orthogonal for random vectors.
print(f'{a.offsets()=}')  # offsets from a.

# Bind and bundle operations
bound = hv.bind(a, b)
print(f'{bound=}\n{hv.to_message(bound)=}')
print(f'{hv.overlap(bound, a)=}, {hv.overlap(bound, b)=}')

bundled1 = hv.bundle(hv.Seed128(10, 1), a, b)
print(f'{bundled1=}\n{hv.to_message(bundled1)=}')
print(f'{bundled1.offsets()=}')
print(f'{hv.overlap(bundled1, a)=}, {hv.overlap(bundled1, b)=}')

bundled2 = hv.bundle(hv.Seed128(10, 2), a, b)
print(f'{bundled2=}\n{hv.to_message(bundled2)=}')
print(f'{bundled2.offsets()=}')
print(f'{hv.overlap(bundled2, a)=}, {hv.overlap(bundled2, b)=}')
```

## LISP Interpreter

A LISP interpreter where every data structure is a hypervector, implementing
McCarthy's original calculus on top of VSA algebra. Available as both a
pure-Python implementation (for readability) and a Rust implementation
(for performance). See [`pylisp/README.md`](pylisp/README.md) for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for release history.

## License

[MIT License](LICENSE)

## References

The library is based on the work outlined in [this arxiv paper](https://arxiv.org/abs/2310.18316), and here is the citation:

> Yang, Zhonghao (2023). Cognitive modeling and learning with sparse binary hypervectors. arXiv:2310.18316v1 [cs.AI]