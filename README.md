# hv

Public release of sparse binary hypervectors and associated learners,
powered by the Rust-backed `kongming-rs-hv` package.

## Installation

```bash
pip install kongming-rs-hv
```

**Supported platforms:**
- Linux (x86_64) - Python 3.10-3.14
- macOS (Apple Silicon & Intel) - Python 3.10-3.14

> A Go-backed `kongming-hv` package with the same API and bit-identical results is also
> available, but requires a working Xcode / Go toolchain on macOS. `kongming-rs-hv` is
> recommended for most users — it ships as a pre-built universal binary with no build-time dependencies.

## Try Online

For quick experimentation without installation:

| Platform | Link | Notes |
|----------|------|-------|
| Google Colab | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yangzh/hv/blob/main/notebook/first.ipynb?flush_cache=true) | Faster startup, requires Google account |
| Binder | [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/yangzh/hv/main?labpath=notebook/first.ipynb) | No account needed, slower startup |

**Colab**: Click the badge, then run the first cell to install `kongming-rs-hv`. Restart the runtime when prompted (Runtime → Restart runtime), then run all cells.

**Binder**: Click the badge and wait for the environment to build (first launch takes 2-5 minutes). Dependencies are pre-installed via `requirements.txt`.

## Getting Started

See the [notebooks](notebook/) for tutorials:

- [`first.ipynb`](notebook/first.ipynb) - Introduction to hypervectors, operations, and composites;
- More to come...

## Quick Example

```python
from kongming_rs import api, hv

# Create hypervectors
a = hv.Sparkle.from_word(api.MODEL_64K_8BIT, hv.d0(), "hello")
b = hv.Sparkle.from_word(api.MODEL_64K_8BIT, hv.d0(), "world")
print(f'{a=}\n{hv.to_message(a)=}')
print(f'{b=}\n{hv.to_message(b)=}')
print(f'Overlap: {hv.overlap(a, b)}')  # Near orthogonal for random vectors.
print(f'{a.core().offsets()=}')  # offsets from a.

# Bind and bundle operations
bound = hv.bind(a, b)
print(f'{bound=}\n{hv.to_message(bound)=}')
print(f'{hv.overlap(bound, a)=}, {hv.overlap(bound, b)=}')

bundled1 = hv.bundle(hv.Seed128(10, 1), a, b)
print(f'{bundled1=}\n{hv.to_message(bundled1)=}')
print(f'{bundled1.core().offsets()=}')
print(f'{hv.overlap(bundled1, a)=}, {hv.overlap(bundled1, b)=}')

bundled2 = hv.bundle(hv.Seed128(10, 2), a, b)
print(f'{bundled2=}\n{hv.to_message(bundled2)=}')
print(f'{bundled2.core().offsets()=}')
print(f'{hv.overlap(bundled2, a)=}, {hv.overlap(bundled2, b)=}')
```

## License

[MIT License](LICENSE)
