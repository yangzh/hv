# Walkthrough

A deeper exploration of the Python API, covering vector creation, similarity, random generation, power/permutation, and online learning.

## Creating Vectors

```python
from kongming import hv

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
learner = hv.Learner(model, hv.Seed128(0, 42))

# Feed observations one at a time
learner.bundle(cat)
learner.bundle(cat)   # seen twice — stronger signal
learner.bundle(dog)

# The learned vector is more similar to cat (seen 2x)
print(hv.overlap(learner, cat))  # higher
print(hv.overlap(learner, dog))  # lower but above random
```
