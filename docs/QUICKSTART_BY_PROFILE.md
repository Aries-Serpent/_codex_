# Quick start by dependency profile

The package always installs the required dependencies in `project.dependencies`.
The `core`, `runtime`, and `full` extras add task-specific dependencies defined in
`pyproject.toml`; they are not separate distributions.

## Choose a profile

| Profile | Package semantics | Expected directories | Typical use |
|---|---|---|---|
| `core` | Base package plus configuration, validation, CLI, and parsing extras | Configuration, CLI, and parser modules under `src/`; `configs/` | CLI use, configuration, code analysis, offline-oriented work |
| `runtime` | Base package plus data/ML, RAG, serving, telemetry, and database extras | `src/codex_ml/`, `src/rag/`, `src/mcp/`, `services/` | Inference, retrieval, embeddings, and API services |
| `full` | Core/runtime capabilities plus test, quality, training, evaluation, tracking, and plugin tools | All `src/` packages, `tests/`, `configs/`, `notebooks/` | Repository development, training, evaluation, and experiments |

`core` is lightweight relative to the ML profiles, but it still installs the package's
required base dependencies. `runtime` contains inference and serving libraries.
`full` is the contributor profile because it includes pytest, nox, Ruff, Black, isort,
mypy, and pre-commit.

## Common environment setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

On Windows, activate with `.venv\Scripts\activate`.

## Contributor setup

```bash
python -m pip install -e '.[full]'
pre-commit install
codex --help
```

Start with [contributor onboarding](onboarding/CONTRIBUTOR.md). Use focused tests while
developing, then run the repository's documented pre-commit and nox gates.

## ML work setup

For inference, serving, or RAG work:

```bash
python -m pip install -e '.[runtime]'
```

For training, evaluation, experiment tracking, or ML development:

```bash
python -m pip install -e '.[full]'
```

Start with [ML engineer onboarding](onboarding/ML_ENGINEER.md). CI-facing tests must be
offline-safe; use local fixtures or mocks rather than downloading models or datasets.

## CI and workflow maintenance setup

```bash
python -m pip install -e '.[full]'
pre-commit install
```

Start with [GitHub Actions maintainer onboarding](onboarding/GITHUB_ACTIONS_MAINTAINER.md)
and the [workflow map](WORKFLOW_MAP.md). Workflow work commonly uses the quality tools
from `full` even when it does not exercise ML features.

## Verify the selected environment

```bash
python -c "import codex_ml; print('codex_ml import OK')"
python -m pip show codex-ml
```

The package metadata in `pyproject.toml` is authoritative when another guide disagrees
with profile contents or version requirements.
