# Customizing runtime behavior

## Environment Variables

All environment variables are read once on first access and cannot be changed at runtime. Unset variables use the documented default.

| Variable | Default | Effect |
|----------|---------|--------|
| `KONGMING_REPR_FORMAT` | `YAML` | Controls `__repr__()` / `Repr()` output format. `YAML`: multi-line YAML dump. `PROTO`: multi-line protobuf debug string. |
| `KONGMING_LEARNER_SAMPLING` | `fisher_yates` | Learner bundling strategy. `fisher_yates`: Fisher-Yates exact selection (default). `classic`: per-segment probabilistic sampling. |

```bash
# Example: switch repr to protobuf debug format
export KONGMING_REPR_FORMAT=PROTO

# Example: use classic sampling in Learner
export KONGMING_LEARNER_SAMPLING=classic
```
