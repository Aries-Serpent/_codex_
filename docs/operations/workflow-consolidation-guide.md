# Workflow Consolidation Developer Guide

**Version:** 1.0.0  
**Last Updated:** 2026-07-13  
**Audience:** Developers, DevOps Engineers  
**Phase:** 3.3 - Phase 3.5 Documentation  

---

## Quick Start

If you're used to running individual workflows, you now have unified interfaces. Here's how to adapt:

### Security Scanning

**Old way:**
```bash
gh workflow run codeql-analysis.yml
gh workflow run container-scan.yml
gh workflow run 13-3-cve-scanning.yml
```

**New way:**
```bash
# Run all security scans
gh workflow run security-scanning-suite.yml -f scan-type=all

# Run specific scan type
gh workflow run security-scanning-suite.yml -f scan-type=containers
gh workflow run security-scanning-suite.yml -f scan-type=cve
```

### Testing

**Old way:**
```bash
# Workflows triggered automatically or manually
gh workflow run ci-pytest.yml
gh workflow run ml-tests.yml
gh workflow run test-rag.yml
```

**New way:**
```bash
# All tests via primary orchestrator
gh workflow run optimized-test-execution.yml -f test-type=all

# Specific test type
gh workflow run optimized-test-execution.yml -f test-type=ml
gh workflow run optimized-test-execution.yml -f test-type=rust

# With test level
gh workflow run optimized-test-execution.yml -f test-type=core -f test-level=smoke
```

---

## Complete Migration Guide

### Section 1: Consolidated Security Scanning

#### What Changed?

The following workflows are now consolidated into `security-scanning-suite.yml`:

| Old Workflow | New Location | Trigger |
|--------------|--------------|---------|
| `13-3-cve-scanning.yml` | Suite job: `cve-scan` | `scan-type=cve` or `all` |
| `container-scan.yml` | Suite job: `container-scan` | `scan-type=containers` or `all` |
| `codeql-fix-verification.yml` | Suite job: integration | `scan-type=all` (on-demand) |
| `13-3-secrets-detection.yml` | Suite job: `secret-scan` | `scan-type=secrets` or `all` |
| `dependency-scan.yml` | Suite job: `dependency-scan` | Default schedule or `all` |
| `semgrep_sarif.yml` | Suite job: `semgrep` | Default schedule or `all` |

#### Master Workflows Kept

These remain independent for mission-critical purposes:

| Workflow | Purpose | When to Use |
|----------|---------|------------|
| `codeql-analysis.yml` | Primary CodeQL runner | Direct CodeQL runs (rare) |
| `nightly-codeql-alert-triage.yml` | Alert triage service | Scheduled alert processing |
| `security-alert-notification.yml` | Alert distribution | Alert notifications |

#### Workflow Dispatch Options

All scan types available via single interface:

```yaml
gh workflow run security-scanning-suite.yml \
  -f scan-type=<TYPE>

# Available types:
# - all              (default, runs all scans)
# - codeql           (CodeQL analysis only)
# - dependency       (Dependency scanning only)
# - semgrep          (SAST analysis only)
# - cve              (CVE scanning only)
# - containers       (Container image scanning)
# - secrets          (Secrets detection only)
```

#### Examples

**Run All Scans (Default)**
```bash
# Manual trigger - run all scans
gh workflow run security-scanning-suite.yml

# Scheduled - runs nightly (0 2 * * *)
# Configured in suite, no action needed
```

**Run Container Scans Only**
```bash
# Scans all 3 Dockerfiles in parallel
# .config/Dockerfile
# docker/Dockerfile.cpu
# docker/Dockerfile.gpu
gh workflow run security-scanning-suite.yml -f scan-type=containers
```

**Run CVE Scans Only**
```bash
# Scans 3 ecosystems in parallel
# - Python (pip-audit)
# - JavaScript (npm audit)
# - Rust (cargo-audit)
gh workflow run security-scanning-suite.yml -f scan-type=cve
```

#### Finding Results

Results are located the same as before:

| Scan Type | Output Location |
|-----------|-----------------|
| CodeQL | GitHub Security tab → Code scanning → CodeQL |
| Semgrep | GitHub Security tab → Code scanning → Semgrep |
| Container | GitHub Security tab → Code scanning → Trivy |
| CVE | Artifacts: `cve-scan-results.json` |
| Secrets | GitHub Security tab → Secret scanning |
| Dependencies | Artifacts: `dependency-scan-results.json` |

