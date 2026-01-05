# Terminology Fix Tracking Document

**Created:** 2026-01-05
**Status:** In Progress  
**Policy Reference:** `.codex/CODEBASE_AGENCY_POLICY.md` Section 4

## Policy Violation Details

**Violation:** Using time-based terminology (weeks, months, quarters, Q1/Q2) for future work planning instead of pre-commit/commit cycle terminology.

**Policy Requirement:**
- ✅ Use: "Pre-commit 1-2", "Pre-commit 3-4", "Phase X", "commit cycles"
- ❌ Avoid: "Week 1", "Month 2", "Q1 2026", "quarterly"

**Exception:** Historical dates and factual external constraints (e.g., "90-day retention") are acceptable.

---

## Files Updated

### Batch 1: Files Created in This PR (COMPLETE)
- [x] `.codex/WORKFLOW_CACHING_IMPLEMENTATION_PLAN.md` (Commit e3fcd68)
- [x] `.codex/KNOWN_BROKEN_LINKS_TRACKING.md` (Commit e3fcd68)
- [x] `.codex/LINK_CHECKER_IMPLEMENTATION_SUMMARY.md` (Commit e3fcd68)

### Batch 2: High Priority .codex/ Files (COMPLETE)
- [x] `.codex/AI_AGENT_UTILITIES_REGISTRY.md` (Fixed: Pre-commit 1-8)
- [x] `.codex/prompts/COGNITIVE_BRAIN_PHASE_8_CONTINUATION.md` (Fixed: Pre-commit 1-2)
- [x] `.codex/prompts/COGNITIVE_BRAIN_PHASE_8_3_CONTINUATION.md` (Fixed: Pre-commit 1-12)
- [x] `.codex/COMPREHENSIVE_WORKFLOW_CONSOLIDATION_PLAN.md` (Already compliant)

### Batch 3: Plans and Reports (COMPLETE ✅ - 11 of 11)
- [x] `.codex/plans/cognitive_brain_phase_implementation.md` (Historical markers preserved) - Commit 86a63a5
- [x] `.codex/plans/COGNITIVE_BRAIN_STATUS_V2.md` (Pre-commit 1-2) - Commit 86a63a5
- [x] `.codex/plans/interactive_demos_plan.md` - Commit this
- [x] `.codex/plans/v10_implementation_verification_and_phases.md` (Cognitive brain, 30 replacements) - Commit this
- [x] `.codex/plans/autonomous_implementation_master_plan.md` - Commit this
- [x] `.codex/plans/COGNITIVE_BRAIN_PHASE_8_STATUS_ASSESSMENT.md` (Cognitive brain, 10 replacements) - Commit this
- [x] `.codex/plans/github_pages_improvement_plan.md` - Commit this
- [x] `.codex/plans/v10_agents_enhanced_implementation_plan.md` - Commit this
- [x] `.codex/reports/COMPREHENSIVE_IMPLEMENTATION_STATUS.md` - Commit this
- [x] `.codex/reports/v10_agents_capabilities_and_research_roadmap.md` (Cognitive brain, 4 replacements) - Commit this
- [x] `.codex/reports/pr_2685_status_report.md` - Commit this

### Batch 4: .github/ Files (IN PROGRESS - 10 of 105+ complete)
- [x] `.github/copilot-prompts/active/COGNITIVE-BRAIN-STATUS-2026-01-01.md` - Commit this
- [x] `.github/PHASE3_FOLLOWUP_PROMPT.md` - Commit this
- [x] `.github/copilot-prompts/active/PHASE5-COMPLETE-SUMMARY.md` - Commit this
- [x] `.github/AGENTS.md` - Commit this
- [x] `.github/copilot_agent_task_prompt_v1.3.0_consolidation.md` - Commit this
- [x] `.github/workflows/CACHE_OPTIMIZATION_REPORT.md` - Commit this
- [x] `.github/workflows/PHYSICS_BASED_WORKFLOW_PRIORITIZATION.md` - Commit this
- [x] `.github/copilot-prompts/active/PHASE1-COMPLETE-NEXT-STEPS.md` - Commit this
- [x] `.github/copilot-prompts/active/PHASE2-COMPLETE-PHASE3-READY.md` - Commit this
- [ ] `.github/agents/*.md` (40+ remaining files)
- [ ] `.github/prompts/*.md` (25+ remaining files)
- [ ] `.github/*.md` (20+ remaining files)

### Batch 5: docs/ Files (IN PROGRESS - 9 of 70+ complete)
- [x] `docs/admin/CONTINUATION_ROADMAP.md` - Commit this
- [x] `docs/REPO_ADMIN_DECISIONS_SUMMARY.md` - Commit this
- [x] `docs/ADMIN_DECISIONS_README.md` - Commit this
- [x] `docs/PHASE4_COMPLETE.md` - Commit this
- [x] `docs/plans/COMPREHENSIVE_PLAN_VERIFICATION.md` - Commit this
- [x] `docs/LEVEL_4_MLOPS_ASSESSMENT.md` - Commit this
- [x] `docs/mcp/ADVANCED_FEATURES_PLANSET.md` - Commit this
- [x] `docs/MASTER_INDEX.md` - Commit this
- [x] `docs/testing/FUTURE_RESEARCH_DEEP_DIVE.md` - Commit this
- [x] `docs/workflows/CONSOLIDATION_PLAN.md` - Commit this
- [ ] `docs/plans/*.md` (20+ remaining files)
- [ ] `docs/*.md` (30+ remaining files)

