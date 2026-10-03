# CI Monitoring & Auto-Remediation Operating Guide
## Commit 194f6af0 | PR #5328

**Last Updated:** 2026-07-16T23:47:00Z  
**Status:** 🟢 **ACTIVE & READY**

---

## Quick Reference

### Initial Assessment ✅

Your commit (194f6af0) is **COMPLIANT** with critical governance requirements:
- ✅ **REQ-4:** AGENT_ACCOUNTABILITY_REPORT.md is updated
- ✅ **REQ-5:** CHANGELOG.md is updated

### What's Been Set Up

I've created a **comprehensive automated CI failure monitoring and remediation system** that includes:

1. **Auto-Remediation Script** — `.codex/scripts/auto_remediate_194f6af0.sh`
2. **Workflow Monitoring Daemon** — `.codex/scripts/monitor_194f6af0_workflows.sh`
3. **Tracking Document** — `.codex/CI_REMEDIATION_194F6AF0.md`
4. **This Operating Guide** — You're reading it!

---

## Files & Tools Created

### 1. Auto-Remediation Script
**Location:** `.codex/scripts/auto_remediate_194f6af0.sh`  
**Size:** ~9 KB  
**Executable:** ✅ YES

**Purpose:** Automatically detect workflow failure patterns and apply targeted fixes.

**Usage:**

```bash
# Check patterns WITHOUT making changes
bash .codex/scripts/auto_remediate_194f6af0.sh --check-only

# Simulate fixes (dry-run mode)
bash .codex/scripts/auto_remediate_194f6af0.sh --dry-run

# Apply all detected fixes
bash .codex/scripts/auto_remediate_194f6af0.sh

# Combine flags
bash .codex/scripts/auto_remediate_194f6af0.sh --check-only --dry-run
```

**What It Does:**

1. **Phase 1: Detection** — Scans for 8 failure patterns (RP-001 through RP-008)
   - Checks REQ-4 compliance (AGENT_ACCOUNTABILITY_REPORT.md)
   - Checks REQ-5 compliance (CHANGELOG.md)
   - Validates WEC section in PR body
   - Detects WEC format issues
   - Attempts to detect approval token, cost, and rate limit issues

2. **Phase 2: Remediation** — Applies targeted fixes
   - Runs `session_wrapup_autofix.py --auto-update` for governance files
   - Runs `wec_enforcer.py --validate-body --fix` for WEC issues
   - Stages changed files

3. **Phase 3: Commit & Push** — Commits with SHA reference
   - Creates descriptive commit message including detected patterns
   - References the commit SHA (194f6af0)
   - Pushes with `--force-with-lease` safety flag

**Logs:**
- All operations logged to `.codex/remediation_logs_194f6af0/`
- Individual phase logs: `rp001_autofix.log`, `rp002_autofix.log`, `wec_enforcer.log`, `commit.log`, `push.log`

---

### 2. Workflow Monitoring Daemon
**Location:** `.codex/scripts/monitor_194f6af0_workflows.sh`  
**Size:** ~6 KB  
**Executable:** ✅ YES

**Purpose:** Continuously monitor GitHub workflows for failures and auto-trigger remediation.

**Usage:**

```bash
# Start monitoring with default settings (30s poll interval, 1-hour timeout)
bash .codex/scripts/monitor_194f6af0_workflows.sh

# Custom poll interval (60s) and timeout (2 hours)
bash .codex/scripts/monitor_194f6af0_workflows.sh 60 7200

# Run in background (recommended for CI systems)
nohup bash .codex/scripts/monitor_194f6af0_workflows.sh &
```

**How It Works:**

1. Polls GitHub Actions API every 30 seconds (configurable)
2. Looks for workflow runs on commit 194f6af0
3. When a failure is detected:
   - Logs the failure
   - Calls `auto_remediate_194f6af0.sh` automatically
   - Updates `.codex/CI_REMEDIATION_194F6AF0.md` tracking file
4. Continues polling until timeout or completion

**Logs:**
- Main log: `.codex/workflow_monitor_194f6af0.log`
- Remediation logs: `.codex/remediation_logs_194f6af0/`

**Fallback Mode:**
- If GitHub API is unavailable (token issue), the daemon switches to local compliance checks
- Checks REQ-4 and REQ-5 by reading git history
- Triggers remediation if local checks fail

---

### 3. Tracking Document
**Location:** `.codex/CI_REMEDIATION_194F6AF0.md`  
**Size:** ~12 KB  
**Format:** Markdown

