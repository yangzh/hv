# Chunk

The fundamental storage unit in the memory system. A Chunk pairs an **immutable identity** (always a Sparkle) with a **mutable semantic code** (any HyperBinary type).

To assist debugging, each Chunk also contains a free-formed **note**, as well as an **extra** field, an arbitrary protobuf message that describes the details for this Chunk.

## Structure

| Field | Type | Description |
|-------|------|-------------|
| `id` | Sparkle | Immutable identity — determines storage key |
| `code` | HyperBinary | Semantic content (can be updated). If absent, defaults to `id` |
| `note` | string | Human-readable annotation |
| `extra` | protobuf Any | Extensible payload for application-specific data |

## Creating Chunks

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
# Chunks are typically created via producers (see Producers),
# but can be inspected after retrieval:
chunk = memory.first_picked_chunk(view, memory.by_item_key("animals", "cat"))
chunk.id        # Sparkle
chunk.code      # HyperBinary
chunk.note      # str
chunk.extra     # Optional[bytes]
```
{{#endtab}}
{{#tab name="Go"}}
```go
chunk := memory.NewChunk(id, code)
chunk := memory.NewChunkFull(id, code, "my note", extraAny)

chunk.ID       // hv.Sparkle
chunk.Code     // hv.HyperBinary
chunk.Note     // string
chunk.Extra    // *anypb.Any
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let chunk = Chunk::new(id, code);
let chunk = Chunk::new_full(id, Some(code), "my note".into(), extra);

chunk.id       // Sparkle
chunk.code     // Option<HyperBinaryKind>
chunk.note     // String
chunk.extra    // Option<prost_types::Any>
```
{{#endtab}}
{{#endtabs}}

## Updating Code

A chunk's identity is immutable, but its code can be replaced:

{{#tabs global="lang"}}
{{#tab name="Python"}}
Not directly exposed in Python.
{{#endtab}}
{{#tab name="Go"}}
```go
updated := chunk.UpdateCode(newCode)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let updated = chunk.update_code(new_code);
```
{{#endtab}}
{{#endtabs}}
