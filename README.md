# hv

Public release of sparse binary hypervectors and associated learners.

## Installation

```bash
pip install kongming-hv
```

**Supported platforms:**
- Linux (x86_64) - Python 3.10-3.14

**Known issues:**
- macOS: Currently experiencing segmentation faults on import due to [gopy compatibility issues](https://github.com/go-python/gopy/issues/370) with recent Go versions. Use Linux or Docker as a workaround.

## Getting Started

See the [notebooks](notebook/) for tutorials:

- `first.ipynb` - Introduction to hypervectors, operations, and composites
- More to come...

## Quick Example

```python
from kongming import api, hv

# Create hypervectors
a = hv.new_sparkle_with_word(api.MODEL_16M_12BIT, hv.d0(), "hello")
b = hv.new_sparkle_with_word(api.MODEL_16M_12BIT, hv.d0(), "world")

# Check orthogonality
print(f"Overlap: {hv.overlap(a, b)}")  # Near zero for random vectors

# Bind and bundle operations
bound = hv.bind(a, b)
bundled = hv.bundle(hv.new_seed128(0, 0), a, b)
```

## License

MIT
