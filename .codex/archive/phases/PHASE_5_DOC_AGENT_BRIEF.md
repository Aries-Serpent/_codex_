# Phase 5: Documentation Maintenance Agent Brief

**Agent:** `unified-doc-agent`  
**Campaign:** Phase 5 Documentation Maintenance & Link Validation  
**Date:** 2026-06-25T23:56:00Z  
**Authority:** CAD-Mandate Phase 5 Documentation Stream  
**Status:** ✅ READY FOR DELEGATION

---

## 📋 Executive Summary

Execute documentation maintenance campaign to maintain **95%+ link validity** and fix critical path issues identified in Phase 4.

**Target Link Validity:** Maintain 95%+ (current: 95.5%)  
**Primary Focus:** Script path fixes (H-1), archive audit (M-1), ongoing maintenance  
**Timeline:** 2026-06-26 through 2026-07-16+ (ongoing, 1-2h/week)  
**Effort Estimate:** 5-10 hours (Phase 5 peak)

---

## 🎯 Primary Objectives

### Objective 1: Fix 388 Broken Script Paths (H-1 Priority, 1-2 hours)

**Problem:**
- 388 broken script path references in documentation
- Scripts moved/consolidated but docs not updated
- Impacts searchability and accessibility
- Phase 4 Priority: HIGH

**Scope:**
- Identify all documentation files referencing scripts
- Verify actual paths in `.github/scripts/`, `scripts/`, etc.
- Update all broken references
- Verify all `.codex/` paths exist and are current

**Implementation Approach:**

1. **Audit Phase (30 min):**
   - Scan all `.md` files for script path references
   - Use grep/ripgrep to find patterns:
     - `scripts/*/` references
     - `.github/scripts/` references
     - `./scripts/` relative paths
   - Catalog broken vs. valid paths

2. **Verification Phase (30 min):**
   - Cross-check against actual repository structure
   - Verify `.codex/` paths are current
   - Check `.github/workflows/` script calls

3. **Update Phase (1 hour):**
   - Update all broken paths to correct locations
   - Test all links post-update
   - Verify docs build successfully

**Expected Impact:** Remove ~388 broken links, improve 95.5% → 96%+

---

### Objective 2: Archive Audit & Policy Documentation (1 hour)

**Problem:**
- 6 template archive references exist (documented but untracked)
- No formal archival policy for Phase 6+
- Unclear which docs are intentionally archived vs. forgotten

**Scope:**
- Document all 6 intentional archive references
- Create archival policy for Phase 6 onward
- Establish process for marking archived content
- Create template for future archived documentation

**Implementation Approach:**

1. **Audit Phase (20 min):**
   - Find and document all 6 template archive references
   - Verify each is intentional (not broken)
   - Assess whether archival is appropriate

2. **Policy Creation (30 min):**
   - Create `.codex/ARCHIVE_POLICY.md`:
     - Definition: What constitutes archival content
     - Criteria: When content should be archived
     - Marking: How to mark content as archived
     - Retention: How long to keep archived versions
     - Cleanup: When to remove archived content

3. **Documentation (10 min):**
   - Create template for archived docs
   - Link policy from main documentation index
   - Document Phase 6 archival roadmap

**Expected Output:** `.codex/ARCHIVE_POLICY.md` + archival documentation template

---

### Objective 3: Link Validation & Ongoing Maintenance

**Scope (Ongoing, 1-2h per week):**
- Weekly link validation scan (all 10,271 internal links)
- Monitor for new broken links
- Maintain 95%+ validity rate
- Track metrics over time

**Current Status (From Phase 4):**
- Total internal links: 10,271
- Valid: 9,811 (95.5%)
- Broken: 460 (4.5%, all non-critical)
- Critical path health: 100% (0 broken in README, CHANGELOG, agent docs)

**Maintenance Tasks:**

1. **Weekly Validation (30 min):**
   - Run link checker against all `.md` files
   - Generate report: `.codex/PHASE_5_LINK_STATUS_WEEK{N}.md`
   - Flag any newly broken links

