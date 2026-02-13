# hv

Public release of sparse binary hypervectors and associated learners.

## Installation

```bash
pip install kongming-hv
```

**Supported platforms:**
- Linux (x86_64) - Python 3.10-3.14
- macOS (Apple Silicon & Intel) - Python 3.10-3.14

## Try Online

For quick experimentation without installation:

| Platform | Link | Notes |
|----------|------|-------|
| Google Colab | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yangzh/hv/blob/main/notebook/first.ipynb?flush_cache=true) | Faster startup, requires Google account |
| Binder | [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/yangzh/hv/main?labpath=notebook/first.ipynb) | No account needed, slower startup |

**Colab**: Click the badge, then run the first cell to install `kongming-hv`. Restart the runtime when prompted (Runtime → Restart runtime), then run all cells.

**Binder**: Click the badge and wait for the environment to build (first launch takes 2-5 minutes). Dependencies are pre-installed via `requirements.txt`.

## Getting Started

See the [notebooks](notebook/) for tutorials:

- [`first.ipynb`](notebook/first.ipynb) - Introduction to hypervectors, operations, and composites;
- More to come...

## Quick Example

```python
from kongming import api, hv

# Create hypervectors
a = hv.new_sparkle_with_word(api.MODEL_64K_8BIT, hv.d0(), "hello")
b = hv.new_sparkle_with_word(api.MODEL_64K_8BIT, hv.d0(), "world")
print(f'{a=}\n{hv.to_message(a)=}')
print(f'{b=}\n{hv.to_message(b)=}')
print(f'Overlap: {hv.overlap(a, b)}')  # Near orthogonal for random vectors.
print(f'{(a.offsets(), b.offsets())=}') # offsets from a/b.

# Bind and bundle operations
bound = hv.bind(a, b)
print(f'{bound=}\n{hv.to_message(bound)=}')
print(f'{hv.overlap(bound, a)=}, {hv.overlap(bound, b)=}')

bundled1 = hv.bundle(hv.new_seed128(10, 1), a, b)
print(f'{bundled1=}\n{hv.to_message(bundled1)=}')
print(f'{bundled1.core().offsets()=}')
print(f'{hv.overlap(bundled1, a)=}, {hv.overlap(bundled1, b)=}')

bundled2 = hv.bundle(hv.new_seed128(10, 2), a, b)
print(f'{bundled2=}\n{hv.to_message(bundled2)=}')
print(f'{bundled2.core().offsets()=}')
print(f'{hv.overlap(bundled2, a)=}, {hv.overlap(bundled2, b)=}')
```

## License

[MIT License](LICENSE)