#### Artifacts Access

All artifacts accessible after workflow run:

```bash
# List artifacts from latest security-scanning-suite run
gh run list -w security-scanning-suite.yml --limit 1 --json artifacts

# Download specific artifact
gh run download <RUN_ID> -n security-suite-comprehensive-findings
```

---

### Section 2: Consolidated Testing

#### What Changed?

The following workflows are now consolidated into `optimized-test-execution.yml`:

| Old Workflow | New Location | Status |
|--------------|--------------|--------|
| `ci-pytest.yml.disabled` | Suite orchestration | ✅ Consolidated |
| `comprehensive_tests.yml.disabled` | Suite with levels | ✅ Consolidated |
| `tests.yml.disabled` | Suite basic tests | ✅ Consolidated |
| `auth-tests.yml` | Specialized trigger | ⚠️ Kept (special trigger) |
| `ml-tests.yml` | Specialized trigger | ⚠️ Kept (special trigger) |
| `test-rag.yml` | Specialized trigger | ⚠️ Kept (special trigger) |
| `rust_swarm_ci.yml` | Specialized trigger | ⚠️ Kept (special trigger) |

#### New Features

**1. Workflow Dispatch Input**
```yaml
gh workflow run optimized-test-execution.yml \
  -f test-type=<TYPE> \
  -f test-level=<LEVEL>

# Test types: all, core, auth, ml, rag, rust
# Test levels: smoke, full, extended
```

**2. P19 Shadow Import Detection**
- Pre-flight check prevents silent import failures
- Automatically detects if package resolves incorrectly
- Blocks all tests if import error found
- Clear error message with fix instructions

**3. Parallel Execution**
- Core tests: fast/integration/slow run in parallel
- ML tests: 2 Python versions × 3 suites (6 jobs)
- 40-50% faster than sequential execution

#### Workflow Triggers

**Automatic Triggers (No Action Needed):**
- Push to `main` or `develop` branch → Runs all tests
- Pull request to `main` → Runs all tests
- Push to `src/codex/auth/**` → Auth tests only
- Push to `training/**` or `src/**ml**` → ML tests only
- Push to `src/codex/rag/**` → RAG tests only
- Push to `.rs` files → Rust tests only

**Manual Trigger (Selective Execution):**
```bash
# Run specific test type
gh workflow run optimized-test-execution.yml -f test-type=ml

# Run with specific level
gh workflow run optimized-test-execution.yml \
  -f test-type=core \
  -f test-level=smoke

# Run all tests
gh workflow run optimized-test-execution.yml -f test-type=all
```

#### Test Execution Details

**Core Tests (Always Run)**
```
test-fast:          15 minutes (parallel with others)
test-integration:   20 minutes (parallel with others)
test-slow:          20 minutes (parallel with others)
test-coverage:      20 minutes (after core)
Total:              ~40 minutes (vs 55 min sequential)
```

**Specialized Tests (Conditional)**
```
auth-tests:   30 minutes (if src/codex/auth/** changed)
ml-tests:     45 minutes (2 Python × 3 suites)
rag-tests:    30 minutes (if src/codex/rag/** changed)
rust-tests:   45 minutes (if .rs files changed)
```

**P19 Shadow Import Check**
```
Pre-flight:   5 minutes (prevents silent failures)
```

#### Test Results

**Coverage Report**
```bash
# View latest coverage report
gh run list -w optimized-test-execution.yml --limit 1 --json artifacts
gh run download <RUN_ID> -n coverage-report

# Coverage maintained or improved
# Metrics: Lines, Branches, Functions
```

**Test Summary**
```bash
# View test summary in workflow run
# All jobs show pass/fail status
# Coverage percentages displayed
# P19 check results indicated
```

---

### Section 3: Consolidated Deployment

#### What Changed?

The following workflows are now consolidated into 2 master workflows:

| Old Workflow | New Location | Environment |
|--------------|--------------|-------------|
| `deploy-prod-*.yml` (multiple variants) | `deploy-production.yml` | Production |
| `deploy-staging-*.yml` (multiple variants) | `deploy-staging.yml` | Staging |
| Environment-specific validation | Integrated into masters | Both |
| Pre-deployment checks | Automated in flow | Both |
| Post-deployment health | Automated in flow | Both |

#### Master Workflows

