# Contributor

## Where to start

Read the [repository map](../REPOSITORY_MAP.md), then install the full development
profile using the [profile quick start](../QUICKSTART_BY_PROFILE.md).

## Where the code lives

- `src/`: canonical Python implementation
- `tests/`: pytest suites
- `configs/`: primary Hydra configuration
- `scripts/`: validation and maintenance commands
- `docs/`: contributor guidance and architecture

Root-level Python directories are generally compatibility or bridge surfaces, but
`pyproject.toml` explicitly maps some installed packages—including `training/`,
`tokenization/`, and `codex_utils/`—to root paths. Follow those mappings when changing
an existing package. Put new general implementation under `src/` and import it by
installed package name, not through `src.*`.

## What this role cares about

Small changes, preserved compatibility, focused tests, and documentation that matches
the package manifest and source.

## Key technologies

Python 3.12+, pytest, nox, Ruff, Black, isort, mypy, pre-commit, Hydra, and
OmegaConf.

## Typical workflow

1. Find the owning package under `src/` and its tests under `tests/`.
2. Install `-e '.[full]'`.
3. Make a focused change and add or update tests.
4. Run `pre-commit run --files <changed-files>` and the relevant nox or pytest target.
5. Update directly affected documentation and the changelog.

## Common gotchas

- Do not add the repository root to `PYTHONPATH`; `pytest.ini` establishes the `src`
  boundary.
- Optional features need the matching dependency profile.
- Dated reports describe historical evidence; they are not current implementation
  contracts.
- Workflow changes have additional repository policy requirements.
