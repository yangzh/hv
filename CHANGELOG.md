# Changelog

All notable changes to `kongming-rs-hv` are documented here.
Only the latest 10 releases are shown.

## v3.8.9 (2026-04-09)

- Add CHANGELOG.md for release tracking
- Add SparseSegmented.from_offsets() constructor (Rust + Python)
- Update pylisp sync path: pylisp/ → examples/pylisp/
- Fix reverse attractors: use ID instead of Code for probe binding
- Reorder pre-commit hooks: Go → buf → ruff → rustfmt
- Rename WithChunk→WithChunks: accept multiple chunks; proto LITERAL→LITERALS
- Remove display_size from SVG rendering (Go/Rust/Python)
- Notebook: SVG viewer with zoom/pan controls, minimap, and reset
- Notebook sync: only trigger from master, not dev
- Notebook: update cell outputs for SVG visualization
## v3.8.9 (2026-04-09)

### API changes
- `SparseSegmented.from_offsets(model, offsets)` — new constructor from per-segment offsets
- `WithChunk()` renamed to `WithChunks()` — accepts multiple chunks
- Removed `display_size` parameter from `to_svg()` / `to_svg_overlap()` — client-side handles viewport

### Notebook
- SVG viewer with zoom/pan controls, minimap, and reset button


## v3.8.8 (2026-04-08)

- SVG: unique pattern IDs (random), show_svg helper with zoom/pan in notebook
## v3.8.7 (2026-04-08)

- Notebook: scrollable SVG containers; auto-mirror releases to hv repo
- SVG: add display_size parameter to Go/Rust/Python (0 = auto)
## v3.8.6 (2026-04-07)

- Notebook: add SVG visualization demo (single vector + overlap)
- SVG renderer: move Go to hv/, add Rust/Python, palette-based overlap coloring
- SVG renderer: replace svgo with raw fmt.Fprintf, fix square layout for all models
- Add Dependabot: weekly checks for Cargo, Go, pip (ruff), GitHub Actions
- Add PyPI project URLs: docs, repo, changelog, issues, discussions
- Update parity.md for hv/ and memory/ with 2-week progress
## v3.8.5 (2026-04-07)

- Revert InMemory to BTreeMap-backed; add read-time TTL filtering
## v3.8.4 (2026-04-07)

- Warn when gc_interval_secs is 0 (background compaction disabled)
- Go: move gc_interval_secs default from library (600) to caller level (0)
- InMemory uses fjall-on-tmpdir; add BTreeMap backend for benchmarking
- Add TTL compaction filter and background GC for fjall storage
- Use meaningful parameter names in Python-facing constructors and static methods
## v3.8.3 (2026-04-06)

- Improve Python docstrings: add constructors, flexible types, remove redundant create()
## v3.8.2 (2026-04-06)

- Add seed128() and hint() to all Python HyperBinary types via macro
- Rename Domain.with_prefix→from_prefix_and_name; remove Seed128.create
- Producers accept flexible domain/pod types; add extra protobuf payload support
## v3.8.1 (2026-04-06)

- Rename first_picked_chunk→first_picked, terminal→new_terminal in Python bindings
- YAML: render Prewired enum as string name instead of numeric value
