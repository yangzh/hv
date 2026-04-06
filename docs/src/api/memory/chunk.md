# Chunk

The fundamental storage unit in the memory system. A Chunk pairs an **immutable identity** (always a Sparkle) with a **mutable semantic code** (any HyperBinary type).

## Structure

| Field | Type | Description |
|-------|------|-------------|
| `id` | Sparkle | Immutable identity — determines storage key |
| `code` | HyperBinary | Semantic content (can be updated). If absent, defaults to `id` |
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
