# Chunk

The fundamental storage unit in the memory system. A Chunk mostly carries a **semantic code** (any `HyperBinary` type) along with various diagnostic information.

## Structure

| Field | Type | Description |
|-------|------|-------------|
| `code` | HyperBinary | Semantic content (can be updated). Required — its domain/pod determines the chunk's identity. |
| `id` | Sparkle | identity vector, as derived from `code`'s domain/pod; determines the storage key. |
| `note` | string | Human-readable annotation, primarily for debugging |
| `extra` | protobuf Any | Extensible payload for application-specific data, primarily for debugging |

## Inspection

Chunks are typically created via producers (see [Producers](../memory/producers.md)) — or directly from a code (`memory.Chunk(code, note="", extra=msg)`; the id derives from the code's domain/pod) — and inspected after retrieval (see [Selectors](../memory/selectors.md)).

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
chunk = memory.first_picked(view, memory.by_item_key("animals", "cat"))

chunk.id               # Sparkle
chunk.code             # HyperBinary
chunk.note             # str
chunk.extra_message()  # deserialized protobuf message, or None
```
{{#endtab}}
{{#endtabs}}
