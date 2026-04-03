# Changelog

All notable changes to `kongming-rs-hv` are documented here.
Only the latest 10 releases are shown.

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
## v3.6.3 (2026-03-25)

- Fix: ship kongming.api.annotations_pb2 and top-level buf in wheel
## v3.6.2 (2026-03-25)

- Fix: include top-level buf package in wheel; bump to 3.6.2
- Fix changelog filter: only exclude pure version bump commits
- Opt into Node.js 24 for all workflows; remove unused deep_clone
## v3.6.1 (2026-03-25)

- Fix: include pylisp module in wheel (resolve symlink before build)
- Opt into Node.js 24 for all GitHub Actions workflows
- Remove unused `HvCore::deep_clone()` method

## v3.6.0 (2026-03-25)

- Add notebook sync to release workflow; add lisp.ipynb with dual interpreter demo
- Make Fisher-Yates default sampling; remove proto constant re-exports from hv
- misc.
- Remove proto Session from Memory/Substrate interfaces; use Go context
- Remove dead Session types from ChunkSelector/ChunkProducer protos
- Change UniformSet/WeightedSet emojis; remove BundleSeed from proto
- Change UniformSet emoji to ⚖️, WeightedSet to 🎚️
- Change Parcel emoji from 🧺 to 🎁; use literal emoji in profile.rs
- Cleanup pylisp: use register_symbol, inline init, cosmetic fixes
- Combine pylisp sync and changelog into release workflow