2. **Quarterly Audits:**
   - Q2 2026 (June-Jul): Critical path fixes, archive cleanup
   - Q3 2026 (Aug-Sep): Comprehensive link audit, broken-link reduction
   - Q4 2026 (Oct-Dec): Full refresh, pages sync, archival cleanup

3. **Monthly Updates:**
   - Update broken link registry
   - Prioritize fixes based on impact
   - Document known limitations

---

## 📊 Current State (From Phase 4 Audit)

**Documentation Health Scorecard:** 9.7/10 (EXCELLENT)

**Link Validation Results:**
- Files scanned: 4,592 documentation files
- Internal links: 10,271 total
  - Valid: 9,811 (95.5%) ✅
  - Broken: 460 (4.5%, all non-critical)
  - Template placeholders: 42 (intentional)
  - Archive references: 6 (intentional)

**Critical Path Status:** 100% (0 broken links in critical docs)
- README.md: ✅ All links valid
- CHANGELOG.md: ✅ All links valid
- Agent documentation: ✅ All links valid
- Admin documentation: ✅ All links valid

**Priority Issues Identified:**

| Priority | Issue | Count | Effort | Status |
|----------|-------|-------|--------|--------|
| 🔴 HIGH (H-1) | Broken script paths | 388 | 1-2h | Phase 5 ACTIONABLE |
| 🟡 MEDIUM (M-1) | Archive references | 6 | 1h | Phase 5 ACTIONABLE |
| 🟢 LOW (L-1) | Absolute path refs | 24 | Q3 2026 | Deferred to refactor |

---

## 🔧 Implementation Strategy

### Phase 1: Script Path Audit & Fix (Week 1, 1-2 hours)

1. **Scan documentation for script references:**
   ```bash
   grep -r "scripts/" docs/ .codex/ --include="*.md"
   grep -r ".github/scripts/" docs/ .codex/ --include="*.md"
   ```

2. **Map actual script locations:**
   - Inventory all scripts in `scripts/` directory
   - Inventory all `.github/scripts/` content
   - Inventory all `.codex/` scripts

3. **Update broken references:**
   - Find/replace all broken paths
   - Test links post-update
   - Verify build succeeds

4. **Document results:**
   - Create `.codex/PHASE_5_SCRIPT_PATH_AUDIT.md`
   - List all fixes applied
   - Verify 388 issues resolved

### Phase 2: Archive Policy & Documentation (Week 2, 1 hour)

1. **Create archival policy:**
   - Document `.codex/ARCHIVE_POLICY.md`
   - Define archival criteria
   - Establish marking conventions

2. **Document 6 intentional archives:**
   - Verify each archive is appropriate
   - Add policy reference
   - Link from main documentation

3. **Create archival template:**
   - Template for future archived docs
   - Checklist for archival process
   - Link policy and template from docs/

### Phase 3: Ongoing Validation (Weeks 3-4 & Beyond, 1-2h/week)

1. **Weekly link validation:**
   - Run comprehensive link checker
   - Generate weekly status report
   - Alert on new broken links

2. **Quarterly comprehensive audits:**
   - Q2: Focus on critical paths (current)
   - Q3: Comprehensive reduction, relative path migration
   - Q4: Full refresh, pages sync

3. **Monthly tracking:**
   - Maintain `.codex/LINK_VALIDITY_TRACKING.md`
   - Document trends over time
   - Identify patterns in breakage

---

## ✅ Success Criteria

### Phase 1: Script Path Fixes
- ✅ All 388 broken script paths identified
- ✅ All broken paths updated to correct locations
- ✅ All `.codex/` path references verified current
- ✅ Audit report created: `.codex/PHASE_5_SCRIPT_PATH_AUDIT.md`
- ✅ Link validity improves: 95.5% → 96%+

### Phase 2: Archive Documentation
- ✅ Archive policy created: `.codex/ARCHIVE_POLICY.md`
- ✅ All 6 intentional archives documented
- ✅ Archive template created
- ✅ Policy integrated into documentation

