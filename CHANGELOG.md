# Changelog

All notable changes to `kongming-rs-hv` are documented here.
Only the latest 10 releases are shown.

## v4.11.0 (2026-08-15)

Headline: `LearnerPool` becomes a first-class Python type, and the resident-pool
substrate format is finalized.

### Breaking changes

- **`memory.similar_composite` → `memory.similar`.** The composite-similarity
  search is renamed; `similar_composite` shipped in v4.8 only as a transitional
  alias and is now removed. Update `memory.similar_composite(...)` →
  `memory.similar(...)`.

### New features

- **`hv.LearnerPool`.** A Python binding for the resident learner pool:
  build/size a pool, iterate its members, hydrate it from a substrate's pool
  sentinel, and read its capacity stats — the read-side counterpart to trained
  pools.
- **`Learner.diversity_margin`.** The post-bundle overlap of a learner's last
  write: a cheap scalar for how much a new write collided with what the learner
  already holds.
- **`hv.SparseOperation(rng_hint=…)`.** Keyword-only selection of the RNG backend
  at the SparseOperation level (parity with Go/Rust), matching the four
  bit-identical backends from v4.10.

## v4.10.0 (2026-08-11)

### Breaking changes

- **`HyperBinary.hint()` removed.** The per-vector type-tag accessor (and its
  `.hint()` Python binding) is gone from every hypervector type — a vector's type
  is known from how it was constructed. The `hv.HINT_*` constants stay for
  wire-format work.
- **Learner & identity serialization changed (persisted-data break).**

### New features

- **Two more RNG backends** — Philox-4×64-10 and xoroshiro128++ join
  xoshiro256++ (default) and PCG-DXSM, all bit-identical across engines. Select
  via the `KONGMING_RNG` environment variable.

## v4.9.0 (2026-08-03)

### Breaking changes

- **`semantic_indexing=` → `enable_semantic_indexing=`.** The impress / produce kwarg
  was renamed across all stores (Embedded, InMemory, Scylla). Update
  `impress(chunk, semantic_indexing=True)` → `impress(chunk, enable_semantic_indexing=True)`.

### New features

- **`disable_id_indexing=` kwarg** on `impress` / `produce` (all stores). When `True`, the
  chunk's Id-Sparkle is skipped from the index (item-key-only chunk) — pairs with
  `enable_semantic_indexing=` for full control over what each write indexes.

## v4.8.0 (2026-07-23)

### Breaking changes

- **Knot / Sequence are immutable** — `expand` / `append` / `prepend` / `reset`
  now return a NEW composite instead of mutating in place (Go/Rust/Python
  aligned).

### Fixes

- Learner age-overflow divide-by-zero in Fisher-Yates bundling.
- Identity-safe `Overlap` via batch offsets.

## v4.7.0 (2026-07-07)

### Breaking changes

- **`Learner.affinity(probe)` → `Learner.support(probe)`**.

### Build / deps

- PyO3 0.28 → 0.29; wheel version injected from the `rel-v*` tag (in-tree placeholder is `0.0.0`).

## v4.6.0 (2026-06-30)

Headline: a **maintenance / internal** release — the Python bindings are rebuilt against a large memory-layer refactor that landed since v4.5.0. No new Python API.

### Breaking changes

- **Index keyspace redesign.** The substrate's on-disk key layout changed;

## v4.5.0 (2026-05-28)

Headline: new **`weights=`** kwarg on `hv.Parcel` plus several Python API tightenings that catch up to upstream Rust/Go drifts. Internally, a large NLP push lands OOV-token recovery and multi-token entity decoding (not Python-facing yet).

### New features

- **`hv.Parcel(seed, *pearls, weights=[...])`** — single Pythonic constructor that collapses Go's `NewParcel` / `NewWeightedParcel` / `NewParcelFromParts`. Omit `weights=` for uniform bundling (existing behavior); supply a list to bundle with per-pearl weights. Length mismatch raises `ValueError`.

### API changes

- **`hv.Sparkle(model, domain, pod)`** — simplified signature.
- **`hv.Learner(model, seed, initial=None)`** — `initial` is now an optional kwarg defaulting to `None`.

## v4.4.0 (2026-05-14)

Headline: new **`LearnerPool`** SDM-style aggregator over N Learners, plus cross-language property/parity test infrastructure and a hardened memory-substrate contract.

### New features
- **`LearnerPool`** — SDM-style (Sparse Distributed Memory) aggregator that distributes writes across N Learners by access-circle.
- **Cross-language parity oracle** — Rust now runs against Go-generated goldens (`testdata/hv/goldens.yaml`) so any Go↔Rust drift trips a test.
- **Algebraic property tests** — 10 property tests covering Bind / Release / Bundle / Cyclone semantics, in Go (`rapid`) and mirrored in Rust (`proptest`). See `hv/parity.md`.

### Build / deps
- **`Cargo.lock` is now tracked** for reproducible Rust builds.
- **`fjall`** pinned to 3.1.4.

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
