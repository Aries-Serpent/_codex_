# copilot-setup-steps.yml Restoration Plan

**Date:** 2026-06-18
**Status:** Implementation plan for restoring stable baseline and preventing future regressions
**Owner:** @mbaetiong

---

## Executive Summary

The current `copilot-setup-steps.yml` (commits 10f8c1c59 / 384cde02 / fad67fd8, 1109 lines) is **unstable and causes Copilot agent session crashes**. 

The root cause is the **removal of three critical CCA version lock environment variables** introduced in Sessions 1294-1295 to fix multi-turn agent crashes.

**Immediate action:** Restore the clean baseline from commit add792eb3 (673 lines) and selectively re-add safe enhancements.

---

## Problem Statement (Verified)

### Current Issues (Confirmed)

1. ✅ **CCA Version Lock Variables Missing**
   - Variable `COPILOT_AGENT_CCA_VERSION_LOCK: "stable"` — REMOVED
   - Variable `COPILOT_AGENT_DEDUPLICATION_ENABLED: "true"` — REMOVED
   - Variable `COPILOT_AGENT_TURN_ISOLATION_ENABLED: "true"` — REMOVED
   - **Impact:** Multi-turn sessions crash on turn 2+ with "Duplicate function call ID" error
   - **Evidence:** Lines 100-130 in commit add792eb3, absent in commit 10f8c1c59+

2. ✅ **LFS Mode Description Typo**
   - Line 29: `full=full=fetch all` (duplicate equals)
   - **Impact:** YAML parsing error, workflow start failures
   - **Source:** Commit 27240d92d ("fix(ci): correct lfs_mode description...")

3. ✅ **Complex Error Handling Pattern**
   - Changed from `if ! cmd; then ... fi` to `cmd || { ... }`
   - Adds GitHub Actions `format()` expressions in script context
   - **Impact:** YAML parser load, potential parse errors

4. ✅ **436 Additional Lines of Code**
   - Added 60+ lines git configuration
   - Added 40+ lines merge conflict detection
   - Added 35+ lines CI failure issue detection
   - Added 200+ lines documentation
   - **Impact:** Increased surface area for parsing errors

5. ✅ **Unquoted Secrets**
   - Changed from `"${{ secrets.KEY }}"` to `${{ secrets.KEY }}`
   - **Impact:** Potential YAML parsing issues if secrets empty or contain special chars

---

## Restoration Strategy

### Phase 1: Restore Clean Baseline (CRITICAL)

**Goal:** Return to commit add792eb3 (673 lines, verified stable)

**Steps:**
1. Reset `.github/workflows/copilot-setup-steps.yml` to add792eb3 version
2. Verify file has exactly 673 lines
3. Confirm all CCA version lock variables are present
4. Test baseline in workflow_dispatch to verify no parse errors

**Validation:**
```bash
git show add792eb3:.github/workflows/copilot-setup-steps.yml > /tmp/baseline.yml
diff /tmp/baseline.yml .github/workflows/copilot-setup-steps.yml
# Should be identical
```

**Commit:** `Restore copilot-setup-steps.yml to clean baseline (commit add792eb3, 673 lines)`

---

### Phase 2: Fix LFS Mode Description Typo (REQUIRED)

**Goal:** Fix the `full=full=fetch all` typo introduced in 27240d92d

**Change:**
```diff
- description: 'Git LFS mode (none=baseline, targeted=fetch specific paths, full=full=fetch all)'
+ description: 'Git LFS mode (none=baseline, targeted=fetch specific paths, full=fetch all)'
```

**Validation:**
```bash
grep "full=full=" .github/workflows/copilot-setup-steps.yml
# Should return nothing
```

**Commit:** `fix(ci): correct LFS mode description typo`

---

### Phase 3: Selective Re-Addition of Safe Enhancements (OPTIONAL)

**Goal:** Re-add useful features from 10f8c1c59/384cde02 WITHOUT removing safety variables

