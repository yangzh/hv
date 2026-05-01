# Changelog

All notable changes to `kongming-rs-hv` are documented here.
Only the latest 10 releases are shown.

## v4.2.0 (2026-04-30)

A meaty release: a new **Deque** chunk-level data structure, a Rust port of NLP `training` / `viterbi_decoder` / `memory_test`, and a few `hv` constructor renames for naming consistency.

### New: Deque

A doubly-linked, payload-carrying chunk chain. See `docs/api/memory/deque.md` for the full reference.

### Refactors / breaking renames

These are mostly Go/Rust internals; the Python public surface is largely unchanged.

## v4.1.1 (2026-04-27)

Docstring polish: every PyO3-emitted item in `kongming_rs` now conforms to the
project's docstring spec, with a structural lint to gate regressions.

### Docs
- All **442** user-facing items across `hv` (332), `memory` (~75), and `lisp` carry
  one-line summaries plus Args / Returns / Raises / Postconditions / Examples
  sections per `docs/python_docstring_spec.md`. `help(...)` output and IDE
  tooltips across the API are now uniform and self-contained.
- New `scripts/lint_pydocstrings.py` — structural checker, **strict by default**
  (`--no-strict` for warning mode). Filters to items defined in the target
  module; ready to drop into CI.

## v4.1.0 (2026-04-26)

A meaty release with two themes: a sweep of polymorphic Python ergonomics across the Domain / Pod / Seed128 / Selector surface, plus full producer-API parity with Go/Rust including a new `producer.produce(view)` batched-write entry point.

### New features

