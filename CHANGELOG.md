# Changelog

All notable changes to `kongming-rs-hv` are documented here.

## v3.2.2

- add per-user namespace isolation for `LispEnv` — multiple users sharing the same substrate won't interfere
- add `namespace` parameter to Python `LispEnv(namespace="alice")`
- notebook uses random namespace per session

## v3.2.1

- add VSA-based LISP interpreter (`kongming_rs.lisp.LispEnv`)
- add fjall-backed persistent storage for LISP environments
- add Jupyter notebook demo for VSA LISP interpreter
- add --model flag to LISP REPL, default to 10bit
- refactor LISP env: use prewired symbols, ~ prefix for builtins
- simplify LISP internals: random cons pointers, cons-encoded DEFINE

## v3.1.17

- (previous release)