**Candidates for Re-Addition (with CCA vars intact):**

✅ **Safe to Re-Add:**
1. Actions v5+ updates (cosmetic, no logic change)
2. Inline documentation comments (non-functional)
3. Git user configuration (add user.email / user.name)

⚠️ **Conditionally Safe (needs careful review):**
1. Git branch promotion logic (may conflict with actions/checkout)
2. Merge conflict pre-check (useful but new complexity)
3. CI failure issue checks (useful but new API calls)

🔴 **DO NOT RE-ADD:**
1. Removal of CCA version lock variables (they STAY)
2. Removal of LFS environment variables (use them directly)
3. Complex GitHub Actions `format()` expressions in scripts
4. Unquoted secrets (keep them quoted)

**Process:**
1. For each enhancement, add it as a separate commit
2. Test each commit independently
3. Verify workflow still parses correctly
4. Verify Copilot agent can complete multi-turn sessions
5. Only advance to next enhancement if current one passes

---

### Phase 4: Document Restoration Rationale (REQUIRED)

**File:** `.codex/COPILOT_SETUP_STEPS_RESTORATION.md`

**Content:**
- Reason for restoration
- What was removed and why
- What was kept from clean baseline
- What may be re-added in future
- How to prevent similar issues

**Commit:** `docs: document copilot-setup-steps.yml restoration rationale`

---

## Implementation Checklist

### Pre-Implementation

- [ ] Read `.codex/COPILOT_SETUP_STEPS_ANALYSIS.md` (comprehensive analysis)
- [ ] Read `.codex/COPILOT_SETUP_STEPS_COMMIT_DIFF_MAP.md` (commit-by-commit breakdown)
- [ ] Understand CCA version lock variables and their purpose
- [ ] Review Sessions 1294-1295 context for CCA deduplication

### Phase 1: Baseline Restoration

- [ ] **Task:** Restore `.github/workflows/copilot-setup-steps.yml` to commit add792eb3
  ```bash
  git show add792eb3:.github/workflows/copilot-setup-steps.yml > .github/workflows/copilot-setup-steps.yml
  ```
- [ ] **Verify:** File has exactly 673 lines
  ```bash
  wc -l .github/workflows/copilot-setup-steps.yml
  # Should output: 673
  ```
- [ ] **Verify:** CCA version lock variables present
  ```bash
  grep "COPILOT_AGENT_CCA_VERSION_LOCK\|COPILOT_AGENT_DEDUPLICATION\|COPILOT_AGENT_TURN_ISOLATION" \
    .github/workflows/copilot-setup-steps.yml
  # Should find 3 variables
  ```
- [ ] **Test:** Validate YAML syntax
  ```bash
  python3 -c "import yaml; yaml.safe_load(open('.github/workflows/copilot-setup-steps.yml'))"
  # Should succeed with no error
  ```
- [ ] **Commit:** With message: `Restore copilot-setup-steps.yml to clean baseline (add792eb3, 673 lines)`
- [ ] **Push:** To current branch

### Phase 2: Fix LFS Typo

- [ ] **Task:** Fix `full=full=fetch all` → `full=fetch all`
  ```bash
  sed -i 's/full=full=/full=/g' .github/workflows/copilot-setup-steps.yml
  ```
- [ ] **Verify:** Typo is gone
  ```bash
  grep "full=full=" .github/workflows/copilot-setup-steps.yml
  # Should return nothing
  ```
- [ ] **Verify:** Correct version present
  ```bash
  grep "full=fetch all" .github/workflows/copilot-setup-steps.yml
  # Should return 1 match
  ```
- [ ] **Commit:** With message: `fix(ci): correct LFS mode description (remove duplicate full=)`
- [ ] **Push:** To current branch

### Phase 3: Optional Enhancements (DO NOT START until Phase 1&2 pass)

