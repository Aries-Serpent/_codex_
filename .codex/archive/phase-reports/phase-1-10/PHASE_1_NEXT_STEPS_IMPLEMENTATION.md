# Phase 1 Next Steps — Implementation Guide (S1263+)

**Status**: ✅ Phase 1 Infrastructure Complete & Code Review Issues Fixed
**Current Session**: S1262 (Code fixes completed)
**Next Session**: S1263+ (Implementation & deployment)

---

## 🎯 Priority 1: Node.js Runtime Baseline Sustainment

**Status**: ✅ Node.js 20 migration completed; baseline is Node.js 22+

Node.js 20 references have been migrated from active runtime paths. Keep Node.js 22+ enforced across workflows, templates, and docs.

### Action Items (Complete in S1263)

1. **Audit Node.js Usage**
   ```bash
   # Verify no Node.js 20 references remain in active workflows
   grep -r "node-version.*20\|NODE.*VERSION.*20" .github/workflows/ || true
   grep -r "node.*20" package.json apps/*/package.json cognitive_app/*/package.json

   # Check current engines spec
   cat package.json | grep -A 2 '"engines"'
   ```

2. **Update `package.json` engines field**
   ```json
   "engines": {
     "node": ">=22.0.0",
     "npm": ">=10.0.0"
   }
   ```

3. **Create Tracking Issue**
   - Title: `[Maintenance] Node.js baseline sustainment (22+)`
   - Labels: `critical`, `deadline`, `nodejs-migration`
   - Milestone: Assign to Phase 1 Completion
   - Body: Link to this document, list affected workflows, coordinate with team

4. **Test Node.js 22 Compatibility**
   ```bash
   # Install Node.js 22
   nvm install 22
   nvm use 22

   # Run all npm-based tests
   npm ci
   npm run test  # Cognitive app tests
   npm run build # Frontend build
   ```

5. **Update Workflows (Gradual Rollout)**
   - First: Critical build pipelines (cognitive_app, docker-build-push)
   - Second: Test workflows (ci-checkpoint-validation, test-rag)
   - Third: All remaining workflows

---

## 🎯 Priority 2: Deploy 9 Repository Variables

**Status**: 📝 Ready for GitHub UI configuration

### Action Items (Complete in S1263)

1. **Create Variables in GitHub UI**

   Navigate to: Repository Settings → Secrets and Variables → Actions

   **CRITICAL Variables** (Set immediately):
   ```
   NODE_JS_VERSION = "22"
   CODEX_CACHE_VERSION = "v3"
   CODEX_COVERAGE_THRESHOLD = "80"
   COGNITIVE_BRAIN_INJECTION_ENABLED = "true"
   SESSION_CONTEXT_AUTO_CAPTURE = "true"
   ```

   **HIGH PRIORITY Variables** (Set this week):
   ```
   CODEX_TEST_TIMEOUT_MINUTES = "60"
   CODEX_SHARD_COUNT = "4"
   CODEX_LOG_LEVEL = "INFO"
   CODEX_MAX_HEALER_RUNS_PER_HOUR = "5"
   ```

2. **Verify Variables Are Set**
   ```bash
   # Option 1: Check via GitHub UI (Settings → Secrets and Variables)
   # Option 2: Run validation script
   python scripts/ci/validate_repo_variables.py
   ```

   Expected output:
   ```
   ✅ NODE_JS_VERSION = "22" (valid)
   ✅ CODEX_CACHE_VERSION = "v3" (valid)
   ✅ CODEX_COVERAGE_THRESHOLD = "80" (valid: 0-100)
   ✅ ... (all 9 variables)
   ```

---

## 🎯 Priority 3: Trigger Variable Validation Workflow

**Status**: 🔄 Ready to run

### Action Items (Complete in S1263)

1. **Manually Trigger Variable Sync Workflow**
   ```bash
   # GitHub CLI approach
   gh workflow run repo-var-sync-schedule.yml --ref main

   # OR visit GitHub Actions UI and manually trigger the workflow
   ```

