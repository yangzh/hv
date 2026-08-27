# Customizing runtime behavior

## Environment Variables

All environment variables are read once on first access and cannot be changed at runtime. Unset variables use the documented default.

### `KONGMING_RNG`

Selects the pseudo-random number generator backend used for hypervector generation.

| Value | Description |
|-------|-------------|
| **`philox`** (default) | Philox-4×64 (Random123) |
| `xoshiro++` | xoshiro256++: simple, fast |
| `pcg` | PCG-DXSM: classic/compat mode |
| `xoroshiro++` | xoroshiro128++ |

All four are bit-parity across the Go and Rust engines. Any unrecognized
value falls back to `philox`.

Changing this affects all generated vectors: Sparkle offsets, Learner bundling, Cyclone patterns. Vectors generated with different backends are **not** compatible.

```bash
export KONGMING_RNG=xoshiro++
```

## Querying the Current Environment

Use `global_env()` to inspect all active settings at runtime. Returns a `GlobalEnv` protobuf message — new fields added to the proto automatically appear.

```python
>>> hv.global_env()
rng_hint: PHILOX_4X64
```
