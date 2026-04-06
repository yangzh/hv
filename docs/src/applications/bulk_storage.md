# Bulk Storage Benchmark

This example populates a local storage with a large number of random terminal chunks, then queries a few by key to verify correctness. It demonstrates how to batch-create items and measure throughput.

## Script

```python
#!/usr/bin/env python3
"""Populate local storage with random terminal chunks and verify retrieval."""

import argparse
import shutil
import tempfile
import time
from kongming import hv, memory


def main():
    parser = argparse.ArgumentParser(description="Bulk storage benchmark")
    parser.add_argument(
        "-n", "--count", type=int, default=10_000,
        help="Number of terminal chunks to create (default: 10000)",
    )
    parser.add_argument(
        "--model", type=int, default=hv.MODEL_1M_10BIT,
        help="HV model (default: MODEL_1M_10BIT)",
    )
    parser.add_argument(
        "--domain", type=str, default="bench",
        help="Domain name for all chunks (default: bench)",
    )
    parser.add_argument(
        "--backend", type=str, choices=["inmemory", "embedded"], default="inmemory",
        help="Storage backend (default: inmemory)",
    )
    parser.add_argument(
        "--path", type=str, default=None,
        help="Disk path for embedded backend (default: temp directory)",
    )
    args = parser.parse_args()

    # --- Create storage ---
    tmpdir = None
    if args.backend == "embedded":
        if args.path:
            path = args.path
        else:
            tmpdir = tempfile.mkdtemp()
            path = f"{tmpdir}/bench_store"
        storage = memory.Embedded(args.model, path)
        print(f"Backend: Embedded (path={path})")
    else:
        storage = memory.InMemory(args.model)
        print("Backend: InMemory")

    # --- Write phase ---
    print(f"Writing {args.count:,} terminal chunks …")
    t0 = time.perf_counter()
    for i in range(args.count):
        storage.mem_set(memory.new_terminal(args.domain, str(i)))
    elapsed = time.perf_counter() - t0
    rate = args.count / elapsed
    print(f"  done in {elapsed:.2f}s  ({rate:,.0f} chunks/s)")
    print(f"  item_count = {storage.item_count():,}")

    # --- Read phase: spot-check a few items ---
    spot_checks = [0, args.count // 2, args.count - 1]
    print(f"Spot-checking keys: {spot_checks}")
    for idx in spot_checks:
        chunk = storage.get(args.domain, str(idx))
        expected = hv.Sparkle.from_word(args.model, args.domain, str(idx))
        ok = hv.equal(chunk.code, expected)
        print(f"  key={idx}  equal={ok}")
        assert ok, f"mismatch at key {idx}"

    print("All checks passed.")

    # --- Cleanup ---
    if tmpdir:
        del storage
        shutil.rmtree(tmpdir)


if __name__ == "__main__":
    main()
```

## Usage

```bash
# Default: 10K chunks, in-memory
python bulk_storage.py

# Embedded (disk-backed) storage
python bulk_storage.py --backend embedded

# Embedded with a specific path
python bulk_storage.py --backend embedded --path /tmp/my_bench

# Custom count
python bulk_storage.py -n 100000

# Different model
python bulk_storage.py -n 10000 --model 1
```
