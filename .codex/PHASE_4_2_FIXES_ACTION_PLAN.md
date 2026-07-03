# PHASE 4.2 DOCUMENTATION FIXES - DETAILED ACTION PLAN

## Quick Stats
- **Total Files to Fix**: 48
- **Total Broken Links**: 123
- **Priority P1 Files**: 15
- **Estimated Total Time**: 15-20 hours
- **Recommended Timeline**: 1-2 weeks

---

## FILES REQUIRING IMMEDIATE ATTENTION (P1)

These files have critical issues affecting documentation navigation.


### 1. ARCHITECTURE_DIAGRAMS_INDEX.md
**Path**: `docs/ARCHITECTURE_DIAGRAMS_INDEX.md`
**Broken Links**: 18
**Priority**: P1 (Multiple broken references)

**Links to Fix**:
- [ ] `CODEBASE_MERMAID_MAPS.md#ci-cd-pipeline` (referenced as: docs/CODEBASE_MERMAID_MAPS.md...)
- [ ] `CODEBASE_MERMAID_MAPS.md#pr-lifecycle` (referenced as: docs/CODEBASE_MERMAID_MAPS.md...)
- [ ] `CODEBASE_MERMAID_MAPS.md#agent-interaction` (referenced as: docs/CODEBASE_MERMAID_MAPS.md...)
- [ ] `CODEBASE_MERMAID_MAPS.md#cognitive-brain` (referenced as: docs/CODEBASE_MERMAID_MAPS.md...)
- [ ] `CODEBASE_MERMAID_MAPS.md#self-healing` (referenced as: docs/CODEBASE_MERMAID_MAPS.md...)
- ... and 13 more

