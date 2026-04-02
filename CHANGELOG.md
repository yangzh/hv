# Changelog

All notable changes to `kongming-rs-hv` are documented here.
Only the latest 10 releases are shown.

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
## v3.5.0 (2026-03-24)

- Refactor pylisp: remove LispSubstrate, add store_chunk/first_picked_chunk APIs
- add more references.
- Add README.md to pylisp package (syncs to hv repo)
- Changelog automation: add release dates, keep latest 10 entries
- Auto-update hv CHANGELOG.md on release
- Include source commit messages in pylisp sync commits
- Clean up pylisp: remove ~ prefix, use DomainPrefix.LISP, fix import order, expose HvError properly, remove inline type hints
- Add CI workflow to sync pylisp to public hv repo
- Add DomainPrefix.LISP (λ) to proto and Rust hash labels
- Add pure-Python LISP interpreter (kongming.pylisp)
## v3.4.0 (2026-03-23)

- version api protos as `kongming.api.v1` (Kubernetes-style path versioning)
- upgrade prost 0.13→0.14, tonic 0.12→0.14; unpin buf plugins
- remove protobuf `<6.0` upper bound; rely on `_pb2.py` plugin pin for Colab compat
- add `DomainPrefix.LISP` (λ) for LISP interpreter domains
- add `write_chunk(hv, code=...)` — separate id and code per chunk
- expose `HvError` and `REASON_NOT_FOUND` from `kongming_rs`
- add pure-Python LISP interpreter (`kongming_rs.pylisp`)
- add spaCy NLP engine support alongside stanza
- add `KONGMING_REPR_FORMAT` env flag (YAML/PROTO) for `Repr()` / `__repr__`
- add `KONGMING_LEARNER_SAMPLING` env flag (classic/fisher_yates)
- expose `UniformSet`, `WeightedSet`, and Frame analysis functions to Python
- change Sequence emoji from ⛓️ to 📿
- remove `IsValid` / `is_valid` from `SparseSegmented` and `Chunk`
- simplify notebook install cells (try/except + `%pip`)
- add weekly GitHub release cleanup (keep latest 10)

## v3.3.0 (2026-03-17)

- expose InMemory and Fjall storage backends to Python
- expose NNS, attractors, and all ChunkSelector/ChunkProducer equivalents to Python
- add `Unmasked()` to Set and Sequence composites
- add Fjall persistent storage + `export()` to Python
- refactor notebooks to use `from kongming_rs import api, hv, memory` style

