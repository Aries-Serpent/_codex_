# Cleanup Validation Infrastructure

## Purpose

This document describes the repository-local validation infrastructure used before cleanup or refactoring work. It provides a repeatable way to inspect the worktree, validate Python changes, and detect repository integrity regressions without mutating coverage, quarantine, or execution baselines.

## Validation Layers

1. **Worktree inspection**: verify the current branch, head, and dirty files before modifying source.
2. **Static validation**: compile changed Python modules and run the configured format and lint tools.
3. **Focused tests**: run only the exact test nodes or owning modules affected by a patch.
4. **Artifact preservation**: leave session evidence, readiness records, and protected JSONL files unchanged.
5. **Handoff**: report changed files, exact validation nodes, remaining clusters, and blockers.

## Critical Files

The cleanup validation suite expects the following repository files:

- `pytest.ini`
- `mypy.ini`
- `pyproject.toml`
- `requirements.txt`
- `.editorconfig`
- `.pre-commit-config.yaml`
- `tests/cleanup_validation/test_cleanup_validation.py`
- `scripts/validate_cleanup.sh`
- `scripts/pre_cleanup_validation.sh`
- `scripts/post_cleanup_validation.sh`
- `docs/cleanup_validation_guide.md`
- `CLEANUP_VALIDATION_INFRASTRUCTURE.md`

The corresponding test modules and scripts must remain readable and executable where declared. Documentation is not a substitute for tests or static checks.

## Python Validation

Use the repository-supported virtual environment for focused Python work:

```bash
.venv/bin/python -m compileall -q <changed-python-files>
.venv/bin/black --check <changed-python-files>
.venv/bin/isort --check-only <changed-python-files>
.venv/bin/ruff check <changed-python-files>
.venv/bin/python -m pytest <exact-node> -q --tb=short
```

Run the narrow owning module first. Expand validation only after the exact node is understood or fixed. Do not use broad test discovery to conceal collection or environment failures.

## Cleanup Safety

Before cleanup, record the protected worktree state and compare it after validation. Preserve existing user modifications, especially `.codex/aftermath/pda_iterations.jsonl` and `.codex/evidence/zendesk_fields.jsonl`.

Do not reset or discard dirty work, alter coverage baselines, change quarantine baselines, commit, push, dispatch workflows, or mutate pull requests unless the separate authorized operation explicitly permits it.

## Failure Reporting

A handoff should separate:

- source defects fixed locally;
- test-fixture defects corrected locally;
- dependency or real-runtime blockers;
- pre-existing baseline failures; and
- checks that were unavailable in the local environment.

Each source or test result should include the exact node, result, and owning file. This keeps cleanup work scoped and reproducible.
