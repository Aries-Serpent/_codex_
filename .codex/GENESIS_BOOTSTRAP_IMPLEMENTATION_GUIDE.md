# PHASE 2.2: Genesis Bootstrap Implementation Guide

**Document ID:** GENESIS_BOOTSTRAP_IMPLEMENTATION_GUIDE  
**Date:** 2026-06-22T03:18:36Z  
**Companion to:** PHASE_2_2_GENESIS_BOOTSTRAP_AUDIT.md  
**Authority:** @mbaetiong

---

## Overview

This guide provides the **code-level implementation details** for Phase 2.2 genesis-bootstrap.yml enhancements based on the audit findings.

**Prerequisite:** Read PHASE_2_2_GENESIS_BOOTSTRAP_AUDIT.md first for full context.

---

## Implementation Roadmap

### Phase 2.2 Deliverables

| Item | Status | Effort | Notes |
|------|--------|--------|-------|
| **GENESIS_DRY_RUN input** | 📋 Design | 1 hour | Add to workflow inputs |
| **Token health checks** | 📋 Design | 2 hours | Call TokenCircuitBreaker |
| **JSON logging** | 📋 Design | 3 hours | Implement machine-readable logs |
| **WEC integration** | 📋 Design | 1 hour | Update PR template |
| **Approval audit trail** | 📋 Design | 1.5 hours | Create wec_approval_log.md |
| **Testing & validation** | 📋 Design | 2 hours | Dry-run and prod tests |
| **Documentation** | 📋 Design | 1.5 hours | Operational runbooks |

**Total Estimated Effort:** ~12 hours

---

## Step 1: Add GENESIS_DRY_RUN Workflow Input

**File:** `.github/workflows/genesis-bootstrap.yml` (to be created)

**Edit 1: Add workflow input**

```yaml
on:
  workflow_dispatch:
    inputs:
      genesis_validation:
        description: 'Confirm Genesis Protocol completion'
        required: true
        type: boolean
        default: false
      human_admin:
        description: 'Human Admin username for audit'
        required: true
        type: string
        default: 'mbaetiong'
      genesis_dry_run:  # 🆕 NEW INPUT
        description: 'Run in dry-run mode (log only, no mutations)'
        required: false
        type: boolean
        default: true  # Safe default!
```

**Edit 2: Map to environment variable**

```yaml
env:
  GENESIS_DRY_RUN: ${{ github.event.inputs.genesis_dry_run || 'true' }}
  # ... existing env vars ...
```

---

## Step 2: Add Token Health Checking Step

**Insert before "Generate genesis validation JSON" step**

```yaml
      - name: Validate token health
        run: |
          echo "🔐 Validating token health..."
          python3 << 'PYTHON_EOF'
          import json
          import sys
          from pathlib import Path

          # Add scripts/ci to path for imports
          sys.path.insert(0, 'scripts/ci')

          try:
              # Import TokenCircuitBreaker from Phase 2.1
              from autonomy.token_broker import (
                  TokenCircuitBreaker,
                  TokenHealthChecker
              )

              # Initialize health checker
              checker = TokenHealthChecker()

              # Check MASTER KEY
              master_status = checker.check_jwt_health('${{ secrets.CODEX_MASTER_KEY }}')
              backup_status = checker.check_jwt_health('${{ secrets.CODEX_BACKUP_KEY }}')

              # Prepare report
              report = {
                  "master_key": {
                      "status": master_status.name,
                      "valid": master_status.name == "HEALTHY"
                  },
                  "backup_key": {
                      "status": backup_status.name,
                      "valid": backup_status.name == "HEALTHY"
                  }
              }

              # Write for later steps
              Path('token_health.json').write_text(json.dumps(report, indent=2))

              # Check circuit breaker
              if master_status.name != "HEALTHY":
                  print(f"⚠️  Master key status: {master_status.name}")
                  if backup_status.name == "HEALTHY":
                      print("✅ Backup key healthy - will use failover")
                  else:
                      print("❌ Both tokens unhealthy!")
                      sys.exit(1)
              else:
                  print("✅ Token health: HEALTHY")

          except Exception as e:
              print(f"❌ Token validation failed: {e}")
              sys.exit(1)
          PYTHON_EOF
```

---

## Step 3: Implement JSON Logging

**Replace "Generate genesis validation JSON" with enhanced version:**

