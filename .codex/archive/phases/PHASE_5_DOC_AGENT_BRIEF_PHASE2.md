# Phase 5 Week 2 Documentation Agent Brief — Phase 2

**Authority:** Phase 5 Execution Mandate (@mbaetiong)  
**Agent:** unified-doc-agent  
**Phase:** Phase 2 (Remediation & Validation)  
**Duration:** 2026-07-03 through 2026-07-09  
**Effort:** 4.5 hours  
**Autonomy Level:** Full (D)

---

## 🎯 Executive Summary

**Phase 1 Status:** ✅ COMPLETE (97.1% link validity, exceeds 95% target)  
**Phase 2 Objectives:** Execute remediation of broken script references (Tier 1 & 4) and create archive policy  
**Expected Outcome:** Improve link validity to 97.5%+, document archive procedures, maintain quality gates

---

## 📊 Week 1 Achievements (Phase 1)

**Results:**
- Link validity: **97.1%** (target: 95%+) — **+2.1pp above target** ✅
- Critical path: **100%** (pristine) ✅
- Links audited: 10,271 total
- Categorization: 4-tier system with clear remediation pathways
- Deliverables: 5 comprehensive reports (47.2 KB)

**Key Findings:**
- Tier 1 (Non-existent scripts): 95 references → mostly in Phase 10/11 planning docs
- Tier 2 (Valid directory refs): 116 references → **actually valid** (reclassified)
- Tier 3 (Phase-specific): 85 references → archive policy needed
- Tier 4 (Moved scripts): 113 references → need location verification

---

## 🎯 Phase 2 Objectives (Week 2)

### Objective 1: Fix Tier 1 Non-Existent Scripts (2-3 hours)

**What:** Address 95 references to scripts that don't exist  
**Where:** Mostly in `.codex/` and `docs/planning/` directories  
**Examples:**
- `scripts/phase_10_ml_optimizer.py` (Phase 10 planning)
- `scripts/phase_11_governance.py` (Phase 11 planning)
- `tools/advanced_analysis.py` (placeholder)

**Approach:**
1. For planning docs: Update with `<!-- NOTE: Script planned for Phase 10+ -->` markers
2. For active docs: Create stubs or link to alternatives
3. For consolidation scripts: Update with actual consolidated locations

**Success Criteria:**
- 60-70% of Tier 1 refs addressed (55-65 scripts)
- All remaining refs have explanatory notes
- No false "broken" links in active documentation

---

### Objective 2: Verify Tier 4 Moved/Relocated Scripts (1-2 hours)

**What:** Verify actual locations of 113 scripts that have moved  
**Where:** Check against actual repository structure

**Approach:**
1. Identify scripts mentioned in broken refs
2. Search for actual location in repository
3. Update documentation with correct paths
4. Add redirect comments where applicable

**Success Criteria:**
- Verify locations of 80+ moved scripts
- Update 70+ documentation references
- Create redirect mapping for commonly referenced scripts

---

### Objective 3: Create Archive Policy (1 hour)

**What:** Document criteria and procedures for archiving content  
**Output:** `.codex/ARCHIVE_POLICY.md` (2-3 KB)

**Requirements:**
- Archive criteria (age, usage, phase completion)
- Archive procedures (how to archive, where archived content goes)
- Recovery procedures (how to retrieve archived content)
- Examples of what should/shouldn't be archived

**Structure:**
1. Introduction & scope
2. Archive criteria
3. Archive procedures
4. Directory structure for archived items
5. Recovery procedures
6. Quarterly maintenance schedule
7. Examples (Phase 4 archive, Phase 5 archive, etc.)

**Success Criteria:**
- Policy document created and documented
- Clear guidance for future Phase transitions
- Aligned with 95%+ link validity target

---

### Objective 4: Link Re-Validation (0.5 hours)

**What:** Run link validator after remediation to confirm improvements  
**Target:** Confirm 97.5%+ link validity (up from 97.1%)

**Approach:**
1. Re-run link validation script on all documentation
2. Compare against Week 1 baseline (10,271 links)
3. Generate new metrics report
4. Verify critical path still 100% valid

**Success Criteria:**
- Link validity: 97.5%+ (from 97.1%)
- Critical path: 100% (maintain perfect score)
- All quality gates pass

---

## 📋 Deliverables

