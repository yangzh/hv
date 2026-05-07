# Word Indexer

> Standalone script: [`word_indexer.py`](https://github.com/yangzh/hv/blob/main/examples/word_indexer/word_indexer.py)

This example encodes ~5,000 English words as `Sequence`s of per-letter `Sparkle`s, then queries them by **exact word** or by **positional suffix** ("six-letter words ending in `er`", "eleven-letter words ending in `tion`") using multi-attractor near-neighbor search.

It demonstrates four ideas together:

- Using [`Sparkle`](../../api/hv/sparkle.md) as a stable per-symbol code (one Sparkle per `a`–`z`).
- Using [`Sequence`](../../api/hv/sequence.md) with a `Pod`-derived seed so chunks are addressable both by word (exact) and by structure (positional).
- The **ChunkProducer API** (`new_terminal`, `from_sequence_members`, `joiner`) staged through a batched `SubstrateMutableView` via `producer.produce(view)`.
- Multi-attractor [`nns`](../../api/memory/selectors/near_neighbor.md) over [`SequenceAttractor`](../../api/memory/selectors/attractors.md#reverse-attractors) for positional conjunctive queries.

## The general idea

```
letters domain                       words domain
─────────────                        ────────────
"a" → Sparkle_a                      "the"      → Sequence(t, h, e)
"b" → Sparkle_b                      "language" → Sequence(l, a, n, g, u, a, g, e)
"c" → Sparkle_c                      ...
...                                  Pod   = word         (exact lookup key)
"z" → Sparkle_z                      note  = word         (recoverable in results)
                                     members = letter Sparkles in order
```

- **Letters as Sparkles.** Pre-write 26 random-looking `Sparkle`s, one per `a–z`, into a `letters` domain via `new_terminal(letters, ch)`. Each letter's Pod is the letter itself, so you can fetch it by `by_item_key("letters", "e")`.
- **Words as Sequences.** Each word is a `Sequence` in a `words` domain whose ordered members are the letter-Sparkles spelling it, built by `from_sequence_members(...)` with a `joiner(...)` of per-letter `by_item_key` selectors. The Sequence's Pod is the word, so exact lookup is `by_item_key("words", "language")`.
- **`note` carries the word string.** Each word-chunk is written with `note=<word>`, so `chunk.note` recovers the word in result loops without decoding the Pod.

## Batched writes via the ChunkProducer API

This example uses the producer API end-to-end. Producers compute their
chunks at `produce()` time against a mutable view, mirroring Go's
`producer.Produce(ctx, view)` and Rust's `producer.produce(view, index)`.
Storage's `new_mutable_view()` is a context manager with transactional
semantics:

- All writes staged by `producer.produce(view)` calls between `__enter__` and `__exit__` go into a single batch.
- Clean exit auto-commits; an exception inside the block discards everything.
- `view.commit()` mid-block flushes the current batch and lets you continue staging — useful for pacing memory pressure on large ingests.

Letters and words go into two separate views; the second commits every
`BATCH_SIZE = 1000` words:

```python
with storage.new_mutable_view() as view:
    for ch in "abcdefghijklmnopqrstuvwxyz":
        memory.new_terminal("letters", ch).produce(view)
    # auto-commits on __exit__

with storage.new_mutable_view() as view:
    for i, w in enumerate(words, start=1):
        members = memory.joiner(*[memory.by_item_key("letters", ch) for ch in w])
        # semantic_indexing=True: index the Sequence's code so suffix
        # queries (sequence_attractor) can find words by structure.
        memory.from_sequence_members(
            "words", w, members, note=w, semantic_indexing=True,
        ).produce(view)
        if i % BATCH_SIZE == 0:
            view.commit()
    # trailing writes auto-commit on __exit__
```

See [Substrate & Views](../../api/memory/substrate.md) for the full view API.

## Multi-attractor NNS

A [`sequence_attractor(model, member_selector, pos, domain)`](../../api/memory/selectors/attractors.md#reverse-attractors) is a positional constraint: "Sequences in `domain` whose member at `pos` overlaps with `member_selector`". Position is **0-based**.

`nns(*attractors)` evaluates all attractors and ranks Sequences by combined overlap. With multiple attractors, the result is a conjunction — a chunk must satisfy each positional constraint to score well.

For "six-letter words ending in `er`":

```python
memory.nns(
    memory.sequence_attractor(model, memory.by_item_key("letters", "e"), 4, WORDS_DOMAIN),
    memory.sequence_attractor(model, memory.by_item_key("letters", "r"), 5, WORDS_DOMAIN),
)
```

This returns Sequences with `e` at index 4 **and** `r` at index 5 — i.e., the last two characters of a six-letter word.

For "eleven-letter words ending in `tion`", anchor `t/i/o/n` at positions 7/8/9/10.

## Counting and ranged results

`storage.mem_get(selector)` returns the full ranked result list as a Python list. Two helpers shape the output:

| Call | Use |
|------|-----|
| `mem_get(nns(...))` | Get every match. `len(...)` is the count. |
| `mem_get(range_sel(nns(...), start, limit))` | Materialize a window — useful for top-N. |

`range_sel(inner, start, limit)` consumes its inner selector, so to demonstrate both **count** and **top 10** the example builds the NNS selector twice (cheap; the substrate work dominates).

See [Working with Results](../../api/memory/selectors/results.md) for more on shaping selector output. When you need per-result `SelectorExtra` (e.g. NNS scores) or lazy iteration, reach for `memory.lazy_selector_iter(view, selector)` — `mem_get` returns Chunks only.

## Running

```bash
pip install kongming-rs-hv
python examples/word_indexer/word_indexer.py
```

Expected output shape:

```
Ingested 4982 words in 8.4s.

by word 'the': 1 match(es) [0.3 ms]
   1. the

by word 'people': 1 match(es) [0.3 ms]
   1. people

****er  (6 letters): N match(es) [~190 ms]
   1. <some six-letter -er word>
   ...

*******tion (11 letters): M match(es) [~480 ms]
   1. <some eleven-letter -tion word>
   ...
```

Approximate timings on an Apple Silicon laptop with the `InMemory` backend:

| Operation | Time |
|-----------|------|
| Ingest ~5,000 words via producer API | ~9 s |
| Exact lookup via `by_item_key` | <1 ms |
| Multi-attractor NNS (2 attractors, e.g. `*****er`) | ~200 ms |
| Multi-attractor NNS (4 attractors, e.g. `*******tion`) | ~460 ms |

## A note on `semantic_indexing`

For NNS by composite structure (i.e. "find Sequences whose member at
position N matches X"), each word's producer is constructed with
`semantic_indexing=True`. This impresses the Sequence's *code* into the
associative index alongside the chunk's id-Sparkle (which is always
indexed). Without the flag, only the id is indexed and
`sequence_attractor` queries return zero hits.

The letter terminals are written without the flag because their code
*is* the id-Sparkle, so id-only indexing is sufficient.

## Switching to persistent storage

`InMemory` is fine for a demo. For a persistent store, swap one line:

```python
storage = memory.Embedded(MODEL, "/path/to/db")
```

Everything else is identical.

## Data attribution

Word-frequency data in `top5000.txt` is sourced from [**www.wordfrequency.info**](https://www.wordfrequency.info/) (top-5000 English words). Please credit the source when reusing this data.

Format (tab-separated, no header):

```
Rank    Word    POS    Frequency    Dispersion
```

## See Also

- [Sparkle ✨](../../api/hv/sparkle.md) — per-symbol code used for letters
- [Sequence 📿](../../api/hv/sequence.md) — ordered composite used for words
- [Attractors](../../api/memory/selectors/attractors.md) — `sequence_attractor` and friends
- [Near-Neighbor Search](../../api/memory/selectors/near_neighbor.md) — `nns` over multiple attractors
- [Substrate & Views](../../api/memory/substrate.md) — batched mutable views
- [Working with Results](../../api/memory/selectors/results.md) — `range_sel`, `mem_get`
