# Task Agent Routing

**Status:** Implemented initial routing helper via `chronicle route-task`

## Decision rules

Use `task` when the command is deterministic and success output can be compressed:

- `pytest`
- `nox`
- `ruff`
- `mypy`
- `pre-commit`
- dependency installs
- `python scripts/ci/auto_fix_common_issues.py`

Use `bash` when the command is exploratory and raw output is the work product:

- `rg`
- `grep`
- `find`
- shell inspection pipelines

Use `general-purpose` when the workflow is multi-step or ambiguous and needs reasoning.

## CLI examples

```bash
python -m codex.cli chronicle route-task "pytest -q tests/cli" --json
python -m codex.cli chronicle route-task "rg chronicle src tests"
python -m codex.cli chronicle route-task "prepare and validate a release candidate" --category general
```

## Goal

Shift deterministic, high-volume CLI work off raw bash and onto the task agent to reduce context noise and preserve token budget for analysis.
