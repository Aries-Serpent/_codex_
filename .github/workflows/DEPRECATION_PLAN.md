# Workflow Deprecation Plan

## Overview

This document tracks the deprecation of workflows that have been consolidated into suite workflows. The old workflows will be disabled gradually after validation of the new consolidated workflows.

## Deprecation Strategy

1. **Phase 1**: Create consolidated workflows (✅ COMPLETE)
2. **Phase 2**: Run both old and new workflows in parallel (1-2 phases)
3. **Phase 3**: Monitor and validate consolidated workflows
4. **Phase 4**: Disable old workflows by adding `.disabled` extension
5. **Phase 5**: Archive to `workflow-archive/` after 30 iterations

## Workflows to Deprecate

### 1. Cache Management Workflows
**Consolidated into:** `cache-suite.yml`

| Workflow | Status | Disable Date | Archive Date |
|----------|--------|--------------|--------------|
| cache-warmup.yml | ⏳ Parallel | TBD | TBD |
| cache-management.yml | ⏳ Parallel | TBD | TBD |
| cache-cleanup.yml | ⏳ Parallel | TBD | TBD |

**Validation Steps:**
- [ ] Verify cache warmup runs successfully
- [ ] Confirm cleanup operates correctly
- [ ] Validate analysis reports
- [ ] Check cache hit rates

### 2. Testing Workflows
**Consolidated into:** `test-suite.yml`

| Workflow | Status | Disable Date | Archive Date |
|----------|--------|--------------|--------------|
| test-comprehensive.yml | ⏳ Keep Active | N/A | N/A |
| test-rag.yml | ⏳ Parallel | TBD | TBD |
| auth-tests.yml | ⏳ Parallel | TBD | TBD |
| coverage_report.yml | ⏳ Parallel | TBD | TBD |
| determinism.yml | ⏳ Parallel | TBD | TBD |
| integration-gated.yml | ⏳ Parallel | TBD | TBD |

**Note:** `test-comprehensive.yml` will remain active as it's the primary PR check. The suite complements it with additional test types.

**Validation Steps:**
- [ ] Run test-suite on multiple PRs
- [ ] Verify all test types execute correctly
- [ ] Confirm coverage reporting works
- [ ] Validate parallel execution
- [ ] Check determinism testing

### 3. CI/CD Health Workflows
**Consolidated into:** `ci-health-suite.yml`

| Workflow | Status | Disable Date | Archive Date |
|----------|--------|--------------|--------------|
| ci-health-monitor.yml | ⏳ Parallel | TBD | TBD |
| ci-diagnostic-automation.yml | ⏳ Parallel | TBD | TBD |
| artifact-monitoring.yml | ⏳ Keep Active | N/A | N/A |
| repository-health-monitoring.yml | ⏳ Parallel | TBD | TBD |
| runner-diagnostics.yml | ⏳ Parallel | TBD | TBD |
| batch-ci-triage.yml | ⏳ Keep Active | N/A | N/A |

**Note:** `artifact-monitoring.yml` has specialized agent integration and will remain active. `batch-ci-triage.yml` includes self-healing features not yet consolidated.

**Validation Steps:**
- [ ] Verify health monitoring runs on schedule
- [ ] Confirm issue creation works
- [ ] Validate artifact checks
- [ ] Test runner diagnostics
- [ ] Check automated diagnostics

## Self-Healing Workflows (Future Consolidation)

These workflows will be consolidated in a future phase:

| Workflow | Target Suite | Timeline |
|----------|--------------|----------|
| self-healing.yml | ci-self-healing-suite.yml | Phase 4 |
| self-healing-ci.yml | ci-self-healing-suite.yml | Phase 4 |
| self-healing-feedback-loop.yml | ci-self-healing-suite.yml | Phase 4 |

## Security Workflows (Future Consolidation)

These workflows will be consolidated in a future phase:

