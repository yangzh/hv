# Workflow

## Review and commit

No GitHub PRs. Review happens in the local workspace.

1. **Make the change, then stop.** Run whatever gates apply (build the docs with
   `mdbook build docs`, run the linters), then show the diff and wait.
2. **Commit only on explicit approval** of that specific diff. An instruction to
   make a change ("add X", "fix Y") approves the change, not the commit.
   Approval must name or clearly cover the commit itself.
3. **Don't branch for review.** Leave edits uncommitted on `main`; a feature
   branch just adds cleanup.
4. **Push after an approved commit** — this repo is the public mirror, so `main`
   is meant to be pushed. Ask before anything that publishes beyond it
   (release tags, workflow dispatches that deploy the docs site).

## Docs site

`docs/` is an mdBook. The site deploys **only on a `v*` tag**, deliberately, so
published docs stay in lockstep with PyPI — see the comment in
`.github/workflows/docs.yml`. Markdown on `main` is expected to run ahead of
the deployed site.

To publish `main` out of band, `gh workflow run docs.yml --ref main`. That
publishes everything merged since the last tag, not just the current change, so
check `git log <last-tag>..main -- docs/` first.

Building locally needs the CI preprocessors (`mdbook-katex`, `mdbook-tabs`,
`mdbook-last-changed`). Without them, mark the three `[preprocessor.*]` blocks
`optional = true` in a scratch copy of `book.toml` and restore it afterwards —
don't commit that edit.