---

## Rationale for Batching

**Immediate (This PR):**
- Files created in this PR session
- Direct responsibility and fresh context

**High Priority (This PR):**
- Active planning documents in `.codex/`
- Cognitive Brain phase prompts (actively used)
- Files likely to be referenced by next agent

**Deferred to Future PR:**
- Historical reports (retrospective - less critical)
- Archived documentation
- Large-scale updates requiring dedicated session
- Files requiring domain-specific context

---

## Update Strategy

### For Each File:
1. **Review context** - Understand whether references are historical or future
2. **Preserve historical** - Keep "Completed: 2025-12-15" style dates
3. **Update future planning** - Replace weeks/months with pre-commits
4. **Maintain consistency** - Use same terminology throughout file
5. **Validate readability** - Ensure changes make sense in context

### Terminology Mapping:
| Old | New | Context |
|-----|-----|---------|
| Week 1-2 | Pre-commit 1-4 | Planning phases |
| Weeks 2-3 | Pre-commit 5-8 | Multi-step work |
| Month 1 | Pre-commit 1-8 | Longer phases |
| Q1 2026 | Phase 2-5 | Quarterly scope |
| weekly | per commit cycle | Frequency |
| monthly | per 4-5 commit cycles | Frequency |
| quarterly | per phase | Frequency |

---

## Self-Review Checklist

### Iteration 1: ✅ COMPLETE
- [x] Identified policy violation
- [x] Fixed 3 files created in this PR
- [x] Committed changes

### Iteration 2: ✅ COMPLETE
- [x] Created tracking document
- [x] Updated high-priority .codex/ files (4 files)
- [x] Validated changes don't break references
- [x] Updated policy file with mandatory session completion protocol
- [x] Committed batch 2 updates

### Iteration 3: ✅ COMPLETE
- [x] Fixed all 9 remaining Batch 3 files
- [x] Maintained cognitive brain architecture correlation
- [x] Preserved AfterMath/PDA loop references
- [x] Applied consistent terminology (44 replacements in cognitive brain files)

### Iteration 4: ✅ COMPLETE
- [x] Fixed 10 high-priority Batch 4 files (.github/)
- [x] Fixed 9 high-priority Batch 5 files (docs/)
- [x] Prioritized active prompts and cognitive brain related files
- [x] Validated changes maintain context appropriateness

### Iteration 5: PENDING
- [ ] Create follow-up prompt for deferred work
- [ ] Submit as PR comment with @copilot
- [ ] Verify submission successful

---

## Deferred Work Justification

**Reasoning for Batch 3-5 Deferral:**

1. **Scope Management:**
   - 200+ files require updates
   - Single PR should focus on immediate violations
   - Large-scale updates risk introducing errors

2. **Context Preservation:**
   - Many historical documents reference completed work
   - Changing dates retroactively can confuse timeline
   - Requires careful review of each file's purpose

3. **Best Effort This Session:**
   - Fixed all files I directly created (100% responsibility)
   - Updating high-priority active planning docs (Batch 2)
   - Created comprehensive plan for remaining work

4. **Continuous Improvement:**
   - Follow-up PR will be dedicated to terminology migration
   - Next agent will have this tracking doc for guidance
   - Systematic approach reduces risk of mistakes

**Resolution Plan:**
- Create follow-up prompt for next Copilot agent
- Include this tracking doc as reference
- Specify files to update in priority order
- Provide terminology mapping table
- Mandate completion before other work

---

## Verification Commands

```bash
# Find remaining violations in .codex/
grep -r "Week [0-9]\|Weeks [0-9]\|Q[1-4] 202[0-9]" --include="*.md" .codex/ -l

# Count total violations
grep -r "Week [0-9]\|Weeks [0-9]\|Q[1-4] 202[0-9]" --include="*.md" --exclude-dir=node_modules --exclude-dir=.git -c | awk -F: '{sum += $2} END {print sum}'

# Check specific file
grep -n "Week\|Q[1-4] 202" filename.md
```

---

## Status: BATCH 3 COMPLETE, BATCH 4-5 IN PROGRESS

**Current:** Batches 4-5 High-Priority Files (19 files updated this commit)  
**Completed:** Batch 1 (3 files), Batch 2 (4 files), Batch 3 (11 files), Batch 4 partial (10 files), Batch 5 partial (9 files)
**Total Progress:** 37 files updated across 5 batches  
**Next:** Continue Batch 4-5 (111+ files remaining)  
**Blocked:** None  
**Estimated Remaining:** ~656 violations across 111+ files

---

**This tracking ensures no work is truly deferred - it's planned, documented, and will be completed in next session.**
