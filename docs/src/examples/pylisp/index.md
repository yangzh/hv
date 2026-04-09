# LISP Interpreter

A LISP interpreter where every data structure — atoms, cons cells, lists, closures — is encoded as a hypervector. No traditional memory allocation, no pointers, no garbage collector. All computation happens through hypervector algebra.

## Two Implementations

The LISP interpreter ships in two forms, both feature-identical:

| | Pure Python (`pylisp`) | Rust (`kongming_rs.lisp`) |
|-|------------------------|--------------------------|
| **Source** | Open-sourced in [`examples/pylisp/`](https://github.com/yangzh/hv/tree/main/examples/pylisp) | Compiled into `kongming-rs-hv` |
| **Readable** | Yes — ~500 lines of annotated Python | No — compiled Rust binary |
| **Performance** | Slower (Python overhead per operation) | Faster (native code) |
| **Import** | `from pylisp import LispEnv` | `from kongming.lisp import LispEnv` |
| **Dependencies** | `kongming-rs-hv` (for hypervector primitives) | Included in `kongming-rs-hv` |
| **Use case** | Learning, debugging, extending | Production, notebooks |

### Rust (built-in)

The `kongming-rs-hv` package includes a Rust-based LISP interpreter built directly on the internal Rust API and primitives. This implementation is compiled into the Python wheel and accessible via `from kongming.lisp import LispEnv`.

Since it operates on Rust-native hypervector types with zero Python overhead, it delivers the best performance for production use.

### Python (open-source)

For research and study, we provide a pure-Python implementation of the same interpreter, built entirely on the public Python API of `kongming-rs-hv`. It mirrors the Rust implementation's architecture but uses Python-level operations (`hv.bind`, `hv.bundle`, `hv.release`, etc.), making the underlying hypervector mechanics fully transparent and easy to modify.

This implementation is ideal for:
- Understanding how LISP primitives map to hypervector operations
- Experimenting with alternative encodings or evaluation strategies
- Teaching and prototyping

## Quick Start

```bash
pip install kongming-rs-hv
```

```python
# Pure Python
from pylisp import LispEnv

env = LispEnv()
env.eval("(CAR (QUOTE (A B C)))")       # => "A"
env.eval("(CDR (QUOTE (A B C)))")       # => "(B C)"
env.eval("(CONS (QUOTE A) (QUOTE B))")  # => "(A . B)"
```

```python
# Rust (same API, same results)
from kongming.lisp import LispEnv

env = LispEnv()
env.eval("(CAR (QUOTE (A B C)))")       # => "A"
```

## Supported Forms

### McCarthy's 7 Primitives (1960)

| Form | Example | Result |
|------|---------|--------|
| `QUOTE` | `(QUOTE (A B C))` | `(A B C)` |
| `CAR` | `(CAR (QUOTE (A B C)))` | `A` |
| `CDR` | `(CDR (QUOTE (A B C)))` | `(B C)` |
| `CONS` | `(CONS (QUOTE A) (QUOTE B))` | `(A . B)` |
| `ATOM` | `(ATOM (QUOTE A))` | `T` |
| `EQ` | `(EQ (QUOTE A) (QUOTE A))` | `T` |
| `COND` | `(COND ((EQ (QUOTE A) (QUOTE B)) (QUOTE NO)) (T (QUOTE YES)))` | `YES` |

### Extensions

| Form | Description |
|------|-------------|
| `LAMBDA` | Anonymous functions with curried beta-reduction and variable shadowing |
| `LABEL` | Recursive self-reference (enables recursion without mutation) |
| `DEFINE` | Bind a name to a function in the environment |

### Examples

```python
# Lambda
env.eval("((LAMBDA (X) (CAR X)) (QUOTE (A B C)))")  # => "A"

# Define a reusable function
env.eval("(DEFINE SECOND (LAMBDA (L) (CAR (CDR L))))")
env.eval("(SECOND (QUOTE (X Y Z)))")                 # => "Y"

# Recursion with LABEL
env.eval(
    "(DEFINE LAST (LAMBDA (L) "
    "  ((LABEL REC (LAMBDA (X) "
    "    (COND ((ATOM (CDR X)) (CAR X)) "
    "          (T (REC (CDR X)))))) L)))"
)
env.eval_full("(LAST (QUOTE (A B C)))")              # => "C"
```

## How It Works

Each LISP value is a **Sparkle** — a sparse binary hypervector seeded by
its content. Atoms like `A`, `B`, `CAR` are sparkles in a symbol domain.

A **cons cell** `(a . b)` is encoded as:

```
cell = bundle(bind(a, LHS), bind(b, RHS))
```

where `LHS` and `RHS` are fixed tag sparkles. The cell is stored under a
fresh random sparkle id. To extract:

```
car(id) = cleanup(release(cell, LHS))
cdr(id) = cleanup(release(cell, RHS))
```

The `release` operation is noisy — it produces an approximate result.
**Cleanup** uses near-neighbor search (NNS) over the substrate's
associative index to find the exact stored sparkle that best matches
the noisy probe.

## File Structure

```
examples/pylisp/
  __init__.py      # Package entry point
  types.py         # HyperBinary type alias
  env.py           # LispEnv: domains, symbols, lexicon, substrate
  cons.py          # Cons cells: cons, car, cdr, cleanup via NNS
  reader.py        # S-expression tokenizer and parser
  evaluator.py     # Single-step and fixed-point evaluator
  lambda_.py       # Beta-reduction with currying and shadowing
  printer.py       # Hypervector → S-expression display
  test_pylisp.py   # 16 tests mirroring the Rust integration suite
```

## Storage Backends

```python
# In-memory (default, volatile)
env = LispEnv()

# Persistent (Embedded disk-backed)
env = LispEnv(path="/tmp/my_lisp_db")
```

## Running Tests

```bash
pip install pytest kongming-rs-hv
pytest examples/pylisp/test_pylisp.py -v
```

## Notebook

We provide a Colab notebook that runs both implementations side by side, demonstrating correctness parity and performance comparison:

<a href="https://colab.research.google.com/github/yangzh/hv/blob/main/notebook/lisp.ipynb" target="_blank"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"></a>

## References

- [Hey, Pentti, We Did it!: A fully Vector-Symbolic Lisp](https://arxiv.org/abs/2510.17889) — the paper that inspired this implementation
- [Peter Norvig's (How to Write a (Lisp) Interpreter (in Python))](https://norvig.com/lispy.html) — the original Lispy that the Python implementation builds upon
