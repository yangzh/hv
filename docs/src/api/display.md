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
| 🌐 | Domain (id) | Numeric domain ID | `🌐0x..c862` (lower 16 bits hex) |
| 🫛 | Pod (seed) | Numeric seed | `🫛0x..80e4` (lower 16 bits hex) |
| 🌱 | Pod (word) | Word-seeded pod | `🌱cat` |
| 🍀 | Pod (prewired) | Prewired constant | `🍀SET_MARKER` |
| 💪 | Exponent | Non-trivial exponent | `💪3` or `💪-1` |

The `0x..` prefix means only the lower 16 bits of the 64-bit value are shown, for compactness.

**Identity vectors** display as `IDENT` (e.g., `✨IDENT`).

## Python `__repr__`

All HyperBinary types implement `__repr__` in Python. When a variable is evaluated in an interactive shell or notebook cell, the repr is displayed automatically:

```python
>>> a = hv.Sparkle.with_word(hv.MODEL_64K_8BIT, hv.d0(), "hello")
>>> a
✨:🌐0x..c862,🫛0x..80e4
```

This is useful for quick inspection without explicitly calling `print()` or serialization functions.

## Go / Rust Equivalents

{{#tabs}}
{{#tab name="Go"}}
```go
// Compact emoji form (used by fmt.Println, etc.)
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
