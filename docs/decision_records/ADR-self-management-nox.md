# ADR: Introduce `nox` sessions & dev requirements (local-only)

## Status
Accepted — 2024-10-26

## Context
Contributors need a one-command way to run local gates and tests without CI. We already provide scripts and pre-commit hooks; `nox` consolidates this into discoverable sessions while staying local-only.

## Decision
- Add `requirements-dev.txt` listing core local tools (`pre-commit`, `nox`, `pytest`, `jsonschema`).
- Add `noxfile.py` with sessions:
  - `gates`: fences → evaluator → (optional) schema checks → selection guard (non-fatal).
  - `tests`: pytest with `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`.
  - `precommit`: run all hooks locally.
- Document usage in `docs/ops/local_gates.md`.

## Consequences
**Positive**
- Single entry-point for local verification; faster onboarding and repeatability.
- No CI changes; minimal cognitive load.

**Trade-offs**
- Another tool in the toolbox; mitigated by keeping sessions small and documented.

## Risks & Mitigations
- **Tool drift**: Keep versions in `requirements-dev.txt`; revisit periodically.
- **Strictness surprises**: `selection_guard` remains non-fatal in the `gates` session (mirrors script).

## Rollback
- Remove `noxfile.py` and `requirements-dev.txt`, and update docs to remove references.

## Testing
- Add tests verifying `requirements-dev.txt` contents and `noxfile.py` session names & key commands by static inspection.
