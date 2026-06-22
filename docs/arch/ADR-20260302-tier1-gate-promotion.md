# ADR-20260302: Tier-1 Gate Promotion for Registry and Handoff Validation
> Generated: 2026-06-22T07:00:00Z | Author: copilot-swe-agent[bot]
> Status: Accepted
> Related PRs: #3447

## 1. Context

Phase 2 of the Soft→GROUNDED conversion introduced two CI validation
workflows as Tier-2 canary gates:

- `agent-registry-validation.yml` — validates AGENT_REGISTRY.yaml against
  the JSON Schema and checks integrity via CODEX_MANIFEST.json.
- `agent-handoff-gate.yml` — validates AgentHandoffManifest documents
  against `.codex/schemas/AgentHandoffManifest_v1.1.json`.

Both workflows initially used `core.warning()` (annotations only) so that
false positives during the observation period would not block PRs. After a
2-sprint observation period with zero false positive gate fires, they were
promoted to Tier-1 (`exit 1` / `core.setFailed()`).

## 2. Problem Statement

Determine when and how to promote CI validation gates from advisory
(Tier-2 canary, `::warning::` only) to blocking (Tier-1, `exit 1`)
without introducing false positive PR blocks.

## 3. Decision

Promote both workflows to Tier-1 GROUNDED enforcement:

| Workflow | Before | After |
|----------|--------|-------|
| `agent-registry-validation.yml` | `core.warning()` | `core.setFailed()` / `exit 1` |
| `agent-handoff-gate.yml` | `core.warning()` | `core.setFailed()` / `exit 1` |

The promotion criteria were:
1. Zero false positive gate fires during the 2-sprint observation period.
2. All 152 agents pass schema validation.
3. CODEX_MANIFEST.json integrity hash matches on every test run.

## 4. Decision Drivers

| Driver | Notes |
|--------|-------|
| Regression prevention | Soft gates allowed schema violations to merge undetected |
| E→D FSM condition C2 | Requires at least 2 Tier-1 gates active |
| Confidence threshold | 2-sprint observation with zero false positives |
| Developer experience | Clear, immediate feedback on invalid registry changes |

## 5. Considered Alternatives

| Alternative | Rejected Because |
|-------------|------------------|
| Keep Tier-2 indefinitely | Schema violations could merge; E→D gate blocked |
| Promote after 1 sprint only | Insufficient observation period for edge cases |
| Promote only registry, not handoff | Partial coverage; handoff validation equally critical |
| Use branch protection rules instead of workflow gates | Less granular; cannot validate YAML schema content |

## 6. Consequences

### Positive
- PRs with invalid AGENT_REGISTRY.yaml are now blocked before merge.
- PRs with malformed AgentHandoffManifest documents are blocked.
- E→D FSM condition C2 (≥2 Tier-1 gates) is satisfied.
- Developers get immediate, actionable CI feedback.

### Negative
- Any JSON Schema bug could block legitimate PRs until fixed.
- Contributors unfamiliar with the 4 required fields may see unexpected failures.

### Risks & Mitigations
- **Risk**: Schema too strict for edge cases.
  **Mitigation**: JSON Schema uses `additionalProperties: true` for agent entries;
  only the 4 enforcement fields are required.
- **Risk**: CODEX_MANIFEST.json stale after manual registry edit.
  **Mitigation**: CI step regenerates manifest and compares; clear error message
  instructs running `python scripts/ci/generate_manifest.py`.

## 7. Provenance & Compliance
- **Observation period**: 2 sprints (no false positives recorded)
- **CI gates**: `.github/workflows/agent-registry-validation.yml`,
  `.github/workflows/agent-handoff-gate.yml`
- **E→D FSM**: Condition C2 satisfied (2 Tier-1 gates active)
- **Change log**: PR #3447 merged to main
