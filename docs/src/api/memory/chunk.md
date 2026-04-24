# Chunk

The fundamental storage unit in the memory system. A Chunk carries a **semantic code** (any HyperBinary type) along with its **derived identity** (a Sparkle as implied from the code's domain/pod).

The identity determines the storage key and drives compositionality — a chunk is either present or absent. The code is potentially learnable, offering opportunities to adapt over time, just like weights from traditional neural nets.

## Structure

| Field | Type | Description |
|-------|------|-------------|
| `code` | HyperBinary | Semantic content (can be updated). Required — its domain/pod determines the chunk's identity. |
| `id` | Sparkle | identity vector, as derived from `code`'s domain/pod; determines the storage key. |
| `note` | string | Human-readable annotation, primarily for debugging |
| `extra` | protobuf Any | Extensible payload for application-specific data, primarily for debugging |

## Inspection

Chunks are typically created via producers (see [Producers](../memory/producers.md)), but can be inspected after retrieval (see [Selectors](../memory/selectors.md)).

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
# chunk = memory.first_picked_chunk(view, memory.by_item_key("animals", "cat"))

chunk.id        # Sparkle
chunk.code      # HyperBinary
chunk.note      # str
chunk.extra     # Optional[bytes]
```
{{#endtab}}
{{#endtabs}}
