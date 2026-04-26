# Substrate & Views

A **Substrate** is a pluggable storage backend. It provides transactional **views** for reading and writing chunks.

## View Pattern

All storage access goes through views:

- **SubstrateView** — read-only, supports key lookup and prefix scanning
- **SubstrateMutableView** — extends SubstrateView with write staging and atomic commit (to underlying storage)

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
# Read-only view (context manager)
with storage.new_view() as view:
    # Check if chunk exists, without actually reading it back.
    exists = view.chunk_exists("animals", "cat")

    cat_chunk = view.read_chunk("animals", "cat")

# Mutable view (auto-commits on clean exit, rollback on exception)
with storage.new_mutable_view() as view:
    # Preferred: build via a producer and stage it with producer.produce(view).
    memory.from_sequence_members("words", "hi", members,
                                  semantic_indexing=True).produce(view)

    # Shortcut for one-off writes when you already hold the final
    # HyperBinary in Python. Pass semantic_indexing=True to index the
    # code (needed for sequence_attractor / set_members / etc.); the
    # id-Sparkle is always indexed.
    view.write_chunk(sparkle, note="my note")

    # commits automatically
```
{{#endtab}}
{{#endtabs}}

## Storage Backends

### InMemory

<!-- NOTE: InMemory args differ across languages:
     - Python: (model, name) — seeds hardcoded to (0,0), no index TTL config
     - Go: (ctx, *api.MemoryOpt) — full config via proto (model, seeds, name, index TTL, realm)
     - Rust: (model, seed_high, seed_low) — raw substrate level, no name, no TTL
     Python/Go are Memory-level wrappers; Rust is raw Substrate.
     TODO: align InMemory constructor args across languages. -->

Volatile, in-process storage. All data lost on exit. Best for testing and ephemeral caches.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
storage = memory.InMemory(hv.MODEL_64K_8BIT, "my_store")
```
{{#endtab}}
{{#endtabs}}

### Embedded

Persistent, single-machine storage backed by an embedded key-value store. Suitable for local development and moderate-scale deployments.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
storage = memory.Embedded(hv.MODEL_64K_8BIT, "/path/to/store")
```
{{#endtab}}
{{#endtabs}}

### ScyllaDB (Distributed)

Distributed storage via Cassandra-compatible ScyllaDB. For high-scale, multi-node deployments.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```Python
# Not exposed yet...
```
{{#endtab}}
{{#endtabs}}