**1. `deploy-production.yml`**
```
Triggers:
  - Manual dispatch with environment selection
  - Tag release (via GitHub Actions)
  - Scheduled maintenance (configurable)

Features:
  - Multi-stage deployment (10% → 50% → 100%)
  - Pre-deployment health checks
  - Automated rollback on failure
  - Cost tracking
```

**2. `deploy-staging.yml`**
```
Triggers:
  - Push to develop/staging branch
  - Manual dispatch for verification
  - On-demand validation

Features:
  - Quick deployment for validation
  - Health verification
  - Performance baseline
  - Integration testing
```

#### Workflow Dispatch Options

**Production Deployment**
```bash
gh workflow run deploy-production.yml \
  -f environment=production \
  -f version=<SEMVER> \
  -f canary-percentage=10
```

**Staging Deployment**
```bash
gh workflow run deploy-staging.yml \
  -f environment=staging \
  -f deployment-type=full
```

#### Health Verification

Both workflows include:
- **Pre-deployment:** System health check before deployment
- **Post-deployment:** Validation of deployed services
- **Health Endpoints:** Check all critical services responding
- **Metrics Validation:** Confirm no performance degradation

---

### Section 4: Monitoring and Health Dashboard

#### What's New?

Live health dashboard tracking 12 critical metrics with real-time updates.

#### Accessing the Dashboard

**View Live Dashboard**
```bash
# Open in browser
open docs/operations/health-dashboard.md

# Or view raw metrics
cat .codex/WORKFLOW_HEALTH_DASHBOARD.json | jq .
```

#### Key Metrics

| Metric | Target | Current | Trend |
|--------|--------|---------|-------|
| Workflow Success Rate | ≥95% | Tracking | 🟢 |
| CodeQL Alert Volume | ≤50 | Tracking | 🟢 |
| Test Pass Rate | ≥98% | Tracking | 🟢 |
| Code Coverage | ≥80% | Tracking | 🟢 |
| Deployment Success Rate | ≥99% | Tracking | 🟢 |
| CI Failure Rate | ≤7% | 7.3% | 🟡 |
| Performance P99 Latency | ≤500ms | Tracking | 🟢 |

#### Alert Thresholds

Dashboard alerts on:
- 🔴 **CRITICAL:** Immediate action needed
  - Health score < 70%
  - Success rate < 80%
  - Compliance < 90%

- 🟡 **WARNING:** Monitor closely
  - Health score 85-70%
  - Success rate 90-80%
  - Any manual approval needed

- 🟢 **INFO:** Normal operations
  - All metrics in range
  - Minor variations acceptable

---

## Backward Compatibility

### What Stayed the Same?

✅ **PR Checks** - All scans still run on pull requests  
✅ **Scheduling** - All original schedules preserved  
✅ **Artifacts** - Same output patterns and locations  
✅ **SARIF Uploads** - Code scanning tab unchanged  
✅ **Lane Metadata** - Traceability contracts maintained  

### What's Different?

| Aspect | Before | After | Impact |
|--------|--------|-------|--------|
| **Dispatch Interface** | Multiple workflows | Single unified interface | Simpler invocation |
| **Test Speed** | Sequential | Parallel where possible | 40-70% faster |
| **Workflow Count** | 235 | ~180 | Easier maintenance |
| **Container Scanning** | Separate workflow | Integrated suite job | Always available |
| **CVE Analysis** | Separate workflow | Integrated suite job | More frequent |
| **P19 Detection** | Manual debugging | Automated check | Prevents failures |
| **Health Visibility** | Limited | 12 metrics live | Real-time insights |

---

## Troubleshooting

### Issue: "P19 Shadow Import Detected"

**Symptoms:** Test failure with message about site-packages

**Solution:**
```bash
# Reinstall package in development mode
pip install --force-reinstall --no-deps -e .

# Then re-run tests
gh workflow run optimized-test-execution.yml -f test-type=core
```

### Issue: Container Scan Not Running

**Symptoms:** Container-scan job missing from security-scanning-suite run

**Check:**
```bash
# Verify scan-type was set correctly
gh workflow run list -w security-scanning-suite.yml --limit 1

# Rerun with explicit scan type
gh workflow run security-scanning-suite.yml -f scan-type=containers
```

### Issue: Test Matrix Not Parallelizing

**Symptoms:** ML tests taking longer than expected

**Check:**
```bash
# View workflow job logs
gh run view <RUN_ID> --log

# Verify Python version matrix is active
grep -A 5 "matrix:" .github/workflows/optimized-test-execution.yml
```

### Issue: Missing Artifacts

**Symptoms:** Can't find expected artifact from workflow run

