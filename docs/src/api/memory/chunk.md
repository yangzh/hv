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
{{#endtabs}}
