# Installation

## PyPI

```bash
pip install kongming-rs-hv
```

## Supported Platforms

| Platform | Architectures | Python Versions |
|----------|--------------|-----------------|
| Linux | x86_64 | 3.10–3.14 |
| macOS | Apple Silicon & Intel | 3.10–3.14 |
| Windows | x86_64 | 3.10–3.14 |

## Verifying Installation

```python
import kongming
print(kongming.__version__)  # e.g. should be "3.6.5", as of Apr. 2026. Yours should be newer. 

from kongming import hv
print(hv.MODEL_64K_8BIT)  # should print 1
```

## Import Paths

The package exposes two main modules:

```python
from kongming import hv       # hypervector operations
from kongming import memory   # storage and selectors
```

Model constants are available directly on `hv`:

```python
hv.MODEL_64K_8BIT      # 1
hv.MODEL_1M_10BIT      # 2
hv.MODEL_16M_12BIT     # 3
hv.MODEL_256M_14BIT    # 4
hv.MODEL_4G_16BIT      # 5
```