```yaml
      - name: Generate machine-readable audit log
        run: |
          echo "📝 Creating audit log entry..."
          python3 << 'PYTHON_EOF'
          import json
          from datetime import datetime, timezone
          from pathlib import Path

          # Load token health (if available)
          token_health = {}
          try:
              token_health = json.loads(Path('token_health.json').read_text())
          except:
              token_health = {"status": "unknown"}

          # Create audit entry
          audit_entry = {
              "event": {
                  "id": "genesis-bootstrap-${{ github.run_id }}",
                  "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
                  "event_type": "BOOTSTRAP_START"
              },
              "execution_context": {
                  "workflow_run_id": ${{ github.run_id }},
                  "workflow_name": "genesis-bootstrap.yml",
                  "trigger": "${{ github.event_name }}",
                  "actor": "${{ github.actor }}",
                  "dry_run_mode": ${{ env.GENESIS_DRY_RUN == 'true' and 'true' or 'false' }},
                  "phase": "2.2",
                  "repo_id": "${{ env.CODEX_REPO_ID }}",
                  "org": "${{ env.CODEX_ORG_NAME }}",
                  "repo": "_codex_"
              },
              "token_health": token_health,
              "validation": {
                  "required_files": [
                      ".codex/autonomous_agent.yaml",
                      ".codex/guardrails.md",
                      ".codex/change_log.md",
                      "scripts/autonomous_agent.py"
                  ],
                  "timestamp": datetime.now(timezone.utc).isoformat() + "Z"
              }
          }

          # Write to JSON log (append mode)
          log_file = Path('.codex/audit/genesis_bootstrap_log.json')
          log_file.parent.mkdir(parents=True, exist_ok=True)

          # Append entry (one JSON object per line)
          log_file.write_text(
              log_file.read_text() if log_file.exists() else ""
          )
          with open(log_file, 'a') as f:
              json.dump(audit_entry, f)
              f.write('\n')

          print("✅ Audit entry written")
          print(json.dumps(audit_entry, indent=2))
          PYTHON_EOF
```

---

## Step 4: Implement Dry-Run Logic for Mutations

**Wrap destructive operations:**

```yaml
      - name: Conditional secret update (dry-run safe)
        if: env.GENESIS_DRY_RUN == 'false'  # Only run if NOT dry-run
        run: |
          echo "🔄 [PRODUCTION] Updating secrets..."
          # Your mutation operations here
          # Example: gh secret set CODEX_MASTER_KEY ...
          echo "✅ Secrets updated"

      - name: Simulate secret update (dry-run)
        if: env.GENESIS_DRY_RUN == 'true'  # Only run if dry-run
        run: |
          echo "📋 [DRY-RUN] Would update secrets..."
          echo "[DRY-RUN] CODEX_MASTER_KEY: Would be rotated"
          echo "[DRY-RUN] CODEX_BACKUP_KEY: Would be refreshed"
          echo "✅ Dry-run simulation complete"
```

---

## Step 5: Record WEC Approval Audit

**Insert after changelog append:**

```yaml
      - name: Record WEC approval audit
        run: |
          mkdir -p .codex/audit
          cat >> .codex/audit/wec_approval_log.md << 'EOF'

          ## Genesis Bootstrap - ${{ github.run_id }}

          **Timestamp:** $(date -u +"%Y-%m-%dT%H:%M:%SZ")

          **Approval Context:**
          - PR/Trigger: ${{ github.ref }}
          - Actor: ${{ github.actor }}
          - Run ID: ${{ github.run_id }}
          - Dry-Run Mode: ${{ env.GENESIS_DRY_RUN }}

          **WEC Approval:** Checked via workflow-execution-gate.yml

          EOF
```

---

## Step 6: Update PR Template for WEC

**File:** `.github/pull_request_template.md`

**Add to WEC section:**

```markdown
## 🔄 Workflow Execution Checklist

Workflows can be skipped/dispatched by updating these checkboxes:

### Core Governance (Always Required)
- [x] pre-merge-validation.yml        ← Blocks merge if unchecked
- [x] comment-review-gate.yml         ← Blocks merge if unchecked
- [x] deferral-language-gate.yml      ← Blocks merge if unchecked
- [x] agent-auth-delegation.yml       ← Blocks merge if unchecked
- [x] workflow-execution-gate.yml     ← Orchestrator (always required)
- [x] cost-gate.yml                   ← Blocks merge if unchecked
- [x] genesis-bootstrap.yml           ← 🆕 PHASE 2.2 (secret rotation)

### Optional Workflows
- [ ] copilot-agent-checkin.yml       ← Optional (agent check-in)
- [ ] copilot-agent-session-done.yml  ← Optional (completion signal)
- [ ] copilot-iterative-self-healing.yml ← Optional (auto-heal CI)
```

---

## Step 7: Update workflow-execution-gate.yml

**File:** `.github/workflows/workflow-execution-gate.yml`

**Add genesis-bootstrap to always-required list:**

```python
# In the workflow's Python/bash logic:
_WEC_ALWAYS_REQUIRED = [
    "pre-merge-validation.yml",
    "comment-review-gate.yml",
    "deferral-language-gate.yml",
    "agent-auth-delegation.yml",
    "workflow-execution-gate.yml",  # Self
    "cost-gate.yml",
    "genesis-bootstrap.yml",  # 🆕 ADD THIS
]
```

