# Workflow Consolidation Audit

**Date:** 2026-01-06  
**Total Workflows:** 66  
**Status:** Analysis Complete  
**Recommendation:** Consolidate 8-12 workflows, standardize naming

## Audit Summary

### Workflow Categories

#### 1. Security & Scanning (8 workflows)
- `codeql-analysis.yml` - CodeQL static analysis
- `security-scan.yml` - Security vulnerability scanning
- `security-suite.yml` - Comprehensive security checks
- `security-alert-notification.yml` - NEW: Security alert automation ✅
- `scan-secrets-variables.yml` - Secrets detection
- `semgrep_sarif.yml` - Semgrep SARIF reports
- `dependency-scan.yml` - Dependency vulnerability checks
- `scheduled-dependency-audit.yml` - Monthly dependency audits

**Consolidation Opportunity:** `security-scan.yml`, `security-suite.yml`, and `semgrep_sarif.yml` could be merged into a single comprehensive security workflow with job matrix.

#### 2. Cache Management (3 workflows) ⚠️ CONSOLIDATE
- `cache-cleanup.yml` - Cache cleanup operations
- `cache-management.yml` - Cache management tasks
- `cache-warmup.yml` - Cache warming

**Recommendation:** Merge into single `cache-lifecycle.yml` with three jobs: cleanup, management, warmup.

#### 3. Cognitive/AI Workflows (6 workflows)
- `cognitive-action.yml` - Cognitive action processing
- `cognitive-aftermath.yml` - Post-action analysis
- `cognitive-decision.yml` - Decision making
- `cognitive-perception.yml` - Perception processing
- `copilot-cascade-review.yml` - Cascade review automation
- `copilot-self-evolution.yml` - Self-evolution processes

**Status:** Keep separate (distinct AI subsystems)

#### 4. Testing & Quality (7 workflows)
- `code-quality.yml` - Code quality checks
- `nox_gates.yml` - Nox-based quality gates
- `pr-checks.yml` - Pull request checks
- `template_lint.yml` - Template linting
- `coverage_report.yml` - Test coverage reporting
- `data_validation.yml` - Data validation tests
- `determinism.yml` - Determinism testing

**Recommendation:** Merge `code-quality.yml` and `nox_gates.yml` into comprehensive quality workflow.

#### 5. CI/CD & Deployment (9 workflows)
- `optimized-ci.yml` - Main CI pipeline
- `integration-gated.yml` - Integration testing
- `docker-build-push.yml` - Docker image builds
- `pre-release-deployment.yml` - Pre-release deployment
- `deploy-cognitive-app.yml` - Cognitive app deployment
- `post-merge-validation-optimized.yml` - Post-merge validation
- `build-chatgpt-package.yml` - ChatGPT package builds
- `zendesk-quantum-packaging.yml` - Zendesk quantum packaging
- `publish_dashboard_release.yml` - Dashboard releases

**Status:** Well-organized, minimal consolidation needed

#### 6. Documentation (4 workflows)
- `api-documentation.yml` - API docs generation
- `documentation-link-checker.yml` - Link validation (with Phase 1 caching ✅)
- `pages-mkdocs.yml` - MkDocs site generation
- `wiki-assemble.yml` - Wiki assembly

**Status:** Keep separate (different purposes)

#### 7. Monitoring & Health (6 workflows)
- `ci-health-monitor.yml` - CI health monitoring
- `runner-diagnostics.yml` - Runner diagnostics
- `self-healing-ci.yml` - Self-healing automation
- `self-healing-feedback-loop.yml` - Feedback loop processing
- `workflow-expiry-enforcer.yml` - Workflow expiry enforcement
- `status_gate.yml` - Status gate checks

**Recommendation:** Merge `self-healing-ci.yml` and `self-healing-feedback-loop.yml` into single workflow.

#### 8. Maintenance & Automation (11 workflows)
- `aftermath.yml` - Post-workflow cleanup
- `auto-update-configs.yml` - Config auto-updates
- `scheduled-archival.yml` - Archival tasks
- `repo-organization.yml` - Repository organization
- `detect-duplicates.yml` - Duplicate detection
- `draft-audit-pr.yml` - Audit PR creation
- `pr-followup-generator.yml` - PR follow-up generation
- `labeler.yml` - Issue/PR labeling
- `ratelimit_history_prune.yml` - Rate limit history pruning
- `sync-env-vars.yml` - Environment variable sync
- `workflow-restore.yml` - Workflow restoration

