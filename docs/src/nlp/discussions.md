# Why this shape

- **Capacity from superposition.** One 65,536-member pool per language
  holds every transition statistic — heavy hubs recruit many members,
  rare transitions keep nearly-private ones.
- **Determinism end to end.** Identical corpus in, identical substrate
  out, bit-for-bit across Go and Rust — the engines are kept at parity and
  verified against shared fixtures.
- **Unified storage.** The "model" is ordinary chunks plus one pool — it
  serializes, ships, and loads with the same [memory](../api/memory/overview.md)
  machinery as any other substrate.