---

## Testing & Validation

### Test 1: Dry-Run Mode (Safe)

```bash
# Trigger workflow via GitHub UI:
# 1. Go to Actions → genesis-bootstrap.yml
# 2. Click "Run workflow"
# 3. Set:
#    - genesis_validation: ✓ (checked)
#    - human_admin: mbaetiong
#    - genesis_dry_run: ✓ (checked - DRY-RUN MODE)
# 4. Click "Run workflow"

# Expected results:
# ✅ No state changes
# ✅ JSON log created at .codex/audit/genesis_bootstrap_log.json
# ✅ Changelog appended
# ✅ Artifact uploaded (genesis-validation-report)
```

### Test 2: Production Mode (Controlled)

```bash
# Trigger workflow via GitHub UI:
# 1. Go to Actions → genesis-bootstrap.yml
# 2. Click "Run workflow"
# 3. Set:
#    - genesis_validation: ✓ (checked)
#    - human_admin: mbaetiong
#    - genesis_dry_run: ✗ (UNCHECKED - PRODUCTION MODE)
# 4. Click "Run workflow"

# Expected results:
# ✅ All operations performed
# ✅ Secrets potentially updated (if designed)
# ✅ JSON log records production mode
# ✅ Immutable audit trail created
```

---

## Validation Checklist

### Pre-Activation

- [ ] Token health checking works
- [ ] JSON logging creates valid JSON
- [ ] Dry-run mode prevents mutations
- [ ] WEC checkbox approval flows correctly
- [ ] Approval audit trail captures events
- [ ] Changelog remains immutable

### Post-Activation

- [ ] First dry-run test passes
- [ ] First production test passes (on dev/test branch)
- [ ] Logs are parseable by downstream tools
- [ ] No existing workflows broken
- [ ] Documentation matches implementation

---

## Troubleshooting

### Issue: Token Health Check Fails

**Symptom:** Workflow stops at token validation step

**Resolution:**
1. Verify CODEX_MASTER_KEY secret exists (Settings → Secrets)
2. Verify CODEX_BACKUP_KEY secret exists
3. Check token format: should start with `ghp_` (PAT) or `eyJ` (JWT)
4. Run `scripts/ci/validate_token_setup.py` locally

### Issue: JSON Logging Not Created

**Symptom:** `.codex/audit/genesis_bootstrap_log.json` doesn't exist

**Resolution:**
1. Check if `.codex/audit/` directory exists
2. Verify Python `json` module available
3. Check workflow logs for Python errors
4. Ensure write permissions to `.codex/audit/`

### Issue: WEC Not Detecting genesis-bootstrap.yml

**Symptom:** Workflow checkbox doesn't appear in WEC section

**Resolution:**
1. Verify PR template updated correctly
2. Check workflow-execution-gate.yml includes genesis-bootstrap.yml
3. Refresh PR page (cache issue)
4. Ensure checkbox format is `- [x] genesis-bootstrap.yml`

---

## Reference Implementation Files

### New/Modified Files

| File | Change Type | Purpose |
|------|-------------|---------|
| `.github/workflows/genesis-bootstrap.yml` | CREATE | Restore and enhance workflow |
| `.codex/audit/genesis_bootstrap_log.json` | AUTO-CREATED | Machine-readable log |
| `.codex/audit/wec_approval_log.md` | AUTO-CREATED | Approval audit trail |
| `.github/pull_request_template.md` | MODIFY | Add WEC checkbox |
| `.github/workflows/workflow-execution-gate.yml` | MODIFY | Add to always-required |

### Related Phase 2.1 Files

| File | Purpose |
|------|---------|
| `src/codex/autonomy/token_broker.py` | TokenCircuitBreaker + TokenHealthChecker |
| `scripts/ci/validate_token_setup.py` | Token validation script |
| `.codex/PHASE_2_1_SECRET_INJECTION_DESIGN.md` | Secret setup procedure |

---

## Success Metrics

**Phase 2.2 Success = All Green:**

```
✅ Audit Document Created (PHASE_2_2_GENESIS_BOOTSTRAP_AUDIT.md)
✅ Implementation Guide Provided (this document)
✅ GENESIS_DRY_RUN Input Added
✅ Token Health Checking Integrated
✅ JSON Audit Logging Implemented
✅ WEC Integration Complete
✅ Approval Audit Trail Functional
✅ Dry-Run Tests Pass
✅ Production Tests Pass
✅ Zero Breaking Changes
```

---

**Status:** 🟢 **READY FOR IMPLEMENTATION**  
**Next Step:** Submit to @mbaetiong for approval and gate-controlled activation
