# CONTRIBUTING Addendum — Decision Gate & Local Quality Checks

This addendum introduces a lightweight approval gate and local-only checks for message/patch proposals.

## 1) Intent Validation & Plan of Action (Approval Gate)
- Before implementing a change, paste the **Intent Validation & Plan of Action** prompt in your issue/PR description, fill its context, and request approval.
- Template location: `docs/templates/intent_validation_gate.md`
- Record the decision: use the ADR format in `docs/decision_records/` (see examples).

## 2) Local-Only Quality Gates
These gates are **local** and do not enable or require GitHub Actions.

**Fence integrity**
```bash
python tools/validate_fences.py
```text

**Message/summary evaluator**
```bash
python tools/codex_evaluator.py \
  --rules manifests/codex_eval_rules.v3.json \
  --input samples/assistant_message_summary.sample.json
```text

**One-shot wrapper**
```bash
./scripts/run_local_gates.sh
```text

## 3) Pre-commit Integration
Hooks are defined in `.pre-commit-config.yaml`:
- `codex-validate-fences` runs at `stages: [commit]`
- `codex-eval` is manual to avoid friction (`stages: [manual]`)

Install:
```bash
pre-commit install
pre-commit run --all-files
```text

## 4) Where to Start
- Read: `docs/templates/intent_validation_gate.md`
- Operate: `docs/ops/local_gates.md`
- Rationale: `docs/decision_records/ADR-intent-approval-gate.md` and `docs/decision_records/ADR-codex-evaluator-v3.md`

## 5) Repository Policy Notes
- **Do not** add or activate GitHub Actions as part of these gates.
- Keep changes small, reviewable, and reversible (document rollback in ADRs).
