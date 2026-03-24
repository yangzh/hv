# Changelog

All notable changes to `kongming-rs-hv` are documented here.
Only the latest 10 releases are shown.

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

## v3.2.4 (2026-03-17)

- fix Prewired enum numbering (NIL, MIDDLE, STEP)
- add DomainPrefix support (INTERNAL, USER, NLP)

## v3.2.3 (2026-03-17)

- unify InMemory and Fjall substrate backends via RwLock-based interior mutability
- fix `first.ipynb`: remove octopus marker references, update Octopus extraction example

## v3.2.2 (2026-03-16)

- add per-user namespace isolation for `LispEnv`
- add `namespace` parameter to Python `LispEnv(namespace="alice")`
- notebook uses random namespace per session

## v3.2.1 (2026-03-16)

- add VSA-based LISP interpreter (`kongming_rs.lisp.LispEnv`)
- add fjall-backed persistent storage for LISP environments
- add Jupyter notebook demo for VSA LISP interpreter
- add --model flag to LISP REPL, default to 10bit
- refactor LISP env: use prewired symbols
- simplify LISP internals: random cons pointers, cons-encoded DEFINE
