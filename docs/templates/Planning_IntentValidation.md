# [Template]: Intent Validation & Plan of Action Approval Gate

- **Version:** v1.0.0
- **Last Updated:** 2025-10-24
- **Owner Role:** Developer (drafter) → Maintainer (approver)
- **Intended Audience:** Engineers planning significant changes, reviewers assessing readiness

---

## Generic Intent Validation Template

1. **Intent Statement**
   - What outcome are we pursuing?
   - Link to related issues, RFCs, or ADRs: `[PLACEHOLDER:intent_link]`.
2. **Current State Summary**
   - Describe relevant modules (`src/`, `docs/`, external services).
   - Capture known constraints or debt.
3. **Assumptions & Unknowns**
   - List assumptions explicitly.
   - Add discovery tasks for each unknown.
4. **Risks & Mitigations**
   - Include operational risks, customer impact, and testing considerations.
5. **Validation Gates**
   - Tests to pass (pytest modules, integration suites, linting).
   - Documentation updates required (`docs/templates/README.md`, `docs/CHANGELOG.md`).
6. **Success Metrics**
   - Define measurable signals (coverage targets, latency budgets, adoption counts).
7. **Approval Checklist**
   - Maintainer sign-off, security review, product acknowledgement.
8. **Timeline & Milestones**
   - Outline delivery windows and dependencies.

## Customization Guide

| Placeholder | Description | Example |
| --- | --- | --- |
| `[PLACEHOLDER:intent_link]` | Issue, ADR, or doc that triggered the request | `RFC-018` |
| `[PLACEHOLDER:baseline_metric]` | Existing KPI to track before/after | `p95 latency 450ms` |
| `[PLACEHOLDER:risk_owner]` | Person accountable for a specific risk | `@maintainer` |
| `[PLACEHOLDER:review_forum]` | Meeting or channel for approvals | `Architecture Review 2025-10-30` |
| `[PLACEHOLDER:rollback_signal]` | Metric or alerting rule to watch | `cli.error_rate > 0.5%` |
| `[PLACEHOLDER:experiment_flag]` | Feature flag controlling rollout | `CODEx_CLI_HARDENING` |

## Example Instantiations

1. **CLI Token Refresh Improvements**
   - Intent: Ensure token refresh CLI subcommand handles offline scenarios.
   - Risks: Regression in telemetry events, stale cache invalidation.
   - Validation Gates: `pytest tests/cli/test_token_refresh.py`, manual dry-run in staging.
2. **Model Artifact Relocation**
   - Intent: Move trained artifacts from `models/legacy/` to `models/managed/`.
   - Risks: Deployment automation referencing old paths, missing checksums.
   - Validation Gates: Data pipeline integration tests, DVC repro run.
3. **Docs Navigation Refresh**
   - Intent: Align docs navigation with new template catalog.
   - Risks: Broken relative links, outdated onboarding references.
   - Validation Gates: `markdown-link-check docs/**/*.md`, content review by Docs lead.

## Usage Pattern

1. Start a planning note using the Generic Intent Validation Template.
2. Replace each `[PLACEHOLDER: ...]` with project-specific information.
3. Share the draft in `[PLACEHOLDER:review_forum]` and gather feedback.
4. Once approved, reference this plan in implementation PRs and commits.
5. Update status weekly until completion or pivot.

## Key Benefits

- Establishes a common language for intent, risk, and validation.
- Reduces time-to-approval by collecting required evidence upfront.
- Encourages measurable success metrics and rollback signals.
- Aligns with the role-gated execution model described in `CONTRIBUTING.md`.

## Repository Context

- Validation docs live in [`docs/validation/`](../validation/).
- Compatibility hooks referenced in [`sitecustomize.py`](../sitecustomize.py).
- Test infrastructure in [`conftest.py`](../../conftest.py) and [`tests/templates/`](../../tests/templates/).
- CLI templates complement this planning workflow: see [Migration – CLI Hardening](./Migration_CLIHardening.md).

---
**Review Gate:** Maintainer confirms risks, validation gates, and rollback signals before authorising implementation work.
