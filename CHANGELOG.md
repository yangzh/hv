# Changelog

All notable changes to `kongming-rs-hv` are documented here.
Only the latest 10 releases are shown.

## v7.1.0 (2026-10-27)

### Breaking changes

- **`Learner.mass()` is removed; `mass_fractional()` is now `mass_units()` and
  `mass_numerator()` is `total_mass_units()`.** Mass is measured in one unit —
  numerators over `mass_denominator(model)` — and the names now say so at both
  scopes: `mass_units(probe)` for one observation's share, `total_mass_units()`
  for the learner's whole. Divide by `mass_denominator(model)` when you want
  whole observations, ONCE, at the end of any summation.

  The removed `mass()` rounded per probe, which read as the primary accessor
  while being the lossy one — sub-observation holdings became 0, and summing
  several of them erased the lot. That is not hypothetical: it is the pool bug
  fixed just below. Every break here is a compile error or an AttributeError,
  not a silent change of units.

  The float version `mass()` was approximating is now the free function
  `hv.mass(learner, probe)` (Go `hv.Mass`, Rust `hv::learner::mass`), which
  returns whole observations: a 0.4-observation holding reads `0.398` rather
  than `0`. It is a unit conversion, not a rounding, so nothing is lost.
  Deliberately not a method — the old `learner.mass(probe)` still breaks loudly,
  and no call site can mistake the numerator for the observation.

- **`Learner.random(so)` is now `Learner.random(domain, so, initial=None)`, and
  `Seed128.random(so)` is removed.** The old constructor was random in neither
  useful sense: with no initial the content is the identity, so two "random"
  learners were byte-identical, and the random DOMAIN made them unaddressable.
  The caller now fixes the domain and supplies an initial value if it wants one.

  The library deliberately does not fill in the learner's own Sparkle: a
  learner's seed names it rather than describing what it holds, and
  auto-filling would leave every learner holding one observation it never saw,
  polluting `age`, mass, and so the conditional. Pass it explicitly when you
  want a learner distinguishable at birth.

  To reproduce the old RNG stream exactly, draw the domain first —
  `Learner.random(Domain.from_id(so.uint64()), so)` consumes the same two
  values in the same order.

- **`Learner.revitalize(age)` is replaced by `Learner.reduce_mass(units)`.**
  The old call set `mass = age * mass_denominator(model)`, which is the
  invariant from before age and mass were split — true only when every write
  was one whole observation. Under `bundle_fractional` it was false, so
  `revitalize(learner.age())`, asking only to keep the SAME age, silently
  rewrote the mass: measured 6.00 observations becoming 21.00.

  The operation was always about PLASTICITY, which lives in the mass: a write's
  mixing share is its weight over the running total, so lowering the total makes
  new input count for more. `reduce_mass` says that and leaves `age` alone.
  Reduction only — raising it would fabricate weight the learner never
  received — and it panics above the current mass, as it already did on a blank
  learner. No library code called `revitalize`, so nothing but direct callers
  breaks.

- **Wire field `LearnerPayload.mass_numerator` is renamed `mass_in_units`.**
  Field number 6 is unchanged, so BINARY payloads round-trip across the rename
  in both directions. What changes is anything that goes by field NAME: JSON and
  prototext encodings, and the YAML repr used by the Go/Rust fixtures. The Go
  and Rust struct fields follow (`massInUnits` / `mass_in_units`), and the
  generated accessor is now `GetMassInUnits()`.