- **Polymorphic Domain / Pod / Seed128 inputs**. Anywhere a `Domain` is expected: `Domain | str | int | (DomainPrefix, str)` tuple. Anywhere a `Pod`: `Pod | Prewired enum | str | int`. Anywhere a `Seed128`: `Seed128 | (domain, pod)` tuple — and the tuple composes (so a prefixed Domain inside a Seed128 tuple Just Works). Drops the `hv.Domain.from_name(...)` / `hv.Pod.from_word(...)` / `hv.Seed128(...)` wrap at every call site. See `docs/api/hv/common/domain_pod.md` and `docs/api/hv/common/seed128.md` for the full table.
- **`producer.produce(view)`**. Run a producer against an open `MutableSubstrateView`, mirroring internal API. The recommended path for batched producer-driven writes; cheaper than `storage.mem_set(producer)` (which opens its own one-shot view).
- **`semantic_indexing` + `extra` kwargs on producer factories**. `from_set_members`, `from_sequence_members`, `from_key_values` now accept `semantic_indexing=False` (impresses the composite's *code* in addition to the id-Sparkle, needed for `set_members` / `tentacle` / `sequence_attractor` queries) and `extra=None` (proto Any payload).
- **`memory.lazy_selector_iter(view, selector)`**. Streaming iterator mirroring Go's `SelectorIter` — yields `(Chunk, SelectorExtra)` pairs lazily. Use when you need NNS scores or want to early-terminate without materializing the full result set.
- **`Sequence.append(*more)` / `prepend(*more)` / `reset(start)`**. In-place mutation methods on Sequence (mirrors `Knot.expand`). `__copy__` / `__deepcopy__` added so `copy.copy(seq)` works for the clone-before-mutate pattern.
- **`Set.member(i)` / `Sequence.member(i)` / `Octopus.value_by_key(k)`** accessors for inspecting composite members after retrieval.
- **`hv.bind_direct(*operands, domain=None, pod=None)`**. Returns a raw `SparseSegmented` (no Knot tracking) — cheaper for intermediate computations.

### API changes

- **`storage.put(chunk, semantic_indexing=False)`** now takes a `memory.Chunk` instead of a bare HyperBinary. Wrap with `memory.Chunk(hv)` (or `memory.Chunk(hv, note="...")`). Always indexes the chunk's id-Sparkle; `semantic_indexing=True` additionally indexes the code (mirrors the producer convention).
- **Removed `storage.store_chunk`** — `storage.put(memory.Chunk(...))` covers the same ground.
- **Removed `view.write_chunk`** — use the producer-API path (`producer.produce(view)`) for batched writes against a mutable view.
- **`hv.bind_more(...)` removed** in favor of in-place `Knot.expand(*more)` (the v3.9.0 free function went away when the refactor made the in-place mutation cleaner).

### Bug fixes

- **`view.write_chunk` (now removed) used to silently skip the associative-index update**, so chunks written via the batched-view path were findable by exact-key lookup but not by NNS. The fix threaded `Substrate::index_arc()` through `MutableSubstrateView`. The followup API redesign (above) replaces the path entirely with `producer.produce(view)`.

## v4.0.0 (2026-04-21)

Major version bump to signal the underlying PyO3 runtime change — the public Python API is unchanged, but the extension is rebuilt against a new binding layer that's a 5-minor-version jump ahead.

### Internal
- Upgrade pyo3 0.23 → 0.28.3. Migration covers `PyObject` → `Py<PyAny>`, `Python::with_gil` → `Python::attach`, and explicit `from_py_object` opt-in on 15 pyclass types. Smoke tests and three Jupyter notebooks (first, memory, lisp — 79 code cells) pass without regression.

## v3.9.1 (2026-04-18)

### Packaging
- New `manylinux_2_28_aarch64` wheel for Linux ARM64. `pip install kongming-rs-hv` now works natively inside ARM Linux containers — e.g. `docker run python:3.12-slim` on Apple Silicon no longer needs `--platform=linux/amd64` / Rosetta emulation.

## v3.9.0 (2026-04-16)

### New features
- `hv.bind_more(knot, *more)` → `Knot` — extend an existing Knot with additional parts without re-binding from scratch. `bind_more(bind(a, b), c)` is equivalent to `bind(a, b, c)`. Returns a new Knot; the original is unchanged. Raises `ValueError` if no additional operands are passed.

### Performance
- `bind_direct()` short-circuits on a single operand, skipping the bind loop and buffer allocation.

### Docs
- Docker installation guide in the Python Quick Start: one-liner REPL, reusable image, and JupyterLab container.

## v3.8.10 (2026-04-11)

### New features
- Constants (MODEL_*, PREWIRED_*, HINT_*, DOMAIN_PREFIX_*) are now native Python `IntEnum` members — iterable, named, and IDE-discoverable via `hv.Model`, `hv.Prewired`, `hv.Hint`, `hv.DomainPrefix`. Fully backward-compatible (IntEnum subclasses int).

### Bug fixes
- Fix pylisp: update stale `Domain.with_prefix` → `from_prefix_and_name` and `first_picked_chunk` → `first_picked`
- Fix HV compliance tests: update for Seed128 composite API, remove PREWIRED_OCTOPUS_MARKER (deleted from proto), fix Sequence step domain (d0)

### Docs
- Document IntEnum constants and enum classes in python_api.md
- Fix `Domain.with_prefix` → `from_prefix_and_name` in python_api.md

## v3.8.9 (2026-04-09)

### API changes
- `SparseSegmented.from_offsets(model, offsets)` — new constructor from per-segment offsets
- `WithChunk()` renamed to `WithChunks()` — accepts multiple chunks
- Removed `display_size` parameter from `to_svg()` / `to_svg_overlap()` — client-side handles viewport

### Notebook
- SVG viewer with zoom/pan controls, minimap, and reset button

## v3.8.8 (2026-04-08)

- SVG: unique pattern IDs (random), show_svg helper with zoom/pan in notebook

## v3.8.7 (2026-04-08)

- Notebook: scrollable SVG containers; auto-mirror releases to hv repo
- SVG: add display_size parameter to Go/Rust/Python (0 = auto)


