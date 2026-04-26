# word_indexer — letter-sequence encoding with multi-attractor NNS

A small end-to-end example using [`kongming-rs-hv`](../../docs/python_api.md):
encode 5,000 English words as letter-Sparkle sequences and query them by
**exact word** or by **positional suffix** ("six-letter words ending in `er`",
"eleven-letter words ending in `tion`") with multi-attractor near-neighbor
search.

## The general idea

- **Letters as Sparkles.** Pre-write 26 random-looking `Sparkle`s, one per
  `a–z`, into a `letters` domain. Each letter's Pod is the letter itself, so
  you can fetch the letter's Sparkle by `by_item_key("letters", "e")`.
- **Words as Sequences.** Each word is a `Sequence` in a `words` domain whose
  ordered members are the letter-Sparkles spelling it. The Sequence's Pod is
  the word, so you can fetch a specific word's chunk by
  `by_item_key("words", "language")`.
- **Note carries the word string.** Each word-chunk is written with
  `note=<word>`, so `chunk.note` recovers the word in result loops without
  decoding the Pod.
- **Suffix queries are positional NNS.** For a query like `*****er`, anchor
  letter `e` at position 4 and `r` at position 5 (0-based), feed both as
  attractors to `nns(...)`. The substrate finds Sequences satisfying both
  positional constraints simultaneously.

## How it works

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

A `Sequence` is constructed as:

```python
hv.Sequence(
    hv.Seed128(WORDS_DOMAIN, hv.Pod.from_word(word)),
    *[letters[ch] for ch in word],
)
```

The `Seed128(domain, pod)` argument names the chunk.

## Batched writes via `SubstrateMutableView`

Storage exposes `new_mutable_view()` as a context manager with transactional
semantics:

- All `view.write_chunk(...)` calls between `__enter__` and `__exit__` are
  staged in a single batch.
- Clean exit auto-commits; an exception inside the block discards everything.
- `view.commit()` mid-block flushes the current batch and lets you continue
  staging into a fresh one — useful for pacing memory pressure on large
  ingests.

This example writes letters and words in two separate views and commits every
`BATCH_SIZE = 1000` words within the second:

```python
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
```

## Multi-attractor NNS

A **`sequence_attractor(member_selector, pos, domain)`** is a positional
constraint: "Sequences in `domain` whose member at `pos` overlaps with
`member_selector`". Position is **0-based**.

`nns(*attractors)` evaluates all attractors and ranks Sequences by combined
overlap. With multiple attractors, the result is a conjunction — a chunk
must satisfy each positional constraint to score well.

For the query "six-letter words ending in `er`":

```python
memory.nns(
    memory.sequence_attractor(memory.by_item_key("letters", "e"), 4, WORDS_DOMAIN),
    memory.sequence_attractor(memory.by_item_key("letters", "r"), 5, WORDS_DOMAIN),
)
```

This returns Sequences with `e` at index 4 **and** `r` at index 5 — i.e., the
last two characters of a six-letter word.

For "eleven-letter words ending in `tion`", anchor `t/i/o/n` at positions
7/8/9/10.

## Counting and ranged results

`storage.mem_get(selector)` returns the full ranked result list as a Python
list. Two helpers shape the output:

| Call | Use |
|------|-----|
| `mem_get(nns(...))` | Get every match. `len(...)` is the count. |
| `mem_get(range_sel(nns(...), start, limit))` | Materialize a window — useful for top-N. |

`range_sel(inner, start, limit)` consumes its inner selector, so to demonstrate
both **count** and **top 10** the example builds the NNS selector twice (it's
cheap; the substrate work is what dominates).

> **Note**: For lazy evaluation or per-result selector metadata
> (`SelectorExtra`), use `memory.lazy_selector_iter(view, selector)` instead —
> it yields `(Chunk, Optional[SelectorExtra])` tuples. `mem_get` is the right
> call when you only need Chunks; `range_sel` is the right wrapper for top-N.

## Running

```bash
pip install kongming-rs-hv
python examples/word_indexer/word_indexer.py
```

Expected output shape:

```
Ingested 4982 words in 3.5s.

by word 'the': 1 match(es) [0.3 ms]
   1. the

by word 'people': 1 match(es) [0.3 ms]
   1. people

by word 'language': 1 match(es) [0.3 ms]
   1. language

****er  (6 letters): N match(es) [~180 ms]
   1. <some six-letter -er word>
   2. ...

*******tion (11 letters): M match(es) [~110 ms]
   1. <some eleven-letter -tion word>
   ...
```

(Exact counts depend on the word list; the `*******tion` query may return
zero if the top 5,000 contains no eleven-letter `-tion` words. Times are
approximate, measured on an Apple Silicon laptop with the `InMemory`
backend.)

## Switching to persistent storage

`InMemory` is fine for a demo. For a persistent store, swap one line:

```python
storage = memory.Embedded(MODEL, "/path/to/db")
```

Everything else is identical.

## Data attribution

Word-frequency data in `top5000.txt` is sourced from
[**www.wordfrequency.info**](https://www.wordfrequency.info/) (top-5000
English words, with rank, part-of-speech tag, raw frequency, and dispersion).

Format (tab-separated, no header):

```
Rank    Word    POS    Frequency    Dispersion
```

Please credit www.wordfrequency.info when reusing this data.
