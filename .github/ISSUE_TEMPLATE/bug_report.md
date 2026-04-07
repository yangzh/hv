---
name: Bug Report
about: Report a bug or unexpected behavior
title: "[Bug] "
labels: bug
assignees: ''
---

**Before filing**: please upgrade to the latest version and check if the issue persists.
See the [CHANGELOG](../../CHANGELOG.md) for recent fixes.

```bash
python3 -m pip install -U kongming-rs-hv
```

## Environment

- **OS**: (e.g. macOS 14.5, Ubuntu 22.04, Windows 11)
- **Python version**: (run `python3 --version`)
- **kongming version**: (run `python3 -c "import kongming; print(kongming.__version__)"`)
- **Installation method**: (pip, source build, etc.)

## Description

A clear description of the bug.

## Steps to Reproduce

```python
from kongming import hv, memory

# Minimal code to reproduce the issue
```

## Expected Behavior

What you expected to happen.

## Actual Behavior

What actually happened. Include the full error traceback if applicable.

## Additional Context

Any other relevant information (screenshots, logs, related issues).