2. **Monitor Workflow Execution**
   - Watch `.github/workflows/repo-var-sync-schedule.yml` execution
   - Verify all variables pass validation (see validation script output)
   - Confirm `.codex/agent_context.json` is auto-generated with current values
   - Check GitHub Actions logs for validation results

3. **Expected Artifacts**
   - `.codex/agent_context.json` updated with current variable values
   - Validation report in workflow logs
   - Auto-generated variable usage documentation

---

## 🎯 Priority 4: Test Pending Workflows

**Status**: ✅ All workflows prepared in PR #4547

### Action Items (Complete in S1263)

1. **Test Session Context Capture**
   ```bash
   # Manually trigger workflow
   gh workflow run session-context-capture.yml --ref main

   # Verify
   # - Captures PR state, commits, tasks, blocking issues, test results
   # - Generates JSON + Markdown outputs
   # - Reduces handoff loss from 20% to <5%
   ```

2. **Test Self-Healing Workflow**
   ```bash
   # Trigger self-healing workflow
   gh workflow run self-healing.yml --ref main

   # Verify
   # - Delegates to copilot-iterative-self-healing.yml
   # - Uses CODEX_MAX_HEALER_RUNS_PER_HOUR variable
   # - Rates limit self-healing executions
   ```

3. **Test Cache Optimization Workflows**
   ```bash
   # Test high-impact workflows with cache enabled
   gh workflow run test-rag.yml --ref main
   gh workflow run auth-tests.yml --ref main
   gh workflow run ci-checkpoint-validation.yml --ref main

   # Verify
   # - Uses CODEX_CACHE_VERSION variable
   # - Hit rates improve on second run
   # - No cache invalidation errors
   ```

4. **Monitor Test Results**
   - All 3 workflows should execute successfully
   - Check cache hit/miss rates in logs
   - Verify no timeout errors
   - Confirm session context is captured

---

## 🎯 Priority 5: Roll Out Cache Optimization to 28+ Workflows

**Status**: 📋 28 workflows identified, optimization tool ready

### Action Items (Complete in S1263+)

1. **Analyze Cache Optimization Opportunities**
   ```bash
   # Identify all analyzable workflows
   python scripts/ci/optimize_ci_cache.py --analyze-all

   # Expected: 62 total workflows, 28 suitable for optimization
   # Output: JSON report with cache tier recommendations
   ```

2. **Apply Cache to High-Impact Workflows** (Week 1)

   Priority tier 1 (highest impact):
   - `.github/workflows/docker-build-push.yml`
   - `.github/workflows/coverage-with-timeout.yml`
   - `.github/workflows/nox_gates.yml`

   For each workflow:
   ```bash
   # Apply cache optimization
   python scripts/ci/optimize_ci_cache.py --fix .github/workflows/docker-build-push.yml

   # Review changes
   git diff .github/workflows/docker-build-push.yml

   # Commit and test
   git add .github/workflows/docker-build-push.yml
   git commit -m "ci: add 4-layer cache hierarchy to docker-build-push.yml"
   ```

3. **Verify Cache Performance** (Week 1)

   For each optimized workflow:
   - [ ] First run: establish baseline (no cache)
   - [ ] Second run: verify cache hits
   - [ ] Measure time savings (target: 15% reduction per workflow)
   - [ ] Monitor cache size and validity

4. **Gradual Rollout** (Weeks 2-4)

   Apply cache to remaining 25+ workflows:
   - All pip-based Python workflows
   - All npm-based Node.js workflows
   - All PyTorch-dependent workflows
   - Test/coverage/CI gate workflows

5. **Documentation & Runbooks**
   - Update `.codex/CI_CACHE_OPTIMIZATION.md` with actual results
   - Document cache tier strategy
   - Create troubleshooting guide for cache misses
   - Add performance baseline tracking

---

## 📊 Success Criteria for Phase 1 Completion

