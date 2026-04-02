# Substrate & Views

A **Substrate** is a pluggable storage backend. It provides transactional **views** for reading and writing chunks.

## View Pattern

All storage access goes through views:

- **SubstrateView** — read-only, supports key lookup and prefix scanning
- **SubstrateMutableView** — extends SubstrateView with write staging and atomic commit

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
# Read-only view (context manager)
with storage.new_view() as view:
    exists = view.chunk_exists("animals", "cat")
    code = view.read_chunk("animals", "cat")

# Mutable view (auto-commits on clean exit, rollback on exception)
with storage.new_mutable_view() as view:
    view.write_chunk(sparkle, code=some_code, note="my note")
    # commits automatically
```
{{#endtab}}
{{#tab name="Go"}}
```go
// Read-only
view := substrate.NewView(nil)
defer view.Discard()

exists := view.KeyExists(ctx, key)
view.Get(ctx, key, func(ctx context.Context, val []byte) error {
    // process value
    return nil
})

// Mutable
mv := substrate.NewMutableView(nil)
defer mv.Discard()

mv.Set(ctx, memory.Cell{Key: key, Value: val})
mv.Commit()
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
// Read-only
let view = substrate.new_view(None);
let exists = view.key_exists(&key);
let val = view.get(&key)?;

// Mutable
let mut mview = substrate.new_mutable_view(None);
mview.set(Cell { key, value, expiration: 0 })?;
mview.commit()?;
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
{{#tab name="Go"}}
```go
m, err := badger.InMemorySubstrate(ctx, memory.KongmingMemoryOpt(
    so, memory.OptName("my_store"), memory.OptIndexTTL(30)))
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let substrate = InMemorySubstrate::new(model, seed_high, seed_low);
```
{{#endtab}}
{{#endtabs}}

### Embedded

Persistent, single-machine storage backed by an embedded key-value store. Suitable for local development and moderate-scale deployments.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
storage = memory.Fjall("/path/to/store", model=hv.MODEL_64K_8BIT)
```
{{#endtab}}
{{#tab name="Go"}}
```go
substrate, err := badger.Connect(ctx, "/path/to/store", opts)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let substrate = FjallSubstrate::new(db, items_ks, index_ks, so, realm, ttl, span);
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
{{#tab name="Go"}}
```go
substrate, err := scylla.Connect(ctx, hosts, opts)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let substrate = ScyllaSubstrate::new(session, runtime, so, realm, ttl, span);
```
{{#endtab}}
{{#endtabs}}

## Associative Index

Each substrate optionally maintains an [Associative Index](../../concepts/associative_index.md) for [near-neighbor search](../../concepts/near_neighbor_search.md). Index entries carry a TTL and expire automatically, modeling memory decay.

The index is populated automatically when chunks are written via producers that opt into semantic indexing.