- [ ] **Actions v5 Updates:** Add `# v5` comments to action versions (cosmetic)
- [ ] **Git Configuration:** Add git user config (add user.email / user.name)
- [ ] **Documentation Comments:** Add 1-2 line comments to complex sections
- [ ] Test each enhancement independently
- [ ] Only proceed to next if current passes

### Phase 4: Documentation

- [ ] **Task:** Create restoration documentation at `.codex/COPILOT_SETUP_STEPS_RESTORATION.md`
- [ ] **Content:** Rationale, what was restored, what was kept
- [ ] **Commit:** With message: `docs: document copilot-setup-steps.yml restoration rationale`
- [ ] **Push:** To current branch

### Post-Implementation Verification

- [ ] **YAML Syntax:** No parse errors
  ```bash
  python3 -c "import yaml; yaml.safe_load(open('.github/workflows/copilot-setup-steps.yml'))"
  ```
- [ ] **Line Count:** Should be 673 (or 673 + conservative enhancements)
  ```bash
  wc -l .github/workflows/copilot-setup-steps.yml
  ```
- [ ] **CCA Variables:** All three present and unchanged
  ```bash
  grep "COPILOT_AGENT_CCA_VERSION_LOCK\|COPILOT_AGENT_DEDUPLICATION\|COPILOT_AGENT_TURN_ISOLATION" \
    .github/workflows/copilot-setup-steps.yml | wc -l
  # Should return 3
  ```
- [ ] **LFS Description:** No typo
  ```bash
  grep "full=full=" .github/workflows/copilot-setup-steps.yml
  # Should return nothing
  ```
- [ ] **Workflow Validation:** Run copilot-setup-steps workflow manually
  - Go to Actions → copilot-setup-steps → Run workflow
  - Select "Workflow dispatch"
  - Select environment_type=security-scan (exercise all code paths)
  - Monitor for parse errors
  - Monitor for multi-turn agent completion

---

## Critical Success Criteria

### Must-Have

✅ **CCA Version Lock Variables Present and Unchanged**
- `COPILOT_AGENT_CCA_VERSION_LOCK: "stable"`
- `COPILOT_AGENT_DEDUPLICATION_ENABLED: "true"`
- `COPILOT_AGENT_TURN_ISOLATION_ENABLED: "true"`

✅ **No LFS Mode Typo**
- `full=full=fetch all` FIXED to `full=fetch all`

✅ **YAML Parsing Success**
- No syntax errors when loading with PyYAML
- No GitHub Actions parser errors

✅ **Multi-Turn Session Support**
- Agent can complete 2+ turn sessions without "Duplicate function call ID" errors
- Session context pre-load completes without failures

### Should-Have

⚠️ **Line Count:** Back to ~673 (or +10-15 with conservative safe enhancements)
- If >750 lines, review for unnecessary expansion

⚠️ **Error Handling:** Simple, clear patterns
- Prefer `if ! cmd; then ... fi` over `cmd || { ... }`
- Avoid GitHub Actions `format()` in script context

⚠️ **Secret Injection:** Quoted for YAML safety
- Prefer `"${{ secrets.KEY }}"` over `${{ secrets.KEY }}`

### Nice-to-Have

💡 **Documentation:** Clear, concise comments
- Max 2-3 lines per section
- Explain "why" not just "what"

💡 **Git Configuration:** User info for commits
- `git config user.email` and `user.name`

---

## Rollback Plan

If restoration fails:

1. **Immediate Revert:**
   ```bash
   git revert HEAD~N  # Where N is number of commits to revert
   ```

2. **Fallback:** Keep commit add792eb3 as emergency baseline
   - Store `.github/workflows/copilot-setup-steps.yml` from add792eb3 as reference
   - File path: `.codex/copilot-setup-steps.safe-baseline.yml`

3. **Escalation:** Contact @mbaetiong with:
   - Failure symptoms
   - YAML parse errors (if any)
   - Workflow logs (if available)
   - Commits attempted

