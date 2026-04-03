# Changelog

All notable changes to `kongming-rs-hv` are documented here.
Only the latest 10 releases are shown.

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
## v3.6.4 (2026-04-02)

- Fix release: sed both pyproject.toml and Cargo.toml for version sync
- CI: auto-sync Cargo.toml version from release tag
- Expose __version__ on kongming_rs Python module
- Add InMemorySubstrate convenience function for badger
- Re-export Model constants into hv Python module
- Cleanup: remove SparseOperation.WidthBits, scope maskLower16Bit locally
- Remove Exp type; use plain int32/i32 for exponent across Go/Rust/Python
- Rename SparsityOffset → SparsityBits, WidthOffset → WidthBits across Go/Rust/Python
- Hierarchical HMM modelling: part 4
- hierarchical HMM modelling: Part 3.
- Rename FirstFromEach to Joiner across Go, Rust, proto, and Python
- Remove unused Unmasked() from Set and Sequence
- misc.
- Fix cleanup-releases: deduplicate tags and tolerate deletion failures
- misc.
- Fix ResetSequence: use D0() for STEP sparkle, not sequence domain
- Simplify Set/Sequence constructors; rename ResetSequence
- Rename NewNaturalSequence → NewSequenceWithStart; use UniformSet in compose
- Remove PORTING.md; superseded by src/kongming/memory/parity.md
- Port parse_tree.go to Rust (kongming::nlp::parse_tree)
- Fjall: read-your-own-writes for get/key_exists before commit
- Replace ViewSession.expiration with ttl_secs across Go/Rust/Python
- Upgrade Arrow Go: apache/arrow/go/v18 → apache/arrow-go/v18 v18.5.2
- Re-add index_ttl_secs; wire through to AssociativeIndex.TTL()
- Remove expiration from AssociativeIndex.Impress; compute from TTL()
- Remove deprecated Redis backend and rueidis dependency
- Fix SparseSegmented emoji: 🫀 → 🍡 to match proto label
- Update parity.md: fix AssociativeIndex methods, remove deprecated backends
- Remove index_ttl_secs from proto and all backends
- Fjall TTL envelope; remove index_ttl_secs from views/substrates; strict tests
- Fix expiration unit: Cell.Expiration is microseconds, not seconds
- Upgrade fjall v2 → v3.1, preparing for TTL support
- Add ViewSession proto; pass to NewView/NewMutableView for view-level expiration
- Upgrade GitHub Actions to Node.js 24 native versions
- Add PyChunk class; all memory reads return Chunk with id/code/note/extra
- Always upgrade kongming-rs-hv in notebook install cells
## v3.6.4 (2026-04-02)

- CI: auto-sync Cargo.toml version from release tag
- Expose __version__ on kongming_rs Python module
- Add InMemorySubstrate convenience function for badger
- Re-export Model constants into hv Python module
- Cleanup: remove SparseOperation.WidthBits, scope maskLower16Bit locally
- Remove Exp type; use plain int32/i32 for exponent across Go/Rust/Python
- Rename SparsityOffset → SparsityBits, WidthOffset → WidthBits across Go/Rust/Python
- Hierarchical HMM modelling: part 4
- hierarchical HMM modelling: Part 3.
- Rename FirstFromEach to Joiner across Go, Rust, proto, and Python
- Remove unused Unmasked() from Set and Sequence
- misc.
- Fix cleanup-releases: deduplicate tags and tolerate deletion failures
- misc.
- Fix ResetSequence: use D0() for STEP sparkle, not sequence domain
- Simplify Set/Sequence constructors; rename ResetSequence
- Rename NewNaturalSequence → NewSequenceWithStart; use UniformSet in compose
- Remove PORTING.md; superseded by src/kongming/memory/parity.md
- Port parse_tree.go to Rust (kongming::nlp::parse_tree)
- Fjall: read-your-own-writes for get/key_exists before commit
- Replace ViewSession.expiration with ttl_secs across Go/Rust/Python
- Upgrade Arrow Go: apache/arrow/go/v18 → apache/arrow-go/v18 v18.5.2
- Re-add index_ttl_secs; wire through to AssociativeIndex.TTL()
- Remove expiration from AssociativeIndex.Impress; compute from TTL()
- Remove deprecated Redis backend and rueidis dependency
- Fix SparseSegmented emoji: 🫀 → 🍡 to match proto label
- Update parity.md: fix AssociativeIndex methods, remove deprecated backends
- Remove index_ttl_secs from proto and all backends
- Fjall TTL envelope; remove index_ttl_secs from views/substrates; strict tests
- Fix expiration unit: Cell.Expiration is microseconds, not seconds
- Upgrade fjall v2 → v3.1, preparing for TTL support
- Add ViewSession proto; pass to NewView/NewMutableView for view-level expiration
- Upgrade GitHub Actions to Node.js 24 native versions
- Add PyChunk class; all memory reads return Chunk with id/code/note/extra
- Always upgrade kongming-rs-hv in notebook install cells
## v3.6.4 (2026-04-02)

- Expose __version__ on kongming_rs Python module
- Add InMemorySubstrate convenience function for badger
- Re-export Model constants into hv Python module
- Cleanup: remove SparseOperation.WidthBits, scope maskLower16Bit locally
- Remove Exp type; use plain int32/i32 for exponent across Go/Rust/Python
- Rename SparsityOffset → SparsityBits, WidthOffset → WidthBits across Go/Rust/Python
- Hierarchical HMM modelling: part 4
- hierarchical HMM modelling: Part 3.
- Rename FirstFromEach to Joiner across Go, Rust, proto, and Python
- Remove unused Unmasked() from Set and Sequence
- misc.
- Fix cleanup-releases: deduplicate tags and tolerate deletion failures
- misc.
- Fix ResetSequence: use D0() for STEP sparkle, not sequence domain
- Simplify Set/Sequence constructors; rename ResetSequence
- Rename NewNaturalSequence → NewSequenceWithStart; use UniformSet in compose
- Remove PORTING.md; superseded by src/kongming/memory/parity.md
- Port parse_tree.go to Rust (kongming::nlp::parse_tree)
- Fjall: read-your-own-writes for get/key_exists before commit
- Replace ViewSession.expiration with ttl_secs across Go/Rust/Python
- Upgrade Arrow Go: apache/arrow/go/v18 → apache/arrow-go/v18 v18.5.2
- Re-add index_ttl_secs; wire through to AssociativeIndex.TTL()
- Remove expiration from AssociativeIndex.Impress; compute from TTL()
- Remove deprecated Redis backend and rueidis dependency
- Fix SparseSegmented emoji: 🫀 → 🍡 to match proto label
- Update parity.md: fix AssociativeIndex methods, remove deprecated backends
- Remove index_ttl_secs from proto and all backends
- Fjall TTL envelope; remove index_ttl_secs from views/substrates; strict tests
- Fix expiration unit: Cell.Expiration is microseconds, not seconds
- Upgrade fjall v2 → v3.1, preparing for TTL support
- Add ViewSession proto; pass to NewView/NewMutableView for view-level expiration
- Upgrade GitHub Actions to Node.js 24 native versions
- Add PyChunk class; all memory reads return Chunk with id/code/note/extra
- Always upgrade kongming-rs-hv in notebook install cells
