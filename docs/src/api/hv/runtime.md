# Customizing runtime behavior

## Environment Variables

All environment variables are read once on first access and cannot be changed at runtime. Unset variables use the documented default.

### `KONGMING_RNG`

Selects the pseudo-random number generator backend used for hypervector generation.

| Value | Description |
|-------|-------------|
| **`xoshiro++`** (default) | xoshiro256++ — simple, fast, cross-language deterministic |
| `pcg` | PCG-DXSM — classic/compat mode (matches pre-v3.7.5 behavior) |

Changing this affects all generated vectors: Sparkle offsets, Learner bundling, Cyclone patterns. Vectors generated with different backends are **not** comparable.

### `KONGMING_REPR_FORMAT`

Controls `__repr__()` / `Repr()` output format.

| Value | Description |
|-------|-------------|
| **`YAML`** (default) | Multi-line YAML dump |
| `PROTO` | Multi-line protobuf debug string |

### `KONGMING_LEARNER_SAMPLING`

Controls the bundling strategy used by [Learner](types.md#learner).

| Value | Description |
|-------|-------------|
| **`FISHER_YATES`** (default) | Fisher-Yates shuffle — selects exactly the right number of segments per round |
| `CLASSIC` | Per-segment probabilistic sampling — each segment is independently sampled with a fixed probability |

```bash
# Example: use PCG for backward compatibility with pre-v3.7.5 vectors
export KONGMING_RNG=pcg

# Example: switch repr to protobuf debug format
export KONGMING_REPR_FORMAT=PROTO

# Example: use classic sampling in Learner
export KONGMING_LEARNER_SAMPLING=CLASSIC
```

## Querying the Current Environment

Use `global_env()` to inspect all active settings at runtime. Returns a `GlobalEnv` protobuf message — new fields added to the proto automatically appear.

```python
>>> hv.global_env()
rng_hint: XOSHIRO256PP
learner_sampling: FISHER_YATES
repr_format: YAML
```
