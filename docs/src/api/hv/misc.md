# Misc

## Display

All HyperBinary types have a compact, emoji-prefixed string representation for quick visual inspection. See [HyperBinary Types](types.md#concrete-types) for type symbols.

### Python `__str__` and `__repr__`

**`__str__`** (triggered by `print()`) returns the compact emoji form:

```python
>>> a = hv.Sparkle.from_word(hv.MODEL_64K_8BIT, hv.d0(), "hello")
>>> print(a)
✨:🌐0x..c862,🫛0x..80e4
```

**`__repr__`** (triggered by evaluating a variable in the shell or notebook) returns a detailed, developer-friendly YAML representation:

```python
>>> a
hint: SPARKLE
model: MODEL_64K_8BIT
stable_hash: 12345678
domain:
  id: ...
pod:
  seed: 12345
```

## Serialization

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
# HyperBinary → protobuf message
msg = hv.to_message(sparkle)

# protobuf message → HyperBinary
obj = hv.from_message(msg)

# raw proto bytes → HyperBinary
obj = hv.from_proto_bytes(data)

# proto bytes → YAML string (for debugging)
hv.format_to_yaml(data)
```
{{#endtab}}
{{#endtabs}}

