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
from kongming import api
from kongming.hv import Sparkle, Seed128, d0, bind, bundle, overlap, to_message

# Create hypervectors
a = Sparkle.from_word(api.MODEL_64K_8BIT, d0(), "hello")
b = Sparkle.from_word(api.MODEL_64K_8BIT, d0(), "world")
print(f'{a=}\n{to_message(a)=}')
print(f'{b=}\n{to_message(b)=}')
print(f'Overlap: {overlap(a, b)}')  # Near orthogonal for random vectors.
print(f'{(a.offsets(), b.offsets())=}') # offsets from a/b.

# Bind and bundle operations
bound = bind(a, b)
print(f'{bound=}\n{to_message(bound)=}')
print(f'{overlap(bound, a)=}, {overlap(bound, b)=}')

bundled1 = bundle(Seed128.create(10, 1), a, b)
print(f'{bundled1=}\n{to_message(bundled1)=}')
print(f'{bundled1.core().offsets()=}')
print(f'{overlap(bundled1, a)=}, {overlap(bundled1, b)=}')

bundled2 = bundle(Seed128.create(10, 2), a, b)
print(f'{bundled2=}\n{to_message(bundled2)=}')
print(f'{bundled2.core().offsets()=}')
print(f'{overlap(bundled2, a)=}, {overlap(bundled2, b)=}')
```

## License

[MIT License](LICENSE)