- **`Learner.barycentric()` is gone — use `Learner.occupancy()`.** The alias
  shipped deprecated in v7.0.0 and delegated to `occupancy()`, so the
  replacement is a rename at the call site with no change in value or
  signature. `hv.frame_barycentric()` is a different function and is
  unaffected.

  The formal name stays in the prose, because the quantity *is* a barycentric
  coordinate (Eq. 28 of https://arxiv.org/pdf/2310.18316) — what moved is the
  method you call to read it.

### New features

- **`hv.Point(frame, coords)` — a position in a frame of basis hypervectors.**
  Given bases `b0..b[n-1]` and coordinates `c0..c[n-1]` the Point is
  `b0**c0 (x) ... (x) b[n-1]**c[n-1]`, so each axis contributes one power and
  bind composes them. `frame()`, `coords()` and `rank()` read it back; a short
  coordinate list pads with the origin, and the all-origin Point is the
  identity. Coordinates are an int or a `(numerator, denominator)` pair and
  always come back as pairs, in lowest terms.

  The coordinates are KEPT as exact rationals rather than folded into the
  vector, because bind is not additive on fractional powers: `K**u (x) K**v`
  agrees with `K**(u+v)` on only ~50% of segments (measured 512–545 of 1024),
  since flooring each factor separately loses what flooring the sum keeps. So
  arithmetic on an encoded value belongs on the rationals, with a single
  truncation at materialization — `Point.power()` scales the coordinates for
  exactly that reason. A frame must be readable: shared model, pairwise
  distinct, no identity basis.

- **Recovering coordinates from a bare `SparseSegmented`**, in three routines
  by regime. A materialized vector holds no coordinates — they were spent into
  its offsets — yet they are fully determined by it given the frame, and all
  three verify against EVERY segment, so a vector that is not a point on the
  frame raises rather than returning a best fit.

  `hv.recover_point(frame, raw)` is exact for INTEGER coordinates and not a
  search: an integer power never truncates, so each segment is one linear
  equation mod `cardinality(model)` and Gaussian elimination solves the system
  outright, with the surplus equations verifying. Exact through rank 20 on
  every model. Coordinates land in `[0, W)`, which is the whole answer — `c`
  and `c+W` scale every offset identically.

  `hv.recover_point_fractional(frame, raw, level)` handles a `1/2**level` grid,
  where the power truncates and the problem becomes a closest-vector one: LLL
  lattice reduction over `4*rank` segments places the answer, then a polish
  pass scores it against all segments. Reliability follows `rank/W`, so it
  tracks the MODEL rather than the level — every rank through 10 recovered at
  10-bit and above, while 8-bit holds to about rank 4. A higher `level` does
  not help; it buys code count, not resolution. `level + sparsity_bits(model)`
  is capped at 28, past which it refuses rather than overflowing.

  `hv.recover_point_noisy(frame, raw, max_bad)` returns `(Point, bad_count)`
  for a vector whose offsets are CORRUPTED. The exact solve cannot do this at
  all — coordinates live in a modular group with no notion of "close", so one
  wrong offset among those the elimination pivots on randomizes the answer
  rather than perturbing it. This repeats the same solve on random segment
  subsets and scores each candidate against all segments, keeping the best.
  Rank costs tolerance, as `(1-f)**rank` predicts: exact recovery held through
  ~60% corrupted segments at rank 3 and ~40% at rank 10. The returned count is
  a diagnostic — on success it is exactly the number of disagreeing segments —
  and a foreign vector still raises rather than passing as heavily corrupted.

  Worked examples: `examples/point/point_2d.py` and `point_3d.py`.

## v7.0.0 (2026-10-18)

### Licensing

- **The wheel is no longer MIT throughout.** The declared expression is now
  `MIT AND LicenseRef-Kongming-Engine-Proprietary`: the Python layer stays MIT,
  the compiled engine is proprietary (`LICENSE-ENGINE`). v6.0.0 declared
  `MIT AND (Apache-2.0 OR BSD-2-Clause)`, which described the dependency tree
  rather than the artifact. Automated license scanners will see the change.
- The wheel now ships `LICENSE`, `LICENSE-ENGINE` and `THIRD-PARTY-NOTICES.md`,
  the last carrying the real notice texts for every statically linked
  dependency. Declared as a PEP 639 license expression, so the metadata is a
  validated `License-Expression:` field rather than the deprecated free-text
  `License:`.

### Breaking changes

- **`Learner.barycentric()` is now `Learner.occupancy()`.** Same signature and
  same value. "Occupancy" is what the design note calls this — the share of the
  `M` segments a probe owns — and `mass()` is the same quantity un-normalized.
  `barycentric()` still works, delegating to `occupancy()`, but is deprecated
  and will be removed: the barycentric coordinate is what the share IS formally,
  which is precise and no help in reading the code.

- **`Learner.barycentric()` can now return a NEGATIVE value.** It no longer
  routes through `support()`, which clamps at 0, so it is an unbiased estimate
  of the probe's share of the accumulated weight. A probe below the chance
  baseline reads negative, which about 4% of never-observed probes do.

  The clamp was quietly biasing the estimate upward exactly where shares are
  smallest: a never-observed probe averaged `+.0004` instead of 0, against a
  resolution floor of `1/M == .0039`. Small per read, but it does not cancel
  when summed over a vocabulary, and averaging more reads no longer converged
  on the truth. `frame_barycentric()` never clamped, so the two agree now.

  If you need a non-negative share, clamp at the call site, or use `support()`
  for the "how strongly is this backed" reading — that one still clamps and is
  unchanged. `mass()` and `mass_fractional()` are also unchanged: they floor at
  0 themselves, since mass is unsigned.

- **`Learner.count()` is now `Learner.mass()`, and `LearnerPool.count()` is
  `LearnerPool.mass()`.** The name was wrong: it never counted writes, it
  reported the probe's accumulated WEIGHT divided by one observation's worth.
  Under fractional writes that distinction is load-bearing, so the new
  `Learner.mass_fractional()` returns the exact numerator — a quarter-observation
  holding reads `mass() == 0` but `mass_fractional() == cardinality // 4`.
  `hv.mass_denominator(model)` gives the units-per-observation those numerators
  are over.

  Two bugs went with the rename. Sub-observation holdings were unrepresentable
  rather than merely rounded, and the two internal storage modes disagreed —
  the list path truncated where the spilled path rounded, so the same holding
  read 0 before a spill and 1 after. `mass()` now rounds in both.

- **The template/replace operators are gone**: `hv.Replacement`,
  `hv.replace()`, `hv.replace_single()` and `hv.Parcel.template()`. They were
  thin spellings of `bind`/`release` that no library code used — `replace(tmpl,
  seed, reps)` is `bind(tmpl, bundle(seed, [release(new, old) for each rep]))`,
  `replace_single(tmpl, old, new)` is `bind(tmpl, release(new, old))`, and
  `Parcel.template(seed, *roles)` is `bundle(seed, [bind(r, r) for r in
  roles])`. Each is one line at the call site, so nothing is lost.

- **`hv.frame_coefficient()` is now `hv.frame_barycentric()`.** Same signature and
  same value; the name says what it returns. A frame member reads its own
  weight and a stranger reads ~0, so over a normalized frame the members'
  coordinates sum to 1 — a barycentric coordinate, not an opaque coefficient.

- **`Learner.weight()` is now `Learner.barycentric()`.** Same signature and same
  value; the name says what it returns. Each of the `M` segments is owned by one
  observation, so the normalized overlap is that observation's barycentric
  coordinate in the learner — a share, not an opaque weight. Not to be confused
  with `bundle_multiple`'s `weight` argument, which is unchanged.

- **`Set.unmasked()` and `Sequence.unmasked()` return a `Dart`**, not a
  `SparseSegmented`. The result is LAZY, so the bits are computed only when you
  ask: call `.core()` for the materialized form. Every HyperBinary read works
  unchanged on the returned value — `overlap()`, `core()`, `stable_hash()` —
  so only an explicit `isinstance(..., SparseSegmented)` needs updating.

- **`Learner.age()` counts bundle calls, not accumulated weight.** A
  `bundle_multiple(obs, 3)` now ages the learner by 1, not 3; the weight it
  carried lands in the new `Learner.mass_numerator()`. The two agree on the
  plain `bundle()` path, so the age is an exact occurrence count there — which
  is the point: it can serve as a frequency without a side table.
  `LearnerPool.load()` likewise counts writes absorbed. Reads that are shares
  or ratios — `barycentric()`, `mass()`, `support()`, `overlap()` — are
  unchanged, because the mixing share depends only on *relative* weights.
  Payloads written before this read back unchanged — a pre-split learner is
  recognised and its weights rescaled, by a missing mass in buffer mode and by
  the weights summing to the age in list mode — but the stored learner bytes
  change, so trained substrates must be regenerated. The mass is serialized in
  buffer mode only; in list mode it is exactly the sum of the stored weights,
  so it is recomputed on load rather than written twice.

### New features

- **Fractional bundle weights**: `Learner.bundle_fractional(obs,
  weight_numerator)` and `LearnerPool.bundle_fractional(data, addr,
  weight_numerator)`. Weights are numerators over `hv.cardinality(model)`, so
  one whole observation is `cardinality` units and a weight of 1/n is
  `cardinality // n` — anything down to a single unit is expressible. This is
  what makes per-observation weighting possible without an integer floor: an
  IDF-style `1/count` write now actually moves the learner by 1/count instead
  of rounding to zero or one. `bundle()` and `bundle_multiple()` are unchanged
  and still take whole observations.

- **`Learner.mass_numerator()`** reports the accumulated weight in those same
  units. This is the quantity that drives the mixing share, where `age()` does
  not, and it accumulates in 64 bits — so it no longer saturates at the `u32`
  roof that used to cap a heavily-trained learner.

- **`LearnerPool` takes an optional RNG backend**:
  `LearnerPool(model, member_domain, total, *, rng_hint=hv.RNG_*)`. Keyword-only
  and defaulting to the process default, so existing calls are unaffected. The
  member roster replays from it, so a pool stored under one backend must be
  reloaded under the same one.

- **`hv.lee_distance(x, y)`** — the sum over segments of the *circular* offset
  difference, `min(d, q - d)` for segment size `q`. Where `hamming` asks only
  whether two segments disagree, Lee asks how far apart their offsets sit on the
  ring of `q` positions, so it is the right metric only where offsets carry an
  ORDINAL meaning (fractional-power encoding). For the seeded random codes a
  `Sparkle` produces, two offsets are unrelated draws and `hamming` stays the
  honest measure. Materializes both operands; identity reads as all-zero.

- **`.hint()` is back on every hypervector type**, reporting the `hv.HINT_*`
  constant the value *serializes* as — which is also the type a proto round-trip
  restores, so an identity reads `HINT_SPARSE_SEGMENTED` whatever carries it.
  Not the construction-time type tag of the same name removed in v4.10.0: that
  one answered "what did you build", this one answers "what goes on the wire,
  and what comes back".

### Fixes

- **`repr()` now shows the packed `env` word with its decoded fields** instead
  of a `hint:` / `model:` pair: `env: 4131 # v1 SPARKLE MODEL_1M_10BIT
  PHILOX_4X64`. The old form rendered two of the four fields env carries and
  silently dropped the other two — the format version and the RNG backend —
  which is the one thing you most need when a seed-derived vector reloads under
  a different backend. The `env:` lines now match Go's dump byte for byte, and
  nested members (a composite's parts, a learner's `deferred_data`) annotate
  too. Debug output only; nothing on the wire changed.

- **`hv.overlap()` / `hv.hamming()` now dispatch on their first operand.** Given
  a `Learner` still in list mode as `x`, both compared materialized content,
  skipping the estimate `Learner.overlap` answers from its stored entries — so
  they disagreed with Go, which delegates to `x.Overlap(y)`. Values move for
  list-mode learners only (measured 13 → 17, 29 → 33, 70 → 65 on a 7-item
  learner); pass `.core()` explicitly for the old buffer-compare behaviour.

- **A seed-derived vector now reloads under the backend that produced it.**
  Sparkle, Cyclone, Set, Sequence, Octopus and Parcel record their RNG backend
  on the wire; previously a reader re-derived their content using *its own*
  default, which silently produced different offsets for the same seed whenever
  the two disagreed (via `KONGMING_RNG`). Payloads written before this read
  back exactly as they did, and older readers ignore the new field, so the
  change is compatible in both directions — but stored payloads grow 2 bytes
  per RNG-fed vector. Vectors whose content is explicit or RNG-free
  (`SparseSegmented`, `Knot`, `Dart`) record nothing; `Learner` keeps the hint
  in its own payload beside the RNG state.
- `Learner` equality no longer reports two learners as equal when they hold the
  same observations under different RNG backends — their bundled content
  genuinely differs.

- **A learner no longer freezes once trained past age `2·cardinality`.** The
  per-observation segment share was rounded with `round()`, which floors to ZERO
  past that point — so every further unit `bundle()` was a silent no-op while
  `age()` kept counting. The wall sat at 512 observations at 8-bit and 2048 at
  10-bit. Measured past it, 5000 unit observations of a fresh vector moved its
  overlap 2 → 3 (chance is 1), where the same mass delivered as a single
  `bundle_multiple(fresh, 5000)` reached 232. That truncated the `1/t` schedule
  to a dead stop, so the learner settled at a biased point instead of
  converging. The share now floors and adds one more with probability equal to
  the leftover fraction — unbiased at every age, and integer-only so Go and Rust
  draw alike. Applies to the spilled-learner replay path too.

### Build / deps

- fjall 3.1.12 (lsm-tree 3.1.10), the `Embedded` storage engine.

## v6.0.0 (2026-10-07)

### Breaking changes

- **`LearnerPool.bundle()` requires an address.**

### New features

- **`count()` on `Learner` and `LearnerPool`** reports the raw bundled count of
  a probe — the integer number of times it was written.

### Performance

- Pool writes allocate less. Bundling now shares an immutable operand instead of
  defensively deep-copying it, removing one `Dart` clone per deferred write
  (672 B / 7 allocations down to 48 B / 1). Measured 19% fewer bytes and 17%
  fewer allocations per write on the open-pool path. Write latency is unchanged
  — it is dominated by the circle scan, not the copy.

## v5.4.0 (2026-10-05)

### Breaking changes

- **A materialized vector never reports an exponent.** `SparseSegmented`
  holds no recipe, so there is nothing for an exponent to be pending against:
  `power()` spends it into the offsets immediately and leaves the exponent at
  1. `ss.power(1, 2).exponent()` and `x.core().exponent()` now return
  `(1, 1)` where they previously returned the accumulated fraction. The LAZY
  value still reports its own, so `Set.power(1, 2).exponent()` is `(1, 2)`
  while its `.core()` is `(1, 1)`.
- **A corrupt `stable_hash` is now rejected.** Reading a `SparseSegmented`
  whose stored hash disagrees with its offsets raises instead of silently
  accepting the payload, matching the reference engine. An absent hash (0)
  stays legal.
- **`memory.learner_sampler` is gone** — removed back in the v5.1.0 cycle but
  never documented. It had no users, and the two engines never agreed on its
  semantics.

### New features

- **`SparseSegmented` keeps its identity across the wire.** `(domain, pod)`
  are now serialized and read back, where both previously reset to the
  defaults on a round trip. Wire-compatible in both directions: an absent
  domain/pod reads as the default, so existing payloads decode unchanged.

### Performance

- Content overlap answers from cached hashes before forcing either operand to
  materialize. The compact-then-compare pattern no longer recomputes a
  composite on every cycle (measured ~845x on a 64-member Set).

### Fixes

- Bundled notebooks are self-contained: the SVG viewer helper is gone, which
  also removes its inline renderings. The visualization now lives in the
  [documentation](https://yangzh.github.io/hv/concepts/hypervectors.html).

## v5.3.0 (2026-09-24)

### Breaking changes

- **Stored substrates from v5.2.0 and earlier must be regenerated, and the
  break is SILENT.** The `exponent` field (number 5) changed from a `sint32`
  to an `Exponent` message, which changes its wire type. Old payloads still
  parse — the field is skipped as unknown and the exponent reads back as 1
  rather than its stored value. There is no format-version gate to catch
  this, so a stale substrate degrades quietly instead of failing. Regenerate
  rather than upgrade in place.
- **`exponent()` returns `(numerator, denominator)`**, not an integer:
  `s.power(3).exponent()` is now `(3, 1)`, and a base vector reports `(1, 1)`.
- **Pretty-printing marks the exponent with 💪**, previously `^`, matching the
  reference engine: `✨:🔗pos,🌱step,💪1/2`. The separator changed with it —
  emitted only after a domain, and never for `Parcel`.
- **`Learner.unique_estimated()` is removed**, along with the learner's
  diversity margin.

### New features

- **Fractional powers** — `power(numerator, denominator=1, denominator_ls=0)`.
  `power(1, 2)` is the square root of the permutation; `denominator_ls` spells
  the denominator as `2 ** ls` and takes an integer scaling path instead of
  float arithmetic. Exponents are kept in lowest terms with the sign on the
  numerator, so `power(6, 2)` *is* the integer `power(3)`.
  Fractional scaling truncates toward zero, so it is lossy once a vector is
  materialized; on a lazy vector the exponents compose first and
  `power(1, 2).power(2, 1)` is exact.

### Performance

- `overlap` short-circuits on matching stable hashes, and proves identity
  lazily before any fill.
- `Dart.bind` cancels provable tails; `Knot.bind` no longer scans its parts.
- `equal` is recipe-first, and `bind` stays lazy across composites.
- Access-circle expansion is a two-scan over the tallied members.

### Fixes

- `AssociativeIndex` is `Send + Sync`, unblocking downstream Rust consumers.
- Set-member reads ignore hits at the NNS noise floor.
- Bundled notebooks regenerated; their outputs had been stale for several
  releases.

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
