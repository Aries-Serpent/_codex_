# Security Sweep — Run {{RUN_NUMBER}} ({{DATE}})

> Menu focus: Security (4)

Use this template to document the security review for each audit run. Replace placeholders and remove sections that do not apply. Link supporting evidence where possible.

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
