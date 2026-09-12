# Contributing to `tllib`

## Prerequisites

- Python 3.10 or newer
- [`uv`](https://docs.astral.sh/uv/)

The repository uses the `dev` dependency group from `pyproject.toml`. From the
`tllib` directory, create the environment and install all development tools:

```powershell
uv sync --dev
```

When the lockfile is present, CI and reproducible local runs use:

```powershell
uv sync --locked --dev
```

## Checks

Run the formatter/linter, type checker, and tests through the project
environment:

```powershell
uv run ruff format --check .
uv run ruff check .
uv run mypy
uv run pytest
```

Pytest enables branch coverage and fails below the configured 80% threshold.
To inspect uncovered lines locally:

```powershell
uv run pytest --cov-report=html
```

The generated report is written to `htmlcov/` and is ignored by Git.

## Specification lock

`specs.lock.json` records the exact `tllib-specs` repository, Git SHA, model
version, catalogue fingerprint, and lock date used by the runtime. Verify it
from the `tllib` directory with:

```powershell
uv run python -m tllib.specs verify
```

To update the lock, first update the checked-out `tllib-specs` repository and
run its validators. Recompute the catalogue SHA-256, update the SHA, version,
fingerprint, and date in `specs.lock.json`, then run:

```powershell
uv run python -m tllib.specs verify
uv run ruff check .
uv run mypy
uv run pytest
```

A human reviewer must compare the new upstream commit and catalogue diff,
confirm that the version and fingerprint describe the intended specification
release, and approve the lock change. Do not update the lock only to silence a
verification failure; investigate the divergence first.

## Pull requests

Keep changes focused, explain the affected domain or contract, and include the
validation commands that were run. Architecture changes should update the
corresponding decision record and include both nominal and failure tests.