# Operational Templates Index

The `docs/templates/` directory curates reusable runbooks that combine execution guidance with customizable placeholders. Each template follows a role-gated workflow: **developers** draft the plan, **maintainers** execute or approve the rollout, and **reviewers** confirm success criteria using the embedded checklists.

## Available Templates

| Template | Summary | Primary Focus |
| --- | --- | --- |
| [Iteration Plan Template](./ITERATION_PLAN_TEMPLATE.md) | Comprehensive iteration-based implementation plan with physics alignment and energy distribution. | Incremental development and flexible timelines |
| [Migration — Python File Relocation](./Migration_PythonFileRelocation.md) | Move Python files or packages while preserving import stability and release hygiene. | Codebase topology and backward compatibility |
| [Migration — CLI Hardening](./Migration_CLIHardening.md) | Strengthen CLI ergonomics, validation, and coverage to meet the 85% testing baseline. | Developer experience and operational resilience |
| [Planning — Intent Validation](./Planning_IntentValidation.md) | Facilitate structured discovery and approval gates before implementation begins. | Alignment, risk framing, and decision records |
| [Status Update — Daily Report (v1.1)](./status/README.md) | Comprehensive daily status update with snapshot, delta tracking, and atomic patch diffs. | Repository audits, reproducibility, and automation |

## When to Use Each Template

### Iteration Plan Template
Use for feature implementations, bug fixes, refactoring, security remediation, or infrastructure improvements that span multiple iterations. The template emphasizes iteration-based workflow (not week-based), physics principle alignment (🛤️🔄👁️🔀⚖️), pre-commit checkpoints, and flexible timelines. See `docs/TERMINOLOGY_MIGRATION.md` for terminology guidance.

### Migration — Python File Relocation
Use when reorganizing modules, extracting packages, or introducing aliases that must remain compatible across integrations. The template includes compatibility shims, release checklist items, and rollback guidance.

### Migration — CLI Hardening
Use when tightening CLI interfaces, adopting new dependencies, or extending coverage for high-touch commands. The template orchestrates baseline audits, phased hardening tasks, and observability checkpoints.

### Planning — Intent Validation
Use before implementing a substantial change. The template standardizes intent statements, validation evidence, risk logs, and approval criteria so AI Assistant validates scope through autonomous analysis and success markers.

### Status Update — Daily Report (v1.1)
Use for comprehensive daily repository audits and status tracking. The template provides:
- Full snapshot with capability audit and reproducibility tracking
- Delta tracking from previous reports
- Atomic patch diffs with validation checklists
- Automation hooks for issues, PRs, coverage, and security scans
- Tokenization insights and secret-masking guidance

See [`status/README.md`](./status/README.md) for complete documentation.

## How to Use These Templates

1. Select the appropriate template from this directory and copy it into your workstream docs.
2. Replace every `[PLACEHOLDER: …]` token with project-specific details; do not remove the metadata header.
3. Cross-link related templates—for example, pair the planning template with the matching migration template for visibility into execution and rollback plans.
4. Update linked assets (tests, dashboards, release notes) as you progress through each phase.
5. On completion, document learnings and version bumps in [`docs/CHANGELOG.md`](../CHANGELOG.md) so future readers understand how the template evolved.

## Cross-References

| Template | Key References |
| --- | --- |
| Iteration Plan | [`docs/TERMINOLOGY_MIGRATION.md`](../TERMINOLOGY_MIGRATION.md), [`docs/plans/`](../plans/), [`AGENTS.md`](.././agents.md) |
| Python File Relocation | [`sitecustomize.py`](../../sitecustomize.py), [`conftest.py`](../../conftest.py), [`tests/`](../../tests/) |
| CLI Hardening | [`src/cli/`](../../src/cli/), [`tests/cli/`](../../tests/cli/), [`pyproject.toml`](../../pyproject.toml) |
| Intent Validation | [`docs/validation/`](../validation/), [`docs/templates/README.md`](./README.md), [`tests/conftest.py`](../../tests/conftest.py) |
| Status Update | [`status/codex_status_template_v1.1.md`](./status/codex_status_template_v1.1.md), [`status/authoring_guide_v1.1.md`](./status/authoring_guide_v1.1.md), [`reports/daily/`](../../reports/daily/) |

## Maintenance Notes

- Keep version numbers in sync across all templates (`v1.0.0` for initial release).
- Retain the role workflow messaging so contributors understand who drafts versus who executes.
- Add new templates to this index to maintain discoverability and update the cross-reference table accordingly.
