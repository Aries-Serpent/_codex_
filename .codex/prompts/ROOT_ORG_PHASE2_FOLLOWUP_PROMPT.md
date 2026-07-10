# Root Organization Phase 2 - Follow-Up Prompt

**Date Created:** 2026-02-06T03:27:26Z  
**Phase:** 2 (Documentation Files)  
**Previous Phase:** Phase 1 Complete ✅  
**Status:** Ready for Execution

---

## 🎯 Quick Start for Next Agent

```
@copilot Continue root folder organization - Phase 2: Move remaining documentation files

Context:
- Phase 1 complete: 30 files moved, 100% success rate
- Root reduced from 92 to 62 files (33% reduction)
- Zero broken links maintained
- All reference updates automated

Phase 2 Objectives:
1. Move docs/analysis/PR_3133_ANALYSIS.md → docs/analysis/PR_3133_ANALYSIS.md
2. Plan and execute .codex/archive/deprecated/AGENTS.md migration (6 references confirmed)
3. Validate all documentation links
4. Update Cognitive Brain status

Previous Work:
- See: .codex/reports/ROOT_ORG_INDEX.md (navigation)
- See: .codex/plans/ROOT_ORG_COMPREHENSIVE_CLEANUP_PLAN.md (master plan)
- See: .codex/reports/ROOT_ORG_PHASE1_EXECUTION_SUMMARY.md (Phase 1 results)

Tools Available:
- scripts/root_org/validate_references.py
- scripts/root_org/organize_root_incremental.py
- scripts/root_org/update_links_atomic.py
- scripts/root_org/rollback_move.py

Safety Requirements:
- Maintain zero-break guarantee
- Validate all references before moving
- Use incremental batches (max 10 files)
- Test after each move
- Document all changes
```

---

## 📋 Phase 2 Detailed Plan

### Files to Move

#### File 1: docs/analysis/PR_3133_ANALYSIS.md
**Source:** `/docs/analysis/PR_3133_ANALYSIS.md`  
**Target:** `docs/analysis/PR_3133_ANALYSIS.md`  
**Risk Level:** MEDIUM (estimated 1-3 references)  
**Priority:** HIGH (documentation should not be in root)

**Steps:**
1. Scan for references using `validate_references.py`
2. Create `docs/analysis/` directory if not exists
3. Execute `git mv docs/analysis/PR_3133_ANALYSIS.md docs/analysis/PR_3133_ANALYSIS.md`
4. Update all references atomically
5. Verify no broken links
6. Commit with message: `docs: Move PR 3133 analysis to docs/analysis/`

**Expected References:**
- Likely in `.codex/` documentation
- Possibly in `docs/` index files
- May be in PR-related files

#### File 2: .codex/archive/deprecated/AGENTS.md
**Source:** `/.codex/archive/deprecated/AGENTS.md`  
**Target:** TBD (requires analysis)  
**Options:**
1. `docs/agents/.codex/archive/deprecated/AGENTS.md` (if documentation focus)
2. `.github/agents/docs/.codex/archive/deprecated/AGENTS.md` (if agent-specific)
3. `.codex/docs/.codex/archive/deprecated/AGENTS.md` (if internal reference)

**Risk Level:** MEDIUM (6 references confirmed, not 293)  
**Priority:** HIGH (important documentation)

**Steps:**
1. Re-scan references to confirm count (should be 6, not 293)
2. Analyze reference types and locations
3. Determine best target location based on usage patterns
4. Create target directory if needed
5. Execute move with reference updates
6. Update Cognitive Brain agent documentation
7. Commit with message: `docs: Move .codex/archive/deprecated/AGENTS.md to appropriate location`

**Expected References:**
- Agent documentation files
- README or CONTRIBUTING
- Possibly in scripts or tools
- May be in .codex/ files

### Prerequisites

Before starting Phase 2:
1. ✅ Phase 1 complete (verified)
2. ✅ All Phase 1 changes committed (verified)
3. ✅ Working tree clean (verified)
4. ⏳ Tests passing (to be verified)
5. ⏳ CI/CD green (to be verified)

---

## 🔍 Reference Analysis Required

### For docs/analysis/PR_3133_ANALYSIS.md

Run this command:
```bash
python scripts/root_org/validate_references.py docs/analysis/PR_3133_ANALYSIS.md
```

Expected output:
```json
{
  "file": "docs/analysis/PR_3133_ANALYSIS.md",
  "references": [
    {"file": "...", "line": ..., "type": "..."}
  ],
  "count": "...",
  "risk_level": "..."
}
```