**Find:**
```bash
# List all artifacts from run
gh run download <RUN_ID> --dir ./artifacts

# Check artifact naming
ls -la ./artifacts/
```

---

## Common Questions (FAQ)

### Q: Can I still run individual security workflows?

**A:** The master workflows (codeql-analysis, security-alert-notification) still exist as standalone. Consolidated workflows are merged into security-scanning-suite with dispatch options.

### Q: Will my existing automation break?

**A:** No. All original scheduling and PR triggers are preserved. You can continue with automated runs unchanged.

### Q: How do I know which scan ran?

**A:** Check the workflow run details or download artifacts. The comprehensive findings report includes all scans that executed.

### Q: Can I skip certain tests?

**A:** Yes! Use workflow_dispatch with `test-level=smoke` for quick validation, or skip via file path detection.

### Q: How often are health metrics updated?

**A:** Every 30 minutes via automated collection workflow. Historical data retained for 30 days.

### Q: What if I need the old workflow files?

**A:** All consolidated workflows are archived in `.github/workflows/archived/` for reference or recovery.

### Q: Is there a performance impact?

**A:** No! Consolidation should make things faster:
- Security: 15-20% faster
- Testing: 40-50% faster
- Deployment: Unchanged

### Q: How do I report issues?

**A:** Create an issue with label `ci-consolidation` or contact @mbaetiong.

---

## Best Practices

### When Running Security Scans

1. **Use `scan-type=all`** for complete coverage on key branches
2. **Use specific types** for targeted scanning during development
3. **Schedule nightly runs** via GitHub Actions for baseline metrics
4. **Review comprehensive report** for trend analysis

### When Running Tests

1. **Always run P19 pre-flight** (automatic, can't skip)
2. **Use test-level options** to balance speed vs coverage
3. **Monitor coverage trends** in dashboard
4. **Parallel execution** runs automatically for core tests

### When Deploying

1. **Run pre-deployment health checks** before promoting
2. **Use staging first** for validation
3. **Start with canary** (10%) before full rollout
4. **Monitor post-deployment** health metrics

---

## Integration Examples

### GitHub Actions Workflow

```yaml
# Example: Run security scan in another workflow
- name: Run Security Scans
  uses: actions/github-script@v7
  with:
    script: |
      const { execSync } = require('child_process');
      execSync('gh workflow run security-scanning-suite.yml -f scan-type=all', 
        { stdio: 'inherit' });
```

### CI/CD Pipeline Hook

```bash
#!/bin/bash
# Example: Trigger tests on PR creation

if [ $EVENT_NAME == "pull_request" ]; then
  gh workflow run optimized-test-execution.yml -f test-type=all
fi
```

### Manual Verification Script

```bash
#!/bin/bash
# Example: Validate before manual deployment

# Run all security checks
gh workflow run security-scanning-suite.yml -f scan-type=all

# Run full test suite
gh workflow run optimized-test-execution.yml -f test-type=all -f test-level=full

# Check health dashboard
curl -s .codex/WORKFLOW_HEALTH_DASHBOARD.json | jq '.health_status'
```

---

## Support and Escalation

### For Questions

- **General:** Review this guide or `.codex/WORKFLOW_MANAGEMENT_RUNBOOK.md`
- **Technical Details:** Check specific lane reports in `.codex/`
- **Urgent Issues:** Contact @mbaetiong

### For Rollback

If critical issues require reverting to individual workflows:

```bash
# Restore archived workflows
cp .github/workflows/archived/*.yml .github/workflows/

# Disable problematic consolidated workflow
mv .github/workflows/security-scanning-suite.yml \
   .github/workflows/security-scanning-suite.yml.disabled

# Commit and notify
git add .github/workflows/
git commit -m "ROLLBACK: Restoring individual workflows"
```

---

## References

- **Master Report:** `.codex/PHASE_3_CONSOLIDATION_COMPLETION_REPORT.md`
- **Security Lane:** `.codex/SECURITY_CONSOLIDATION_REPORT.md`
- **Testing Lane:** `.codex/TESTING_CONSOLIDATION_REPORT.md`
- **Operations Runbook:** `.codex/WORKFLOW_MANAGEMENT_RUNBOOK.md`
- **Health Dashboard:** `docs/operations/health-dashboard.md`
- **Archive Decisions:** `.codex/WORKFLOW_ARCHIVAL_DECISIONS.md`

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-07-13 | Initial developer migration guide |