### Phase 3: Ongoing Maintenance
- ✅ **Maintain 95%+ link validity** (current: 95.5%)
- ✅ Weekly validation reports generated
- ✅ Zero critical path broken links
- ✅ Quarterly audits scheduled and tracked

### Overall Metrics
- ✅ Documentation health scorecard: ≥9.5/10
- ✅ Critical link health: 100%
- ✅ GitHub Pages deployment ready
- ✅ Weekly progress checkpoints created

---

## 🔄 Weekly Checkpoint Schedule

**Week 1 (Jun 26 - Jul 02):**
- Script path audit complete
- 388 broken paths identified and mapped
- Initial fixes applied
- Checkpoint: `.codex/PHASE_5_WEEK1_CHECKPOINT.md`

**Week 2 (Jul 03 - Jul 09):**
- Archive policy completed
- All 6 archives documented
- Archive template created
- Ongoing validation started
- Checkpoint: `.codex/PHASE_5_WEEK2_CHECKPOINT.md`

**Week 3 (Jul 10 - Jul 16):**
- All fixes validated
- Final link validation run
- Quarterly Q2 summary completed
- Checkpoint: `.codex/PHASE_5_WEEK3_CHECKPOINT.md`

**Week 4+ (Jul 17+):**
- Ongoing weekly validation (1-2h/week)
- Monthly tracking updates
- Quarterly audit schedule

---

## 📁 Artifact Locations

**All artifacts stored in repository-tracked `.codex/` directory:**
- `.codex/PHASE_5_SCRIPT_PATH_AUDIT.md` — Script path fixes documented
- `.codex/ARCHIVE_POLICY.md` — Archive policy and guidelines
- `.codex/PHASE_5_LINK_STATUS_WEEK1.md` — Weekly link status
- `.codex/PHASE_5_LINK_STATUS_WEEK2.md` — Weekly link status
- `.codex/PHASE_5_LINK_STATUS_WEEK3.md` — Weekly link status
- `.codex/LINK_VALIDITY_TRACKING.md` — Long-term tracking
- `.codex/PHASE_5_WEEK1_CHECKPOINT.md` — Week 1 progress
- `.codex/PHASE_5_WEEK2_CHECKPOINT.md` — Week 2 progress
- `.codex/PHASE_5_WEEK3_CHECKPOINT.md` — Week 3 progress

**Test files:**
- `templates/archived_doc_template.md` — Template for archived docs
- `docs/ARCHIVE_POLICY.md` — Link to archive policy

---

## 🎯 Known Constraints & Resources

### Constraints
- No major documentation refactoring (out of scope)
- Script path changes must be non-breaking
- Archive policy cannot conflict with existing CI patterns

### Available Resources
- Phase 4 link validation report: `.codex/PHASE_4_LINK_VALIDATION_REPORT.md`
- Phase 4 maintenance roadmap: `.codex/PHASE_4_DOC_MAINTENANCE_ROADMAP.md`
- Existing link checker: `link_validator.py`
- GitHub Pages config: `mkdocs.yml`

### Link Checker Tools
- Built-in validator: `scripts/link_validator.py`
- MkDocs build: `mkdocs build` (validates pages)
- Manual grep for patterns: `grep -r` with script path patterns

---

## 📞 Escalation & Blockers

**Blocker Escalation:** If any of these issues arise:
- Script paths no longer exist (consolidation changes)
- Broken links are in CI/build infrastructure
- Archive references are legitimately broken
- Cannot determine intentionality of archive refs

→ Escalate to @mbaetiong with detailed context

**Authority Level:** Full autonomy (D) to make maintenance decisions

---

## 📝 Phase 4 Reference

From Phase 4 Documentation Audit:
- 95.5% link validity confirmed
- 388 broken script paths identified (H-1 priority)
- 6 template archive references documented
- 24 absolute path references deferred to Q3
- GitHub Pages ready for production

---

**Brief Created:** 2026-06-25T23:56:00Z  
**Status:** ✅ READY FOR AGENT EXECUTION  
**Next Step:** Launch unified-doc-agent with this brief
