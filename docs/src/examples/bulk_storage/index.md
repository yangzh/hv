# Bulk Storage Benchmark

> Standalone script: [`bulk_storage.py`](https://github.com/yangzh/hv/blob/main/examples/bulk_storage/bulk_storage.py)

This example populates a storage with a large number of random terminal chunks, then queries a few by key to verify correctness. It demonstrates how to batch-create items and measure throughput.

Note associative index is also prepared in the process, and near-neighbor search is available immediately upon successful conclusion of all writing.

Motivated readers can further improve this script to test various [producers](../../api/memory/producers.md) or [selectors](../../api/memory/selectors.md).

## What it does

Full script: [`bulk_storage.py`](https://github.com/yangzh/hv/blob/main/examples/bulk_storage/bulk_storage.py). The core loop is three lines — pick a backend, write N terminals through `mem_set`, then spot-check ids:

```python
storage = memory.InMemory(args.model)   # or memory.Embedded(args.model, path)

for i in range(args.count):
    storage.mem_set(memory.new_terminal(args.domain, str(i)))

# verify: stored id must equal the deterministic Sparkle for the same key
chunk = storage.get(args.domain, str(idx))
assert hv.equal(chunk.id, hv.Sparkle.from_word(args.model, args.domain, str(idx)))
```

The script wraps this with argparse (count, model, backend, path), timing, and throughput reporting.

## Usage

```bash
# Default: 10K chunks, in-memory storage substrate.
python bulk_storage.py

# Embedded (disk-backed storage substrate).
python bulk_storage.py --backend embedded

# Embedded with a specific path (tip: use a tmpfs mount for near-in-memory speed)
python bulk_storage.py --backend embedded --path /dev/shm/my_bench

# Custom count
python bulk_storage.py -n 100000

# Different model, 1 implies MODEL_64K_8BIT model, etc.
python bulk_storage.py -n 10000 --model 1
```
