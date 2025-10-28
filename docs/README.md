# Documentation index

Welcome to the `_codex_` knowledge base. Start here to navigate the reasoning roadmap, architectural references, and
hands-on guides that keep bespoke model hosting disciplined.

## 🧭 Orientation pillars
- **Reasoning roadmap** — Track milestone health and forward-looking bets in [`README_ROOT.md`](./README_ROOT.md).
- **Architecture** — Pair [`diagrams/architecture.svg`](./diagrams/architecture.svg) with the systems notes in
  [`guides/reasoning_overview.md`](./guides/reasoning_overview.md).
- **Curriculum design** — Apply the phased training playbooks from
  [`guides/first_principles_curricula.md`](./guides/first_principles_curricula.md).
- **Bespoke hosting expectations** — Align ops and status updates with [`deployment/reasoning_pod.md`](./deployment/reasoning_pod.md)
  and the rollout checklists under [`templates/`](./templates/README.md).

## 🚀 Quick links for reasoning teams
- **Reasoning templates in the CLI** — `codex reasoning-templates list` surfaces curated training/eval bundles. See the
  [`codex_cli` help](../src/codex_cli/app.py) for command details.
- **End-to-end quickstart** — Follow [`quickstart.md`](./quickstart.md) with the `+reasoning=baseline` overrides highlighted in
  [`README_ROOT.md`](./README_ROOT.md#training-quickstart).
- **Evaluation ledger** — Use [`guides/reasoning_overview.md`](./guides/reasoning_overview.md#evaluation-readiness) to configure
  NDJSON metrics pipelines.
- **Deployment guardrails** — Cross-check bespoke model expectations against [`guides/serving_reproducibility.md`](./guides/serving_reproducibility.md).

## 📋 Operational templates
Operational templates encode recurring delivery rituals so teams can execute migrations, hardening passes, and planning
checkpoints with consistent safeguards. Begin with the [Operational Templates index](./templates/README.md) to review
prerequisites, required metadata, and cross-references before copying a template into your service.

### When to use a template
- You are planning a migration or hardening effort that will cross team boundaries.
- You need an auditable checklist with rollback, communications, and verification steps.
- You want a consistent structure for maintaining ≥85% coverage through scoped test additions.

### Quick links
- [Migration — Python File Relocation](./templates/Migration_PythonFileRelocation.md)
- [Migration — CLI Hardening](./templates/Migration_CLIHardening.md)
- [Planning — Intent Validation](./templates/Planning_IntentValidation.md)

### Handoff checklist
Each template includes role guidance (developers draft → maintainers execute), `[PLACEHOLDER: …]` prompts, and success
criteria aligned with the coverage standard. Ensure the following before requesting review:

1. All placeholders are replaced with repo-specific context and linked artifacts.
2. Rollback and communication steps point to real runbooks or dashboards.
3. The template is stored alongside the service codebase (usually under `docs/`) and linked from the change description or PR.

See [`docs/CONTRIBUTING.md`](./CONTRIBUTING.md#using-operational-templates) for the full drafting workflow and role expectations.

## Conventions
- Keep docs small and composable.
- Use a single fenced `diff` block for proposed patches in prompts/guides.
- Prefer citations to live repo files when referencing code or config.

## Related
- Project audit ritual: see `AUDIT_PROMPT.md`
- CHANGELOG practices follow “Keep a Changelog” with an **Unreleased** section at the top.

---
Last updated: 2025-10-25