**Status:** Most are specialized, minimal consolidation

#### 9. Security & Compliance (6 workflows)
- `audit-improvement-pipeline.yml` - Audit improvements
- `genesis-bootstrap.yml` - Genesis setup
- `autonomous-agent.yml` - Autonomous agent operations
- `agent-runtime.yml` - Agent runtime management
- `security-tools-bootstrap.yml` - Security tools setup
- `token-rotation.yml` - Token rotation automation

**Status:** Keep separate (compliance requirements)

#### 10. Specialized Tasks (6 workflows)
- `sbom.yml` - Software Bill of Materials
- `biweekly-research-digest.yml` - Research digest generation
- `monthly-model-retraining.yml` - Model retraining
- `decode-validate-artifact.yml` - Artifact validation
- `html_visual_baseline.yml` - Visual baseline testing
- `html_visual_regression.yml` - Visual regression testing

**Recommendation:** Merge visual testing workflows into single `visual-testing.yml`.

---

## Consolidation Plan

### High Priority (Complete in next 2-4 pre-commit cycles)

#### 1. Cache Management Consolidation ⚠️ HIGH IMPACT
**Current:** 3 workflows  
**Target:** 1 workflow

**New File:** `.github/workflows/cache-lifecycle.yml`
```yaml
name: Cache Lifecycle Management

on:
  schedule:
    - cron: '0 2 * * *'  # Cleanup at 2 AM
    - cron: '0 6 * * *'  # Warmup at 6 AM
  workflow_dispatch:
    inputs:
      operation:
        type: choice
        options: [cleanup, warmup, management]

jobs:
  cache-cleanup:
    if: github.event.schedule == '0 2 * * *' || github.event.inputs.operation == 'cleanup'
    runs-on: ubuntu-latest
    steps:
      # Cache cleanup logic from cache-cleanup.yml

  cache-warmup:
    if: github.event.schedule == '0 6 * * *' || github.event.inputs.operation == 'warmup'
    runs-on: ubuntu-latest
    steps:
      # Cache warmup logic from cache-warmup.yml

  cache-management:
    if: github.event.inputs.operation == 'management'
    runs-on: ubuntu-latest
    steps:
      # Cache management logic from cache-management.yml
```

**Benefits:**
- Single place for all cache operations
- Reduced workflow count
- Easier maintenance

#### 2. Self-Healing Consolidation
**Current:** 2 workflows (`self-healing-ci.yml`, `self-healing-feedback-loop.yml`)  
**Target:** 1 workflow

**New File:** `.github/workflows/self-healing-system.yml`

**Benefits:**
- Unified self-healing logic
- Better feedback loop integration
- Reduced context switching

#### 3. Visual Testing Consolidation
**Current:** 2 workflows (`html_visual_baseline.yml`, `html_visual_regression.yml`)  
**Target:** 1 workflow

**New File:** `.github/workflows/visual-testing.yml`

**Benefits:**
- Shared setup steps
- Consistent baseline management
- Single artifact storage

### Medium Priority (Complete in 4-8 pre-commit cycles)

#### 4. Security Workflow Consolidation
**Current:** 3 workflows  
**Target:** 1 comprehensive workflow with job matrix

**Approach:** Create `security-comprehensive.yml` with:
- Job 1: CodeQL analysis
- Job 2: Dependency scanning
- Job 3: Secrets detection
- Job 4: SARIF report generation

#### 5. Code Quality Consolidation
**Current:** 2 workflows (`code-quality.yml`, `nox_gates.yml`)  
**Target:** 1 workflow

**New File:** `.github/workflows/quality-gates.yml`

---

## Naming Standardization

### Current Issues
❌ Inconsistent naming conventions:
- Some use hyphens: `cache-cleanup.yml`
- Some use underscores: `coverage_report.yml`
- Some are verbose: `post-merge-validation-optimized.yml`
- Some reference old terms: "weekly" vs "per-commit-cycle"

### Standardization Rules

1. **Use hyphens only** (no underscores)
2. **Use descriptive, action-based names**
3. **Keep under 40 characters**
4. **Use present tense verbs**
5. **Group by category prefix**

### Renaming Plan

