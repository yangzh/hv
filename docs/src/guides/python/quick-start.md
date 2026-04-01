# Python Quick Start

## Installation

```bash
pip install kongming-rs-hv
```

## Quick Example

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

**What's happening:**
1. `Sparkle.from_word` generates a deterministic hypervector from a word. Same word always produces the same vector.
2. Two unrelated vectors have near-zero overlap (~1) — random high-dimensional vectors are nearly orthogonal.
3. `hv.bind(a, b)` produces a vector dissimilar to both (low overlap). Binding is reversible.
4. `hv.bundle(seed, a, b)` produces a vector similar to both (high overlap). Different seeds produce different but equally valid results.

## Creating Vectors

```python
from kongming_rs_hv import hv

model = hv.MODEL_64K_8BIT

# Create sparkles (atomic vectors) from words
cat = hv.Sparkle.with_word(model, "animals", "cat")
dog = hv.Sparkle.with_word(model, "animals", "dog")

# Same inputs always produce the same vector
cat2 = hv.Sparkle.with_word(model, "animals", "cat")
assert cat.stable_hash() == cat2.stable_hash()
```

## Measuring Similarity

```python
# Random vectors have ~1 overlap
print(hv.overlap(cat, dog))   # ≈ 1 (near-orthogonal)

# A vector is maximally similar to itself
print(hv.overlap(cat, cat))   # = 256 (= cardinality)
```

## Using SparseOperation for Random Generation

```python
so = hv.SparseOperation(model, 123, 456)

# Generate random sparkles
a = hv.Sparkle.random("my_domain", so)
b = hv.Sparkle.random("my_domain", so)

# Each call to so produces a new random seed
print(hv.overlap(a, b))  # ≈ 1
```

## Power and Permutation

```python
# Power creates a permuted vector
s = hv.Sparkle.with_word(model, "pos", "step")
s2 = s.power(2)
s3 = s.power(3)

# Different powers are near-orthogonal
print(hv.overlap(s, s2))   # ≈ 1
print(hv.overlap(s, s3))   # ≈ 1

# Inverse: power(-1) undoes power(1)
s_inv = s.power(-1)
# bind(s, s_inv) ≈ identity
```

## Online Learning with Learner

```python
learner = hv.Learner(model, "animals", 42)

# Feed observations one at a time
learner.bundle(cat)
learner.bundle(cat)   # seen twice — stronger signal
learner.bundle(dog)

# The learned vector is more similar to cat (seen 2x)
print(hv.overlap(learner, cat))  # higher
print(hv.overlap(learner, dog))  # lower but above random
```

See also: [Notebook Quick Start](../notebook/quick-start.md) for interactive walkthroughs and notebook links.
