# Misc

## Display

All HyperBinary types have a compact, emoji-prefixed string representation for quick visual inspection. See [HyperBinary Types](types.md#type-symbols) for type symbols and [Sparkle](sparkle.md#display-labels) for field labels.

### Python `__str__` and `__repr__`

**`__str__`** (triggered by `print()`) returns the compact emoji form:

```python
>>> a = hv.Sparkle.with_word(hv.MODEL_64K_8BIT, hv.d0(), "hello")
>>> print(a)
✨:🌐0x..c862,🫛0x..80e4
```

**`__repr__`** (triggered by evaluating a variable in the shell or notebook) returns a detailed, developer-friendly YAML representation, controlled by the `KONGMING_REPR_FORMAT` environment variable:

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

Set `KONGMING_REPR_FORMAT=PROTO` for protobuf debug output instead of the default YAML. See [Environment Variables](runtime.md#environment-variables) for all supported variables.

### Go / Rust Display

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
print(sparkle)      # compact emoji form via __str__
repr(sparkle)       # detailed YAML/proto form via __repr__
```
{{#endtab}}
{{#tab name="Go"}}
```go
// Compact emoji form
fmt.Println(sparkle)          // ✨:🌐0x..c862,🫛0x..80e4

// Detailed YAML/proto form (controlled by KONGMING_REPR_FORMAT env)
fmt.Println(sparkle.Repr())
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
// Compact emoji form (via Display trait)
println!("{}", sparkle);      // ✨:🌐0x..c862,🫛0x..80e4
```
{{#endtab}}
{{#endtabs}}

## Serialization

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
# HyperBinary → protobuf bytes
msg = hv.to_message(sparkle)

# protobuf bytes → HyperBinary
obj = hv.from_message(msg)

# raw proto bytes → HyperBinary
obj = hv.from_proto_bytes(data)

# proto bytes → YAML string (for debugging)
hv.format_to_yaml(data)
```
{{#endtab}}
{{#tab name="Go"}}
```go
// HyperBinary → proto
pb, err := sparkle.ToProto(ctx)

// YAML formatting
yaml := hv.FormatToYaml(protoMsg)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
// HyperBinary → proto
let pb = sparkle.to_proto();

// proto → HyperBinary
let sparkle = Sparkle::from_proto(&pb)?;
```
{{#endtab}}
{{#endtabs}}

