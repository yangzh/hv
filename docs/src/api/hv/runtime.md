# Customizing runtime behavior

## Environment Variables

All environment variables are read once on first access and cannot be changed at runtime. Unset variables use the documented default.

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
# Example: switch repr to protobuf debug format
export KONGMING_REPR_FORMAT=PROTO

# Example: use classic sampling in Learner
export KONGMING_LEARNER_SAMPLING=CLASSIC
```
