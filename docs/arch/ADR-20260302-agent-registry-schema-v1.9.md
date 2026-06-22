# ADR-20260302: Agent Registry Schema Extension (v1.9.0)
> Generated: 2026-06-22T07:00:00Z | Author: copilot-swe-agent[bot]
> Status: Accepted
> Related PRs: #3447

## 1. Context

The AGENT_REGISTRY.yaml (v1.7.0) tracked 128 agents with basic metadata
(name, description, location, status) but lacked enforcement semantics.
The Soft→GROUNDED conversion plan (docs/plans/Agentic_AI_System/soft_to_GROUNDED.md)
required every agent to declare its enforcement posture so that CI gates,
orchestrator routing, and the E→D transition FSM could query tier and
handoff capabilities programmatically.

Without structured enforcement metadata, the system could not distinguish
between agents that were merely documented and agents whose behavior was
enforced by CI pipelines.

## 2. Problem Statement

Extend the agent registry schema to support enforcement tiers, autonomy
models, and inter-agent handoff protocols without breaking backward
compatibility with existing consumers of AGENT_REGISTRY.yaml.

## 3. Decision

Add four new required fields to every agent entry in AGENT_REGISTRY.yaml:

| Field | Type | Values | Purpose |
|-------|------|--------|---------|
| `enforcement_tier` | enum | `GROUNDED`, `PARTIAL`, `SOFT` | CI enforcement level |
| `autonomy_model` | enum | `E_ONLY`, `D_CAPABLE` | Advisory (E) vs autonomous (D) |
| `handoff_protocol` | enum | `structured`, `unstructured`, `none` | Inter-agent handoff format |
| `accepts_handoff_from` | list | agent names or `["*"]` | Inbound handoff allowlist |

Create a JSON Schema (draft-07) at `.codex/schemas/AgentRegistrySchema.json`
to validate the registry structure in CI. Introduce CODEX_MANIFEST.json at
the repository root to provide SHA-256 integrity verification of the
registry file.

Version the registry at v1.9.0 with 152 agents (128 original + 24 newly
registered agents discovered during the frequency-sorted audit).

## 4. Decision Drivers

| Driver | Notes |
|--------|-------|
| Enforcement queryability | Gates need machine-readable tier data |
| Orchestrator routing | `orchestrator_routing.py` selects agents by capability tags |
| E→D FSM prerequisite | Condition C1 requires schema-validated registry |
| Backward compatibility | Existing agent .md files remain unchanged |
| Integrity guarantee | CODEX_MANIFEST.json prevents silent registry corruption |

## 5. Considered Alternatives

| Alternative | Rejected Because |
|-------------|------------------|
| Store enforcement metadata in individual agent .md files | Not machine-queryable; fragile parsing |
| Create a separate enforcement-only YAML | Dual-source-of-truth risk; sync burden |
| Use GitHub labels for enforcement tiers | No CI gate integration; manual maintenance |
| Embed metadata in workflow files | Scattered across 90+ files; ungovernable |

## 6. Consequences

### Positive
- All 152 agents have machine-readable enforcement metadata.
- CI gates (`agent-registry-validation.yml`) validate schema on every PR.
- CODEX_MANIFEST.json provides tamper-evident integrity checking.
- Orchestrator routing can filter agents by tier and capability.
- Top-20 frequency-ranked agents have `consolidation_priority: true`.

### Negative
- Registry file size increased (~40 KB YAML).
- All future agent additions must include the 4 new fields.
- Schema changes require updating both the JSON Schema and manifest generator.

### Risks & Mitigations
- **Risk**: Schema drift between registry and JSON Schema.
  **Mitigation**: `agent-registry-validation.yml` runs on every PR touching `.github/agents/`.
- **Risk**: Manual edits to large YAML introduce errors.
  **Mitigation**: Convention to edit via Python scripts; `generate_manifest.py` regenerates integrity hashes.

## 7. Provenance & Compliance
- **Schema**: `.codex/schemas/AgentRegistrySchema.json` (draft-07)
- **Manifest**: `CODEX_MANIFEST.json` (SHA-256 integrity)
- **CI validation**: `.github/workflows/agent-registry-validation.yml` (Tier-1)
- **Change log**: PR #3447 merged to main
