# [Template]: Intent Validation & Plan of Action Approval Gate
**Version:** v1.0.0  
**Last Updated:** Previous Cycle-10-25  
**Role Workflow:** Developers draft → Maintainers review → Stakeholders approve

> [PLACEHOLDER: INTENT_STATEMENT]

Use this planning template before committing to a significant implementation effort. It surfaces assumptions, validation work, and decision gates so AI Assistant maintains a single source of truth through autonomous validation prior to execution.

## Template Overview
- Initiative name: [PLACEHOLDER: INITIATIVE_NAME]
- Primary owner: [PLACEHOLDER: OWNER]
- Time horizon: [PLACEHOLDER: TIMELINE]
- Linked execution templates: [PLACEHOLDER: LINKED_TEMPLATES]
- Approval deadline: [PLACEHOLDER: APPROVAL_DEADLINE]

## Intent Brief
Summarize the user problem, measurable outcome, and scope boundaries. Reference supporting docs such as [`docs/validation/`](../validation/) or `../../docs/prompts/` where helpful.

## Discovery Inputs
- User research, bug reports, or telemetry referenced.
- Dependencies or services impacted (e.g., [`src/cli/`](../../src/cli/), `codex_ml` pipelines).
- Feature flags or configuration toggles that gate the rollout.

## Validation Activities
List experiments, spikes, or prototypes that validate feasibility. Link to notebooks under `../../notebooks/` or tests added to `../../tests/`.

## Decision Gates
| Gate | Entry Criteria | Decision Owner |
| --- | --- | --- |
| Gate 1 — Intent review | Document circulated and placeholders resolved | Maintainer |
| Gate 2 — Validation results | Experiments complete, risks documented | Tech lead |
| Gate 3 — Launch approval | Success criteria met, rollout plan approved | Stakeholder |

## Risk Register
| Risk | Impact | Mitigation |
| --- | --- | --- |
| [PLACEHOLDER: RISK_DESCRIPTION] | [PLACEHOLDER: RISK_IMPACT] | [PLACEHOLDER: RISK_MITIGATION] |
| [PLACEHOLDER: SECONDARY_RISK] | [PLACEHOLDER: SECONDARY_IMPACT] | [PLACEHOLDER: SECONDARY_MITIGATION] |

## Customization Guide
| Placeholder | Description | Example |
| --- | --- | --- |
| `[PLACEHOLDER: INTENT_STATEMENT]` | One-sentence summary of desired outcome. | "Validate GPU fine-tuning pipeline for codex-14b." |
| `[PLACEHOLDER: INITIATIVE_NAME]` | Internal or customer-facing project name. | "Arcturus CLI refactor" |
| `[PLACEHOLDER: OWNER]` | Person accountable for delivery. | "@maintainer-handle" |
| `[PLACEHOLDER: LINKED_TEMPLATES]` | Execution templates paired with this plan. | "Migration — CLI Hardening" |
| `[PLACEHOLDER: APPROVAL_DEADLINE]` | Deadline for stakeholder sign-off. | "Previous Cycle-11-07" |

## Example Instantiations
1. **CLI stabilization** — Pair with [Migration — CLI Hardening](./Migration_CLIHardening.md) to capture discovery for argument contract updates.
2. **Module relocation** — Combine with [Migration — Python File Relocation](./Migration_PythonFileRelocation.md) for larger refactors affecting imports.
3. **New service launch** — Use alongside `docs/PR_PLAN.md` to align milestones and incident response.

## Usage Pattern
1. Draft the template during the planning kickoff and circulate to stakeholders.
2. Resolve all placeholders prior to Gate 1 review and attach related artifacts (tests, dashboards, notebooks).
3. Maintain living status by updating the Decision Gates table as approvals arrive.
4. Once execution begins, link the corresponding migration template and update [`docs/CHANGELOG.md`](../CHANGELOG.md).

## Key Benefits
- Establishes shared understanding before execution begins.
- Provides audit trail for why decisions were made and by whom.
- Aligns planning with coverage expectations (≥85% for execution templates).
- Encourages pairing with technical assets (`sitecustomize.py`, `conftest.py`, CLI scripts) for cross-team visibility.