---

## Prevention Strategy

To prevent similar regressions in the future:

### 1. Lock Critical Variables

**File:** `.codex/COPILOT_SETUP_CRITICAL_VARIABLES.md`

Document the three CCA variables as **LOCKED CRITICAL**:
```markdown
# LOCKED CRITICAL: These variables MUST NEVER be removed

- COPILOT_AGENT_CCA_VERSION_LOCK
- COPILOT_AGENT_DEDUPLICATION_ENABLED
- COPILOT_AGENT_TURN_ISOLATION_ENABLED

Removing them causes: "Duplicate function call ID" errors on turn 2+
Source: Sessions 1294-1295 (initial fix commit 10f8c1c59)
```

### 2. Pre-Commit Hook

Add to `.pre-commit-config.yaml`:

```yaml
- repo: local
  hooks:
    - id: check-copilot-setup-critical-vars
      name: Check copilot-setup-steps.yml critical variables
      entry: bash -c 'grep -q "COPILOT_AGENT_CCA_VERSION_LOCK" .github/workflows/copilot-setup-steps.yml'
      language: system
      files: .github/workflows/copilot-setup-steps.yml
      fail_fast: true
```

### 3. CI Gate

Add to workflow:

```yaml
- name: "🔒 Verify copilot-setup-steps.yml critical variables"
  run: |
    for var in COPILOT_AGENT_CCA_VERSION_LOCK COPILOT_AGENT_DEDUPLICATION_ENABLED COPILOT_AGENT_TURN_ISOLATION_ENABLED; do
      if ! grep -q "$var" .github/workflows/copilot-setup-steps.yml; then
        echo "❌ CRITICAL VARIABLE MISSING: $var"
        exit 1
      fi
    done
    echo "✅ All critical variables present"
```

### 4. Commit Message Validation

Reject commit messages that claim "hardening" or "fixes" while removing critical variables.

### 5. Documentation Reference

In every commit that touches `copilot-setup-steps.yml`:
- Reference `.codex/COPILOT_SETUP_CRITICAL_VARIABLES.md`
- Confirm critical variables are not being removed
- Document any changes with rationale

---

## Timeline

| Phase | Duration | Effort | Start | End |
|-------|----------|--------|-------|-----|
| Phase 1: Baseline Restore | 30 min | Low | T+0h | T+0.5h |
| Phase 2: Fix LFS Typo | 15 min | Low | T+0.5h | T+0.75h |
| Phase 3: Optional Enhancements | 2-4 hrs | Medium | T+0.75h | T+4.75h |
| Phase 4: Documentation | 1 hr | Low | T+4.75h | T+5.75h |
| **Post-Implementation Verification** | **1-2 hrs** | **High** | T+5.75h | **T+7.75h** |
| **TOTAL** | **~8 hours** | — | — | — |

**Accelerated Path (Critical Only):**
- Phase 1 + Phase 2 + Verification: **~2 hours**

---

## Success Criteria

✅ **Phase 1 Complete:** copilot-setup-steps.yml restored to 673 lines with all CCA variables present

✅ **Phase 2 Complete:** LFS mode typo fixed, YAML parses cleanly

✅ **Phase 3 Complete (Optional):** Safe enhancements added with independent testing

✅ **Phase 4 Complete (Required):** Restoration documented with prevention strategy

✅ **Verification Complete:** Multi-turn Copilot sessions work without "Duplicate function call ID" errors

---

## Notes

- This plan assumes git history is intact and commits are accessible
- All file edits should be reviewed for YAML syntax before commit
- Each commit should be independently testable
- Verification should include live workflow_dispatch testing
- Prevention strategy should be implemented immediately after restoration

---

**Document Status:** Ready for implementation
**Last Updated:** 2026-06-18
**Next Steps:** Execute Phase 1 (Baseline Restoration)

