# Documentation Hub

**Welcome to the `_codex_` documentation hub**. Comprehensive documentation for the ML/AI platform with autonomous agent orchestration.

**Last Updated**: 2026-03-30

---

## 🧠 Cognitive Brain (Start Here for AI Agents)

### **Unified Navigation System**
- 🗺️ **[Cognitive Map](./system/CODEBASE_COGNITIVE_MAP.md)** - Complete architecture, components, flows, dependencies
- 📊 **[Dashboard](./system/CODEBASE_DASHBOARD.md)** - Live status, current work, blockers, metrics
- 🎯 **[Roadmap](./ROADMAP.md)** - Iteration plans, priorities, future scope

### **Why This Matters**
The cognitive brain enables:
- **Context Continuity**: AI agents maintain understanding across sessions
- **Efficient Navigation**: Quick discovery of components, entry points, relationships
- **Duration-Aware Planning**: Maximize work within token/time budgets
- **Best Path Forward**: Always know the next most valuable task
- **Autonomous Operation**: Self-directed agents without constant human guidance

---

## 🚀 Quick Links

### 🚨 CI Rescue & Health
- 🔄 **[CI Rescue Pipeline](ci/CI_RESCUE_PIPELINE.md)** — Golden-path documentation: how workflow failures automatically trigger Copilot sessions. Includes Mermaid flowcharts, sequence diagrams, deduplication state machine, anti-pattern map. *(S244 — 2026-03-30)*
- 📋 **[CI/CD Index](ci/INDEX.md)** — All CI failure analysis, fix summaries, and validation reports

### Core Documentation
- 📖 **[Architecture](./ARCHITECTURE.md)** - Detailed technical architecture
- 🤝 **[Contributing](CONTRIBUTING.md)** - Development workflow and guidelines
- 🔐 **[Admin Guide](ADMIN_IMPLEMENTATION_GUIDE.md)** - Setup and management
- 📚 **[API Reference](api/index.md)** - Complete API documentation
- 📋 **[Getting Started](guides/quickstart.md)** - Quick start guide
- 📝 **[Examples](guides/examples.md)** - Code examples
- 📜 **[Changelog](CHANGELOG.md)** - Release history

### MCP Package System (93+ KB Documentation)
- 📦 **[Quick Start](mcp/QUICK_START.md)** - 5-minute onboarding guide
- 📘 **[Packaging Guide](mcp/PACKAGING_GUIDE.md)** - Complete packaging workflows
- 🎯 **[Packageable Capabilities](mcp/PACKAGEABLE_CAPABILITIES.md)** - Capability transfer framework
- 🤖 **[ChatGPT System Prompt](mcp/ChatGPT_Project_SYSTEM_PROMPT.md)** - AI assistant prompt template
- 🧭 **[Navigation System](mcp/GENERIC_NAVIGATION_SYSTEM.md)** - Universal navigation framework
- 🚀 **[Advanced Features](mcp/ADVANCED_FEATURES_PLANSET.md)** - Future roadmap

### Capability Guides
- 📝 **[Model Checkpointing](capabilities/checkpointing.md)** - Checkpoint management with SafeTensors
- 🏋️ **[Training Loops](capabilities/train_loop.md)** - Production training patterns
- 🔧 **[PEFT Techniques](capabilities/peft_hooks.md)** - Parameter-efficient fine-tuning
- ✅ **[Code Quality](capabilities/code_quality_tooling.md)** - Complete quality stack

---

## 🧭 Orientation Pillars

- **Reasoning roadmap** — Track milestone health and forward-looking bets in README_ROOT.md.
- **Architecture** — Pair [`diagrams/architecture.svg`](./diagrams/architecture.svg) with the systems notes in [`guides/reasoning_overview.md`](./guides/reasoning_overview.md).
- **Curriculum design** — Apply the phased training playbooks from [`guides/first_principles_curricula.md`](./guides/first_principles_curricula.md).
- **Bespoke hosting expectations** — Align ops and status updates with [`deployment/reasoning_pod.md`](./deployment/reasoning_pod.md) and the rollout checklists under [`templates/`](./templates/README.md).

