# Installation

## Python (via PyPI)

```bash
pip install kongming-rs-hv
```

**Supported platforms:**
- Linux (x86_64) — Python 3.10–3.14
- macOS (Apple Silicon & Intel) — Python 3.10–3.14
- Windows (x86_64) — Python 3.10–3.14

## Try Online

For quick experimentation without installation:

| Platform | Link | Notes |
|----------|------|-------|
| Google Colab (tutorial) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yangzh/hv/blob/main/notebook/first.ipynb?flush_cache=true) | Faster startup, requires Google account |
| Colab (Memory) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yangzh/hv/blob/main/notebook/memory.ipynb?flush_cache=true) | In-memory storage, NNS, and persistent export |
| Colab (LISP) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yangzh/hv/blob/main/notebook/lisp.ipynb?flush_cache=true) | VSA-based LISP interpreter demo |
| Binder (tutorial) | [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/yangzh/hv/main?labpath=notebook/first.ipynb) | No account needed, slower startup |

**Colab**: Click the badge, then run the first cell to install `kongming-rs-hv`. Restart the runtime when prompted (Runtime → Restart runtime), then run all cells.

**Binder**: Click the badge and wait for the environment to build (first launch takes 2–5 minutes). Dependencies are pre-installed via `requirements.txt`.
