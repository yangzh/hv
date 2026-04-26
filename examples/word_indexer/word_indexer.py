#!/usr/bin/env python3
"""Words-as-letter-sequences index, queried by suffix via multi-attractor NNS.

Encodes each word from top5000.txt as a Sequence whose members are
per-letter Sparkles; demonstrates exact retrieval by word and positional
suffix retrieval via NNS with multiple sequence_attractors.

This example uses the **ChunkProducer API** end-to-end (mirroring
Go/Rust): producers compute and stage their chunks at ``produce()`` time
against a batched mutable view, instead of pre-computing Sparkles or
Sequences in Python.

Run:
    python examples/word_indexer/word_indexer.py
"""

import time
from pathlib import Path

from kongming import hv, memory

MODEL = hv.MODEL_1M_10BIT
LETTER_DOMAIN = "letters"
WORDS_DOMAIN = hv.Domain.from_name("words")
DATA_PATH = Path(__file__).resolve().parent / "top5000.txt"
BATCH_SIZE = 1000


def read_words(path: Path) -> list[str]:
    """Return lowercase words from each line of top5000.txt (col 1, tab-separated).

    Skips entries with non-alpha characters (e.g. "middle-class") since the
    encoding only handles a-z.
    """
    out: list[str] = []
    with path.open() as f:
        for line in f:
            w = line.split("\t")[1].strip().lower()
            if w.isalpha():
                out.append(w)
    return out


def ingest(storage, words: list[str]) -> None:
    """Stage 26 letter-terminals + one Sequence-producer per word.

    Letters are written as Terminal producers (chunk code = id Sparkle).
    Each word becomes a from_sequence_members producer whose ``members``
    selector pulls the right letter chunks at produce() time.
    """
    with storage.new_mutable_view() as view:
        for ch in "abcdefghijklmnopqrstuvwxyz":
            memory.new_terminal(LETTER_DOMAIN, ch).produce(view)
        # auto-commits on __exit__

    with storage.new_mutable_view() as view:
        for i, w in enumerate(words, start=1):
            members = memory.joiner(*[memory.by_item_key(LETTER_DOMAIN, ch) for ch in w])
            # semantic_indexing=True: index the Sequence's code so suffix
            # queries (sequence_attractor) can find words by structure.
            memory.from_sequence_members(
                WORDS_DOMAIN.name(),
                w,
                members,
                note=w,
                semantic_indexing=True,
            ).produce(view)
            if i % BATCH_SIZE == 0:
                view.commit()
        # trailing writes auto-commit on __exit__


def report(label: str, storage, build_selector) -> None:
    """Print match count + first 10 results, prefixed with elapsed query time."""
    t0 = time.perf_counter()
    all_hits = storage.mem_get(build_selector())
    top10 = storage.mem_get(memory.range_sel(build_selector(), 0, 10))
    dt_ms = (time.perf_counter() - t0) * 1000
    print(f"\n{label}: {len(all_hits)} match(es) [{dt_ms:.1f} ms]")
    for i, c in enumerate(top10, 1):
        print(f"  {i:>2}. {c.note}")


def main() -> None:
    words = read_words(DATA_PATH)
    storage = memory.InMemory(MODEL)
    t0 = time.perf_counter()
    ingest(storage, words)
    print(f"Ingested {len(words)} words in {time.perf_counter() - t0:.2f}s.")

    # Query A — exact lookup
    for w in ["the", "people", "language"]:
        report(
            f"by word {w!r}",
            storage,
            lambda w=w: memory.by_item_key("words", w),
        )

    # Query B — six-letter words ending in "er": positions 4='e', 5='r'
    report(
        "****er  (6 letters)",
        storage,
        lambda: memory.nns(
            memory.sequence_attractor(memory.by_item_key("letters", "e"), 4, WORDS_DOMAIN),
            memory.sequence_attractor(memory.by_item_key("letters", "r"), 5, WORDS_DOMAIN),
        ),
    )

    # Query C — eleven-letter words ending in "tion": positions 7..10
    report(
        "*******tion (11 letters)",
        storage,
        lambda: memory.nns(
            *[
                memory.sequence_attractor(memory.by_item_key("letters", ch), pos, WORDS_DOMAIN)
                for pos, ch in [(7, "t"), (8, "i"), (9, "o"), (10, "n")]
            ]
        ),
    )


if __name__ == "__main__":
    main()