**Contains:**
- Current status and workflow information
- Detection results for all 8 patterns (RP-001 through RP-008)
- Complete remediation strategies with command-by-command procedures
- Fallback (manual) procedures for each pattern
- Progress checklist
- Links to related documentation

**Updated By:**
- Initial setup (current session)
- Monitoring daemon (when failures detected and remediated)
- Manual updates (if escalation needed)

---

## Pattern Reference Summary

| ID | Name | Pattern | Auto-Fix | Blocking | Status |
|----|------|---------|----------|----------|--------|
| RP-001 | WF-001 | REQ-4: AGENT_ACCOUNTABILITY_REPORT.md missing | ✅ AUTO | ✅ YES | ✅ COMPLIANT |
| RP-002 | WF-002 | REQ-5: CHANGELOG.md not updated | ✅ AUTO | ✅ YES | ✅ COMPLIANT |
| RP-003 | WF-003 | WEC state loss (section stripped) | ⚠️ PARTIAL | ✅ YES | ⏳ PENDING |
| RP-004 | WF-004 | WEC format invalid (checkbox syntax) | ✅ AUTO | ✅ YES | ⏳ PENDING |
| RP-005 | WF-005 | Approval token insufficient | ❌ NO | ❌ NO | ⏳ PENDING | <!-- pragma: allowlist secret -->
| RP-006 | WF-006 | REQUIRED WEC items unchecked | ⚠️ MANUAL | ✅ YES | ⏳ PENDING |
| RP-007 | WF-007 | Cost gate exceeded | ❌ NO | 🟡 CONDITIONAL | ⏳ PENDING |
| RP-008 | WF-008 | Rate limiting (API exhaustion) | ✅ RETRY | ❌ NO | ⏳ PENDING |

---

## Operational Scenarios

### Scenario 1: Check Current Status (No Changes)

```bash
# See what patterns would be detected without making changes
bash .codex/scripts/auto_remediate_194f6af0.sh --check-only

# Expected output:
# [... timestamp ...] Auto-Remediation Started
# [... timestamp ...] PHASE 1: Detection & Classification
# [... timestamp ...] ✅ RP-001 NOT DETECTED: File was updated
# [... timestamp ...] ✅ RP-002 NOT DETECTED: CHANGELOG.md was updated
# [... timestamp ...] ⚠️ RP-003 CHECK SKIPPED: Cannot access PR (GitHub token issue)
```

---

### Scenario 2: Simulate Remediation (Dry-Run)

```bash
# See what would be changed without actually committing/pushing
bash .codex/scripts/auto_remediate_194f6af0.sh --dry-run

# Expected output:
# [... timestamp ...] Auto-Remediation Started for Commit 194f6af0
# [... timestamp ...] Dry-Run Mode: true
# [... timestamp ...] PHASE 2: Remediation
# [... timestamp ...] Would apply auto-fix (DRY-RUN)
# [... timestamp ...] Would run wec_enforcer (DRY-RUN)
# [... timestamp ...] PHASE 3: Would commit and push (DRY-RUN)
```

---

### Scenario 3: Apply Immediate Remediation

```bash
# Apply all detected fixes right now
bash .codex/scripts/auto_remediate_194f6af0.sh

# This will:
# 1. Detect any failing patterns
# 2. Apply targeted fixes (session_wrapup_autofix.py, wec_enforcer.py)
# 3. Commit with SHA reference
# 4. Push to remote

# Check results in:
cat .codex/remediation_logs_194f6af0/commit.log
cat .codex/remediation_logs_194f6af0/push.log
```

---

### Scenario 4: Start Background Monitoring

```bash
# Start the monitoring daemon in background (recommended for CI)
nohup bash .codex/scripts/monitor_194f6af0_workflows.sh &

# The daemon will:
# - Poll GitHub API every 30 seconds
# - Watch for workflow failures on commit 194f6af0
# - Auto-trigger remediation.sh when failures occur
# - Log all activity to .codex/workflow_monitor_194f6af0.log

# Check progress
tail -f .codex/workflow_monitor_194f6af0.log

# View remediation tracking
cat .codex/CI_REMEDIATION_194F6AF0.md
```

---

### Scenario 5: Monitor With Custom Settings

```bash
# Poll every 60 seconds, timeout after 2 hours
bash .codex/scripts/monitor_194f6af0_workflows.sh 60 7200

# This is useful if:
# - You want less frequent API calls (rate limiting)
# - You expect long-running workflows
# - You want a longer monitoring window
```

---

### Scenario 6: Troubleshooting

