# Quick Example

A minimal example showing the core operations:

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

## What's Happening

1. **Creating vectors**: `Sparkle.from_word` generates a deterministic hypervector from a word. Same word always produces the same vector.

2. **Overlap**: Two unrelated vectors have near-zero overlap (~1). This is the foundation of HDC — random high-dimensional vectors are nearly orthogonal.

3. **Bind**: `hv.bind(a, b)` produces a vector dissimilar to both `a` and `b` (low overlap with each). Binding is reversible.

4. **Bundle**: `hv.bundle(seed, a, b)` produces a vector similar to both `a` and `b` (high overlap with each). Different seeds produce different but equally valid results.

## Notebooks

For deeper walkthroughs, see the interactive notebooks:

- [`first.ipynb`](https://github.com/yangzh/hv/blob/main/notebook/first.ipynb) — Introduction to hypervectors, bind/bundle operations, and composites
- [`memory.ipynb`](https://github.com/yangzh/hv/blob/main/notebook/memory.ipynb) — In-memory and persistent storage, near-neighbor search with attractors, and export to disk
- [`lisp.ipynb`](https://github.com/yangzh/hv/blob/main/notebook/lisp.ipynb) — VSA-based LISP interpreter where every data structure is a hypervector

## LISP Interpreter

A LISP interpreter where every data structure is a hypervector, implementing McCarthy's original calculus on top of VSA algebra. Available as both a pure-Python implementation (for readability) and a Rust implementation (for performance). See [`pylisp/README.md`](https://github.com/yangzh/hv/blob/main/pylisp/README.md) for details.

Inspired by the ArXiv paper [Hey, Pentti, We Did it!: A fully Vector-Symbolic Lisp](https://arxiv.org/abs/2510.17889).
