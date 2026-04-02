# Walkthrough

A step-by-step introduction to Kongming HV in a notebook, cell by cell.

## Setup

```python
# Cell 1: Install and import
# !pip install kongming-rs-hv pandas

from kongming import hv
import pandas as pd

model = hv.MODEL_64K_8BIT
so = hv.SparseOperation(model, 0, 1)
```

## Building a Vocabulary

```python
# Cell 2: Create vectors for a set of words
words = ["cat", "dog", "fish", "bird", "tree", "rock"]
vectors = {w: hv.Sparkle.with_word(model, "vocab", w) for w in words}

print(f"Created {len(vectors)} vectors")
print(f"Model: {model}, Cardinality: {hv.cardinality(model)}")
```

Output:
```
Created 6 vectors
Model: 1, Cardinality: 256
```

## Similarity Matrix

```python
# Cell 3: Compute pairwise overlap
data = {}
for w1 in words:
    data[w1] = {w2: hv.overlap(vectors[w1], vectors[w2]) for w2 in words}

pd.DataFrame(data, index=words)
```

Output:

|      | cat | dog | fish | bird | tree | rock |
|------|-----|-----|------|------|------|------|
| cat  | 256 |   1 |    0 |    2 |    1 |    1 |
| dog  |   1 | 256 |    1 |    0 |    1 |    2 |
| fish |   0 |   1 |  256 |    1 |    0 |    1 |
| bird |   2 |   0 |    1 |  256 |    1 |    0 |
| tree |   1 |   1 |    0 |    1 |  256 |    1 |
| rock |   1 |   2 |    1 |    0 |    1 |  256 |

The diagonal is 256 (cardinality = perfect self-overlap). Off-diagonal values are near 0-2 (random noise), confirming the vectors are near-orthogonal.

## Learning from Observations

```python
# Cell 4: Create a learner and feed it observations
learner = hv.Learner(model, "animals", so.uint64())

# "cat" seen 3 times, "dog" once, "bird" once
for _ in range(3):
    learner.bundle(vectors["cat"])
learner.bundle(vectors["dog"])
learner.bundle(vectors["bird"])

print(f"Learner age: {learner.age()}")
```

Output:
```
Learner age: 5
```

## Probing the Learner

```python
# Cell 5: Check what the learner remembers
results = []
for w in words:
    ov = hv.overlap(learner, vectors[w])
    results.append({"word": w, "overlap": ov})

df = pd.DataFrame(results).sort_values("overlap", ascending=False)
df
```

Output:

| word | overlap |
|------|---------|
| cat  |    ~75  |
| dog  |    ~30  |
| bird |    ~30  |
| fish |     ~1  |
| tree |     ~1  |
| rock |     ~1  |

"cat" has the highest overlap (seen 3x). "dog" and "bird" (seen 1x each) have moderate overlap. Unseen words are at noise level (~1).

## Binding: Role-Filler Pairs

```python
# Cell 6: Create a structured representation
#   "a cat that is red"
color_role = hv.Sparkle.with_word(model, "role", "color")
animal_role = hv.Sparkle.with_word(model, "role", "animal")

red = hv.Sparkle.with_word(model, "color", "red")
blue = hv.Sparkle.with_word(model, "color", "blue")
cat = vectors["cat"]

# Bind role with filler, then bundle the pairs
learner2 = hv.Learner(model, "record", so.uint64())
learner2.bundle(hv.Sparkle.bind(color_role, red))
learner2.bundle(hv.Sparkle.bind(animal_role, cat))

# Probe: "what color?"
query = hv.Sparkle.bind(learner2, color_role.power(-1))
print(f"red overlap:  {hv.overlap(query, red)}")   # high
print(f"blue overlap: {hv.overlap(query, blue)}")   # ~1
print(f"cat overlap:  {hv.overlap(query, cat)}")    # ~1
```
