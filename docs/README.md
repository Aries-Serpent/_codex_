# Documentation Hub

**Welcome to the `_codex_` documentation hub**. Comprehensive documentation for the ML/AI platform with autonomous agent orchestration.

**Last Updated**: 2025-12-30

---

## 🧠 Cognitive Brain (Start Here for AI Agents)

### **Unified Navigation System** - NEW!
- 🗺️ **[Cognitive Map](system/CODEBASE_COGNITIVE_MAP.md)** - Complete architecture, components, flows, dependencies
- 📊 **[Dashboard](system/CODEBASE_DASHBOARD.md)** - Live status, current work, blockers, metrics
- 🎯 **[Roadmap](ROADMAP.md)** - Iteration plans, priorities, future scope (Q1-Q3 2026)

### **Why This Matters**
The cognitive brain enables:
- **Context Continuity**: AI agents maintain understanding across sessions
- **Efficient Navigation**: Quick discovery of components, entry points, relationships
- **Duration-Aware Planning**: Maximize work within token/time budgets
- **Best Path Forward**: Always know the next most valuable task
- **Autonomous Operation**: Self-directed agents without constant human guidance

---

## 📁 Quick Links

### Core Documentation
- 📖 **[Architecture](ARCHITECTURE.md)** - Detailed technical architecture
- 🤝 **[Contributing](CONTRIBUTING.md)** - Development workflow and guidelines
- 🔐 **[Admin Guide](ADMIN_IMPLEMENTATION_GUIDE.md)** - Setup and management
- 📚 **[API Reference](API_REFERENCE.md)** - Complete API documentation

### MCP Package System (93+ KB Documentation)
- 📦 **[Quick Start](mcp/QUICK_START.md)** - 5-minute onboarding guide
- 📘 **[Packaging Guide](mcp/PACKAGING_GUIDE.md)** - Complete packaging workflows
- 🎯 **[Packageable Capabilities](mcp/PACKAGEABLE_CAPABILITIES.md)** - Capability transfer framework
- 🤖 **[ChatGPT System Prompt](mcp/ChatGPT_Project_SYSTEM_PROMPT.md)** - AI assistant prompt template
- 🧭 **[Navigation System](mcp/GENERIC_NAVIGATION_SYSTEM.md)** - Universal navigation framework
- 🚀 **[Advanced Features](mcp/ADVANCED_FEATURES_PLANSET.md)** - Future roadmap (Q1-Q3 2026)

### Capability Guides
- 📝 **[Model Checkpointing](capabilities/checkpointing.md)** - Checkpoint management with SafeTensors
- 🏋️ **[Training Loops](capabilities/train_loop.md)** - Production training patterns
- 🔧 **[PEFT Techniques](capabilities/peft_hooks.md)** - Parameter-efficient fine-tuning
- ✅ **[Code Quality](capabilities/code_quality_tooling.md)** - Complete quality stack

---

## Original Documentation Index

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
