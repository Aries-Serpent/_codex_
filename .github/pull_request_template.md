## Intent Validation (2–3 sentences)
<!-- Restate the intent, primary goal, constraints/scope, success + out-of-scope. -->

## Plan of Action (phased)
<!-- For each phase: objective, concrete steps, decision gate, effort/deps. -->

### Assumptions (✓ ? ⚠️)
- ✓
- ?
- ⚠️

### Open Questions (prioritized)
1.
2.
3.

### Risks and Mitigations
| Risk | Severity | Mitigation |
| --- | --- | --- |
|  |  |  |

### Deliverables
- [ ] 

### Acceptance Criteria
- [ ] 

### Rollback / Fallback
<!-- Brief steps to revert/recover. -->

---

## Local Gates (must run locally)
- [ ] Fences: `python tools/validate_fences.py` → **PASS**
- [ ] Evaluator: `python tools/codex_evaluator.py --rules manifests/codex_eval_rules.v3.json --input samples/assistant_message_summary.sample.json` → **PASS**

References:
- Template: `docs/templates/intent_validation_gate.md`
- Checklist: `docs/checklists/approval_gate_checklist.md`
- Ops: `docs/ops/local_gates.md`
- ADRs: `docs/decision_records/ADR-intent-approval-gate.md`, `docs/decision_records/ADR-codex-evaluator-v3.md`