### For .codex/archive/deprecated/AGENTS.md

Run this command:
```bash
python scripts/root_org/validate_references.py .codex/archive/deprecated/AGENTS.md
```

**Note:** Previous analysis indicated 293 references, but actual count is likely 6. Verify before proceeding.

---

## 🛠️ Execution Commands

### Step 1: Validate References
```bash
cd /home/runner/work/_codex_/_codex_

# Check docs/analysis/PR_3133_ANALYSIS.md
python scripts/root_org/validate_references.py docs/analysis/PR_3133_ANALYSIS.md > /tmp/refs_pr3133.json

# Check .codex/archive/deprecated/AGENTS.md (re-verify count)
python scripts/root_org/validate_references.py .codex/archive/deprecated/AGENTS.md > /tmp/refs_agents.json

# Review outputs
cat /tmp/refs_pr3133.json
cat /tmp/refs_agents.json
```

### Step 2: Move docs/analysis/PR_3133_ANALYSIS.md
```bash
# Create target directory
mkdir -p docs/analysis

# Execute move with batch script
python scripts/root_org/organize_root_incremental.py \
  --file docs/analysis/PR_3133_ANALYSIS.md \
  --target docs/analysis/PR_3133_ANALYSIS.md \
  --update-refs \
  --validate

# Verify
ls -la docs/analysis/PR_3133_ANALYSIS.md
git status
```

### Step 3: Move .codex/archive/deprecated/AGENTS.md
```bash
# Determine target based on analysis
# Option 1: docs/agents/
mkdir -p docs/agents
python scripts/root_org/organize_root_incremental.py \
  --file .codex/archive/deprecated/AGENTS.md \
  --target docs/agents/.codex/archive/deprecated/AGENTS.md \
  --update-refs \
  --validate

# OR Option 2: .github/agents/docs/
mkdir -p .github/agents/docs
python scripts/root_org/organize_root_incremental.py \
  --file .codex/archive/deprecated/AGENTS.md \
  --target .github/agents/docs/.codex/archive/deprecated/AGENTS.md \
  --update-refs \
  --validate

# Verify
git status
```

### Step 4: Validation
```bash
# Check for broken links
python scripts/root_org/validate_references.py --check-all

# Run tests (if available)
pytest tests/ -v

# Verify git status
git diff --stat
git status
```

---

## 📊 Success Criteria

### Required Outcomes
- [ ] docs/analysis/PR_3133_ANALYSIS.md moved successfully
- [ ] .codex/archive/deprecated/AGENTS.md moved successfully
- [ ] All references updated (100%)
- [ ] Zero broken links
- [ ] Tests passing
- [ ] Git history clean (proper renames)
- [ ] Documentation updated

### Metrics Targets
- **Success Rate:** 100% (2/2 files)
- **Reference Updates:** 100% (6-9 expected)
- **Broken Links:** 0
- **Execution Time:** <5 minutes
- **Rollbacks:** 0

---

## 🔄 Rollback Plan

If anything fails:

### Option 1: Script-Based Rollback
```bash
python scripts/root_org/rollback_move.py --operation last
```

### Option 2: Git Rollback
```bash
# Reset to before Phase 2
git reset --hard HEAD^

# Or reset specific files
git checkout HEAD -- docs/analysis/PR_3133_ANALYSIS.md
git checkout HEAD -- .codex/archive/deprecated/AGENTS.md
```

---

## 📝 Documentation Updates Required

After Phase 2 completion:

### 1. Update Root Organization Index
File: `.codex/reports/ROOT_ORG_INDEX.md`
- Update Phase 2 status to ✅
- Add file counts (62 → 60 expected)
- Update metrics

### 2. Create Phase 2 Execution Summary
File: `.codex/reports/ROOT_ORG_PHASE2_EXECUTION_SUMMARY.md`
- Document all moves
- List all reference updates
- Report validation results
- Include metrics

### 3. Update Cognitive Brain Status
File: `.codex/cognitive_brain/status/COGNITIVE_BRAIN_STATUS_ROOT_ORG_PHASE2_COMPLETE.md`
- Update phase status
- Add Phase 2 achievements
- Update health metrics
- Plan Phase 3

### 4. Update Comprehensive Plan
File: `.codex/plans/ROOT_ORG_COMPREHENSIVE_CLEANUP_PLAN.md`
- Mark Phase 2 as complete
- Update file counts
- Note any deviations from plan

