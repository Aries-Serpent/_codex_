# Workflow Management Runbook - Phase 5

**Document Version**: 1.0  
**Last Updated**: 2026-07-13 (Phase 3 Consolidation Complete)  
**Audience**: Developers, DevOps Engineers, Incident Responders  

---

## 📖 Table of Contents

1. [Phase 3 Consolidation Overview](#phase-3-consolidation-overview)
2. [Emergency Procedures](#emergency-procedures)
3. [Workflow Restoration](#workflow-restoration)
4. [Performance Troubleshooting](#performance-troubleshooting)
5. [Adding New Workflows](#adding-new-workflows)
6. [Modifying Workflows](#modifying-workflows)
7. [Archiving Workflows](#archiving-workflows)
8. [Dashboard Interpretation](#dashboard-interpretation)
9. [Action Version Updates](#action-version-updates)
10. [Quick Reference](#quick-reference)

---

## Phase 3 Consolidation Overview

**Status:** ✅ COMPLETE (2026-07-13)  
**Reference:** `.codex/PHASE_3_CONSOLIDATION_COMPLETION_REPORT.md`

### Consolidated Master Workflows (Use These)

Phase 3.3 consolidated 235+ workflows down to ~180, creating unified interfaces:

#### Security Scanning

**Master Workflow:** `security-scanning-suite.yml`

Available scan types via dispatch:
```bash
# Run all scans (default)
gh workflow run security-scanning-suite.yml

# Run specific scan type
gh workflow run security-scanning-suite.yml -f scan-type=cve
gh workflow run security-scanning-suite.yml -f scan-type=containers
gh workflow run security-scanning-suite.yml -f scan-type=semgrep
```

**Consolidated Into Suite (8 workflows):**
- `13-3-cve-scanning.yml` → `cve-scan` job
- `container-scan.yml` → `container-scan` job (NEW)
- `13-3-secrets-detection.yml` → `secret-scan` job
- `codeql-fix-verification.yml` → verification logic
- `dependency-scan.yml` → `dependency-scan` job
- `semgrep_sarif.yml` → `semgrep` job
- `security-scan-phase-16.yml` → archived (legacy)
- `security-tools-bootstrap.yml` → archived (one-time)

**Still Independent:**
- `codeql-analysis.yml` (primary CodeQL runner)
- `nightly-codeql-alert-triage.yml` (scheduled triage)
- `security-alert-notification.yml` (alert distribution)

#### Testing

**Master Workflow:** `optimized-test-execution.yml`

Available test types and levels via dispatch:
```bash
# Run all tests (default)
gh workflow run optimized-test-execution.yml

# Run specific test type
gh workflow run optimized-test-execution.yml -f test-type=ml
gh workflow run optimized-test-execution.yml -f test-type=auth

# Run with test level
gh workflow run optimized-test-execution.yml \
  -f test-type=core \
  -f test-level=smoke
```

**Features:**
- P19 shadow import pre-flight check (prevents silent failures)
- Parallel core tests (40-50% faster)
- ML matrix: 2 Python × 3 suites (6 parallel jobs)
- Conditional execution based on file changes

**Consolidated Into Optimized (3 workflows):**
- `ci-pytest.yml.disabled` → core test jobs
- `comprehensive_tests.yml.disabled` → test-level options
- `tests.yml.disabled` → basic functionality

**Still Independent (Specialized Triggers):**
- `auth-tests.yml` (runs on auth path changes)
- `ml-tests.yml` (runs on ML path changes)
- `test-rag.yml` (runs on RAG path changes)
- `rust_swarm_ci.yml` (runs on .rs path changes)

#### Deployment

**Master Workflows:**
- `deploy-production.yml` (production orchestration)
- `deploy-staging.yml` (staging validation)

**Features:**
- Multi-environment support
- Canary deployment support (10% → 50% → 100%)
- Pre/post-deployment health checks
- Automated rollback on failure

**Consolidated:** 5 deployment workflow variants into 2 masters

#### Health Monitoring

**New Capability:** 12 metrics live

**Access Dashboard:**
```bash
# View health dashboard
cat docs/operations/health-dashboard.md

# View raw metrics
cat .codex/WORKFLOW_HEALTH_DASHBOARD.json | jq .
```

**Key Metrics:**
- Workflow success rate
- CodeQL alert volume
- Test pass rate
- Code coverage
- Deployment success rate
- CI failure rate
- Performance latency
- Documentation freshness

### Migration for Developers

**Impact:** If you manually trigger workflows, use new consolidated interfaces above.

**No Changes to:**
- ✅ PR checks (still automatic)
- ✅ Push triggers (still automatic)
- ✅ Artifact locations
- ✅ SARIF output to GitHub Security tab
- ✅ Schedule timing

**See Also:** `docs/operations/workflow-consolidation-guide.md` for detailed migration guide.

### Archives

**Location:** `.github/workflows/archived/`

Consolidated workflows moved here for reference. Can be restored if needed:

```bash
# Restore archived workflow
cp .github/workflows/archived/security-workflows/container-scan.yml \
   .github/workflows/

# Push changes
git add .github/workflows/
git commit -m "RESTORE: container-scan.yml from archive"
```

**See:** `.codex/WORKFLOW_ARCHIVAL_DECISIONS.md` for recovery procedures.

---

### Scenario: Workflow Health Dashboard Unavailable

**Symptoms**: Dashboard generation failed, no data in `.codex/workflow_health_snapshot.json`

**Resolution**:
1. Check if `workflow-health-update.yml` workflow ran successfully
   ```bash
   gh run list -w workflow-health-update.yml --limit 5
   ```

2. If workflow failed, manually collect metrics:
   ```bash
   python scripts/ci/workflow_health_collector.py \
     --days 30 \
     --output .codex/workflow_health_snapshot.json
   ```

3. Generate dashboard manually:
   ```bash
   python scripts/ci/workflow_health_dashboard.py \
     --input .codex/workflow_health_snapshot.json \
     --output .codex/WORKFLOW_HEALTH_DASHBOARD.md
   ```

4. If GitHub API is unavailable, use cached snapshot from last 24 hours

---

### Scenario: CodeQL Offline / Alert System Down

**Symptoms**: CodeQL alerts not updating, alert categorization failing

**Fallback Procedures**:
1. Check GitHub status: https://www.githubstatus.com/
2. Use GitHub Code Scanning API directly:
   ```bash
   gh api repos/{owner}/{repo}/code-scanning/alerts
   ```
3. Manually review recent PRs for CodeQL failures
4. Post alert status to #security Slack channel

---

### Scenario: Critical Alert Flood

**Symptoms**: >10 CRITICAL or >50 HIGH alerts in triage report

**Immediate Actions**:
1. Page on-call security engineer
2. Trigger emergency standup (Slack: `@security-team`)
3. Run manual alert categorization:
   ```bash
   python scripts/security/codeql_alert_categorizer.py --repo Aries-Serpent/_codex_
   ```
4. Prioritize by age + severity (oldest first)
5. Create emergency task force if needed

---

### Scenario: Action Version Enforcement Failing

**Symptoms**: `action-version-check.yml` failing on PRs

**Resolution**:
1. Check what versions failed:
   ```bash
   python scripts/ci/enforce_actions_versions.py --check
   ```

2. Review `.codex/ACTION_VERSIONS_BASELINE.md` for current requirements

3. If baseline is outdated, update it:
   ```bash
   # Edit .codex/ACTION_VERSIONS_BASELINE.md
   # Update versions + document reason
   ```

4. Run auto-fix on main branch:
   ```bash
   git checkout main
   python scripts/ci/enforce_actions_versions.py --fix
   git add .github/workflows/
   git commit -m "chore: Update action versions to baseline"
   git push
   ```

---

## 🔄 Workflow Restoration

### Complete Workflow Failure (100% fail rate)

**Diagnosis Flowchart**:
```
Is it a new workflow?
  ├─ YES → Check recent commits for changes
  └─ NO → Skip to "Did it fail recently?"

Did it fail recently?
  ├─ YES (< 24 hours) → Check recent PRs/commits
  └─ NO → Likely infrastructure issue

Check GitHub Actions status:
  ├─ INCIDENT → Wait for GitHub resolution
  └─ NORMAL → Check workflow logs

Review workflow logs:
  ├─ Permission denied → Check secrets/tokens
  ├─ Tool not found → Check runner OS/setup
  └─ Test failures → Run locally first
```

### Step-by-Step Recovery

1. **Identify the workflow**:
   ```bash
   gh run list --limit 20 --state failed
   ```

2. **Get failure details**:
   ```bash
   gh run view [RUN_ID] --log
   ```

3. **Check recent changes** to that workflow:
   ```bash
   git log -p --follow .github/workflows/[WORKFLOW].yml | head -100
   ```

4. **Verify locally** (if applicable):
   ```bash
   # Try running test/lint locally to see if it's env-specific
   ./scripts/test.sh  # or relevant script
   ```

5. **Create fix branch**:
   ```bash
   git checkout -b fix/workflow-[WORKFLOW]-recovery
   # Make fixes
   git push -u origin fix/workflow-[WORKFLOW]-recovery
   ```

6. **Test on canary** before merging to main:
   - Create PR and monitor run
   - Verify success before merge

7. **Document the fix** in `.codex/WORKFLOW_OPTIMIZATION_DECISIONS.md`

---

### Rollback Procedure

If a recent change broke a workflow:

```bash
# Find the breaking commit
git log --oneline .github/workflows/[WORKFLOW].yml | head -5

# Revert the breaking commit
git revert [COMMIT_SHA]

# Review the revert
git show

# Push directly to main (if urgent) or via PR
git push origin HEAD:main
```

---

## 🔧 Performance Troubleshooting

### Workflow Running >30 Minutes (Slow)

**Investigation Steps**:

1. **Check historical runtime**:
   ```bash
   gh run list -w [WORKFLOW] --limit 10 --json durationMinutes
   ```

2. **Identify the slow job**:
   ```bash
   gh run view [RUN_ID] -v
   ```

3. **Review logs for bottlenecks**:
   - Dependency resolution (pip/npm)
   - Long-running tests
   - Artifact downloads
   - Cache misses

4. **Fix strategies** (in priority order):
   - **Increase parallelism**: Use matrix strategies
   - **Improve caching**: Cache dependencies, build artifacts
   - **Split workflows**: Break into smaller, parallel workflows
   - **Optimize test selection**: Run only affected tests
   - **Use faster runners**: Consider `ubuntu-latest` vs `ubuntu-22.04`

**Example**: Parallelize tests
```yaml
strategy:
  matrix:
    python-version: ['3.11', '3.12']
    test-group: [unit, integration, performance]
```

---

### High Cancellation Rate (>10%)

**Causes & Solutions**:
- **Concurrent runs**: Limit via concurrency group
- **Quota limits**: GitHub Actions quota exhaustion
- **Timeout**: Workflow timeout too short
- **Manual cancellation**: Frequent developer cancellations

**Fix**:
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

---

### Flaky Tests (Intermittent Failures)

**Detection**:
```bash
# Run locally multiple times
for i in {1..5}; do pytest tests/; done
```

**Solutions**:
- Add `@pytest.mark.flaky(reruns=2)` to unstable tests
- Increase test timeouts for slow machines
- Fix race conditions in test setup/teardown
- Isolate test state (use fixtures)

**Example**:
```python
@pytest.mark.flaky(reruns=2, reruns_delay=1)
def test_async_operation():
    result = async_func()
    assert result is not None
```

---

## ➕ Adding New Workflows

### Pre-Launch Checklist

- [ ] Clear business requirement documented
- [ ] Template selected (see `.github/templates/`)
- [ ] Trigger condition defined (push, PR, schedule, etc.)
- [ ] Concurrency group assigned (prevent conflicts)
- [ ] Monitoring setup (added to health dashboard)
- [ ] Performance baseline established
- [ ] Cost estimate calculated (runner-hours)
- [ ] Security requirements reviewed
- [ ] Documentation written

### Step-by-Step

1. **Create from template**:
   ```bash
   cp .github/templates/workflow-template.yml .github/workflows/my-workflow.yml
   ```

2. **Configure basics**:
   ```yaml
   name: My New Workflow
   on:
     push:
       branches: [main]
   concurrency:
     group: my-workflow-${{ github.ref }}
     cancel-in-progress: false
   ```

3. **Add monitoring metadata** (for health dashboard):
   ```yaml
   env:
     WORKFLOW_TIER: standard  # critical, standard, optional
     ESTIMATED_RUNTIME_MIN: 15
   ```

4. **Test on PR** before adding to production:
   ```bash
   git push origin feature/my-workflow
   # Create PR and monitor run
   ```

5. **Document in `.codex/WORKFLOW_OPTIMIZATION_DECISIONS.md`**:
   ```markdown
   ## New Workflow: my-workflow.yml
   - Purpose: [description]
   - Trigger: [when it runs]
   - Expected Runtime: [X] minutes
   - Cost: [X] runner-hours/month
   - Justification: [why it's needed]
   ```

6. **Enable monitoring** for new workflow:
   ```bash
   # Add to health collector
   echo "my-workflow" >> .codex/workflows-monitored.txt
   ```

---

## ✏️ Modifying Workflows

### Safety Checklist Before Changes

- [ ] Understand current behavior (check recent runs)
- [ ] Test change locally/on canary
- [ ] Document change reason
- [ ] Have rollback plan ready
- [ ] Monitor first 3 runs after change
- [ ] Get peer review for critical workflows

### Change Types & Procedures

**Minor Changes** (dependencies, env vars):
- ✅ Commit directly to main
- Update via PR (recommend for visibility)

**Moderate Changes** (job order, script updates):
- ✅ Always via PR
- Test on canary branch
- Require one approval

**Major Changes** (trigger conditions, new jobs):
- ✅ Via PR with discussion
- Require two approvals
- Monitor for 3 days after merge
- Be prepared to rollback

### Example: Safe Workflow Modification

```bash
# 1. Create feature branch
git checkout -b chore/optimize-test-timeout

# 2. Make changes
vim .github/workflows/test.yml  # Change timeout from 10m to 15m

# 3. Test locally (syntax validation)
yamllint .github/workflows/test.yml

# 4. Commit with good message
git commit -m "chore: increase test timeout to 15m (tests timing out on slow runs)"

# 5. Create PR for review
git push -u origin chore/optimize-test-timeout
# Create PR with explanation

# 6. After approval, merge and monitor
git merge --squash
git push origin main

# 7. Monitor first 3 runs
sleep 3600
gh run list -w test.yml --limit 3
```

---

## 🗑️ Archiving Workflows

### Decision Criteria

Archive a workflow if:
- Unused for >3 months
- Functionality replaced by another workflow
- Technology deprecated
- Business need no longer exists
- Causing consistent failures with no fix in sight

### Archive Procedure

1. **Create deprecation branch**:
   ```bash
   git checkout -b deprecate/[workflow-name]
   ```

2. **Move workflow to archive**:
   ```bash
   mkdir -p .github/workflows-archive/$(date +%Y-%m)
   mv .github/workflows/[workflow].yml .github/workflows-archive/$(date +%Y-%m)/
   ```

3. **Document the archive**:
   ```markdown
   # Archived: [workflow].yml
   - Archived Date: [DATE]
   - Last Run: [DATE]
   - Reason: [reason]
   - Historical Data: `.github/workflows-archive/[path]`
   ```

4. **Remove from health monitoring**:
   ```bash
   sed -i '/[workflow]/d' .codex/workflows-monitored.txt
   ```

5. **Create PR with detailed message**:
   ```bash
   git commit -m "chore: archive [workflow].yml (unused for >3 months)"
   git push -u origin deprecate/[workflow-name]
   # Create PR
   ```

6. **Update documentation**:
   - Remove from `.codex/WORKFLOW_MANAGEMENT_RUNBOOK.md`
   - Link in archived workflows list
   - Keep for historical reference

---

## 📊 Dashboard Interpretation

### Dashboard Color Scheme

| Color | Meaning | Action |
|-------|---------|--------|
| 🟢 Green (≥95%) | Healthy | Monitor regularly |
| 🟡 Yellow (80-95%) | Warning | Review trends |
| 🔴 Red (<80%) | Critical | Urgent investigation |

### Key Metrics Explained

**Success Rate**: Percentage of runs that completed successfully
- Target: ≥95% for standard workflows
- Target: ≥99% for critical workflows (CodeQL, security)
- Formula: successful_runs / total_runs × 100

**Average Runtime**: Mean execution time over last 30 days
- Useful for capacity planning
- Trend indicates efficiency changes

**P95 Runtime**: 95th percentile (worst-case typical)
- Use for SLA commitments
- More realistic than average for variable workloads

**Flakiness Score**: 0-1 scale (0=stable, 1=very unstable)
- >0.2 indicates problematic intermittency
- Correlates with test quality issues

**Trend Indicators**:
- 📈 Improving: Success rate increased last week
- 📉 Degrading: Success rate decreased last week
- ➡️ Stable: No significant trend

### Reading the Dashboard

1. **Look for red workflows** first (action required)
2. **Scan yellow warnings** (monitor for escalation)
3. **Check trends** for workflows you manage
4. **Review recommendations** section for team action items

---

## 🔄 Action Version Updates

### Baseline Versions

See `.codex/ACTION_VERSIONS_BASELINE.md` for current requirements:
```
- actions/checkout: v4 → v5
- actions/setup-python: v4 → v5
- github/codeql-action/*: v2 → v3
```

### Update Procedure

1. **Check for available updates**:
   ```bash
   python scripts/ci/enforce_actions_versions.py --check-updates
   ```

2. **Review breaking changes**:
   - Check action release notes
   - Look for breaking changes
   - Test in non-critical workflow first

3. **Update baseline document**:
   ```markdown
   ## Update: actions/checkout v4 → v5
   - Date: 2026-07-15
   - Reason: Security fix + performance improvement
   - Breaking Changes: None for our usage
   - Migration: Automated by enforce_actions_versions.py
   ```

4. **Test in PR**:
   - Update one non-critical workflow
   - Monitor 5 runs
   - Verify compatibility

5. **Update baseline**:
   ```bash
   vim .codex/ACTION_VERSIONS_BASELINE.md
   # Update version
   ```

6. **Automated fix**:
   ```bash
   python scripts/ci/enforce_actions_versions.py --fix
   git add .github/workflows/
   git commit -m "chore: update to action version baseline"
   git push
   ```

7. **Verify all workflows updated**:
   ```bash
   python scripts/ci/enforce_actions_versions.py --check
   # Should return success
   ```

---

## 🎯 Quick Reference

### Useful Commands

```bash
# View workflow runs
gh run list -w [workflow-name] --limit 10

# View specific run details
gh run view [RUN_ID] --log

# Rerun failed jobs
gh run rerun [RUN_ID] --failed

# Watch live workflow
gh run watch [RUN_ID]

# Collect health metrics
python scripts/ci/workflow_health_collector.py

# Check action versions
python scripts/ci/enforce_actions_versions.py --check

# Categorize alerts
python scripts/security/codeql_alert_categorizer.py --repo owner/repo

# Validate YAML syntax
yamllint .github/workflows/
```

### Escalation Paths

**Performance Issues**:
→ DevOps team → Architecture review

**Security Alerts**:
→ @mbaetiong (security lead) → incident response team

**Workflow Failures** (multiple):
→ Team owner → Debug together → Root cause analysis

**Emergency**:
→ #incident Slack → on-call engineer → escalation

### SLAs

| Issue Type | Target Response | Escalation |
|-----------|------------------|-----------|
| Critical workflow failure | 15 minutes | Immediate |
| Security alert (CRITICAL) | 1 hour | 30 min warning |
| Security alert (HIGH) | 24 hours | 12 hour warning |
| Performance degradation | 1 day | 6 hour warning |
| Low priority issue | 1 week | None |

---

## 📞 Support & Feedback

**Questions?**
- Check `.codex/PHASE_5_CONTINUOUS_ENABLEMENT_MONITORING.md` (architecture)
- Open issue in repository
- Contact DevOps team

**Improvements?**
- Suggest in next optimization cycle meeting
- Document in `.codex/WORKFLOW_OPTIMIZATION_DECISIONS.md`
- Create feature request issue

---

**Document Status**: 🟢 PRODUCTION  
**Last Review**: 2026-07-13  
**Next Review**: 2026-08-13
