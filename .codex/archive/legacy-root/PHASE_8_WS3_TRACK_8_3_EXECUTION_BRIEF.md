# 🎯 Track 8.3 WS3 Execution Brief — Case-Collision De-Duplication

**Authority:** @mbaetiong (D-tier autonomous, GO CONTINUE)  
**Priority:** 🔴 **FIRST** (blocks Track 8.1 documentation work)  
**Timeline:** 2026-07-07T18:00Z → 2026-07-08T06:00Z (12-hour execution window)  
**Status:** Ready for immediate execution

---

## 📋 Executive Summary

Track 8.3 removes case-collision filename conflicts that prevent case-sensitive systems (Linux, macOS CI) from properly indexing repository files. This work is a prerequisite for Track 8.1 (documentation remediation) because renamed files must settle before bulk documentation updates.

**Key Deliverable:** `.gitattributes` configured for case-sensitivity enforcement + all case-collision renames completed.

---

## 🎯 Execution Objective

**Primary Goal:** Resolve all detected filename case-collisions in `.codex/` directory through systematic renaming.

**Success Criteria:**
- ✅ All case-colliding files identified and de-sequenced (from COMPATIBILITY_MATRIX.md)
- ✅ Renames executed in priority order (high → medium → low)
- ✅ `.gitattributes` created with case-sensitivity rules
- ✅ Git diff confirms all renames staged
- ✅ No duplicate files remain after execution

---

## 📊 Planning Reference Documents

**Primary Source:** `.codex/PHASE_8_3_COMPATIBILITY_MATRIX.md` (379 lines)
- Lists all detected case-collisions
- Priority wave assignments (High/Medium/Low)
- Remediation rationale per collision

**Secondary Sources:**
- `.codex/PHASE_8_3_REMEDIATION_PRIORITY.md` (628 lines) — 3-wave remediation sequence
- `.codex/PHASE_8_3_WORKSTREAM_2_COMPLETION_REPORT.md` (412 lines) — WS2 findings
- `.codex/PHASE_8_3_PLANNING_DOCUMENTS_INDEX.md` (307 lines) — Full planning index

---

## 🚀 Execution Workflow (Agent Handoff)

### Agent Assignment
**Primary Agent:** `unified-doc-agent` + `branch-divergence-resolution-agent` (case-sensitivity specialist)

### Workflow Steps

#### Step 1: Load Planning Documents (5 min)
1. Read COMPATIBILITY_MATRIX.md to extract all case-collisions
2. Extract priority waves (High/Medium/Low)
3. Build rename manifest (old → new mapping)

#### Step 2: Wave 1 — HIGH PRIORITY (30 min)
**Action:** Execute high-priority renames
```bash
# Example mappings from COMPATIBILITY_MATRIX
Old: .codex/phase_8_3_2_PLANNING.md
New: .codex/PHASE_8_3_2_PLANNING.md

Old: .codex/PHASE_8_3_2_PLANNING.md (lowercase "phase")
New: .codex/PHASE_8_3_2_PLANNING.md (uppercase "PHASE")
```

**Commands:**
```bash
git mv ".codex/[old_name]" ".codex/[new_name]"
# Repeat for all high-priority collisions
```

**Validation After Wave 1:**
```bash
git ls-files .codex/ | grep -iE "^.codex/phase_8.*phase.*\.(md|json|txt)$" | wc -l
# Should be 0 (no more lowercase phase prefixes)
```

#### Step 3: Wave 2 — MEDIUM PRIORITY (20 min)
Same workflow as Wave 1, applied to medium-priority files.

**Validation After Wave 2:**
```bash
git status --porcelain | grep "^R" | wc -l
# Should show 5-10 renames depending on collision count
```

#### Step 4: Wave 3 — LOW PRIORITY (15 min)
Final low-priority renames (if applicable).

