# Changelog

All notable changes to `kongming-rs-hv` are documented here.
Only the latest 10 releases are shown.

## v5.2.0 (2026-09-03)

### Breaking changes

- **`Learner.has_cached_data()` / `cached_data()` renamed** to
  `has_deferred_data()` / `deferred_data()` (wire fields likewise
  `deferred_*`; wire-compatible by field number).
- **Misuse now panics instead of erroring**: bundling or reading an
  uninitialized pool, and constructing a zero-member pool, raise
  `PanicException` (they were errors or silent before).
- Deferred-mode `support()` reads are noise-corrected estimates and can
  read ~1 lower than the spilled path for the same content.

### New features

- **`Learner(model, seed, initial=None, *, rng_hint=None)`** — pin the RNG
  backend per learner (`hv.RNG_*`); pools, the deserializer, and producers
  thread their own hints instead of falling back to the process default.
- Multi-attractor NNS: one pushed-down scan over the access-circle union.

### Performance

- Learner reads retain the multi-entry mixture fill (computed once, reused
  across reads, dropped on writes); pool member reads are one lazy Bind.

### Fixes

- A failed `hydrate()` no longer leaves the pool half-initialized — the
  loader can be corrected and retried.
- Learner snapshot/exposure holes closed: escaped views stay stable across
  later writes (copy-on-write), `Power(1)` included.
- Knot parts are canonically ordered; composite `Power(0)` returns the
  typed identity; exponents fold into member recipes (exp-1 shells).

## v5.1.0 (2026-08-28)

### Breaking changes

- **Stored substrates from v5.0.0 cannot be read.** Three wire-format
  changes land together.
- **`LearnerPool(model, member_domain, total)`** — the two trailing seed
  arguments (ignored since the write seed was dropped) are removed.
- **`Learner.full()` removed** (reconstruction stays engine-side);
  `HyperBinarySet` is retired — `Parcel` answers the member queries.
- **The train subsystem is removed** (`Train*` producers and carriages).

### New features

- **zh corpus 995 → 4231 sentences** (parity with en); combined substrate
  retrained.
- **`Learner.blank()`** in Python; pool `load()` / `unique_estimated()`
  are tracked incrementally.
- `lazy_selector_iter` raises on truncation instead of silently clipping.

### Performance

- Serialization: Parquet row groups 1K → 16K and reader batching — much
  faster substrate load; footers stamp pre-compression size.
- Learner hot path: support reads borrow offsets (no per-probe copies),
  deferred lists replay into recycled scratch, identity hashes memoized.

### Fixes

- The Dart producer's documented formula matched its inverse; corrected to
  `Inv(tail) ⊗ head` (Go, Rust, Python docstrings).
- `Revitalize` rescales correctly in list mode; blank-learner age/weights
  stay in sync.
- Empty-prefix scans work again (the reject guard had broken export).

## v5.0.0 (2026-08-22)

Headline: hypervectors become lazy — content is computed on first use.

### Breaking changes

- **Stored substrates from v4.x cannot be read.** Three independent format /
  content changes land together, so a substrate written by an older release
  will not round-trip. Retrain, or pin the old wheel:
  - **Philox-4×64 is now the default RNG** (was xoshiro256++). Every seeded
    vector generates different offsets, so *all* stored content differs.
    `KONGMING_RNG=xoshiro++` restores the previous generator.
  - **`Dart` storage and content changed.** A Dart is now `Inv(tail) ⊗ head`
    with compact member storage.
  - **The `Learner` wire form changed.**
- **`Learner.support()` is noise-subtracted now: the chance floor moved into member reads, so values saturate at 0 rather than starting at chance.
- **`KONGMING_REPR_FORMAT` is gone.** `repr()` always renders YAML.

### New features

- **`compact()` on every hypervector.** Releases cached content, recursively
  through members; the next observation recomputes exactly the same bits.
- **`equal_lazy()` and `equal()`.** Two levels of content equality:
  `equal_lazy` compares recipes and already-known hashes without ever
  materializing (a `False` may mean "not provable cheaply"), while `equal` is
  exact and materializes only when it must.
- **`Learner.has_cached_data()` / `Learner.cached_data()`.** Inspect the
  observations a young learner is still holding verbatim.
- **`Learner.age()` accepts and reports values beyond 2^32** (widened to u64).

### Performance

- **Lazy materialization.** Vectors are recipes until observed, so constructing
  candidates you never look at is nearly free. Measured on the decode
  benchmark: resident memory −45%, and stored substrates shrink ~39%.
- **Cheaper training.** The pool's member-open check no longer divides
  per member: full-corpus training −5%.

## v4.12.0 (2026-08-17)

Headline: LearnerPool write path reworked.

### Breaking changes

- **`UniformSet.inner_prod()` / `WeightedSet.inner_prod()` removed.** The
  set-vs-vector inner product is gone from the set types; the frame helpers
  (`frame_inner_product`, `frame_coefficient`, …) fold it over the members
  internally.

### New features

- **`hv.LearnerPool.unique_estimated()`.** Estimated unique-item count across the
  whole pool (Σ 1/diversity_margin over the written members).

### Performance

- Overlap uses portable SIMD (`wide`) for the byte-aligned models (8-/16-bit).
- NNS candidate tally switched to a fast integer hasher, and `CircleReadResult`
  reuses a read-session bind buffer — both trim decode CPU.

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

