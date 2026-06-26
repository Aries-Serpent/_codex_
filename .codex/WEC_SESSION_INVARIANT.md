# WEC Session Invariant — Mandatory Contract for Copilot Agent Sessions

**Version:** 1.0.0  
**Effective Date:** 2026-06-26  
**Scope:** ALL Copilot Agent sessions working on PRs to `Aries-Serpent/_codex_`  
**Enforcement:** Validated by `copilot-setup-steps.yml` session preload + `phase-12-2-compliance-check.yml` gate

---

## Purpose

The **Workflow Execution Checklist (WEC)** is the authoritative specification for which workflows a Copilot Agent session intends to execute on a given PR. This document defines the invariant contract that MUST be maintained throughout the entire session to ensure:

1. **WEC State Preservation** — The WEC checklist state is never lost or corrupted during `report_progress` calls
2. **Governance Compliance** — AGENT_ACCOUNTABILITY_REPORT.md and CHANGELOG.md are always updated in the final commit
3. **Workflow Intent Clarity** — Every checked workflow is intentionally approved for that session
4. **Merge Readiness** — All REQUIRED workflows for the target branch are present and properly checked

---

## Session Phases & WEC State Requirements

### PHASE 1: Session Initialization

**Timing:** First action of session (before any code changes)

**Actions:**
1. **Read Current WEC:** Fetch PR body and extract existing WEC state
2. **Validate Format:** Ensure `## 🔄 Workflow Execution Checklist` section exists and is well-formed
3. **Log State:** Post a session context comment showing:
   - Current WEC state (all checked/unchecked items)
   - Required workflows for target branch
   - Any missing or malformed items
4. **Escalate if Needed:** If WEC is corrupted or missing, STOP and post diagnostic before proceeding

**Example Session Log Comment:**
```
## 🔄 Session Initialization - WEC State
**Time:** 2026-06-26T22:35:00Z
**PR:** #5104
**Branch:** copilot/wec-hardening → 0D_base_

### Current WEC State
✅ pre-merge-validation.yml (Pre-merge checks)
✅ comment-review-gate.yml (Comment review gate)
✅ workflow-execution-gate.yml (WEC gate)
⏭️ cost-gate.yml (Cost governance gate)

### Required for Merge to 0D_base_
- pre-merge-validation.yml ✅
- comment-review-gate.yml ✅
- workflow-execution-gate.yml ✅
- agent-auth-delegation.yml ⏳ (missing from WEC)

### Issues Detected
❌ `agent-auth-delegation.yml` is REQUIRED but not in WEC — will add it
```

---

### PHASE 2: Session Work

**Duration:** Main work phase (code changes, commits)

**WEC State Invariant:**
```
FOR EACH report_progress call:
  1. READ current PR body → extract WEC state
  2. MERGE new WEC items (if any)
  3. APPEND WEC block to prDescription parameter
  4. CALL report_progress with WEC included
  5. VERIFY PR body still contains WEC after push
```

**Pre-Report-Progress Checklist:**

Before every `report_progress` call:

```python
# Pseudo-code for WEC preservation

wec_before = fetch_pr_body().extract_wec_section()  # Get current state
new_progress_description = build_progress_checklist()
wec_after = rebuild_wec_state(wec_before)  # Preserve selections
pr_description = new_progress_description + "\n\n" + wec_after
report_progress(prDescription=pr_description)

# After push: verify WEC is in new PR body
pr_body_after_push = fetch_pr_body()
assert "## 🔄 Workflow Execution Checklist" in pr_body_after_push, \
    "WEC was stripped by report_progress!"
```

**Maintainer Override Protocol:**

If a maintainer manually edits the WEC during the session:
1. Copilot Agent MUST read the latest WEC state before its next `report_progress` call
2. Copilot Agent MUST preserve the maintainer's changes (do NOT overwrite them)
3. Copilot Agent MUST post a comment acknowledging the maintainer's WEC selections
4. Example:
   ```
   Detected maintainer WEC update:
   - Newly checked: cost-gate.yml
   - Newly unchecked: copilot-agent-session-done.yml
   
   These selections are preserved in this session.
   ```

---

### PHASE 3: Pre-Commit Validation

**Timing:** Before final commit

**Actions:**
1. **Run Compliance Check:**
   ```bash
   python scripts/ci/session_wrapup_autofix.py --check --pr-number N
   ```
