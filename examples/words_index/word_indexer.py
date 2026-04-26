#!/usr/bin/env python3
"""Words-as-letter-sequences index, queried by suffix via multi-attractor NNS.

Encodes each word from top5000.txt as a Sequence whose members are
per-letter Sparkles; demonstrates exact retrieval by word and positional
suffix retrieval via NNS with multiple sequence_attractors.

Run:
    python examples/words_index/ingest_and_query.py
"""

from pathlib import Path

from kongming import hv, memory

MODEL = hv.MODEL_1M_10BIT
LETTER_DOMAIN = hv.Domain.from_name("letters")
WORDS_DOMAIN = hv.Domain.from_name("words")
DATA_PATH = Path(__file__).resolve().parent / "top5000.txt"
BATCH_SIZE = 1000


def build_letter_alphabet() -> dict[str, "hv.Sparkle"]:
    """One Sparkle per a-z, keyed by (MODEL, LETTER_DOMAIN, Pod.from_word(letter))."""
    return {ch: hv.Sparkle(MODEL, LETTER_DOMAIN, hv.Pod.from_word(ch)) for ch in "abcdefghijklmnopqrstuvwxyz"}


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


def word_to_sequence(word: str, letters: dict[str, "hv.Sparkle"]) -> "hv.Sequence":
    return hv.Sequence(
        hv.Seed128(WORDS_DOMAIN, hv.Pod.from_word(word)),
        *[letters[ch] for ch in word],
    )


def ingest(storage, words: list[str], letters: dict[str, "hv.Sparkle"]) -> None:
    """Write 26 letters in one view, then all word-sequences in another."""
    with storage.new_mutable_view() as view:
        for sp in letters.values():
            view.write_chunk(sp)
        # auto-commits on __exit__

    with storage.new_mutable_view() as view:
        for i, w in enumerate(words, start=1):
            view.write_chunk(word_to_sequence(w, letters), note=w)
            if i % BATCH_SIZE == 0:
                view.commit()
        # trailing writes auto-commit on __exit__


def report(label: str, storage, build_selector) -> None:
    """Print match count, then first 10 results."""
    all_hits = storage.mem_get(build_selector())
    top10 = storage.mem_get(memory.range_sel(build_selector(), 0, 10))
    print(f"\n{label}: {len(all_hits)} match(es)")
    for i, c in enumerate(top10, 1):
        print(f"  {i:>2}. {c.note}")


def main() -> None:
    letters = build_letter_alphabet()
    words = read_words(DATA_PATH)
    storage = memory.InMemory(MODEL)
    ingest(storage, words, letters)
    print(f"Ingested {len(words)} words.")

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
