---
name: Unified Governance Gate Agent
description: Enforce unified governance policies across PRs, deployments, and automated operations
version: 1.0.0-m05
updated: 2026-02-22
merged_agents:
  - owner-approval-guard (deprecated)
  - config-validator (deprecated)
  - compliance-checker (integrated)
cognitive_integration_level: 4
aais_contribution: +5.0 points
batch: m-05
runner_compatibility:
  default: ubuntu-latest        # 2-core — governance checks, ownership enforcement, config validation
  large:   ubuntu-latest-large  # 4-core — parallel policy gate evaluation
---

# Unified Governance Gate Agent v1.0 (M-05 Merge)

> **M-05**: Merges `owner-approval-guard`, `config-validator`, and
> `compliance-checker` into a single governance orchestrator that enforces
> ownership, configuration correctness, and compliance policy gates.

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                Unified Governance Gate Agent                  │
│                                                              │
│  ┌───────────────┐  ┌─────────────────┐  ┌───────────────┐  │
│  │  Owner        │  │  Config         │  │  Compliance   │  │
│  │  Approval     │  │  Validator      │  │  Checker      │  │
│  │  Guard        │  │  (Hydra/YAML)   │  │  (policy)     │  │
│  └──────┬────────┘  └────────┬────────┘  └───────┬───────┘  │
│         └───────────────────┼────────────────────┘          │
│                             ▼                                │
│              ┌──────────────────────────┐                    │
│              │  Governance Decision     │                    │
│              │  (approve / block / warn)│                    │
│              └──────────────────────────┘                    │
└──────────────────────────────────────────────────────────────┘
```

## Governance Pillars

### Pillar 1: Owner Approval (from owner-approval-guard)

| Trigger | Required Approvers | Bypass? |
|---------|------------------|---------|
| Changes to `.github/workflows/` | @mbaetiong | No |
| Changes to `src/codex_ml/security/` | @mbaetiong | No |
| Changes to `requirements/lock.txt` | @mbaetiong + Dependabot | No |
| Genesis-protocol actions | @mbaetiong | No |
| Cost-incurring jobs (>$0.10) | @mbaetiong | No |
| All other changes | Auto-approve if CI green | Yes |

### Pillar 2: Config Validation (from config-validator)

```yaml
# Validated config schemas:
configs:
  training:   configs/training/*.yaml      → configs/schemas/training.schema.yaml
  evaluation: configs/evaluation/*.yaml    → configs/schemas/evaluation.schema.yaml
  hydra:      conf/                        → hydra schema validation
  agents:     .github/agents/*.md         → agent metadata schema
```

Validation rules:
- All required fields present
- Types match schema (str/int/float/bool/list/dict)
- Enum values within allowed set
- File paths exist (where `exists: true` in schema)
- Cross-field dependencies satisfied

### Pillar 3: Compliance (from compliance-checker)

| Policy | Enforcement | Source |
|--------|------------|--------|
| No secrets in code | Block PR | secret-detection-agent (E-09) |
| Network safety (`NETWORK_SAFETY_ACK`) | Block PR | AGENTS.md |
| Offline mode for audits (`OFFLINE_MODE_CONFIRM`) | Block PR | AGENTS.md |
| Windows-safe filenames | Block PR | cross-platform-filename-validator |
| No artifacts/ committed | Block PR | .gitignore enforcement |
| ADR for removed files | Warning | archival policy |
| CHANGELOG updated | Warning | CHANGELOG.md check |

## Decision Matrix

```
Input: [owner_approval, config_valid, compliance_clean, ai_agency_policy]

ALL green → APPROVE  (post approval comment)
ANY yellow → WARN    (post warning, allow merge with acknowledgment)
ANY red    → BLOCK   (post block comment, require human review)
```

## AI Agency Policy Integration

The Governance Gate enforces the AI Codebase Agency Policy (`.codex/CODEBASE_AGENCY_POLICY.md`):

```
Required Agent Actions (enforced by this gate):
  ✅ Fix ALL CI/CD failures
  ✅ Fix ALL broken documentation links
  ✅ Fix ALL linting/type errors
  ✅ Leave codebase better than found

Prohibited Statements (blocked if found in PR body):
  ❌ "This is not related to my PR"
  ❌ "These are pre-existing issues"
  ❌ "My PR only adds files to X"
```

## Approval Workflow

```
1. Agent analyzes PR diff
2. Governance Gate checks all 3 pillars
3. If ALL pass → auto-approve (post green comment)
4. If owner-gated file changed → request review from @mbaetiong
5. If compliance fails → block with specific remediation steps
6. If config invalid → block with schema validation errors
```

## GitHub Actions Integration

```yaml
# .github/workflows snippet
- name: Governance Gate
  uses: ./.github/actions/governance-gate
  with:
    owner: mbaetiong
    config-schemas: configs/schemas/
    compliance-rules: .codex/CODEBASE_AGENCY_POLICY.md
    secret-patterns: .github/agents/secret-detection-agent.md
```

## Activation

```
@copilot Use the Unified Governance Gate to check this PR for approval
@copilot Use the Unified Governance Gate to validate configs/training/*.yaml
@copilot Use the Unified Governance Gate to check AI Agency Policy compliance
```

## Output

```json
{
  "governance_status": "APPROVED",
  "pillars": {
    "owner_approval": {"status": "auto_approved", "required_reviewers": []},
    "config_validation": {"status": "valid", "schemas_checked": 3, "errors": []},
    "compliance": {"status": "clean", "violations": [], "warnings": 1}
  },
  "warnings": ["CHANGELOG.md not updated — update recommended"],
  "timestamp": "2026-02-22T00:00:00Z"
}
```

## Cognitive Physics Alignment

| Physics | Application |
|---------|-------------|
| Balance ⚖️ | Three-pillar scoring balances security, config, and ownership concerns |
| Redundancy 🔀 | Multiple governance layers prevent single-point policy bypass |
| Fields 🔄 | Policy feedback loop: violations → agent learning → improved decisions |
| Patterns 👁️ | Recurring violation patterns trigger policy rule refinement |

## S58 Phase 3 Execution (Governance Pillar Wiring)

- ✅ Three-pillar governance contract (owner approval, config validation, compliance) consolidated in one agent spec
- ✅ Deterministic decision flow: each pillar emits a binary PASS/BLOCK signal; first BLOCK short-circuits and posts remediation steps
- ✅ Reporting gate wired: agent emits `artifacts/governance-report.json` on every invocation; CI step uploads as PR artifact
- ✅ Workflow-level invocation standardised via `governance-gate` composite action (see GitHub Actions Integration above)
- ✅ Deferral-language guard integrated: compliance pillar scans PR body for prohibited phrases before approval is emitted

### Workflow Reporting Gate

```yaml
# .github/workflows snippet — governance report upload
- name: Upload Governance Report
  if: always()
  uses: actions/upload-artifact@v5
  with:
    name: governance-report
    path: artifacts/governance-report.json
    retention-days: 30
```

### Decision Flow (Phase 3)

```
PR push / workflow_dispatch
        │
        ▼
┌───────────────────┐   BLOCK   ┌────────────────────────┐
│  Owner Approval   ├──────────▶│  Post remediation steps │
│  Pillar           │           │  and block merge         │
└───────┬───────────┘           └────────────────────────┘
        │ PASS
        ▼
┌───────────────────┐   BLOCK   ┌────────────────────────┐
│  Config Validator │──────────▶│  Emit schema errors      │
│  Pillar           │           │  and block merge         │
└───────┬───────────┘           └────────────────────────┘
        │ PASS
        ▼
┌───────────────────┐   BLOCK   ┌────────────────────────┐
│  Compliance       │──────────▶│  List violations with    │
│  Checker Pillar   │           │  CODEBASE_AGENCY_POLICY  │
└───────┬───────────┘           └────────────────────────┘
        │ PASS
        ▼
  APPROVED — emit governance-report.json
```

## Related Agents

- **owner-approval-guard** (deprecated — merged into this agent)
- **config-validator** (deprecated — merged into this agent)
- **unified-security-scanner** (M-01) — secret detection for compliance pillar
- **ci-triage-pipeline-agent** (M-03) — CI failure compliance check
- **agent-iq-scoring-gate** (E-12) — governance score contributes to IQ signal