2. **Validate REQ-4 & REQ-5:**
   - ✅ AGENT_ACCOUNTABILITY_REPORT.md was updated in this session
   - ✅ CHANGELOG.md was updated in this session
   - ✅ Both files will be in the final commit
3. **Validate WEC Presence:**
   - ✅ PR body contains `## 🔄 Workflow Execution Checklist`
   - ✅ All required items are listed
   - ✅ Checkbox syntax is valid (no typos in `[x]` or `[ ]`)
4. **Auto-Fix or Escalate:**
   - If compliance check fails: Run `session_wrapup_autofix.py --auto-update` to auto-populate files
   - If auto-update fails: Post blocking comment and STOP

---

### PHASE 4: Session Finalization

**Timing:** Last action (after all commits)

**Actions:**
1. **Final WEC Validation:**
   - Fetch latest PR body
   - Confirm WEC section is present with all changes preserved
   - Log final WEC state to session summary comment
2. **Generate Session Accountability Entry:**
   ```markdown
   ## Session [DATE/ID]
   
   **PR:** #{PR_NUMBER}
   **Branch:** copilot/[branch] → [base]
   **Commit:** [final commit SHA]
   **Objective:** [user's objective]
   
   ### WEC State Changes (This Session)
   - ✅ pre-merge-validation.yml (checked at session start)
   - 🔄 cost-gate.yml (NEW: checked by user mid-session)
   - ⏭️ copilot-agent-session-done.yml (unchecked per auto-complete rules)
   
   ### Governance Compliance
   - ✅ REQ-4: AGENT_ACCOUNTABILITY_REPORT.md updated
   - ✅ REQ-5: CHANGELOG.md updated
   - ✅ WEC: Preserved across all commits
   
   ### Workflow Selection Rationale
   - Pre-merge validation: REQUIRED for all merges
   - Cost gate: Enabled to check deployment costs before merge
   - Session done: Disabled (redundant with auto-post-review workflow)
   ```
3. **Post Session Summary to PR:**
   - Post final session comment with WEC state, governance compliance, and workflow execution log
   - Include link to AGENT_ACCOUNTABILITY_REPORT.md entry

---

## WEC Requirements by Merge Target

### Merge to `main` Branch

**REQUIRED Workflows (ALL must be checked):**
- `pre-merge-validation.yml` — Final pre-merge checks
- `comment-review-gate.yml` — Comment review validation
- `workflow-execution-gate.yml` — WEC enforcement gate
- `agent-auth-delegation.yml` — Token delegation validation (if agent-delegated PR)
- `deferral-language-gate.yml` — Policy language enforcement

**OPTIONAL Workflows (checked per session objective):**
- `cost-gate.yml` — Cost governance (check if budget impact expected)
- `copilot-agent-checkin.yml` — Agent status reporting
- `copilot-agent-session-done.yml` — Auto-post-review workflow
- `copilot-iterative-self-healing.yml` — Self-healing automation

**Merge Blocked If:**
- ANY REQUIRED workflow is unchecked ❌
- WEC is missing or malformed ❌
- REQ-4 or REQ-5 compliance check fails ❌

---

### Merge to `0D_base_` (Integration/Staging) Branch

**REQUIRED Workflows:**
- `pre-merge-validation.yml` — Pre-merge checks
- `comment-review-gate.yml` — Comment validation
- `workflow-execution-gate.yml` — WEC gate

**OPTIONAL Workflows:**
- All workflows in OPTIONAL section above (policy less strict for staging)

**Merge Blocked If:**
- ANY REQUIRED workflow is unchecked ❌
- WEC is missing or malformed ❌
- REQ-4/REQ-5 check fails (if this branch enforces governance) ❌

---

## WEC State Loss Prevention

### Root Causes of State Loss (Identified Issues)

| Issue | Cause | Prevention |
|-------|-------|-----------|
| WEC stripped on `report_progress` | Tool replaces entire PR body | Always append WEC to `prDescription` parameter |
| Maintainer selections overwritten | Agent reads stale WEC | Agent reads WEC from PR BEFORE every `report_progress` call |
| WEC corrupted during merge | Conflict resolution errors | Use `--auto-fix` mode for WEC recovery |
| Workflow added/removed without WEC update | Manual workflow changes | Update WEC before deploying new workflows |

### Prevention Checklist for Copilot Agent

- [ ] **Session Start:** Read WEC from PR, log state to comment
- [ ] **Every report_progress:** Read current WEC, merge with new items, append to prDescription
- [ ] **Mid-session:** If maintainer edits WEC, read it again and preserve their selections
- [ ] **Pre-commit:** Run compliance check, validate WEC format and required items
- [ ] **Session End:** Post final session comment with WEC state preserved

