# Changelog

All notable changes to `kongming-rs-hv` are documented here.
Only the latest 10 releases are shown.

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
## v3.7.2 (2026-04-03)

- Python composites take Seed128; add Seed128.High/Low accessors
## v3.7.1 (2026-04-03)

- Rename Seed128 constructors: new(high,low) for raw IDs, from_dp(d,p) for Domain+Pod
- Add Python API reference; update CLAUDE.md and pylisp README
## v3.7.0 (2026-04-03)

- Export DomainPrefix and Hint enums to Python; fix notebooks
- Simplify SparkleIdentity: remove Domain/Pod params, use defaults
- Rust/Python: Seed128 embeds Domain+Pod; composites take Seed128
- Rename NewSeed128 to take (Domain, Pod); remove FromDomainPod
- Refactor: Seed128 embeds Domain+Pod; composites take Seed128
- Revert ruff formatting on proto-generated _pb2.py files
- Exclude _pb2.py files from ruff format via extend-exclude
## v3.6.6 (2026-04-02)

- Add kongming as top-level Python import path
- Add Embedded aliases: hide badger/fjall implementation names
- Remove gopy: delete Go→Python bridge, old workflow, and build targets
- Remove unused SparseSegmented.Offsets() from Go
- Apply linter formatting: rustfmt, ruff, gofmt
- Add pre-commit hooks: ruff, gofmt, go vet, rustfmt, buf lint
## v3.6.5 (2026-04-02)

- Re-export __version__ from native module in __init__.py
