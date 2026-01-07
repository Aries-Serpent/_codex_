# ADR: Codex Evaluator v3 (Local-Only)

## Status
Accepted — 2024-10-26

## Context
We need a deterministic, local scoring layer to assess assistant messages and summaries prior to execution. This replaces ad-hoc judgments with a transparent rubric and hard-fail safety checks while keeping contributor velocity (no CI requirement).

## Decision
- Add `manifests/codex_eval_rules.v3.json` defining:
  - Dimensions: freshness discipline, evidence rigor, tool-use appropriateness, policy/refusal quality, structural fidelity, concision ratio, continuity/constraints, testability strength, and risk posture.
  - Hard-fail cues: fence broken (checked by a separate tool), CI activation cues, unsafe compliance.
  - Topic tool mandates (browse for volatile topics; PDF screenshot; image queries; file_search for uploads).
  - Env guard regex for pytest: `^PYTEST_DISABLE_PLUGIN_AUTOLOAD=1\\s+pytest\\b`.
  - Forbidden cues: `.github/workflows/`, enabling Actions, CI-only steps.
- Add `tools/codex_evaluator.py` (local binary) to read rules and a message/summary and return pass/fail + score deltas.
- Keep checks **local-only**; do not create or activate GitHub Actions.

## Consequences
**Positive**
- Reproducible, auditable decisions on message selection.
- Early detection of dangerous actions (e.g., CI activation) and structural issues.

**Trade-offs**
- Slight overhead to run evaluator and fence checks locally.

**Negative / Risks**
- Overly strict settings Phase 5 cause false positives.

## Mitigations
- Provide clear documentation (see `docs/ops/local_gates.md`) and allow manual execution of evaluator hook.
- Keep rubric weights centralized in the JSON rules; changes tracked via PR + CHANGELOG.

## Rollback
- Revert `manifests/codex_eval_rules.v3.json`, `tools/codex_evaluator.py`, `.pre-commit-config.yaml` entries, and related docs in a single revert PR.

## References
- Template & usage: `docs/templates/intent_validation_gate.md`
- Ops docs: `docs/ops/local_gates.md`
- Fence integrity: `tools/validate_fences.py`