| Workflow | Target Suite | Timeline |
|----------|--------------|----------|
| codeql-analysis.yml | security-scanning-suite.yml | Phase 5 |
| codeql-chunked.yml | security-scanning-suite.yml | Phase 5 |
| security-scan.yml | security-scanning-suite.yml | Phase 5 |
| security-suite.yml | security-scanning-suite.yml | Phase 5 |
| semgrep_sarif.yml | security-scanning-suite.yml | Phase 5 |
| dependency-scan.yml | security-scanning-suite.yml | Phase 5 |
| auth-security-audit.yml | auth-security-suite.yml | Phase 5 |
| auth-secret-rotation.yml | secrets-management-suite.yml | Phase 5 |
| auth-token-rotation.yml | secrets-management-suite.yml | Phase 5 |
| auth-compliance-report.yml | auth-security-suite.yml | Phase 5 |
| scan-secrets-variables.yml | secrets-management-suite.yml | Phase 5 |
| validate-secrets-documentation.yml | secrets-management-suite.yml | Phase 5 |

## Documentation Workflows (Future Consolidation)

These workflows will be consolidated in a future phase:

| Workflow | Target Suite | Timeline |
|----------|--------------|----------|
| pages-mkdocs.yml | docs-build-deploy.yml | Phase 6 |
| api-documentation.yml | docs-build-deploy.yml | Phase 6 |
| wiki-assemble.yml | docs-build-deploy.yml | Phase 6 |
| documentation-link-checker.yml | docs-quality-suite.yml | Phase 6 |

## Monitoring During Parallel Phase

### Metrics to Track
1. **Execution Time**: Compare suite vs individual workflows
2. **Success Rate**: Ensure consolidated workflows are reliable
3. **Cache Hit Rate**: Verify cache optimization is effective
4. **Cost**: Monitor compute minutes usage
5. **Coverage**: Ensure no functionality is lost

### Monitoring Tools
- GitHub Actions Usage API
- workflow-analytics workflows
- ci-health-suite monitoring
- Manual review of workflow runs

### Decision Criteria for Deprecation
A workflow can be deprecated when:
- ✅ Consolidated workflow runs successfully for 2 phases
- ✅ All features are verified working
- ✅ Success rate ≥ old workflow success rate
- ✅ No issues reported by users or agents
- ✅ Cache performance is equal or better

## Rollback Plan

If issues are discovered with consolidated workflows:

1. **Immediate**: Re-enable individual workflows by removing `.disabled`
2. **Investigation**: Review logs and identify root cause
3. **Fix**: Update consolidated workflow
4. **Validation**: Test fix in isolation
5. **Retry**: Resume parallel phase with fixed workflow

## Communication

### Stakeholders
- @mbaetiong (Owner)
- AI Agents using workflows
- CI/CD monitoring systems

### Notifications
- Create tracking issue for deprecation phase
- Update CONSOLIDATION_GUIDE.md with progress
- Post in discussions when workflows are disabled
- Update agent documentation

## Archive Process

When a workflow is ready for archival:

1. Rename workflow file: `workflow.yml` → `workflow.yml.disabled`
2. Move to archive: `.github/workflows/` → `.github/workflow-archive/deprecated/`
3. Update documentation references
4. Create redirect in CONSOLIDATION_GUIDE.md
5. Tag commit with deprecation note

## Timeline

| Phase | Start Date | End Date | Status |
|-------|------------|----------|--------|
| Phase 1: Create Suites | 2026-01-26 | 2026-01-26 | ✅ Complete |
| Phase 2: Parallel Run | 2026-01-27 | 2026-02-10 | ⏳ Starting |
| Phase 3: Validation | 2026-02-03 | 2026-02-10 | ⏳ Pending |
| Phase 4: Deprecation | 2026-02-10 | 2026-02-17 | ⏳ Pending |
| Phase 5: Archive | 2026-03-10 | 2026-03-17 | ⏳ Pending |

## Success Metrics

**Target Goals:**
- 🎯 Zero functionality loss
- 🎯 ≥95% success rate maintained
- 🎯 30-50% faster execution time
- 🎯 20-30% cost reduction
- 🎯 100% AI agent compatibility

## Notes

- Individual workflows remain in parallel until validation complete
- Critical workflows (like test-comprehensive.yml) may never be deprecated
- New consolidated workflows prioritize flexibility and agent integration
- All decisions documented and reversible

---

**Last Updated**: 2026-01-26
**Status**: Phase 1 Complete, Phase 2 Starting
**Owner**: @mbaetiong