### By End of S1263
- [x] Node.js 20 → 22 migration completed in active runtime paths
- [ ] All 9 repository variables created in GitHub UI
- [ ] Variable validation workflow passes
- [ ] 3 pending workflows tested successfully with variables
- [ ] Cache optimization applied to 3 high-impact workflows

### By End of S1264
- [x] Node.js 22 migration 100% complete (active workflows)
- [ ] Cache optimization applied to 15+ workflows
- [ ] Performance baseline established (time savings tracked)
- [ ] Session context capture validated in production
- [ ] Self-healing workflow operational

### Ongoing Sustainment (Post-migration)
- [x] Node.js 20 → 22 migration 100% complete
- [x] All active workflows using Node.js 22+
- [x] package.json engines field updated
- [ ] Cache optimization applied to 28+ workflows
- [ ] Phase 1 infrastructure fully operational

---

## 📝 Variables Quick Reference

| Variable | Category | Type | Default | Required |
|----------|----------|------|---------|----------|
| `NODE_JS_VERSION` | Runtime | String | `22` | Yes |
| `CODEX_CACHE_VERSION` | Cache | String | `v3` | Yes |
| `CODEX_COVERAGE_THRESHOLD` | Testing | Int (0-100) | `80` | Yes |
| `COGNITIVE_BRAIN_INJECTION_ENABLED` | Cognitive | Bool | `true` | Yes |
| `SESSION_CONTEXT_AUTO_CAPTURE` | Cognitive | Bool | `true` | Yes |
| `CODEX_TEST_TIMEOUT_MINUTES` | Testing | Int | `60` | No |
| `CODEX_SHARD_COUNT` | Testing | Int | `4` | No |
| `CODEX_LOG_LEVEL` | Logging | String | `INFO` | No |
| `CODEX_MAX_HEALER_RUNS_PER_HOUR` | Reliability | Int | `5` | No |

### Usage Example in Workflow:
```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    env:
      NODE_VERSION: ${{ vars.NODE_JS_VERSION || '22' }}
      CACHE_VERSION: ${{ vars.CODEX_CACHE_VERSION || 'v3' }}
      COVERAGE_THRESHOLD: ${{ vars.CODEX_COVERAGE_THRESHOLD || '80' }}
    steps:
      - uses: actions/setup-node@v5
        with:
          node-version: ${{ env.NODE_VERSION }}
```

---

## 📚 Related Documentation

- **Variables Configuration**: `.codex/CRITICAL_REPOSITORY_VARIABLES.md`
- **Pending Workflows**: `.codex/PENDING_WORKFLOWS_VARIABLE_DEPLOYMENT.md`
- **Cache Strategy**: `.codex/CI_CACHE_OPTIMIZATION.md`
- **Validation Script**: `scripts/ci/validate_repo_variables.py`
- **Session Context**: `scripts/ci/session_context_enrichment.py`
- **Cache Optimization Tool**: `scripts/ci/optimize_ci_cache.py`
- **Phase 1 Tracking**: `.codex/PHASE_1_ROADMAP_TRACKING.md`

---

## 🔗 Important Links

- **Node.js Release Schedule**: https://nodejs.org/en/about/releases/
- **GitHub Variables Documentation**: https://docs.github.com/en/actions/learn-github-actions/variables
- **GitHub Actions Secrets Management**: https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions

---

## 📌 Notes for Next Session (S1263)

- Variables are **NOT** automatically created; they must be manually configured in GitHub UI
- Variables become available to all workflows on **next execution** after creation
- All workflows use safe fallback defaults via `${{ vars.VAR_NAME || 'default' }}` pattern
- Node.js 20 deadline has passed; keep Pattern 21 checks clean and baseline at Node.js 22+
- Cache optimization should be tested incrementally on high-impact workflows first
- Session context enrichment and self-healing are ready to deploy immediately upon variable creation

**Priority**: Preserve Node.js 22+ baseline and variable setup first, then proceed with cache rollout.
