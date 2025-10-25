---
title: "Planning Template — Intent Validation"
status: "draft"
template_version: "v1.0.0"
owner: "Docs & Enablement"
last_reviewed: 2025-10-20
tags:
  - planning
  - discovery
  - risk-management
---

# Planning Template — Intent Validation

> {{intent_summary}}

Adopt this template before committing to major migrations, CLI hardening projects, or other operational shifts. It ensures stakeholders align on scope, risks, and validation artifacts.

## Snapshot metadata

- **Initiative name:** `{{initiative_name}}`
- **Sponsor / decision maker:** `{{sponsor_name}}`
- **Implementation owner:** `{{implementation_owner}}`
- **Target release / milestone:** `{{target_release}}`
- **Success metrics:** `{{success_metrics}}`

## Related templates

- [Migration — Python File Relocation](./Migration_PythonFileRelocation.md)
- [Migration — CLI Hardening](./Migration_CLIHardening.md)
- [Manual Verification Checklist](./verification.md)

## Stakeholder checklist

- {{stakeholder_alignment}}
- {{risk_acceptance}}
- {{comms_alignment}}
- {{open_questions}}

## 🔁 Execution phases

### Phase 0 — Intake

1. Capture problem statement, desired outcomes, and non-goals in `{{intake_doc}}`.
2. Identify required capabilities, impacted systems, and dependencies.
3. Confirm funding/time allocation and align on decision deadline `{{decision_deadline}}`.

### Phase 1 — Discovery

1. Gather existing documentation, metrics, and incident history relevant to the initiative.
2. Conduct stakeholder interviews or async questionnaires using `{{discovery_form}}`.
3. Draft preliminary risk register entries in `{{risk_register}}`.

### Phase 2 — Validation Design

1. Define validation experiments or proofs-of-concept, including success/fail criteria.
2. Enumerate required environments, datasets, or feature flags.
3. Coordinate with release engineering to schedule dry runs or guardrails.

### Phase 3 — Review & Sign-off

1. Compile findings into `{{review_brief}}` with recommended go/no-go decision.
2. Present to decision makers, capturing approvals or required follow-ups in `{{signoff_log}}`.
3. If approved, transition into execution by instantiating the relevant migration template(s) and linking them here.

## Risk register snapshot

| Risk | Impact | Likelihood | Mitigation | Owner |
| --- | --- | --- | --- | --- |
| {{risk_1}} | {{risk_1_impact}} | {{risk_1_likelihood}} | {{risk_1_mitigation}} | {{risk_1_owner}} |
| {{risk_2}} | {{risk_2_impact}} | {{risk_2_likelihood}} | {{risk_2_mitigation}} | {{risk_2_owner}} |
| {{risk_3}} | {{risk_3_impact}} | {{risk_3_likelihood}} | {{risk_3_mitigation}} | {{risk_3_owner}} |

## Decision log

- `{{date_decision_1}}` — {{decision_1}}
- `{{date_decision_2}}` — {{decision_2}}
- `{{date_decision_3}}` — {{decision_3}}

## Evidence collection

- Store interview notes in `docs/planning/{{timestamp_token}}/`.
- Attach validation experiment outputs to `artifacts/intent_validation/{{timestamp_token}}/`.
- Publish a summary to `docs/status_updates/` referencing this planning cycle.