| Current | Recommended | Category |
|---------|-------------|----------|
| `coverage_report.yml` | `coverage-report.yml` | testing |
| `data_validation.yml` | `data-validation.yml` | testing |
| `html_visual_baseline.yml` | `visual-baseline.yml` | testing |
| `html_visual_regression.yml` | `visual-regression.yml` | testing |
| `nox_gates.yml` | `quality-gates-nox.yml` | quality |
| `template_lint.yml` | `template-lint.yml` | quality |
| `ratelimit_history_prune.yml` | `ratelimit-prune.yml` | maintenance |
| `semgrep_sarif.yml` | `security-semgrep.yml` | security |

### Category Prefixes (Optional Enhancement)
For better organization, consider prefixing workflows:
- `sec-` for security workflows
- `test-` for testing workflows
- `deploy-` for deployment workflows
- `docs-` for documentation workflows
- `maint-` for maintenance workflows

**Example:**
- `security-scan.yml` → `sec-vulnerability-scan.yml`
- `documentation-link-checker.yml` → `docs-link-checker.yml`

---

## Implementation Timeline

### Phase 1 (Pre-commit cycles 1-2)
- [ ] Consolidate cache management workflows
- [ ] Consolidate self-healing workflows
- [ ] Consolidate visual testing workflows
- [ ] Rename files with underscores to hyphens
- [ ] Update all workflow references in documentation

### Phase 2 (Pre-commit cycles 3-4)
- [ ] Consolidate security workflows
- [ ] Consolidate code quality workflows
- [ ] Implement category prefixes (optional)
- [ ] Update CI/CD documentation

### Phase 3 (Pre-commit cycles 5-8)
- [ ] Review and optimize consolidated workflows
- [ ] Add comprehensive workflow documentation
- [ ] Create workflow dependency map
- [ ] Implement workflow health monitoring

---

## Metrics & Success Criteria

### Current State
- **Total Workflows:** 66
- **Estimated Duplication:** ~15-20%
- **Maintenance Burden:** High (66 files to track)

### Target State (After Consolidation)
- **Total Workflows:** 58-60 (-6 to -8 workflows)
- **Duplication:** <5%
- **Maintenance Burden:** Medium-Low

### Success Metrics
- ✅ Reduce workflow count by 10-12%
- ✅ 100% naming consistency (hyphens only)
- ✅ Zero duplicate functionality
- ✅ All workflows documented
- ✅ <10% increase in average workflow runtime

---

## Documentation Updates Required

### Files to Update After Consolidation

1. **`.codex/COMPREHENSIVE_WORKFLOW_CONSOLIDATION_PLAN.md`**
   - Update Phase status
   - Document completed consolidations
   - Add new workflow references

2. **`README.md`**
   - Update CI/CD section
   - Reference consolidated workflows
   - Update badges if needed

3. **`docs/ops/ci-cd.md`** (if exists)
   - Document new workflow structure
   - Update troubleshooting guides

4. **Workflow files themselves**
   - Add inline comments explaining consolidation
   - Reference related workflows
   - Document job dependencies

---

## Risk Assessment

### Low Risk Consolidations ✅
- Cache management workflows (independent operations)
- Visual testing workflows (similar technology stack)
- Naming standardizations (no functionality change)

### Medium Risk Consolidations ⚠️
- Self-healing workflows (complex dependencies)
- Security workflows (compliance requirements)
- Quality workflows (CI pipeline integration)

### Mitigation Strategies
1. **Gradual rollout:** One consolidation per pre-commit cycle
2. **Parallel testing:** Run both old and new workflows initially
3. **Rollback plan:** Keep old workflows disabled (not deleted) for 1 month
4. **Monitoring:** Track workflow success rates before/after
5. **Documentation:** Comprehensive migration guides

---

## Next Steps

1. **Immediate (This PR)**
   - ✅ Complete workflow audit
   - ✅ Create consolidation plan
   - ✅ Document naming standards

2. **Next PR (Pre-commit cycle 1)**
   - Consolidate cache management workflows
   - Test consolidated workflow
   - Update documentation

3. **Following PRs (Pre-commit cycles 2-8)**
   - Implement remaining consolidations
   - Standardize all naming
   - Add comprehensive documentation

---

## Appendix: Workflow Reference Table

See [WORKFLOW_INVENTORY.md](./WORKFLOW_INVENTORY.md) for complete workflow listing with descriptions, triggers, and dependencies (to be created in next phase).

---

**Audit Completed By:** GitHub Copilot  
**Audit Date:** 2026-01-06  
**Next Review:** 2026-02-06 (monthly after consolidation complete)  
**Status:** ✅ READY FOR IMPLEMENTATION