#### Step 5: Create `.gitattributes` (10 min)
```bash
# Create .gitattributes at repository root
cat > .gitattributes << 'EOF'
# Case-sensitivity enforcement for .codex/ files
.codex/** text=auto

# Prevent case-collision regressions
.codex/PHASE_*.md text=auto
.codex/phase_*.md text=auto

# Enforce UTF-8 for all tracked files
* text=auto encoding=UTF-8
EOF

git add .gitattributes
```

#### Step 6: Final Validation (10 min)
```bash
# Verify no duplicate basenames with different cases
git ls-files .codex/ | tr '[:upper:]' '[:lower:]' | sort | uniq -d
# Should return empty (no duplicates)

# Verify all renames are staged
git diff --cached --name-status
# Should show 'R' entries for all renamed files
```

---

## 📋 Success Checklist

- [ ] All case-collisions identified from COMPATIBILITY_MATRIX.md
- [ ] Wave 1 (High) renames completed and validated
- [ ] Wave 2 (Medium) renames completed and validated
- [ ] Wave 3 (Low) renames completed and validated
- [ ] `.gitattributes` created with case-sensitivity rules
- [ ] Git diff shows 0 conflicts in renamed files
- [ ] Final validation: no duplicate basenames with different cases
- [ ] Single commit created: "refactor(case): De-duplicate filename case-collisions in .codex/"

---

## ⚠️ Risk Mitigation

**Potential Issues:**
1. **Git rename conflicts** — Use `git mv` to ensure proper tracking
2. **Workflow symlink issues** — Verify .github/workflows/ uses correct paths post-rename
3. **Documentation references** — Links within .codex/ files should auto-resolve post-rename

**Rollback Plan (if needed):**
```bash
git reset --hard HEAD~1  # Revert all renames
# Contact @mbaetiong for re-planning
```

---

## 🔄 Dependency Management

**MUST COMPLETE BEFORE:** Track 8.1 (documentation remediation)
- Reason: Bulk doc updates require stable filenames

**PARALLEL WITH:** Track 8.4 (dependency standardization) — independent
- Reason: No file path dependencies

**AFTER COMPLETION:** Notify Track 8.1 agent that renaming stable, ready to proceed

---

## 📊 Metrics & Reporting

**Expected Outputs:**
- Number of case-collisions resolved: 8-12
- Files renamed: 8-12
- Execution time: ~90 minutes
- Completion time: 2026-07-07T19:30Z (estimated)

**Success Criteria Met When:**
- All renames in git index
- No case-collision warnings from `git ls-files`
- `.gitattributes` committed
- Commit message: "refactor(case): De-duplicate case-collisions" + summary

---

## 🎯 Next Phase Handoff

**Upon Completion:**
1. Reply with execution summary
2. Include commit SHA: `git rev-parse HEAD`
3. Post status: "Track 8.3 WS3 COMPLETE — Ready for Track 8.1 coordination"
4. Provide `.gitattributes` snippet for documentation in Track 8.1 brief

**Expected Reply Format:**
```markdown
## Track 8.3 Execution Summary
- Renames Executed: X of Y planned
- Execution Time: Z minutes
- Commit SHA: [SHA]
- Status: ✅ COMPLETE / ❌ ISSUES ENCOUNTERED
- Blocking Issues: [none / details]
- Ready for Track 8.1: [YES / NO]
```

---

## 📞 Support & Escalation

**If stuck on:**
- Rename conflicts → Check COMPATIBILITY_MATRIX.md for sequence order
- Git merge conflicts → Use `git status` to identify conflicting files
- Validation failures → Re-run validation scripts with verbose output

**Escalation Point:**
- If >50% of renames fail → Stop, document errors, escalate to @mbaetiong
- Authority: D-tier autonomous (GO CONTINUE unless escalation needed)

---

**Authority:** @mbaetiong D-tier autonomous  
**Entry Point:** `.codex/PHASE_8_WS2_SESSION_CONSOLIDATION_HANDOFF.md`  
**Status:** 🟢 **READY FOR AGENT ACTIVATION**
