# Notebook Platforms

Setup and behavior differ across Jupyter, Google Colab, and Binder. This page covers the key differences.

## Try Online

| Notebook | Platform | Link |
|----------|----------|------|
| `first.ipynb` | Google Colab | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yangzh/hv/blob/main/notebook/first.ipynb?flush_cache=true) |
| `first.ipynb` | Binder | [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/yangzh/hv/main?labpath=notebook/first.ipynb) |
| `memory.ipynb` | Google Colab | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yangzh/hv/blob/main/notebook/memory.ipynb?flush_cache=true) |
| `lisp.ipynb` | Google Colab | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yangzh/hv/blob/main/notebook/lisp.ipynb?flush_cache=true) |

## Comparison

| | Jupyter (local) | Google Colab | Binder |
|-|-----------------|-------------|--------|
| **Account** | None | Google account required | None |
| **Install** | `pip install` in terminal beforehand | `!pip install` in first cell | Pre-installed via `requirements.txt` |
| **Restart needed** | No | Yes — after first install | No |
| **Startup time** | Instant | Fast (~5s) | Slow (2–5 min cold start) |
| **Persistence** | Local filesystem | Google Drive (optional mount) | Ephemeral — lost on timeout |
| **GPU** | If available locally | Free tier available | Not available |
| **Custom packages** | Full control | `!pip install` per session | Via `requirements.txt` only |

## Jupyter (Local)

Install once in your terminal, then use in any notebook:

```bash
pip install kongming-rs-hv
```

```python
# Cell 1 — no restart needed
from kongming_rs import hv
```

For development workflows with frequent code changes, use autoreload:

```python
%load_ext autoreload
%autoreload 2
```

## Google Colab

Colab runs in the cloud with a fresh environment each session. Install in the first cell:

```python
# Cell 1 — install
!pip install kongming-rs-hv
```

After the first install, Colab requires a **runtime restart**:
1. Go to **Runtime → Restart runtime** (or use the button Colab shows after install)
2. Then run the remaining cells

```python
# Cell 2 — after restart
from kongming_rs import hv
model = hv.MODEL_64K_8BIT
```

Subsequent sessions on the same notebook will need the install cell again — Colab does not persist pip packages across sessions.

**Saving work**: Use `google.colab.drive` to mount Google Drive for persistent storage:

```python
from google.colab import drive
drive.mount('/content/drive')
# Then use paths like /content/drive/MyDrive/...
```

## Binder

Binder builds a Docker image from your repo's `requirements.txt` and launches a Jupyter server. No account needed.

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/yangzh/hv/main?labpath=notebook/first.ipynb)

- **First launch**: Takes 2–5 minutes to build the environment
- **Subsequent launches**: Faster if the image is cached
- **No install needed**: `kongming-rs-hv` is pre-installed from `requirements.txt`
- **Ephemeral**: All work is lost when the session times out (~10 min idle)

```python
# Cell 1 — works immediately, no install
from kongming_rs import hv
```

<div class="callout callout-warning">
<div class="callout-title">Limitation</div>
You cannot install additional packages not in <code>requirements.txt</code> (the environment is read-only).
</div>

## Choosing a Platform

| Use case | Recommended |
|----------|-------------|
| Daily development | Jupyter (local) |
| Quick demo / sharing | Google Colab |
| Zero-setup exploration | Binder |
| Teaching / workshops | Google Colab (students have accounts) |
| Persistent storage needed | Jupyter (local) or Colab + Drive |
