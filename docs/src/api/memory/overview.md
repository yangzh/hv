# Memory

The memory package provides persistent and in-memory storage for hypervectors with semantic indexing and near-neighbor search.

The core abstraction is a **Chunk** — an immutable identity (Sparkle) paired with a mutable semantic code (any HyperBinary). Chunks are stored in a **Substrate** (pluggable storage backend), queried via **ChunkSelectors**, and created via **ChunkProducers**.

| Section | Description |
|---------|-------------|
| [Chunk](chunk.md) | The fundamental storage unit |
| [Substrate & Views](substrate.md) | Storage backends and transactional views |
| [Selectors](selectors.md) | Query builders for reading chunks |
| [Producers](producers.md) | Write builders for creating chunks |
