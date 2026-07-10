# Workflow Cleanup Implementation Checklist

## Phase 1: Critical Workflow Fixes (DO FIRST ✅)

### Must Complete Before Any Other Changes

- [ ] **copilot-setup-steps.yml**
  - [ ] Update trigger paths for pyproject.toml
  - [ ] Test trigger on .codex/ changes
  - [ ] Test trigger on pyproject.toml changes
  - [ ] Verify setup execution
  - Estimated time: 15 minutes

- [ ] **required-actions-enforcer.yml**
  - [ ] Verify trigger configuration
  - [ ] Test enforcement logic
  - [ ] Confirm workflow runs on trigger
  - Estimated time: 10 minutes

- [ ] **resilient_validation.yml**
  - [ ] Update trigger paths for tests/ and .codex/
  - [ ] Verify artifact upload paths
  - [ ] Test on test file changes
  - [ ] Verify coverage.json artifacts
  - Estimated time: 15 minutes

- [ ] **test-rag.yml**
  - [ ] Update trigger paths for pyproject.toml
  - [ ] Update trigger paths for tests/
  - [ ] Verify environment setup
  - [ ] Test RAG validation workflow
  - Estimated time: 15 minutes

**Subtotal Phase 1**: 55 minutes

---

## Phase 2: Configuration File Reference Updates

### By Priority (Complete in order)

#### Priority 1: Trigger Path Filters (87 workflows)
- [ ] Batch update all trigger paths using search-replace
- [ ] Test 5 workflows manually as samples
- [ ] Verify triggers work correctly
- Estimated time: 2-3 hours

#### Priority 2: Cache Dependencies (41 workflows)
- [ ] Update cache-dependency-path references
- [ ] Update pyproject.toml references in run commands
- [ ] Test cache invalidation works
- Estimated time: 1-2 hours

#### Priority 3: Artifact Paths (68 workflows)
- [ ] Verify upload paths are correct
- [ ] Update download paths if needed
- [ ] Test artifact uploads in 3-5 workflows
- Estimated time: 1-2 hours

#### Priority 4: Dependency Installation (35 workflows)
- [ ] Update requirements file references
- [ ] Update pip install commands
- [ ] Test dependency installation
- Estimated time: 1 hour

**Subtotal Phase 2**: 5-8 hours

---

## Phase 3: Testing & Validation

- [ ] Run full workflow test suite
- [ ] Verify all 207 workflows parse correctly
- [ ] Check trigger conditions work
- [ ] Validate artifact upload/download
- [ ] Monitor first 20 runs after deployment
- [ ] Address any issues found
- Estimated time: 2-3 hours

---

## Phase 4: Documentation

- [ ] Update CONTRIBUTING.md with new structure
- [ ] Document any special migration steps
- [ ] Create migration guide for contributors
- [ ] Update internal wiki/docs
- Estimated time: 1 hour

---

## Grand Total Effort Estimate

| Phase | Time | Cumulative |
|-------|------|-----------|
| Phase 1: Critical Fixes | 55 min | 55 min |
| Phase 2: Reference Updates | 5-8 hr | 6-9 hr |
| Phase 3: Testing | 2-3 hr | 8-12 hr |
| Phase 4: Documentation | 1 hr | 9-13 hr |

**Total Estimated Effort: 9-13 hours**

---

## Success Criteria

- [ ] All 4 critical workflows fixed and tested
- [ ] All 129 high-risk workflows updated
- [ ] Zero broken trigger filters
- [ ] All workflows passing in CI
- [ ] No artifact upload/download failures
- [ ] Documentation updated
- [ ] Team briefed on new structure

---

## Risk Mitigation

- [ ] Create feature branch for all changes
- [ ] Test on non-main branch first
- [ ] Use workflow_dispatch for manual testing
- [ ] Have rollback plan ready
- [ ] Monitor closely for 48 hours after merge
- [ ] Keep git history for quick reference

---

## Rollback Plan

If issues occur:
1. Revert all workflow changes with single commit
2. Revert all file movements with single commit
3. Keep old structure for 1-2 weeks as fallback
4. Post-mortem on failures

---

## Sign-Offs Needed

- [ ] Engineering lead approval
- [ ] DevOps/CI team approval
- [ ] Team notification completed
- [ ] Documentation reviewed
