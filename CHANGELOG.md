# Changelog

All notable changes to `kongming-rs-hv` are documented here.
Only the latest 10 releases are shown.

## v3.8.0 (2026-04-06)

- Clean up obsolete build tooling: remove govvv, proto plugins, ruff.sh
- Update CLAUDE.md: mark lbd as unmaintained, remove redundant HvCore/Composites docs
- support for SequenceAppender.
- Hierarchical HMM: part 5
- Use emoji-only in String/Display for all types; Chunk omits id when redundant
- misc.
- update doc for PARITY.md.
- Fix biweekly release reminder: true biweekly on odd-week Mondays
- Python: Seed128 preserves Domain/Pod metadata; add Seed128.random(so); update parity.md
- GlobalEnv enums: restore UNKNOWN=0 placeholders so defaults are non-zero
- Python: global_env() returns proto GlobalEnv message directly
## v3.8.0 (2026-04-06)

- Clean up obsolete build tooling: remove govvv, proto plugins, ruff.sh
- Update CLAUDE.md: mark lbd as unmaintained, remove redundant HvCore/Composites docs
- support for SequenceAppender.
- Hierarchical HMM: part 5
- Use emoji-only in String/Display for all types; Chunk omits id when redundant
- misc.
- update doc for PARITY.md.
- Fix biweekly release reminder: true biweekly on odd-week Mondays
- Python: Seed128 preserves Domain/Pod metadata; add Seed128.random(so); update parity.md
- GlobalEnv enums: restore UNKNOWN=0 placeholders so defaults are non-zero
- Python: global_env() returns proto GlobalEnv message directly
## v3.7.9 (2026-04-05)

- Python: global_env() returns formatted string respecting repr_format
- Consolidate env flags into GlobalEnv proto; single global_env() accessor
## v3.7.8 (2026-04-04)

- Python: Chunk repr/str shows "(id)" when code equals id; cleanup
- Python: accept Domain/int/str and Pod/int/str everywhere; remove Seed128.from_dp
- Python: Sparkle constructors accept Domain/int/str for all args
- Python: SparseOperation accepts flexible seed args; refactor shared helpers
- Update notebooks for Seed128/xoshiro256++ API changes
## v3.7.8 (2026-04-04)

- Python: Chunk repr/str shows "(id)" when code equals id; cleanup
- Python: accept Domain/int/str and Pod/int/str everywhere; remove Seed128.from_dp
- Python: Sparkle constructors accept Domain/int/str for all args
- Python: SparseOperation accepts flexible seed args; refactor shared helpers
- Update notebooks for Seed128/xoshiro256++ API changes
## v3.7.7 (2026-04-03)

- Python: Seed128 constructor accepts Domain/int/str for each arg
## v3.7.6 (2026-04-03)

- Python: improve Chunk __repr__ and __str__
- Go: add Set.Unmasked() and Sequence.Unmasked()
- Expose read-only env flag accessors in Go, Rust, and Python
- tweak.
- Add Notebook Sync CI; remove notebook sync from Rust Wheels
- Python: add Seed128.from_dp(domain, pod) constructor
- Use canonical lowercase xoshiro256++ in all comments and docs
- Rust: fix env.rs doc table to match Go (xoshiro++ not xoshiro)
## v3.7.5 (2026-04-03)

- Switch default RNG to xoshiro256++ with PCG as classic fallback
- Python: add SparseSegmented-specific methods back to PySparseSegmented
## v3.7.4 (2026-04-03)

- Go: stop embedding SparseSegmented in core; prevent method promotion leak
- Python: remove leaked SparseSegmented methods from HyperBinary types; add bind_direct
## v3.7.3 (2026-04-03)

- tweaks to make Python API match Go/Rust.