### Documentation Phase 2 Deliverables

1. **`.codex/PHASE_5_ARCHIVE_POLICY.md`** (2-3 KB)
   - Archive criteria and procedures
   - Directory structure guidelines
   - Recovery procedures

2. **`.codex/PHASE_5_WEEK2_REMEDIATION_LOG.md`** (3-4 KB)
   - Tier 1 fixes applied (script count, doc updates)
   - Tier 4 verifications completed (script locations found)
   - Before/after link validity metrics

3. **`.codex/PHASE_5_LINK_STATUS_WEEK2.md`** (2-3 KB)
   - Updated link validity metric (target: 97.5%+)
   - Tier-by-tier status summary
   - Quality gates validation (all 7/7 pass)

4. **`.codex/PHASE_5_WEEK2_CHECKPOINT.md`** (4-5 KB)
   - Go/No-Go decision for Phase 3
   - Archive policy status
   - Link validation results
   - Ready for Week 3

### Expected Total Output
- 4 comprehensive documents (12-15 KB)
- Maintained/improved link validity (97.5%+ vs 97.1%)
- Archive policy operationalized
- All quality gates pass ✅

---

## 🚀 Execution Timeline

### Wednesday, July 3 (Phase 2 Start)
- **Morning:** Receive Phase 2 brief
- **Day:** Begin Tier 1 script reference fixes (2-3h)
- **Evening:** Document fixes in remediation log

### Thursday, July 4
- **Day:** Continue Tier 1 fixes (additional scripts)
- **Day:** Start Tier 4 location verification
- **Evening:** Prepare for policy creation

### Friday, July 5
- **Day:** Complete Tier 1 fixes
- **Day:** Create archive policy document
- **Day:** Begin link re-validation

### Saturday-Sunday, July 6-7
- Passive checkpoint (manual validation runs)

### Monday-Tuesday, July 8-9 (Week 2 End)
- **Morning:** Complete link re-validation
- **Day:** Final metrics consolidation
- **Afternoon:** Prepare Week 2 checkpoint report
- **Evening:** Deliver all 4 Phase 2 deliverables

---

## 📊 Success Criteria

### Primary Targets

| Criterion | Target | Status |
|-----------|--------|--------|
| Link validity | 97.5%+ (from 97.1%) | Aim for +0.4pp improvement |
| Tier 1 fixes | 60-70% complete (55-65/95) | Success if 60%+ done |
| Tier 4 verification | 70-80% complete (80-113) | Success if 70%+ verified |
| Archive policy | Complete & operationalized | Success if documented & clear |
| Critical path | Maintain 100% | Success if pristine maintained |
| Quality gates | All 7/7 pass | Success if all pass |

### Secondary Targets

- Improved searchability through better archive policy
- Clear remediation pathways for future phases
- Reduced "false broken" link reports going forward

---

## 🔧 Tools & Resources Available

- Link validation script (from Phase 1)
- `.codex/PHASE_5_SCRIPT_PATH_AUDIT.md` (from Phase 1 — detailed audit)
- `.codex/LINK_VALIDITY_TRACKING.md` (from Phase 1 — tracking template)
- Repository file system (for location verification)
- GitHub API (for cross-repository reference resolution)

---

## 📞 Escalation Guidelines

**Escalate to @mbaetiong if:**
- Script consolidation prevents verification (can't find actual location)
- Archive policy conflicts with CI infrastructure
- Link validity drops below 95% (shouldn't happen, but alert if it does)
- Week 2 effort exceeds 5 hours (original estimate: 4.5h)

**Authority:** Phase 5 Execution Mandate (@mbaetiong)  
**Autonomy:** Full (D) — Execute independently, escalate only critical blockers

---

## 🎯 Phase 2 Success = Phase 3 Ready

Upon successful Phase 2 completion:
- ✅ Archive policy operationalized (99.5%+ users understand archival procedures)
- ✅ Link validity improved to 97.5%+ (exceeds 95% minimum)
- ✅ Critical path maintained at 100%
- ✅ Ready for Phase 3 (ongoing weekly validation)

---

**Phase 2 Brief Generated:** 2026-07-02  
**Phase 2 Launch:** 2026-07-03 (morning)  
**Expected Completion:** 2026-07-09 (evening)  
**Authority:** Phase 5 Execution Mandate (@mbaetiong)
