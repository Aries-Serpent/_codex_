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

### Reasoning Pod Deployment
Refer to [`deployment/reasoning_pod.md`](./deployment/reasoning_pod.md) and
[`../configs/deploy/reasoning_pod.yaml`](../configs/deploy/reasoning_pod.yaml) for dry-run deployment guidance.
These assets are designed for offline validation and do not require hosted services.

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

## Deployment and Operational Expectations

To generate and review a deployment manifest for a bespoke reasoning agent,
run a dry-run deploy. Example:

```bash
codex deploy \
  --config configs/deploy/reasoning_pod.yaml \
  --model artifacts/runs/reasoning-starter:last \
  --dry-run
```text

This renders the "reasoning pod" manifest for inspection. It does **not**
create or update any live service. See [`deployment/reasoning_pod.md`](./deployment/reasoning_pod.md)
for what that pod is expected to look like (resources, telemetry, trace
capture mode, curriculum phase, etc.). The CLI intentionally supports
dry-run review only — there is no automatic apply step, and the embedded
`rollout_ring` is declarative intent, not permission.

Always keep `--dry-run` in place; manifests must be reviewed before any
apply/rollout tooling is engaged.

### Rollout rings

This repository uses staged rollout rings to represent maturity and review
state:

* `0A_base_` / `0B_base_`: active development, unstable knobs.
* `0C_base_`: integration of multiple features landing together.
* `0D_base_`: release candidate. Content here should be explainable
  to Engineering and Product.
* `main`: canonical internal "alpha product" surface after approval.

When you generate a deployment manifest (`configs/deploy/reasoning_pod.yaml`),
it includes a `rollout_ring` field. That field is a declaration of intent
("this artifact is targeting 0D_base_ next"), not permission to ship.

Nothing targeting `main` should be treated as eligible for hosting without:
1. offline evaluation gates passing,
2. trace/curriculum settings documented,
3. explicit signoff.

## Related
- Project audit ritual: see `AUDIT_PROMPT.md`
- CHANGELOG practices follow “Keep a Changelog” with an **Unreleased** section at the top.

---
Last updated: 2025-10-25
