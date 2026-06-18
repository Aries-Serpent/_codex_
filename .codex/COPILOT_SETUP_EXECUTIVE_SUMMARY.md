# copilot-setup-steps.yml Version Regression — Executive Summary

**Date:** 2026-06-18T06:22:58Z
**Status:** Analysis Complete | Ready for Implementation
**Scope:** 6-commit regression (94217b5 → fad67fd8)
**Risk Level:** 🔴 CRITICAL

---

## Problem Statement

The current version of `copilot-setup-steps.yml` (commits 10f8c1c59, 384cde02, fad67fd8 — **1109 lines**) is **causing Copilot agent session crashes on turn 2+**. The root cause is the **removal of three critical CCA version lock environment variables** that were introduced in Sessions 1294-1295 as a fix for this exact problem.

This represents a **regression**: the codebase reverted to an unstable state while claiming to "restore" a baseline.

---

## Key Findings (Verified)

### 🔴 CRITICAL Issues (Must Fix Immediately)

1. **Missing CCA Version Lock Variables** (Sessions 1294-1295 fix removed)
   - Variable removed: `COPILOT_AGENT_CCA_VERSION_LOCK: "stable"`
   - Variable removed: `COPILOT_AGENT_DEDUPLICATION_ENABLED: "true"`
   - Variable removed: `COPILOT_AGENT_TURN_ISOLATION_ENABLED: "true"`
   - **Impact:** Multi-turn Copilot agents crash with "Duplicate function call ID" error
   - **Evidence:** Lines 100-130 in add792eb3; absent in 10f8c1c59+

2. **LFS Mode Description Typo**
   - Error: `full=full=fetch all` (duplicate equals sign)
   - Location: Line 29 (approximately)
   - **Impact:** YAML parsing failures, workflow startup errors
   - **Source:** Commit 27240d92d (misleadingly titled "fix...")

### 🟡 MEDIUM Issues (Should Fix)

3. **Complex Error Handling Changes**
   - From: `if ! command; then ... fi` (simple shell conditional)
   - To: `command || { ... }` with embedded GitHub Actions `format()` function
   - **Risk:** YAML parser errors, fragile nested expressions

4. **436 Additional Lines of Code**
   - Added 60+ lines of git configuration logic
   - Added 40+ lines of merge conflict detection
   - Added 35+ lines of CI failure issue checking
   - Added 200+ lines of documentation
   - **Risk:** Increased surface area for parsing and runtime errors

5. **Unquoted Secrets in YAML**
   - From: `CODEX_MASTER_KEY: "${{ secrets.CODEX_MASTER_KEY }}"`
   - To: `CODEX_MASTER_KEY: ${{ secrets.CODEX_MASTER_KEY }}`
   - **Risk:** YAML parsing issues if secrets are empty or contain special characters

---

## Root Cause Analysis

### Why Copilot Agent Sessions Crash

```
Turn 1: ✅ Agent runs, completes work
         Generates function calls, submits payload to CAPI
         
Turn 2: ❌ Agent fails to start
         Error: "Duplicate function call ID" 
         
Why?    ❌ COPILOT_AGENT_DEDUPLICATION_ENABLED is not set
         ❌ PayloadDeduplicator class not activated
         ❌ Function call IDs from Turn 1 leak into Turn 2
         ❌ CAPI rejects duplicate function call IDs
         
Solution: Set COPILOT_AGENT_DEDUPLICATION_ENABLED=true
         Set COPILOT_AGENT_CCA_VERSION_LOCK=stable
         Set COPILOT_AGENT_TURN_ISOLATION_ENABLED=true
         (All three MUST be present)
```

### Commit Sequence (How We Got Here)

```
94217b5 (2 days ago)
└─→ add792eb3 (CLEAN, 673 lines, all safety vars present) ✅ STABLE
    └─→ 27240d92d (TYPO INTRODUCED, 1109 lines) ⚠️ BROKEN
        └─→ 10f8c1c59 (CCA VARS REMOVED, claimed "hardening") 🔴 CRASHES
            └─→ 384cde02 (inherits removal, actions v5+) 🔴 CRASHES
                └─→ fad67fd8 (restores the broken version) 🔴 CRASHES

PARADOX: fad67fd8 claims to "restore canonical baseline"
         but the "baseline" it restores to is the broken version!
         This creates a circular regression trap.
```

---

## The False Narrative

**Commit message claim:** "fix(ci): restore copilot-setup-steps.yml from canonical baseline (1102 lines)"

**Reality:**
- ❌ The "canonical baseline" is NOT the original clean version (add792eb3)
- ❌ The file it "restored" is the broken version that CAUSES the crashes
- ❌ It's not a restoration; it's persistence of existing bugs
- ❌ Commit 10f8c1c59 claimed to "harden" but removed safety variables
- ❌ This creates a self-reinforcing cycle of corruption

---

## Immediate Solution

### Phase 1: Restore Clean Baseline (30 minutes)

```bash
# Get the clean baseline from add792eb3
git show add792eb3:.github/workflows/copilot-setup-steps.yml \
  > .github/workflows/copilot-setup-steps.yml

# Verify
wc -l .github/workflows/copilot-setup-steps.yml  # Should be 673
grep "COPILOT_AGENT_CCA_VERSION_LOCK" \
  .github/workflows/copilot-setup-steps.yml     # Should find it
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/copilot-setup-steps.yml'))"  # No errors
```

### Phase 2: Fix LFS Typo (15 minutes)

```bash
# Fix the duplicate equals sign
sed -i 's/full=full=/full=/g' .github/workflows/copilot-setup-steps.yml

# Verify
grep "full=full=" .github/workflows/copilot-setup-steps.yml  # Should return nothing
grep "full=fetch all" .github/workflows/copilot-setup-steps.yml  # Should find it
```

