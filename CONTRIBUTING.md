# Contributing

Thanks for your interest in **hv** / [`kongming-rs-hv`](https://pypi.org/project/kongming-rs-hv/)!

## What this repository is

This is the public home for the `kongming-rs-hv` Python package — its
[documentation](https://yangzh.github.io/hv/), runnable [examples](examples/),
and [notebooks](notebook/). The examples, docs, and notebooks here are
MIT-licensed. The underlying engine shipped on PyPI as `kongming-rs-hv` is
proprietary and is **not** developed in this repository.

Some content (the notebooks and the `pylisp` reference implementation) is
generated and synced from an upstream source, so a direct edit here may be
overwritten by the next release sync. For changes to that content, please
open an issue first so the fix can land at the source.

## How to contribute

- **Questions & ideas** → [GitHub Discussions](https://github.com/yangzh/hv/discussions).
- **Bug reports** → [Issues](https://github.com/yangzh/hv/issues) (please use the templates).
- **Docs & example fixes** → pull requests welcome. Keep examples runnable
  against the published wheel and lint-clean:

```bash
pip install kongming-rs-hv     # or: pip install -r requirements.txt
pip install pre-commit && pre-commit install   # ruff lint + format on commit
```

## Guidelines for examples & docs

- Examples import the public surface: `from kongming import hv`.
- Each example carries a module docstring (what it shows, how to run) and a
  `See docs:` link to its page on the site.
- Run `ruff check .` and `ruff format .` before committing.

By contributing, you agree that your contributions to the MIT-licensed content
in this repository are provided under the [MIT License](LICENSE).