```bash
# Check if automation scripts are executable
ls -la .codex/scripts/auto_remediate_194f6af0.sh
ls -la .codex/scripts/monitor_194f6af0_workflows.sh

# View remediation logs
ls -la .codex/remediation_logs_194f6af0/
cat .codex/remediation_logs_194f6af0/*.log

# Check tracking file
cat .codex/CI_REMEDIATION_194F6AF0.md

# Run detection in check-only mode to diagnose issues
bash .codex/scripts/auto_remediate_194f6af0.sh --check-only 2>&1 | tee /tmp/debug.log

# Manually check specific patterns
# RP-001 & RP-002
git diff HEAD~1 HEAD -- docs/accountability/.codex/archive/reports/AGENT_ACCOUNTABILITY_REPORT.md CHANGELOG.md

# RP-003 & RP-004
gh pr view 5328 --json body -q '.body' | grep -A 20 "Workflow Execution Checklist"
```

---

### Scenario 7: Restore GitHub Token & Re-Run

When the GitHub token is refreshed:

```bash
# Verify token is working
gh auth status

# Expected output:
# github.com
#   ✓ Logged in to github.com as <username>
#   ✓ Git operations use https protocol

# Re-run detection to check WEC patterns
bash .codex/scripts/auto_remediate_194f6af0.sh --check-only

# Now RP-003 and RP-004 checks will run (previously skipped)
```

---

## Integration with CI/CD

### GitHub Actions Workflow Integration

Add this to your workflow YAML to auto-remediate:

```yaml
- name: Auto-remediate CI failures (194f6af0)
  run: |
    bash .codex/scripts/auto_remediate_194f6af0.sh
  continue-on-error: true  # Continue even if remediation finds no issues
```

### Scheduled Monitoring

To continuously monitor in the background:

```yaml
name: CI Monitor - Commit 194f6af0
on:
  schedule:
    - cron: '*/5 * * * *'  # Run every 5 minutes
  workflow_dispatch:

jobs:
  monitor:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Monitor and auto-remediate
        run: bash .codex/scripts/monitor_194f6af0_workflows.sh 30 600
        timeout-minutes: 15
```

---

## Manual Remediation (If Automation Fails)

If the scripts encounter issues, refer to the detailed manual procedures in:

- **Main Guide:** `.codex/CI_REMEDIATION_194F6AF0.md`
- **Pattern Details:** `.codex/WORKFLOW_FAILURE_MATRIX.md`
- **Governance Rules:** `.codex/CODEBASE_AGENCY_POLICY.md`

Each pattern has a complete manual remediation procedure documented.

---

## Success Criteria

Your commit (194f6af0) is **READY** when:

✅ RP-001 (REQ-4) — PASSED  
✅ RP-002 (REQ-5) — PASSED  
⏳ RP-003 (WEC stripped) — Must be checked when GitHub API available  
⏳ RP-004 (WEC format) — Must be checked when GitHub API available  
🟢 RP-005 (Approval) — Non-blocking (skip if not applicable)  
⏳ RP-006 (REQUIRED items) — Must be checked when GitHub API available  
🟢 RP-007 (Cost gate) — Non-blocking (skip if not applicable)  
🟢 RP-008 (Rate limit) — Non-blocking (auto-retries)

**Current Status:** ✅ COMPLIANT on critical patterns (RP-001, RP-002)

---

## Key Commands Reference

```bash
# Status Check
bash .codex/scripts/auto_remediate_194f6af0.sh --check-only

# Dry-Run (Simulate)
bash .codex/scripts/auto_remediate_194f6af0.sh --dry-run

# Apply Fixes
bash .codex/scripts/auto_remediate_194f6af0.sh

# Start Monitoring
bash .codex/scripts/monitor_194f6af0_workflows.sh

# View Tracking
cat .codex/CI_REMEDIATION_194F6AF0.md

# View Logs
tail -f .codex/workflow_monitor_194f6af0.log

# Manual Pattern Check
git diff HEAD~1 HEAD -- CHANGELOG.md docs/accountability/.codex/archive/reports/AGENT_ACCOUNTABILITY_REPORT.md
```

---

## Support & Escalation

If automation cannot resolve issues:

1. **Check logs:** `.codex/remediation_logs_194f6af0/` and `.codex/workflow_monitor_194f6af0.log`
2. **Review patterns:** `.codex/WORKFLOW_FAILURE_MATRIX.md` §Remediation Steps
3. **Escalate:** Commit with all logs to PR for human review
4. **Contact:** Reference commit 194f6af0 in any issue/discussion

---

**Document Created:** 2026-07-16T23:47:00Z  
**Automation Status:** ✅ READY  
**Commit:** 194f6af0  
**PR:** #5328
