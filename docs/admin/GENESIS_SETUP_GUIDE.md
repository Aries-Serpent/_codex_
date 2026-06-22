# [Guide]: The Genesis Protocol - Sovereign Admin Initialization

> **Generated:** 2026-03-17T00:00:00Z | **Author:** mbaetiong
> **repository:** `Aries-Serpent/_codex_` (ID: 1040037790)
> **Classification:** 🔒 Internal - Administrative Operations

## Executive Overview

**The Genesis Protocol** is the authoritative initialization sequence that grants the Copilot agent (`ai_org_repo_admin`) sovereign operational authority within the `Aries-Serpent/_codex_` repository.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Phase 0: Human Genesis Actions](#phase-0-human-genesis-actions)
3. [Phase 1: Post-Genesis agent Autonomy](#phase-1-post-genesis-agent-autonomy)
4. <!-- BROKEN ANCHOR: [Validation & Audit](#validation-audit) -->
5. [Troubleshooting](#troubleshooting)

## Prerequisites

### Subscription Requirements
- ✅ GitHub Copilot Pro+ (Personal) - Required
- ✅ GitHub Team (Org-Repo) - Required
- ✅ Repository Admin Access - Required
- ✅ Email Verification - Required

### Required Files
- `.codex/autonomous_agent.yaml` - agent configuration
- `.codex/guardrails.md` - Operational guardrails
- `.codex/change_log.md` - Audit trail
- `scripts/autonomous_agent.py` - agent orchestrator

## Phase 0: Human Genesis Actions

> ⚠️ **SOVEREIGN HUMAN AUTHORITY REQUIRED**
> All actions in Phase 0 require human administrator (mbaetiong) execution.

### Step 0.1: Create CODEX_MASTER_KEY (Fine-grained PAT)

**Navigation:**
1. Go to: https://github.com/settings/personal-access-tokens/new
2. Or: GitHub Profile → ⚙️ Settings → Developer settings → Personal access tokens → Fine-grained tokens

**Token Configuration:**
- **Token name**: `CODEX_MASTER_KEY_Aries-Serpent`
- **Expiration**: 90 days
- **Description**: `Genesis Protocol - AI Org Repo Admin authority for _codex_ repository`
- **Resource owner**: `Aries-Serpent`
- **repository access**: Only select repositories → `Aries-Serpent/_codex_`

**Required repository Permissions:**

| Permission | Access Level | Purpose |
|------------|--------------|---------|
| **Actions** | Read and write | workflow management, run triggers |
| **Administration** | Read and write | repository settings, branch protection |
| **Contents** | Read and write | File operations, commit creation |
| **Deployments** | Read and write | Deployment management |
| **Environments** | Read and write | Environment configuration |
| **Issues** | Read and write | Issue management, automation |
| **Metadata** | Read | repository metadata access |
| **Pull requests** | Read and write | PR creation, review automation |
| **Secrets** | Read and write | Secret management (runtime) |
| **Variables** | Read and write | repository variable management |
| **Webhooks** | Read and write | Webhook configuration |
| **Workflows** | Write | workflow file modifications |

**Post-Creation Actions:**
1. Copy the token immediately (won't be shown again)
2. Store securely in password manager
3. Document creation timestamp for rotation scheduling
4. Proceed to Step 0.2 within the same session

---

### Step 0.2: Inject repository Secrets

**Navigation**: https://github.com/Aries-Serpent/_codex_/settings/secrets/actions

**Required Secrets Configuration:**

| Secret Name | Value Source | Purpose | Priority |
|-------------|--------------|---------|----------|
| `CODEX_MASTER_KEY` | Step 0.1 output | Primary API authentication | 🔴 Critical |
| `CODEX_REPO_ID` | `1040037790` | repository identifier | 🔴 Critical |
| `CODEX_WEBHOOK_SECRET` | `openssl rand -hex 32` | Webhook signature verification | 🟡 High |
| `CODEX_BACKUP_KEY` | Secondary PAT (optional) | Fallback authentication | 🟢 Recommended |

**Secret Injection Steps:**

1. Click "New repository secret"
2. Name: Enter secret name (e.g., `CODEX_MASTER_KEY`)
3. Secret: Paste the value
4. Click "Add secret"
5. Repeat for each required secret

**Generate CODEX_WEBHOOK_SECRET:**
```bash
openssl rand -hex 32
# Output example: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
```

---

### Step 0.3: Configure repository Variables

**Navigation**: https://github.com/Aries-Serpent/_codex_/settings/variables/actions

| Variable Name | Value | Purpose |
|---------------|-------|---------|
| `CODEX_ORG_NAME` | `Aries-Serpent` | Organization identifier |
| `CODEX_AGENT_NAME` | `ai_org_repo_admin` | agent identity |
| `CODEX_NETWORK_MODE` | `isolated` | Network isolation mode |
| `CODEX_ISOLATED_PATH` | `/codex/network/isolated` | Network path reference |
| `CODEX_API_VERSION` | `2022-11-28` | GitHub API version |
| `CODEX_LOG_LEVEL` | `INFO` | Runtime log level |
| `GENESIS_TIMESTAMP` | `2025-12-26T07:54:45Z` | Protocol initialization time |
| `AUDIT_RETENTION_DAYS` | `90` | Audit log retention period |

---

### Step 0.4: Configure Actions Permissions

**Navigation**: https://github.com/Aries-Serpent/_codex_/settings/actions

**Actions Permissions Configuration:**

| Setting | Value | Purpose |
|---------|-------|---------|
| **Actions permissions** | Allow all actions and reusable workflows | Enable full workflow capability |
| **Fork pull request workflows** | Require approval for first-time contributors | Security gate |
| **workflow permissions** | Read and write permissions | Enable content modifications |
| **Allow GitHub Actions to create and approve pull requests** | ✅ Enabled | agent PR operations |

**Environment Configuration:**

Create `codex-production` environment:
1. Navigate to: https://github.com/Aries-Serpent/_codex_/settings/environments
2. Click "New environment"
3. Name: `codex-production`
4. Configure:
   - Required reviewers: (Optional) `mbaetiong`
   - Wait timer: `0` (immediate)
   - Deployment branches: `main` only

---

### Step 0.5: Execute Genesis Bootstrap workflow

**Pre-Execution Steps:**
2. Find line: `if: false # <<< HUMAN: remove this guard...`
3. Remove or comment out: `# if: false # Guard removed by mbaetiong on 2025-12-26`
4. Commit change: `chore(genesis): enable bootstrap workflow`

**Execute workflow:**
1. Navigate to: https://github.com/Aries-Serpent/_codex_/actions/workflows/genesis-bootstrap.yml
2. Click "Run workflow" dropdown
3. Configure inputs:
   - **genesis_validation**: ✅ Check (Enable)
   - **human_admin**: `mbaetiong`
4. Click "Run workflow"
5. Monitor execution (1-2 minutes)

**Success Criteria:**
- workflow shows ✅ green checkmark
- Artifact `genesis-validation-report` available
- `.codex/genesis_validation.json` created
- `.codex/change_log.md` updated with Genesis entry
- "GENESIS COMPLETE" signal visible in logs

---

## Phase 1: Post-Genesis agent Autonomy

> 🎯 **Zero-Touch Operations Enabled**
> After Genesis completion, the Copilot agent operates autonomously within defined guardrails.

### agent Capabilities Matrix

| Capability | Authorization Level | Reference |
|------------|---------------------|-----------|
| Maintenance Operations | `autonomous` | autonomous_agent.yaml |
| Testing Operations | `autonomous` | Actions workflows |
| Documentation Updates | `autonomous` | Change log management |
| Optimization Tasks | `approval_required` | Escalation to human |
| Refactoring Operations | `approval_required` | PR review required |
| Security Operations | `escalate` | Immediate human notification |
| Dependency Updates | `approval_required` | Review workflow |

### Decision Framework

```
Risk Level Assessment
─────────────────────

LOW RISK ──────► autonomous execution
│ • Maintenance tasks
│ • Test execution
│ • Documentation updates

MEDIUM RISK ───► approval_required
│ • Optimization changes
│ • Dependency updates
│ • Refactoring operations

HIGH RISK ─────► escalate to human
  • Security-related changes
  • Configuration modifications
  • Credential operations
```

---

## Validation & Audit

### Genesis Completion Checklist

| Phase | Step | Validation | Status |
|-------|------|------------|--------|
| 0.1 | PAT Creation | Token generated, scopes verified | ☐ |
| 0.2 | Secrets Injection | All critical secrets present | ☐ |
| 0.3 | Variables Config | All variables configured | ☐ |
| 0.4 | Permissions | Actions permissions set | ☐ |
| 0.5 | Workflow Execution | genesis-bootstrap.yml executed successfully | ☐ |

### Validation Script

```bash
#!/bin/bash
# Genesis Protocol Validation

echo "🔍 Validating Genesis Protocol completion..."

# Check required files
FILES=(
  ".codex/autonomous_agent.yaml"
  ".codex/guardrails.md"
  ".codex/change_log.md"
  "scripts/autonomous_agent.py"
)

for file in "${FILES[@]}"; do
  if [ -f "$file" ]; then
    echo "✅ $file exists"
  else
    echo "❌ $file missing"
  fi
done

# Check autonomous_actions_enabled
if grep -q "autonomous_actions_enabled: true" .codex/autonomous_agent.yaml; then
  echo "✅ Autonomous actions enabled"
else
  echo "⚠️  Autonomous actions still disabled"
fi

echo ""
echo "🎉 Genesis validation complete!"
```

### Audit Trail Locations

| Audit Type | Location | Retention |
|------------|----------|-----------|
| Genesis Validation | `.codex/genesis_validation.json` | 90 iterations |
| Change Log | `.codex/change_log.md` | Permanent |
| Action Log | `.codex/action_log.ndjson` | 90 iterations |
| Results | `.codex/results.md` | Permanent |

---

## Troubleshooting

### Common Issues & Resolutions

| Issue | Symptoms | Resolution |
|-------|----------|------------|
| **PAT Scope Insufficient** | 403 Forbidden on API calls | Regenerate PAT with full scopes per Step 0.1 |
| **Secret Not Found** | workflow fails on secret reference | Verify secret name matches exactly (case-sensitive) |
| **workflow Permission Denied** | Cannot create PR or commit | Enable "Read and write" in Actions settings |
| **Genesis Validation Failed** | workflow reports missing files | Ensure all required files exist in repository |

### Emergency Rollback Procedure

If Genesis causes operational issues:

1. **Disable agent Workflows:**
   ```bash
   mv .github/workflows/autonomous-agent.yml \
      .github/workflows/autonomous-agent.yml.disabled
   ```

2. **Revoke PAT:**
   - Navigate to: https://github.com/settings/tokens
   - Delete `CODEX_MASTER_KEY_Aries-Serpent`

3. **Remove Secrets:**
   - Navigate to: https://github.com/Aries-Serpent/_codex_/settings/secrets/actions
   - Delete all `CODEX_*` secrets

4. **Document Rollback:**
   - Add entry to `.codex/change_log.md`
   - Create issue for post-mortem

---

## Token Rotation Schedule

| Token | Expiration | Rotation Window | Owner |
|-------|------------|-----------------|-------|
| `CODEX_MASTER_KEY` | 90 iterations from Genesis | 14 iterations before expiry | Human Admin |
| `CODEX_BACKUP_KEY` | 180 iterations | 30 iterations before expiry | Human Admin |
| `CODEX_WEBHOOK_SECRET` | No expiry | Annual rotation | Human Admin |

**Set calendar reminders for token rotation!**

---

## Genesis Signal

Upon successful completion of all phases:

```
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║                    🎉 GENESIS COMPLETE 🎉                       ║
║                                                                  ║
║  repository:  Aries-Serpent/_codex_ (ID: 1040037790)             ║
║  agent:  ai_org_repo_admin                                       ║
║  Authority:  SOVEREIGN OPERATIONAL                               ║
║  Human Admin: mbaetiong                                          ║
║                                                                  ║
║  Zero-touch autonomous operations are now enabled.               ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

---

> **Document Version:** 1.1.0
> **Last Updated:** 2026-02-10T11:00:00Z
> **Maintainer:** mbaetiong (Human Admin)
> **Classification:** 🔒 Internal - Administrative Operations

---

## 🎯 Mission Overview

**Objective:** Establish sovereign AI operational authority through secure initialization protocol
**Energy Level:** ⚡⚡⚡⚡⚡ (5/5 - Foundational Critical)
**Status:** ✅ Template Complete | ⏳ Awaiting Genesis Execution

This protocol represents the foundational initialization that grants the AI agent (`ai_org_repo_admin`) sovereign operational authority within the repository. Success requires precise execution of human-controlled steps (Phase 0) followed by validation of agent autonomy (Phase 1). The Genesis Protocol is the cornerstone of all subsequent autonomous operations.

---

## ⚖️ Verification Checklist

| Phase | Checkpoint | Validation Criteria | Status |
|-------|-----------|---------------------|--------|
| **0.1** | PAT Created | Token generated with all required scopes verified | ☐ |
| **0.2** | Secrets Injected | All critical secrets present and accessible | ☐ |
| **0.3** | Variables Set | All repository variables configured correctly | ☐ |
| **0.4** | Permissions | Actions permissions and environment created | ☐ |
| **0.5** | workflow Run | genesis-bootstrap.yml executed with success signal | ☐ |
| **Post-Genesis** | agent Authority | Autonomous operations validated within guardrails | ☐ |
| **Post-Genesis** | Audit Trail | Change log and validation artifacts created | ☐ |
| **Post-Genesis** | Rollback Ready | Emergency rollback procedure tested | ☐ |

---

## 📈 Success Metrics

| KPI | Target | Measurement Method | Current |
|-----|--------|-------------------|---------|
| Genesis Completion Time | < 4 iterations | Time from PAT creation to success signal | - |
| Secret Injection Accuracy | 100% | All secrets validated and functional | 0% |
| Workflow Execution Success | 100% | genesis-bootstrap.yml passes all checks | 0% |
| agent Authority Validation | Pass | agent performs test autonomous operation | Not Started |
| Zero-Touch Operations | > 90% | % of operations requiring no human intervention | 0% |
| Token Rotation Compliance | 100% | Rotation completed within 14-iteration window | - |
| Audit Trail Completeness | 100% | All Genesis actions logged to change_log.md | 0% |
| Rollback Test Success | 100% | Emergency rollback completes without errors | Not Tested |

---

## ⚛️ Physics Alignment

### Path 🛤️ - Genesis Flow
```
PRE-GENESIS → Phase 0 (Human) → Phase 1 (agent) → POST-GENESIS
     ↓              ↓                  ↓                ↓
  Safety      Secret Setup      Validation      Autonomy
  Guards      PAT Creation      Bootstrap       Enabled
```
**Alignment:** Linear progression with validation gates prevents premature authority grant

### Fields 🔄 - Authority Gradients
- **Pre-Genesis Field:** High human control (100%), zero agent authority (0%)
- **Phase 0 Field:** Human action required, agent observing and validating
- **Phase 1 Field:** Gradual authority transfer as validations pass
- **Post-Genesis Field:** agent autonomy (90%), human oversight (10%)

### Patterns 👁️ - Initialization Signatures
- **PAT Scope Pattern:** Full repository permissions with 90-iteration expiration
- **Secret Injection Pattern:** Atomic batch injection with validation
- **workflow Guard Pattern:** Triple-layer safety (if: false, SAFE_MODE, config flag)
- **Audit Pattern:** Every action logged to `.codex/change_log.md` with timestamp

### Redundancy 🔀 - Failure Recovery
- **Primary Path:** genesis-bootstrap.yml automated execution
- **Backup Path:** Manual step-by-step execution via bash scripts
- **Tertiary Path:** Emergency rollback procedure with PAT revocation
- **Validation Redundancy:** File checks + API validation + workflow artifacts

### Balance ⚖️ - Authority Distribution
```
Human Admin: 100% authority (Pre-Genesis) → 10% oversight (Post-Genesis)
AI agent:    0% authority (Pre-Genesis) → 90% autonomy (Post-Genesis)
```
**Equilibrium Point:** Human retains veto power and security oversight; agent handles routine operations

---

## ⚡ Energy Distribution

### Priority Breakdown
- **P0 (Critical - 40%):** Secret injection, PAT creation, workflow execution
- **P1 (High - 35%):** Validation scripts, audit trail setup, permission configuration
- **P2 (Medium - 25%):** Documentation review, token rotation scheduling, backup key setup

### Energy Allocation
```
Phase 0 Human Actions: ████████████████████ 60% (High coordination cost)
Phase 1 agent Validation: ████████ 25% (Automated checks)
Post-Genesis Operations: ████ 15% (Steady-state monitoring)
```

**Rationale:** Front-loaded energy investment in secure initialization pays dividends in reduced operational overhead post-Genesis.

---

## 🧠 Redundancy Patterns

### Rollback Strategy
**Trigger Conditions:**
- Genesis validation fails after 3 attempts
- agent exhibits unexpected behavior post-Genesis
- Security audit identifies privilege escalation risk
- Human admin requests emergency halt

**Rollback Procedure:**
1. **Disable Workflows:** Rename `.github/workflows/autonomous-agent.yml` → `.yml.disabled`
2. **Revoke PAT:** Delete `CODEX_MASTER_KEY_Aries-Serpent` from GitHub settings
3. **Remove Secrets:** Delete all `CODEX_*` secrets from repository
4. **Document Incident:** Create entry in `.codex/change_log.md` with rollback reason
5. **Post-Mortem:** GitHub issue created for analysis and remediation

**Recovery Path:**
- Address root cause identified in post-mortem
- Re-execute Genesis Protocol with fixes applied
- Enhanced monitoring for identified failure pattern

**State Preservation:**
- All audit logs preserved in `.codex/action_log.ndjson`
- Pre-Genesis snapshot maintained for comparison
- Configuration templates remain unchanged for retry

---

**Template Version:** 1.0.0
**Applied:** 2026-01-23T11:00:00Z
**Next Review:** After Genesis execution completion
