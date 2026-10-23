# Contributing

Thanks for your interest in improving csv-names!

## Setup

```bash
git clone https://github.com/akuwarrior1/basic1.git
cd basic1
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Before opening a pull request

```bash
pytest --cov=csv_names
mypy
ruff check . && ruff format --check .
```

All three must pass; CI runs the same checks on Python 3.10–3.13 across Linux, macOS and Windows.

- Add tests for any behaviour change.
- Keep the public API typed and documented with docstrings.
- Add an entry under **Unreleased** in `CHANGELOG.md`.
- The library must stay free of runtime dependencies.

## Releasing (maintainers)

1. Bump `__version__` in `src/csv_names/__init__.py`.
2. Move the **Unreleased** changelog entries under a new version heading.
3. Commit, then tag and push: `git tag v0.2.0 && git push origin main --tags`.
4. Create a GitHub Release from the tag. The `release` workflow builds the package and publishes it to PyPI.