### Reasoning Pod Deployment
Refer to [`deployment/reasoning_pod.md`](./deployment/reasoning_pod.md) and the [configs/deploy/reasoning_pod.yaml](https://github.com/Aries-Serpent/_codex_/blob/main/configs/deploy/reasoning_pod.yaml) for dry-run deployment guidance. These assets are designed for offline validation and do not require hosted services.

---

## 🚀 Quick Links for Reasoning Teams

- **Reasoning templates in the CLI** — `codex reasoning-templates list` surfaces curated training/eval bundles. See the [`codex_cli` help](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_cli/app.py) for command details.
- **End-to-end quickstart** — Follow `quickstart.md` with the `+reasoning=baseline` overrides highlighted in [`README_ROOT.md`](./README_ROOT.md#training-quickstart).
- **Evaluation ledger** — Use [`guides/reasoning_overview.md`](./guides/reasoning_overview.md#evaluation-readiness) to configure NDJSON metrics pipelines.
- **Deployment guardrails** — Cross-check bespoke model expectations against `guides/serving_reproducibility.md`.

---

## 📋 Operational Templates

Operational templates encode recurring delivery rituals so teams can execute migrations, hardening passes, and planning checkpoints with consistent safeguards. Begin with the [Operational Templates index](./templates/README.md) to review prerequisites, required metadata, and cross-references before copying a template into your service.

### When to Use a Template
- You are planning a migration or hardening effort that will cross team boundaries.
- You need an auditable checklist with rollback, communications, and verification steps.
- You want a consistent structure for maintaining ≥85% coverage through scoped test additions.

### Quick Links
- [Migration — Python File Relocation](./templates/Migration_PythonFileRelocation.md)
- [Migration — CLI Hardening](./templates/Migration_CLIHardening.md)
- [Planning — Intent Validation](./templates/Planning_IntentValidation.md)

### Handoff Checklist
Each template includes role guidance (developers draft → maintainers execute), `[PLACEHOLDER: …]` prompts, and success criteria aligned with the coverage standard. Ensure the following before requesting review:

1. All placeholders are replaced with repo-specific context and linked artifacts.
2. Rollback and communication steps point to real runbooks or dashboards.
3. The template is stored alongside the service codebase (usually under `docs/`) and linked from the change description or PR.

See [`docs/CONTRIBUTING.md`](./CONTRIBUTING.md#using-operational-templates) for the full drafting workflow and role expectations.

---

## 📊 Phase 8.7: Universal Intelligence

Complete meta-learning framework with 170 tests.

**Components:**
- Universal Task Interface
- Meta-Policy Router (MAML/Reptile)
- Abstraction Engine
- Grounding Layer
- Pattern Store
- Safety Monitor
- EXP-10 Validation

### Quick Example

```python
from github.agents.core.universal_intelligence import UniversalTaskInterface, TaskSpec

spec = TaskSpec(
    environment="gridworld",
    initial_state={"x": 0, "y": 0, "goal": {"x": 5, "y": 5}},
    reward_spec={"id": "reward:v1"},
    termination={"max_steps": 100},
)

uti = UniversalTaskInterface(seed=12345)
result = uti.execute_task(spec)
```

---

## ⚙️ Installation

```bash
pip install -e .
```

---

## 🚢 Deployment and Operational Expectations

To generate and review a deployment manifest for a bespoke reasoning agent, run a dry-run deploy:

```bash
codex deploy \
  --config configs/deploy/reasoning_pod.yaml \
  --model artifacts/runs/reasoning-starter:last \
  --dry-run
```

This renders the "reasoning pod" manifest for inspection. It does **not** create or update any live service. See [`deployment/reasoning_pod.md`](./deployment/reasoning_pod.md) for what that pod is expected to look like (resources, telemetry, trace capture mode, curriculum phase, etc.).

### Rollout Rings

This repository uses staged rollout rings to represent maturity and review state:

* `0A_base_` / `0B_base_`: active development, unstable knobs.
* `0C_base_`: integration of multiple features landing together.
* `0D_base_`: release candidate. Content here should be explainable to Engineering and Product.
* `main`: canonical internal "alpha product" surface after approval.

---

## 📏 Conventions

- Keep docs small and composable.
- Use a single fenced `diff` block for proposed patches in prompts/guides.
- Prefer citations to live repo files when referencing code or config.

---

## 📚 Related

- Project audit ritual: see `AUDIT_PROMPT.md`
- CHANGELOG practices follow "Keep a Changelog" with an **Unreleased** section at the top.

---

Last updated: 2026-02-10
