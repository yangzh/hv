# LISP Interpreter (pylisp)

A LISP interpreter built entirely on hyperdimensional computing. Every data structure — atoms, cons cells, lists, closures — is a sparse binary hypervector. Every operation is VSA algebra: bind, bundle, release, and near-neighbor search.

Inspired by [Hey, Pentti, We Did it!: A fully Vector-Symbolic Lisp](https://arxiv.org/abs/2510.17889), originally developed by Peter Norvig [here](https://norvig.com/lispy.html).

## Two Implementations

The LISP interpreter ships in two forms, both feature-identical:

| | Pure Python (`pylisp`) | Rust (`kongming_rs.lisp`) |
|-|------------------------|--------------------------|
| **Source** | Included in `kongming-rs-hv`, also [open-sourced](https://github.com/yangzh/hv/tree/main/pylisp) | Compiled into `kongming-rs-hv` |
| **Readable** | Yes — ~500 lines of annotated Python | No — compiled Rust binary |
| **Performance** | Slower (Python overhead per operation) | Faster (native code) |
| **Import** | `from pylisp import LispEnv` | `from kongming_rs.lisp import LispEnv` |
| **Use case** | Learning, debugging, extending | Production, notebooks |

Both use the same API and produce identical results.

## Quick Start

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
from kongming_rs.lisp import LispEnv

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
| `COND` | `(COND ((EQ ...) (QUOTE NO)) (T (QUOTE YES)))` | `YES` |

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

Each LISP value is a **Sparkle** — a sparse binary hypervector seeded by its content. Atoms like `A`, `B`, `CAR` are sparkles in a symbol domain.

A **cons cell** `(a . b)` is encoded as:

$$\text{cell} = \text{bundle}(\text{bind}(a, \text{LHS}),\ \text{bind}(b, \text{RHS}))$$

where $\text{LHS}$ and $\text{RHS}$ are fixed tag sparkles. The cell is stored in a substrate under a fresh random sparkle id. To extract:

$$\text{car}(\text{id}) = \text{cleanup}(\text{release}(\text{cell}, \text{LHS}))$$

$$\text{cdr}(\text{id}) = \text{cleanup}(\text{release}(\text{cell}, \text{RHS}))$$

The `release` operation is noisy — it produces an approximate result. **Cleanup** uses [near-neighbor search](../concepts/near_neighbor_search.md) over the substrate's [associative index](../concepts/associative_index.md) to find the exact stored sparkle that best matches the noisy probe.

## Storage Backends

```python
# In-memory (default, volatile)
env = LispEnv()

# Persistent (Fjall disk-backed)
env = LispEnv(path="/tmp/my_lisp_db")
```

## Interactive Demo

Try it in Colab: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yangzh/hv/blob/main/notebook/lisp.ipynb?flush_cache=true)

## File Structure

```
pylisp/
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