---

## 🧠 Cognitive Brain Integration

### Knowledge to Capture
1. .codex/archive/deprecated/AGENTS.md reference count (actual: 6, not 293)
2. Best location for .codex/archive/deprecated/AGENTS.md (based on analysis)
3. Documentation organization patterns
4. Reference update patterns for doc files

### Patterns to Document
- Documentation files prefer `docs/` hierarchy
- Agent files prefer `.github/agents/` hierarchy
- Analysis files belong in `docs/analysis/`
- Central navigation files stay in root (README, CONTRIBUTING)

---

## ⚠️ Known Issues to Address

### Issue 1: .codex/archive/deprecated/AGENTS.md Reference Discrepancy
- **Problem:** Initial scan showed 293 refs, but actual is 6
- **Root Cause:** Likely counting agent name mentions, not file references
- **Solution:** Use more precise reference scanning
- **Action:** Re-verify before moving

### Issue 2: Documentation Link Validation
- **Problem:** Some doc links may use relative paths
- **Solution:** Update to use proper relative paths from new location
- **Action:** Test links after move

---

## 🎯 Phase 3 Preview

After Phase 2 completion, Phase 3 will address:

### Directory Consolidation
- Investigate `_codex` vs `_codex_` duplication
- Consolidate `config`, `configs`, `conf` directories
- Standardize naming conventions

### Configuration Standardization
- Unified configuration management
- Clear configuration hierarchy
- Validation tooling

**Estimated Effort:** 2-3 hours  
**Risk Level:** MEDIUM

---

## 📞 Support Resources

### Documentation
- Navigation: `.codex/reports/ROOT_ORG_INDEX.md`
- Master Plan: `.codex/plans/ROOT_ORG_COMPREHENSIVE_CLEANUP_PLAN.md`
- Phase 1 Results: `.codex/reports/ROOT_ORG_PHASE1_EXECUTION_SUMMARY.md`
- Tools: `scripts/root_org/README.md`

### Scripts
- `validate_references.py` - Reference scanning
- `organize_root_incremental.py` - File moving
- `update_links_atomic.py` - Atomic updates
- `rollback_move.py` - Recovery

### Contact
- Agent Issues: Use Root Organizer Agent
- Critical Issues: @mbaetiong
- Questions: Create GitHub issue

---

## ✅ Pre-Flight Checklist

Before starting Phase 2:
- [ ] Phase 1 verified complete
- [ ] All Phase 1 commits pushed
- [ ] Working tree clean
- [ ] Tests passing (verify)
- [ ] CI/CD green (verify)
- [ ] Reference validation tools working
- [ ] Backup created (optional)

---

## 🚀 Execution Timeline

### Estimated Duration: 30-45 minutes

**Stage 1: Analysis** (10 min)
- Validate references for both files
- Determine best location for .codex/archive/deprecated/AGENTS.md
- Review dependencies

**Stage 2: Execution** (10 min)
- Move docs/analysis/PR_3133_ANALYSIS.md
- Move .codex/archive/deprecated/AGENTS.md
- Update references

**Stage 3: Validation** (10 min)
- Check for broken links
- Run tests
- Verify git status

**Stage 4: Documentation** (10 min)
- Update index
- Create execution summary
- Update Cognitive Brain status

**Stage 5: Review** (5 min)
- Final verification
- Commit changes
- Push to remote

---

## 💡 Tips for Success

1. **Start with reference validation** - Know exactly what you're updating
2. **Use dry-run mode first** - Test without making changes
3. **One file at a time** - Don't batch both files together
4. **Verify after each move** - Catch issues early
5. **Document as you go** - Don't save documentation for the end
6. **Test thoroughly** - Don't assume references were updated correctly

---

## 🎓 Learning Objectives

From Phase 2, we should learn:
- How to handle documentation file moves
- Best practices for .codex/archive/deprecated/AGENTS.md location
- Reference count validation techniques
- Documentation link update patterns
- Integration with existing doc structure

---

**Ready to Execute:** ✅  
**Prerequisites Met:** Pending verification  
**Estimated Success:** HIGH (based on Phase 1 success)  
**Risk Level:** LOW-MEDIUM

---

**Follow-Up Prompt Version:** 1.0.0  
**Created:** 2026-02-06T03:27:26Z  
**For Use By:** Next Copilot session or Root Organizer Agent  
**Status:** Ready for Execution
