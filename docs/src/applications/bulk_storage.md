# Bulk Storage Benchmark

This example populates a local storage with a large number of random terminal chunks, then queries a few by key to verify correctness. It demonstrates how to batch-create items and measure throughput.

## Script

```python
#!/usr/bin/env python3
"""Populate local storage with random terminal chunks and verify retrieval."""

import argparse
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
    args = parser.parse_args()

    storage = memory.InMemory(args.model)

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


if __name__ == "__main__":
    main()
```

## Usage

```bash
# Default: 10K chunks with MODEL_1M_10BIT
python bulk_storage.py

# Custom count
python bulk_storage.py -n 100000

# Different model
python bulk_storage.py -n 10000 --model 1
```