---

## Validation Gates

### Session Preload Gate (copilot-setup-steps.yml)

```bash
# Pseudo-code
if ! pr_has_wec_section; then
  echo "❌ WEC section missing — please add it before proceeding"
  exit 1
fi

if ! validate_wec_format; then
  echo "❌ WEC format invalid (check checkbox syntax)"
  exit 1
fi

# Log state for visibility
log_wec_state_to_actions_output
```

### Pre-Merge Gate (pre-merge-validation.yml)

```bash
# Checks that:
# 1. All required workflows are listed
# 2. No deprecated workflows are in WEC
# 3. Workflow format is valid
# 4. For main branch: all REQUIRED workflows are checked
```

### Compliance Gate (phase-12-2-compliance-check.yml)

```bash
# Checks that:
# 1. REQ-4: AGENT_ACCOUNTABILITY_REPORT.md updated in last commit
# 2. REQ-5: CHANGELOG.md updated in last commit
# Fails if either file is missing
```

---

## Recovery Procedures

### If WEC is Stripped During Session

**Detection:**
- PR body is missing `## 🔄 Workflow Execution Checklist` section

**Recovery:**
```bash
# 1. Fetch last known WEC state from git history
git log --all --pretty=format:"%B" | grep -A 20 "## 🔄 Workflow Execution Checklist" | head -1

# 2. Rebuild WEC from canonical items + last known selections
python scripts/ci/wec_enforcer.py --validate-body --pr N

# 3. If recovery needed: run autofix
python scripts/ci/session_wrapup_autofix.py --fix-wec --pr N

# 4. Re-run compliance check to verify
python scripts/ci/phase_12_2_compliance_dashboard.py --check
```

### If REQ-4/REQ-5 Compliance Check Fails

**Root Causes:**
- AGENT_ACCOUNTABILITY_REPORT.md not in latest commit
- CHANGELOG.md not in latest commit
- Files were updated earlier but not in the final commit

**Recovery:**
```bash
# 1. Run autofix to update files and stage them
python scripts/ci/session_wrapup_autofix.py --auto-update --pr N

# 2. Amend the last commit to include updated files
git add CHANGELOG.md docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md
git commit --amend --no-edit

# 3. Force push (if branch allows)
git push --force-with-lease

# 4. Re-run compliance check
python scripts/ci/phase_12_2_compliance_dashboard.py --check
```

### If Maintainer Overrides WEC Mid-Session

**Workflow:**
1. Copilot Agent detects WEC has changed (via `git diff` on PR body)
2. Copilot Agent reads new WEC state
3. Copilot Agent posts acknowledgment comment
4. Copilot Agent includes new WEC state in next `report_progress` call
5. Copilot Agent does NOT revert maintainer's selections

---

## Testing & Validation

### Unit Tests

Location: `tests/ci/test_wec_enforcer.py`

Tests cover:
- WEC extraction from PR body
- WEC state preservation across `report_progress` calls
- Validation of required vs optional workflows
- Recovery from corrupted WEC

### Integration Tests

Location: `tests/ci/test_wec_session_invariant.py` (new)

Tests cover:
- Full session workflow: init → work → pre-commit → finalize
- Maintainer override handling
- Governance compliance enforcement

### Manual Verification

After each session:
```bash
# Verify WEC is in final PR body
gh pr view N --json body | jq -r '.body' | grep -A 20 "## 🔄 Workflow"

# Verify compliance files were updated
git show HEAD -- CHANGELOG.md | head -20
git show HEAD -- docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md | head -30

# Verify all required workflows are checked
gh pr view N --json body | jq -r '.body' | \
  grep -E "pre-merge-validation|comment-review-gate|workflow-execution-gate" | \
  grep -c "\[x\]"  # Should match number of required workflows
```

---

## References

- **WEC PR Body Conflicts:** `docs/workflows/WEC_PR_BODY_CONFLICTS.md`
- **Canonical WEC Items:** `.codex/WEC_CANONICAL_ITEMS.md`
- **Workflow Execution Gate:** `.github/workflows/workflow-execution-gate.yml`
- **Session Wrapup Tool:** `scripts/ci/session_wrapup_autofix.py`
- **Compliance Gate:** `.github/workflows/phase-12-2-compliance-check.yml`

---

**Version History:**
- 2026-06-26: Initial version — WEC Session Invariant established
