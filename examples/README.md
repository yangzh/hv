# Examples

Standalone, runnable scripts — each demonstrates a facet of hypervector
computing with the published
[`kongming-rs-hv`](https://pypi.org/project/kongming-rs-hv/) package.

**Prerequisite:** `pip install kongming-rs-hv` (or `pip install -r ../requirements.txt`).
Every script imports `from kongming import hv`. `matplotlib` is optional, and only
for `weighted_schedule.py --plot`.

| Example | What it shows |
|---------|---------------|
| [Mexican Dollar](mexican_dollar/) | Analogical reasoning — *"What's the Dollar of Mexico?"*: `bind`/`bundle` as the math behind analogy. |
| [Word Indexer](word_indexer/) | Encode 5,000 English words and query by positional suffix via multi-attractor NNS. |
| [Bulk Storage](bulk_storage/) | Populate in-memory / embedded substrates with thousands of chunks and measure retrieval. |
| [Operators from Scratch](operators/) | Reimplement `bind` and `bundle` in pure Python — the core math underneath the library. |
| [LISP Interpreter](pylisp/) | A full LISP where every atom, cons cell, and environment is a hypervector. |
| [Learner Revisited](learner_revisited/) | What a `Learner` holds: each segment is a weighted reservoir, and the write weights choose whether occupancy measures $P$, $\log P$, or $P/N$. |

## Running

```bash
python examples/mexican_dollar/mexican_dollar.py          # also: mexican_dollar_memory.py
python examples/word_indexer/word_indexer.py
python examples/bulk_storage/bulk_storage.py -n 10000     # --backend embedded, --model, ...
python examples/operators/operators.py
python examples/learner_revisited/learner_revisited.py   # then weighted_schedule.py; --quick for fewer trials
python examples/learner_revisited/weighted_schedule.py --plot /tmp/figs   # + figures, needs matplotlib
pytest examples/pylisp/                                    # LISP interpreter tests; see pylisp/README.md
```

Full walkthroughs for each example live in the docs:
**[yangzh.github.io/hv/examples](https://yangzh.github.io/hv/examples/index.html)**.
