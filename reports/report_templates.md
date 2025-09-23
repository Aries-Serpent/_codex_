# Audit Report Template Library

> Update reference: Run {{RUN_NUMBER}} — {{DATE}}

Use these templates to refresh audit artefacts quickly during each run. Replace placeholders in double braces and prune sections that do not apply. Keep fenced code blocks language-tagged to satisfy `tools/validate_fences.py`.

## Repo Map (`reports/repo_map.md`)

```markdown
# Repo Map — Run {{RUN_NUMBER}} ({{DATE}})

## Scope
- Branch: {{BRANCH_NAME}}
- Snapshot commit: {{SHORT_SHA}}

## Top-Level Layout
| Path | Purpose | Notes |
| --- | --- | --- |
| {{PATH}} | {{PURPOSE}} | {{NOTES}} |

## High-Signal Mapping Notes
1. {{NOTE_ONE}}
2. {{NOTE_TWO}}

## Quick Wins Identified
1. {{QUICK_WIN_ONE}}
2. {{QUICK_WIN_TWO}}
```

## Branch Analysis (`reports/branch_analysis.md`)

```markdown
# Branch Analysis — Run {{RUN_NUMBER}} ({{DATE}})

## Default vs Active Branch
| Item | Observation |
| --- | --- |
| Default branch (local) | {{DEFAULT_BRANCH}} |
| Focus branch | {{FOCUS_BRANCH}} |
| Recent commit | {{SHORT_SHA}} — {{SUMMARY}} |

## Focus Justification
- {{REASON_ONE}}
- {{REASON_TWO}}

## Risks & Follow-Ups
- {{RISK_ONE}}
- {{RISK_TWO}}
```

## Capability Audit (`reports/capability_audit.md`)

```markdown
# Capability Audit Snapshot — Run {{RUN_NUMBER}} ({{DATE}})

| Capability | Status | Existing Artifacts | Gaps | Risks | Minimal Patch Plan | Rollback Plan |
| --- | --- | --- | --- | --- | --- | --- |
| {{CAPABILITY}} | {{STATUS}} | {{ARTIFACTS}} | {{GAPS}} | {{RISKS}} | {{PATCH_PLAN}} | {{ROLLBACK}} |
```

## High-Signal Findings (`reports/high_signal_findings.md`)

```markdown
# High-Signal Findings — Run {{RUN_NUMBER}} ({{DATE}})

1. **{{TITLE}}** — {{DETAIL}} _Action_: {{ACTION}}.
2. **{{TITLE_2}}** — {{DETAIL_2}} _Action_: {{ACTION_2}}.
```

## Local Checks (`reports/local_checks.md`)

```markdown
# Local Checks & Tooling — Run {{RUN_NUMBER}} ({{DATE}})

## Environment Preparation
| Step | Command | Notes |
| --- | --- | --- |
| {{STEP}} | `{{COMMAND}}` | {{NOTES}} |

## Quality Gates to Run After Changes
| Category | Command | Purpose |
| --- | --- | --- |
| {{CATEGORY}} | `{{COMMAND}}` | {{PURPOSE}} |

## Notes
- {{NOTE}}
```

## Reproducibility Checklist (`reports/reproducibility.md`)

```markdown
# Reproducibility Checklist — Run {{RUN_NUMBER}} ({{DATE}})

| Item | Status | Notes |
| --- | --- | --- |
| {{ITEM}} | {{STATUS}} | {{NOTES}} |

## Immediate Follow-Ups
- {{FOLLOW_UP}}
```

## Deferred Items (`reports/deferred.md`)

```markdown
# Deferred Items — Run {{RUN_NUMBER}} ({{DATE}})

| Item | Reason Deferred | Proposed Next Step |
| --- | --- | --- |
| {{ITEM}} | {{REASON}} | {{NEXT_STEP}} |
```

## CHANGELOG Entry (`CHANGELOG.md`)

```markdown
## Unreleased - {{DATE}}
- {{SUMMARY_OF_CHANGES}}
```

## Open Questions (`OPEN_QUESTIONS.md`)

```markdown
# Open Questions & Next Steps — Run {{RUN_NUMBER}} ({{DATE}})

## Menu Items Covered This Run
- ✅ **{{MENU_ITEM}}** — {{OUTCOME}}.

## Proposed Menu Focus for Run {{NEXT_RUN}}
1. {{PROPOSAL_ONE}}
2. {{PROPOSAL_TWO}}
3. {{PROPOSAL_THREE}}

## Outstanding Questions
- {{QUESTION}}
```

## Security Sweep (`reports/security_audit.md`)

```markdown
# Security Sweep — Run {{RUN_NUMBER}} ({{DATE}})

> Menu focus: Security (4)

## Run Metadata
- Branch: {{BRANCH_NAME}}
- Snapshot commit: {{SHORT_SHA}}
- Participants: {{AUDITORS}}

## Secrets & Credentials Review
- [ ] Scan repositories (e.g., `git secrets`, `detect-secrets`) across touched paths.
- Findings: {{SECRETS_FINDINGS}}
- Remediation status: {{SECRETS_STATUS}}

## Dependency & Supply-Chain Review
| Package/Tool | Current Version | Source | Notes |
| --- | --- | --- | --- |
| {{PACKAGE}} | {{VERSION}} | {{SOURCE}} | {{NOTES}} |

## Configuration & Policy Review
- Policies referenced: {{POLICIES}}
- Deviations detected: {{DEVIATIONS}}
- Actions required: {{ACTIONS_REQUIRED}}

## Security Testing
| Check | Command | Result | Follow-Up |
| --- | --- | --- | --- |
| {{CHECK}} | `{{COMMAND}}` | {{RESULT}} | {{FOLLOW_UP}} |

## Outstanding Risks
- {{RISK_ONE}}
- {{RISK_TWO}}

## Next Steps
- {{NEXT_STEP_ONE}}
- {{NEXT_STEP_TWO}}
```

## Observability Runbook (`reports/observability_runbook.md`)

```markdown
# Observability Runbook — Run {{RUN_NUMBER}} ({{DATE}})

> Menu focus: Observability (5)

## Run Metadata
- Branch: {{BRANCH_NAME}}
- Snapshot commit: {{SHORT_SHA}}
- Incident commander: {{ONCALL}}

## Logging
| System | Location | Retention | Action Owner |
| --- | --- | --- | --- |
| {{SYSTEM}} | {{LOCATION}} | {{RETENTION}} | {{OWNER}} |

### Log Review Checklist
- [ ] Confirm log shipping is operational ({{LOG_SHIP_TOOL}})
- [ ] Review error rates for {{SERVICE}}
- Findings: {{LOG_FINDINGS}}

## Metrics & Dashboards
| Metric | Source | Threshold | Current Value | Notes |
| --- | --- | --- | --- | --- |
| {{METRIC}} | {{SOURCE}} | {{THRESHOLD}} | {{VALUE}} | {{NOTES}} |

### Dashboard Links
- {{DASHBOARD_NAME}} — {{URL_OR_PATH}}

## Alerting
| Alert | Trigger | Channel | Runbook |
| --- | --- | --- | --- |
| {{ALERT}} | {{TRIGGER}} | {{CHANNEL}} | {{RUNBOOK_LINK}} |

## Incident Review
- Past incidents referenced: {{INCIDENTS}}
- Lessons applied this run: {{LESSONS}}

## Next Steps
- {{NEXT_STEP_ONE}}
- {{NEXT_STEP_TWO}}
```

Update this template library whenever audit artefacts evolve so future runs remain consistent.