**Actions**:
1. Verify all broken link targets exist
2. Update relative paths if files have moved
3. Fix anchor references (#section-names)
4. Test links before committing

**Estimated Time**: 30-45 minutes

---

### 2. BROKEN_LINKS_REPORT.md
**Path**: `docs/quality/BROKEN_LINKS_REPORT.md`
**Broken Links**: 15
**Priority**: P1 (Multiple broken references)

**Links to Fix**:
- [ ] `[^"\']+` (referenced as: "\'...)
- [ ] `state["inputs"]` (referenced as: GitHub\`
  - Status: not_found: /home/ru...)
- [ ] `outputs, state["targets"]` (referenced as: "criterion"...)
- [ ] `[^"\']+` (referenced as: "\'...)
- [ ] `state["inputs"]` (referenced as: GitHub\`
  - Status: not_found: /home/ru...)
- ... and 10 more

**Actions**:
1. Verify all broken link targets exist
2. Update relative paths if files have moved
3. Fix anchor references (#section-names)
4. Test links before committing

**Estimated Time**: 30-45 minutes

---

### 3. copilot-directives-to-implementation-plan.md
**Path**: `docs/plans/copilot-directives-to-implementation-plan.md`
**Broken Links**: 9
**Priority**: P1 (Multiple broken references)

**Links to Fix**:
- [ ] `.+?` (referenced as: "\'...)
- [ ] `[^"\']+` (referenced as: "\'...)
- [ ] `[^"\']+` (referenced as: "\'...)
- [ ] `[^"\']+` (referenced as: "\'...)
- [ ] `[^"\']+` (referenced as: "\'...)
- ... and 4 more

**Actions**:
1. Verify all broken link targets exist
2. Update relative paths if files have moved
3. Fix anchor references (#section-names)
4. Test links before committing

**Estimated Time**: 30-45 minutes

---

### 4. PHASE_6_CONSISTENCY_CHECKS_REPORT.md
**Path**: `docs/PHASE_6_CONSISTENCY_CHECKS_REPORT.md`
**Broken Links**: 4
**Priority**: P1 (Multiple broken references)

**Links to Fix**:
- [ ] `docs/file.md` (referenced as: docs...)
- [ ] `/docs/file.md` (referenced as: docs...)
- [ ] `docs/nonexistent.md` (referenced as: missing...)
- [ ] `file.md#missing` (referenced as: bad-anchor...)

**Actions**:
1. Verify all broken link targets exist
2. Update relative paths if files have moved
3. Fix anchor references (#section-names)
4. Test links before committing

**Estimated Time**: 30-45 minutes

---

### 5. LEARNING_PATHS.md
**Path**: `docs/LEARNING_PATHS.md`
**Broken Links**: 4
**Priority**: P1 (Multiple broken references)

**Links to Fix**:
- [ ] `./configuration/hydra_quickstart.md#sweeps` (referenced as: Hyperparameter Tuning...)
- [ ] `./CI.md` (referenced as: CI/CD Pipelines...)
- [ ] `./cognitive_brain/INDEX.md#memory` (referenced as: Memory Systems...)
- [ ] `./agent/OPERATIONAL_GUIDELINES.md#orchestration` (referenced as: Agent Orchestration...)

**Actions**:
1. Verify all broken link targets exist
2. Update relative paths if files have moved
3. Fix anchor references (#section-names)
4. Test links before committing

**Estimated Time**: 30-45 minutes

---

### 6. LINK_VALIDATION_FIX_SUMMARY.md
**Path**: `docs/analysis/LINK_VALIDATION_FIX_SUMMARY.md`
**Broken Links**: 4
**Priority**: P1 (Multiple broken references)

**Links to Fix**:
- [ ] `[^"\']+` (referenced as: "\'...)
- [ ] `state["inputs"]` (referenced as: "model"...)
- [ ] `blob:https://chatgpt.com/...` (referenced as: !\[GitHub\...)
- [ ] `items: list[T]` (referenced as: T...)

**Actions**:
1. Verify all broken link targets exist
2. Update relative paths if files have moved
3. Fix anchor references (#section-names)
4. Test links before committing

**Estimated Time**: 30-45 minutes

---

### 7. survey-0D_base_-and-1926-2025-10-30.md
**Path**: `docs/status_updates/survey-0D_base_-and-1926-2025-10-30.md`
**Broken Links**: 4
**Priority**: P1 (Multiple broken references)

**Links to Fix**:
- [ ] `../README_ROOT.md#training-quickstart` (referenced as: `README_ROOT.md`...)
- [ ] `./guides/reasoning_overview.md#evaluation-readiness` (referenced as: `guides/reasoning_overview.md`...)
- [ ] `./CONTRIBUTING.md#using-operational-templates` (referenced as: `docs/CONTRIBUTING.md`...)
- [ ] `./CONTRIBUTING.md#using-operational-templates` (referenced as: `docs/CONTRIBUTING.md`...)

**Actions**:
1. Verify all broken link targets exist
2. Update relative paths if files have moved
3. Fix anchor references (#section-names)
4. Test links before committing

**Estimated Time**: 30-45 minutes

---

### 8. INDEX.md
**Path**: `docs/tokens/INDEX.md`
**Broken Links**: 4
**Priority**: P1 (Multiple broken references)

**Links to Fix**:
- [ ] `CI_CD_TROUBLESHOOTING.md#diagnosing-403-errors` (referenced as: CI/CD Troubleshooting...)
- [ ] `TOKEN_REGENERATION_GUIDE.md#zero-downtime-rotation` (referenced as: Token Regeneration Guide...)
- [ ] `TOKEN_USAGE_AUDIT.md#generating-audit-reports` (referenced as: Token Usage Audit...)
- [ ] `TOKEN_HIERARCHY_GUIDE.md#scope-hierarchy` (referenced as: Token Hierarchy Guide...)

**Actions**:
1. Verify all broken link targets exist
2. Update relative paths if files have moved
3. Fix anchor references (#section-names)
4. Test links before committing

**Estimated Time**: 30-45 minutes

---

### 9. LINK_VALIDATION_REPORT.md
**Path**: `docs/maintenance/LINK_VALIDATION_REPORT.md`
**Broken Links**: 4
**Priority**: P1 (Multiple broken references)

**Links to Fix**:
- [ ] `[^"\']+` (referenced as: "\'...)
- [ ] `[^"\']+` (referenced as: "\'...)
- [ ] `state["inputs"]` (referenced as: GitHub\` → No suggestion
- `!\[GitHub\` ...)
- [ ] `outputs, state["targets"]` (referenced as: "criterion"...)

**Actions**:
1. Verify all broken link targets exist
2. Update relative paths if files have moved
3. Fix anchor references (#section-names)
4. Test links before committing

**Estimated Time**: 30-45 minutes

---

### 10. questions_for_research.md
**Path**: `docs/tech_debt/research_queue/questions_for_research.md`
**Broken Links**: 4
**Priority**: P1 (Multiple broken references)

**Links to Fix**:
- [ ] `../../../src/codex_init.py#L15` (referenced as: src/codex_init.py:15...)
- [ ] `../../../tools/validate.py#L25` (referenced as: tools/validate.py:25...)
- [ ] `../../../src/codex_ml/training/unified_training.py#L42` (referenced as: src/codex_ml/training/unified_training.p...)
- [ ] `../../../src/codex_ml/training/unified_training.py#L43` (referenced as: src/codex_ml/training/unified_training.p...)

**Actions**:
1. Verify all broken link targets exist
2. Update relative paths if files have moved
3. Fix anchor references (#section-names)
4. Test links before committing

**Estimated Time**: 30-45 minutes

---

### 11. GITHUB_AGENT_PR_REVIEWER_IMPLEMENTATION.md
**Path**: `docs/GITHUB_AGENT_PR_REVIEWER_IMPLEMENTATION.md`
**Broken Links**: 3
**Priority**: P1 (Multiple broken references)

**Links to Fix**:
- [ ] `[^"\']+` (referenced as: "\'...)
- [ ] `[^"\']+` (referenced as: "\'...)
- [ ] `[^"\']+` (referenced as: "\'...)

**Actions**:
1. Verify all broken link targets exist
2. Update relative paths if files have moved
3. Fix anchor references (#section-names)
4. Test links before committing

**Estimated Time**: 30-45 minutes

---

### 12. index.md
**Path**: `docs/index.md`
**Broken Links**: 3
**Priority**: P1 (Multiple broken references)

**Links to Fix**:
- [ ] `guides/quickstart.md` (referenced as: Getting Started...)
- [ ] `README_ROOT.md#training-quickstart` (referenced as: `README_ROOT.md`...)
- [ ] `../CONTRIBUTING.md#using-operational-templates` (referenced as: CONTRIBUTING...)

**Actions**:
1. Verify all broken link targets exist
2. Update relative paths if files have moved
3. Fix anchor references (#section-names)
4. Test links before committing

**Estimated Time**: 30-45 minutes

---

### 13. WORKFLOW_LINK_VALIDATION_FINAL_REPORT.md
**Path**: `docs/analysis/WORKFLOW_LINK_VALIDATION_FINAL_REPORT.md`
**Broken Links**: 3
**Priority**: P1 (Multiple broken references)

**Links to Fix**:
- [ ] `[^"\']+` (referenced as: "\'...)
- [ ] `state["inputs"]` (referenced as: "model"...)
- [ ] `items: list[T]` (referenced as: T...)

**Actions**:
1. Verify all broken link targets exist
2. Update relative paths if files have moved
3. Fix anchor references (#section-names)
4. Test links before committing

**Estimated Time**: 30-45 minutes

---

### 14. README.md
**Path**: `docs/plans/README.md`
**Broken Links**: 3
**Priority**: P1 (Multiple broken references)

**Links to Fix**:
- [ ] `./plans/PLAN_TITLE.md` (referenced as: Plan Name...)
- [ ] `./docs/plans/PLAN_TITLE.md` (referenced as: Plan Name...)
- [ ] `./plans/archive/PLAN_TITLE.md` (referenced as: Plan Name...)

**Actions**:
1. Verify all broken link targets exist
2. Update relative paths if files have moved
3. Fix anchor references (#section-names)
4. Test links before committing

**Estimated Time**: 30-45 minutes

---

### 15. CONSISTENCY_CHECKS_SETUP.md
**Path**: `docs/CONSISTENCY_CHECKS_SETUP.md`
**Broken Links**: 2
**Priority**: P1 (Multiple broken references)

**Links to Fix**:
- [ ] `docs/file.md` (referenced as: text...)
- [ ] `docs/file.md#anchor` (referenced as: text...)

**Actions**:
1. Verify all broken link targets exist
2. Update relative paths if files have moved
3. Fix anchor references (#section-names)
4. Test links before committing

**Estimated Time**: 30-45 minutes

---


## VERSION UPDATE REQUIRED

**Current Version**: 0.1.0
**References to Update**:
- v1.0.0 (21 mentions) - CRITICAL
- v7.0.0 (4 mentions)
- Other versions (various mentions)

**Files Affected**: 53 files across documentation

**Action Plan**:

1. **Batch Find & Replace**:
   ```bash
   # Find all v1.0.0 references
   grep -r "v1\.0\.0" docs/
   
   # Replace with current version
   find docs -name "*.md" -exec sed -i 's/v1\.0\.0/v0.1.0/g' {} \;
   ```

2. **Manual Review**:
   - Check each file for version context
   - Ensure replacements make sense
   - Look for version-specific API documentation

3. **Testing**:
   - Rebuild documentation (mkdocs build)
   - Check for any broken references
   - Verify links still work

**Estimated Time**: 1-2 hours

---

## CONFIGURATION EXAMPLE UPDATES

Based on documentation analysis, the following configuration examples need review:

### Hydra/OmegaConf Examples
- **Files**: hydra_quickstart.md, HYDRA_GUIDE.md, etc.
- **Issue**: May reference deprecated config patterns
- **Action**: Update config examples to current schema
- **Time**: 1 hour

### Import Statement Updates
- **Issue**: Import paths may reference old package structure
- **Action**: Verify current import paths match documentation
- **Time**: 1 hour

### API Signature Verification
- **Issue**: Function examples may use outdated signatures
- **Action**: Cross-reference with actual codebase
- **Time**: 2 hours

---

## LINK VALIDATION AUTOMATION

### Setup CI/CD Link Checking

Add to your GitHub Actions:

```yaml
- name: Validate Documentation Links
  uses: gaurav-nelson/github-action-markdown-link-check@v1
  with:
    use-quiet-mode: 'yes'
    use-verbose-mode: 'yes'
```

**Time to Implement**: 30 minutes

---

## PRIORITY CHECKLIST

Use this checklist to track progress:

### Phase 1: Critical Fixes (24 hours)
- [ ] Fix ARCHITECTURE_DIAGRAMS_INDEX.md (18 links)
- [ ] Fix PHASE_6_CONSISTENCY_CHECKS_REPORT.md (4 links)
- [ ] Fix API_REFERENCE.md (1 link)
- [ ] Test all fixes

### Phase 2: Version Updates (2-3 hours)
- [ ] Update v1.0.0 → v0.1.0 (21 files)
- [ ] Update other version references (26 files)
- [ ] Verify documentation builds correctly

### Phase 3: Code Example Review (4-6 hours)
- [ ] Audit Hydra/OmegaConf examples
- [ ] Verify import statements
- [ ] Test code examples if possible
- [ ] Update outdated APIs

### Phase 4: Automation (1-2 hours)
- [ ] Setup CI/CD link validation
- [ ] Add version sync automation
- [ ] Add pre-commit checks

---

## QUICK FIX GUIDE

### How to Fix Broken Markdown Links

**Pattern 1: Relative Path Issues**
```
❌ BROKEN: [Link](./docs/file.md)
✅ FIXED: [Link](file.md)

❌ BROKEN: [Link](../docs/QUICKSTART.md)
✅ FIXED: [Link](../../QUICKSTART.md)
```

**Pattern 2: Anchor References**
```
❌ BROKEN: [Link](file.md#old-section-name)
✅ FIXED: [Link](file.md#new-section-name)

Ensure # matches actual heading in target file
```

**Pattern 3: Missing Files**
```
❌ BROKEN: [Link](guides/QUICKSTART.md) - file doesn't exist
✅ FIXED: [Link](QUICKSTART.md) - use actual location

Or create the file if it was recently renamed/moved
```

### How to Fix Version References

**Pattern 1: Simple Replace**
```bash
sed -i 's/v1\.0\.0/v0.1.0/g' docs/FILE.md
```

**Pattern 2: Context-Aware Replace**
- Check if version is in changelog (keep as historical)
- Check if version is in example code (update)
- Check if version is in current feature description (update)

**Pattern 3: Batch Operation**
```bash
# Find all files with old version
grep -r "v1\.0\.0" docs/ | cut -d: -f1 | sort -u

# For each file, manually verify and update
```

---

## EXTERNAL LINKS STATUS

**Good News**: All major external domains are active
- ✅ github.com (1028 references) - Active
- ✅ docs.github.com (148 references) - Active
- ✅ pypi.org (34 references) - Active
- ✅ pytorch.org (24 references) - Active

**No deprecated URLs detected**

**Recommendation**: Implement automated external link validation quarterly

---

## ESTIMATED TIMELINE

| Phase | Tasks | Time | Priority |
|-------|-------|------|----------|
| **Phase 1** | Fix critical broken links | 3-4 hours | P0 |
| **Phase 2** | Update version references | 1-2 hours | P1 |
| **Phase 3** | Review code examples | 4-6 hours | P1 |
| **Phase 4** | Implement automation | 1-2 hours | P2 |
| **Phase 5** | Final validation | 1 hour | P0 |
| **Total** | Complete remediation | 10-15 hours | - |

---

## SUCCESS CRITERIA

- [x] All 48 broken links fixed
- [ ] All version references updated
- [ ] All code examples validated
- [ ] CI/CD link validation enabled
- [ ] Documentation builds without warnings
- [ ] All external links verified working

---

## NEXT PHASE: AUTOMATION

After manual fixes are complete, implement:

1. **Automated Link Validation** - CI/CD check
2. **Version Sync** - Auto-update from pyproject.toml
3. **Code Example Testing** - Run examples as tests
4. **Documentation Freshness** - Monitor and alert on stale docs

---

**Prepared By**: PHASE 4.2 Documentation Audit Agent
**Date**: 2026-07-03
**Status**: Action Plan Ready for Execution
