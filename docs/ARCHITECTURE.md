# Fence Validation Architecture

This document explains how `tools/validate_fences.py` traverses Markdown inputs and surfaces
fence issues for local contributors. The validator is designed for lightweight, local-only
checks and integrates with existing tooling through a backwards-compatible API.

## Component overview

- **Target discovery (`iter_files`)** walks the requested roots while skipping generated
  or noisy locations listed in `SKIP_DIRS` and `SKIP_FILES`.
- **Line preparation (`_prepare_line`)** strips diff prefixes and indentation so scanners
  only evaluate the fence-relevant characters.
- **Fence analysis (`_scan_file`)** maintains `FenceState` metadata to validate open/close
  symmetry, info strings, and nested fence runs.
- **Public entry points**
  - `validate_file` offers a Python API for existing tests and scripts.
  - `main` provides the CLI used by local hooks and developer workflows.

```mermaid
flowchart TD
    A[CLI or caller] -->|argv / path list| B[_parse_args + _gather_targets]
    B --> C{Targets?}
    C -- none --> D[Emit "[fence-check] No matching files"]
    C -- files --> E[iter_files]
    E --> F[_scan_file]
    F -->|errors| G[[STDOUT error lines]]
    F -->|warnings| H[[STDOUT warning lines]]
    F -->|ok state| I[["[fence-check] OK"]]
```

## Running the validator locally

The validator is Python-only and depends on the standard library. Use the
shared development requirements for linting and formatting when needed.

```bash
python -m pip install -r requirements-dev.txt
pytest -q tests/test_validate_fences.py
```

## Quick reference

- **Why**: codifies fence discipline expectations for Markdown patches.
- **Risk**: limited to file-scoped parsing with deterministic checks.
- **Rollback**: delete `docs/ARCHITECTURE.md` and related tests if no longer required.
- **Tests/docs updates**: run the pytest command above and ensure docs build via MkDocs if applicable.
