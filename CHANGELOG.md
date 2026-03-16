# Changelog

All notable changes to `kongming-rs-hv` are documented here.

This file is updated before each release by collecting commit messages from the
[primary repo](https://github.com/yangzh/primary) since the previous `rel-v*` tag:

```bash
git log --oneline --reverse rel-vPREV..HEAD | sed 's/^[a-f0-9]* /- /'
```

The resulting list is prepended under a new version heading, committed to this
repo (`hv`), and pushed alongside the release.

---

## v3.2.1

- support for prepend/append sequences
- port prepend/append sequence support to Rust
- Learner.age: int32 -> uint32
- Learner multiple: int32 -> uint32 in proto and all languages
- add NewNaturalSequence to reset sequence start to 0, with tests
- add OnlyDomain ChunkSelector to filter by domain, in proto/Go/Rust
- adjust parameter order for Range and OnlyDomain
- remove marker for octopus objects
- remove LearningTentacleAttractor
- use hv.D0() to construct Octopus objects
- port Go changes to Rust: remove octopus marker, remove LearningTentacleAttractor, use D0() for octopus keys
- add InMemoryIndex so NearNeighborSearch works with in-memory substrates
- add kongming-lisp: VSA-based LISP interpreter using sparse binary hypervectors
- add REPL example, lambda/LABEL tests, and fix recursive evaluation
- add fjall backend support for LispEnv
- add PyO3 bindings for LISP interpreter
- add Jupyter notebook demo for VSA LISP interpreter
- bump version to 3.2.0 for VSA LISP interpreter release
- add --model flag to LISP REPL, default to 10bit
- refactor LISP env: use prewired symbols for T/F/NIL/LHS/RHS, ~ prefix for builtins, add NIL to prewired enum
- simplify LISP internals: random cons pointers, cons-encoded DEFINE, extract cons_parcel helper

## v3.1.17

- (previous release)
