# Display & Emoji Guide

All HyperBinary types have a compact, emoji-prefixed string representation designed for quick visual inspection in terminals, notebooks, and logs.

## Type Symbols

Each type has a unique emoji prefix:

| Emoji | Type | Example |
|-------|------|---------|
| ✨ | Sparkle | `✨:🌐0x..c862,🫛0x..80e4` |
| 🍡 | SparseSegmented | `🍡H0x..a1b2` |
| 💫 | Learner | `💫:🌐0x..c862,🫛0x..80e4` |
| 🫧 | Set | `🫧:🌐0x..c862,🫛0x..80e4` |
| 📿 | Sequence | `📿:🌐0x..c862,🫛0x..80e4` |
| 🐙 | Octopus | `🐙:🌐0x..c862,🫛0x..80e4` |
| 🪢 | Knot | `🪢:🌐0x..c862,🫛0x..80e4` |
| 🎁 | Parcel | `🎁:🌐0x..c862,🫛0x..80e4` |
| 🌀 | Cyclone | `🌀(p=16)` |
| 🎯 | Dart | `🎯:🌐0x..c862,🫛0x..80e4` |

## Field Labels

After the type prefix, fields are separated by commas:

| Emoji | Field | Meaning | Format |
|-------|-------|---------|--------|
| 🔗 | Domain (named) | Semantic namespace | `🔗animals` or `🔗PREFIX.name` |
| 🌐 | Domain (id) | Numeric domain ID | `🌐0x..c862` (lower 16 bits hex of the domain id), for compactness |
| 🫛 | Pod (seed) | Numeric seed | `🫛0x..80e4` (lower 16 bits hex of the seed), for compactness |
| 🌱 | Pod (named) | Word-seeded pod | `🌱cat` |
| 🍀 | Pod (prewired) | Prewired constant | `🍀SET_MARKER` |
| 💪 | Exponent | Non-trivial exponent | `💪3` or `💪-1` |

**Identity vectors** display as `IDENT` (e.g., `✨IDENT`).

## Python `__str__` and `__repr__`

Python's two display hooks serve different purposes:

**`__str__`** (triggered by `print()`) returns the compact emoji form:

```python
>>> a = hv.Sparkle.with_word(hv.MODEL_64K_8BIT, hv.d0(), "hello")
>>> print(a)
✨:🌐0x..c862,🫛0x..80e4
```

**`__repr__`** (triggered by evaluating a variable in the shell or notebook) returns a detailed, developer-friendly representation. The default format is **YAML**, controlled by the `KONGMING_REPR_FORMAT` environment variable:

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

Set `KONGMING_REPR_FORMAT=PROTO` for protobuf debug output instead of the default YAML. See [Environment Variables](misc.md#environment-variables) for all supported variables.

## Go / Rust Equivalents

{{#tabs}}
{{#tab name="Go"}}
```go
// Compact emoji form (used by fmt.Println, etc.)
//
// Or equivalently, fmt.Println(sparkle.String())
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
