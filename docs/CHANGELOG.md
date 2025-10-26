# Changelog

All notable changes to this project will be documented in this file.

## 2025-10-26

### Added
- Introduced **Intent Validation & Plan of Action Approval Gate** template (`docs/templates/intent_validation_gate.md`).
- Added **local-only quality gates**:
  - Fence integrity validator (`tools/validate_fences.py`) with pre-commit hook.
  - Codex evaluator and rubric (`tools/codex_evaluator.py`, `manifests/codex_eval_rules.v3.json`) with manual pre-commit hook.
- Added **ops docs** for running local gates (`docs/ops/local_gates.md`).
- Added **CLI wrapper** (`tools/cli/codex_tools.py`) and **test** (`tests/evaluators/test_codex_evaluator.py`).
- Added **ADR** documenting rationale and rollback (`docs/decision_records/ADR-intent-approval-gate.md`).

### Notes
- No GitHub Actions were created or modified.
- Hooks are **local-only** and optional to run in CI.

