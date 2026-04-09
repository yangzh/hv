# Operators from Scratch

> Standalone script: [`operators.py`](https://github.com/yangzh/hv/blob/main/examples/operators/operators.py)

This example implements the **bind**, **release**, and **bundle** operators in pure Python using only the low-level offset API, then verifies correctness against the library's built-in implementations.

The script does **not** call `hv.bind()`, `hv.release()`, or `hv.bundle()` for computation — it reimplements them to show how they work at the offset level.

## Bind

Per-segment offset addition modulo segment size:

```python
for seg in range(cardinality):
    result[seg] = (core_a.offset(seg) + core_b.offset(seg)) % segment_size
```

Properties:
- Result is nearly orthogonal to both inputs (overlap ≈ 1)
- Commutative: `bind(a, b) == bind(b, a)`
- Associative: `bind(a, b, c) == bind(bind(a, b), c)`

## Release (Unbind)

Per-segment offset subtraction modulo segment size:

```python
for seg in range(cardinality):
    result[seg] = (core_c.offset(seg) - core_k.offset(seg)) % segment_size
```

Properties:
- `release(bind(a, b), b) = a` (exact recovery)
- Multi-release: `release(release(bind(a, b, c), c), b) = a`

## Bundle

PRNG-based random selection among inputs. For each segment, a seeded PRNG
picks which input vector contributes its offset:

```python
# Divide [0, 65535] into N equal ranges, one per input vector.
# For 3 inputs: anchors = [21845, 43690, 65535]
anchors = [int((i + 1) / n * 65535) for i in range(n)]

for seg in range(0, cardinality, 4):
    r = so.uint64()                          # one PRNG call → 4 × 16-bit values
    for j in range(4):
        dial = (r >> (48 - 16 * j)) & 0xFFFF # extract 16-bit random value
        chosen = first input whose anchor >= dial
        result[seg + j] = cores[chosen].offset(seg + j)
```

Properties:
- Result is similar to all inputs (overlap ≈ cardinality / N)
- Not reversible — information is lost

**Note**: The library supports two bundling strategies: `classic` (shown above) and `fisher_yates` (default). To verify exact match with the pure Python implementation, set:

```bash
KONGMING_LEARNER_SAMPLING=classic python operators.py
```

## Running

```bash
pip install kongming-rs-hv

# Default (fisher_yates) — bind/release exact, bundle approximate
python operators.py

# Classic sampling — all operators match exactly
KONGMING_LEARNER_SAMPLING=classic python operators.py
```
