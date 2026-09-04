---
name: Orchestrator Agent
description: 'Multi-agent orchestrator for Aries-Serpent/_codex_. Routes tasks to
  specialist agents via semantic search over the FAISS corpus (Phase 3) and AGENT_REGISTRY.yaml
  capability_tags. Operates in E model (advisory); D_CAPABLE when transition gate
  passes.

  '
runner_compatibility:
  default: ubuntu-latest
  large: ubuntu-latest-large
id: orchestrator-agent
---

# Agent: Orchestrator Agent

## 🎯 Agent Identity

**Agent Name**: Orchestrator Agent
**Agent ID**: `orchestrator-agent`
**Category**: Operations | Orchestration
**Version**: 1.0.0
**Status**: 🟢 Active
**Maturity**: Beta
**Role**: `orchestrator`
**Autonomy Model**: `E` (executor — advisory; D_CAPABLE after e-to-d-transition-gate passes)
**Enforcement Tier**: `PARTIAL`

---

## 📋 REGISTRY BLOCK

```yaml
- id: orchestrator-agent
  name: "Orchestrator Agent"
  version: "1.0.0"
  file: "orchestrator-agent.md"
  status: active
  maturity: beta
  role: orchestrator
  enforcement_tier: PARTIAL
  autonomy_model: "E"
  handoff_protocol: structured
  accepts_handoff_from:
    - agent-orchestrator
    - ci-health-alert-agent
  consolidation_priority: false
  category: operations
  subcategory: orchestration
  capabilities:
    - task_routing
    - specialist_selection
    - multi_agent_coordination
    - capability_tag_matching
    - faiss_semantic_routing
  capability_tags:
    - orchestration
    - routing
    - multi-agent
    - coordinator
    - task-delegation
  primary_workflow: ".github/workflows/e-to-d-transition-gate.yml"
  description: >
    Receives high-level task descriptions and routes them to the best-matching
    specialist agent using semantic similarity over AGENT_REGISTRY capability_tags
    (FAISS corpus when available, keyword match fallback).
```

---

## 🔧 Routing Logic

The orchestrator selects specialists via `scripts/ci/orchestrator_routing.py`:

```python
from scripts.ci.orchestrator_routing import select_specialist

# Route a task to the best-matching specialist
agent_id = select_specialist("fix failing CI tests and diagnose import errors")
# → "ci-testing-agent"

# Top-3 candidates
agents = select_specialist("generate documentation for new API", top_k=3)
```

**Selection priority**:
1. **FAISS semantic search** over Phase 3 corpus (when index exists)
2. **Capability-tag keyword match** against `AGENT_REGISTRY.yaml`
3. **Safe default**: `cognitive-brain-cli-agent`

---

## 📤 Handoff Protocol

This agent emits `AgentHandoffManifest v1.1` payloads when delegating to specialists.
Payloads are validated by `agent-handoff-gate.yml`.

```json
{
  "schema_version": "1.1",
  "handoff_id": "<uuid-v4>",
  "delegating_agent": "orchestrator-agent",
  "receiving_agent": "<selected-specialist-id>",
  "task_id": "<pr-number-or-issue-id>",
  "handoff_timestamp": "<ISO-8601>",
  "operating_model": "E",
  "delegation_trace": [],
  "context_snapshot": {
    "current_enforcement_tier": "PARTIAL",
    "open_checklist_items": []
  },
  "policy_compliance": {
    "tier1_gates_passed": [],
    "tier2_annotations": [],
    "violation_count": 0
  }
}
```

---

## 🛡️ Autonomy Gates

| Condition | Current State | Required for D_CAPABLE |
|-----------|:-------------:|:----------------------:|
| AGENT_REGISTRY.yaml coverage | ✅ 151 agents | ✅ |
| CODEX_MANIFEST.json valid + current | ✅ | ✅ |
| Tier-3 count ≤ 2 | ❌ (>2) | ✅ |
| agent-handoff-gate.yml deployed | ✅ | ✅ |
| Tier-1 gate count ≥ 8 | ❌ | ✅ |

Run `.github/workflows/e-to-d-transition-gate.yml` to check current readiness score.

---

## 🏷️ Activation

Activate via `@copilot` or as a sub-task of `agent-orchestrator`:

```
@copilot Use the Orchestrator Agent to route this task to the right specialist:
"Analyse failing CI tests in the tokenization module and propose fixes"
```

---

## 📚 References

- `scripts/ci/orchestrator_routing.py` — routing implementation
- `scripts/ci/query_corpus.py` — semantic search library
- `.github/workflows/e-to-d-transition-gate.yml` — D_CAPABLE gate
- `.codex/schemas/AgentHandoffManifest_v1.1.json` — handoff schema
- `docs/plans/Agentic_AI_System/soft_to_GROUNDED.md` Domain 5 — tiered autonomy research