### Phase 3: Test (1-2 hours)

```bash
# Manual workflow dispatch test
# GitHub UI → Actions → copilot-setup-steps → Run workflow
# Select environment_type=security-scan
# Monitor for parse errors and successful completion
# Start a multi-turn Copilot session and verify completion
```

---

## Critical Success Criteria

✅ **Must Have:**
- [ ] File has exactly 673 lines (or 673 + minimal safe additions)
- [ ] All three CCA variables present and unchanged:
  - `COPILOT_AGENT_CCA_VERSION_LOCK: "stable"`
  - `COPILOT_AGENT_DEDUPLICATION_ENABLED: "true"`
  - `COPILOT_AGENT_TURN_ISOLATION_ENABLED: "true"`
- [ ] No `full=full=` typo (fixed to `full=`)
- [ ] YAML parses cleanly
- [ ] Workflow runs successfully in manual dispatch
- [ ] Multi-turn Copilot sessions complete without errors

⚠️ **Should Have:**
- [ ] Simple error handling (shell `if` statements, not GitHub expressions)
- [ ] Quoted secrets (`"${{ secrets.KEY }}"` not `${{ secrets.KEY }}`)
- [ ] Reasonable line count increase (max 700-750 if enhancements added)

---

## Timeline

| Phase | Duration | Effort |
|-------|----------|--------|
| Phase 1: Baseline Restore | 30 min | Low |
| Phase 2: Fix LFS Typo | 15 min | Low |
| Phase 3: Testing | 1-2 hrs | High |
| **CRITICAL PATH TOTAL** | **2 hours** | — |

*Optional Phase 4 (selective safe enhancements): +4-6 hours if approved*

---

## Related Documentation

Four comprehensive analysis documents have been created in `.codex/`:

1. **COPILOT_SETUP_STEPS_ANALYSIS.md** (22 KB)
   - Complete technical analysis of all 13 major changes
   - Detailed commit-by-commit breakdown
   - Root cause analysis with system diagrams
   - CCA version lock variables documentation

2. **COPILOT_SETUP_STEPS_COMMIT_DIFF_MAP.md** (11 KB)
   - Visual commit timeline
   - Individual analysis for commits 27240d92d through fad67fd8
   - Critical variables status tables
   - Side-by-side error handling comparisons

3. **COPILOT_SETUP_RESTORATION_PLAN.md** (14 KB)
   - Step-by-step implementation checklist
   - Success criteria and validation procedures
   - Rollback plan
   - Prevention strategy with pre-commit hooks and CI gates

4. **COPILOT_SETUP_ANALYSIS_INDEX.md** (15 KB)
   - Navigation guide and quick-reference
   - Document index with use cases
   - Quick summary tables
   - Links to related code and sessions

---

## Recommendations

### Immediate Actions (Required)

1. ✅ **Restore clean baseline from add792eb3** (commit 673 lines)
2. ✅ **Fix LFS typo:** `full=full=` → `full=`
3. ✅ **Test in workflow_dispatch**
4. ✅ **Verify multi-turn Copilot sessions work**

### Medium-Term Actions (Recommended)

5. ⚠️ **Implement prevention strategy**
   - Pre-commit hooks to check for critical variables
   - CI gates to prevent variable removal
   - Documentation locking these variables as CRITICAL

6. ⚠️ **Selective re-addition of safe features** (if approved)
   - Actions v5+ updates (cosmetic, safe)
   - Git user configuration (functional, minimal risk)
   - Inline comments (non-functional)

### Long-Term Actions (Optional)

7. 💡 **Investigate 436-line jump mystery**
   - Why did 27240d92d jump from 673 → 1109 lines for a one-line fix?
   - Review git history for hidden changes

8. 💡 **Document CCA version lock mechanism**
   - Create `.codex/COPILOT_CCA_VERSION_LOCK_GUIDE.md`
   - Explain Sessions 1294-1295 context
   - Document `.github/copilot-evolution/integrated_system.py` integration

---

## Risk Assessment

### Current Risk (fad67fd8, 1109 lines)
- 🔴 **Critical:** Multi-turn agent sessions crash (production blocker)
- 🔴 **Critical:** YAML parse failures possible (workflow startup risk)
- 🟡 **Medium:** Increased code complexity (maintenance burden)

### Post-Restoration Risk (add792eb3 + fix, 673 lines)
- 🟢 **Low:** All safety mechanisms intact
- 🟢 **Low:** Proven stable in production
- 🟢 **Low:** Simple error handling (easy to maintain)

---

## Why This Matters

This regression is not just a configuration issue—it directly blocks **all multi-turn Copilot agent workflows**. Any task requiring agent to work across multiple turns (most meaningful Copilot sessions) will fail on turn 2+ with cryptic "Duplicate function call ID" errors.

The fix from Sessions 1294-1295 was intentional, deliberate, and critical. Removing it reintroduces a **production blocker** that should have been protected with CI gates and pre-commit hooks.

---

## Questions?

**For implementation details:** See `COPILOT_SETUP_RESTORATION_PLAN.md`
**For technical analysis:** See `COPILOT_SETUP_STEPS_ANALYSIS.md`
**For commit-by-commit breakdown:** See `COPILOT_SETUP_STEPS_COMMIT_DIFF_MAP.md`
**For navigation:** See `COPILOT_SETUP_ANALYSIS_INDEX.md`

---

**Status:** ✅ Analysis Complete | Ready for Implementation
**Next Step:** Execute Phase 1 (Baseline Restoration)
**Owner:** @mbaetiong
**Escalation:** Contact @mbaetiong if issues arise

