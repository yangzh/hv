# Quick Example

A minimal example showing the core operations:

```python
from kongming_rs import hv

# Create hypervectors
a = hv.Sparkle.from_word(hv.MODEL_64K_8BIT, hv.d0(), "hello")
b = hv.Sparkle.from_word(hv.MODEL_64K_8BIT, hv.d0(), "world")
print(f'Overlap: {hv.overlap(a, b)}')  # Near orthogonal (~1)

# Bind: result is dissimilar to both inputs
bound = hv.bind(a, b)
print(f'{hv.overlap(bound, a)=}, {hv.overlap(bound, b)=}')  # ~1, ~1

# Bundle: result is similar to both inputs
bundled = hv.bundle(hv.Seed128(10, 1), a, b)
print(f'{hv.overlap(bundled, a)=}, {hv.overlap(bundled, b)=}')  # high, high
```

## What's Happening

1. [`Sparkle.from_word`](../../api/hv/sparkle.md) generates a deterministic hypervector from a word. Same word always produces the same vector.
2. Two unrelated vectors have near-zero [overlap](../../api/hv/common/utilities.md#similarity) (~1) — random high-dimensional vectors are nearly orthogonal.
3. [`hv.bind(a, b)`](../../api/hv/operators.md#bind) produces a vector dissimilar to both (low overlap). Binding is reversible.
4. [`hv.bundle(seed, a, b)`](../../api/hv/operators.md#bundle) produces a vector similar to both (high overlap). Different seeds produce different but equally valid results.
