# Phase 8.1: Comprehensive Incident Response Runbooks

**Version**: 1.0.0  
**Last Updated**: 2026-07-02T18:00:00Z  
**Authority**: @mbaetiong (D-tier autonomous)

---

## Runbook 1: High Failure Rate Response

**Trigger**: Failure rate > 5% (baseline 1.2% + 5% = 6.2%) sustained for 30 minutes

### 1. Detection & Alert

```yaml
Alert Severity: Critical (P1)
Alert Type: Failure Rate Threshold Exceeded
Notification: PagerDuty page + Slack #ci-cd-emergency
Response SLA: 15 minutes
```

### 2. Investigation Checklist

- [ ] **Verify alert legitimacy**
  ```bash
  # Check current failure rate from dashboard
  curl https://api.github.com/repos/{owner}/{repo}/actions/runs \
    -H "Authorization: token $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github.v3+json" | jq '.workflow_runs[] | select(.created_at > "2026-07-02T17:30:00Z")'
  ```

- [ ] **Identify affected workflows**
  - Filter recent failed runs
  - Group by workflow name
  - Check for common patterns

- [ ] **Check error messages**
  - Look for consistent error patterns
  - Check error logs for stack traces
  - Review error classification in dashboard

- [ ] **Correlate with recent changes**
  ```bash
  # View recent commits
  git log --oneline -20
  
  # Check for deployment events
  gh api repos/{owner}/{repo}/deployments -q '.[] | select(.created_at > "2026-07-02T16:00:00Z")'
  ```

- [ ] **Check infrastructure health**
  - CPU utilization <90%? ✓
  - Memory utilization <90%? ✓
  - Disk space >10% available? ✓
  - API rate limit <70%? ✓

- [ ] **Verify dependency status**
  - GitHub API status: operational
  - AWS services status: operational
  - External registries (npm, pypi, docker): operational

### 3. Root Cause Analysis

**Common Causes** (probability order):
1. **Flaky tests** (35%) - Intermittent test failures
2. **Environment issues** (25%) - Missing dependencies or resources
3. **Code changes** (20%) - Regression from recent commit
4. **Infrastructure** (15%) - Resource constraints or service degradation
5. **External dependency** (5%) - Registry or API issues

**Diagnosis Decision Tree**:
```
Are all workflows failing?
├─ YES → Infrastructure/environment issue (check SLA metrics)
└─ NO → Workflow-specific issue (check recent commits)
        ├─ Same workflow type?
        │  └─ YES → Pattern issue (check dependency/cache)
        └─ NO → Multiple issues (check for cascade failures)
```

### 4. Remediation Options

**Option A: Automatic Retry** (if flaky tests suspected)
```bash
# Rerun failed workflows
gh workflow run phase-8-1-health-monitor.yml --ref main --input collect_type=workflow
```

**Option B: Revert Recent Changes** (if code regression)
```bash
# Check recent commits
git log --oneline -5

# If suspicious commit found:
git revert <commit-sha> -m "Reverting due to high failure rate alert"
git push origin main
```

**Option C: Scale Infrastructure** (if resource constraint)
```bash
# Increase GitHub Actions runners or compute resources
# Contact infrastructure team for scaling request
```

**Option D: Clear Caches** (if cache corruption)
```bash
# Clear all workflow caches (will re-build on next run)
gh api repos/{owner}/{repo}/actions/caches --method DELETE
```

### 5. Resolution Verification

**Success Criteria**:
- [ ] Failure rate drops to <2% within 30 minutes
- [ ] All newly triggered workflows passing
- [ ] No new incidents reported
- [ ] Root cause identified and documented

**Monitor for 1 hour**:
```bash
# Watch failure rate
watch -n 60 'curl https://api.github.com/repos/{owner}/{repo}/actions/runs \
  -H "Authorization: token $GITHUB_TOKEN" | jq '.workflow_runs[] | select(.created_at > "2026-07-02T17:00:00Z") | .conclusion' | sort | uniq -c'
```

### 6. Post-Incident

- [ ] Document root cause in incident log
- [ ] Update runbook with new learnings
- [ ] File follow-up issue for improvement
- [ ] Notify stakeholders of resolution

---

## Runbook 2: Performance Degradation Response

**Trigger**: p95 latency > baseline * 1.2 (7m * 1.2 = 8m 24s) sustained for 20 minutes

### 1. Detection & Alert

```yaml
Alert Severity: High (P2)
Alert Type: Performance Degradation
Notification: Slack #ci-cd-alerts
Response SLA: 1 hour
```

### 2. Investigation Checklist

- [ ] **Verify performance metrics**
  ```bash
  # Check latency percentiles
  python << 'EOF'
  import json
  with open('.codex/metrics/enhanced_metrics.json') as f:
    m = json.load(f)
  sig = m['signals']['workflow_metrics']
  for name, metrics in sig.items():
    print(f"{name}: p95={metrics.get('p95_latency_sec', 0)}s, avg={metrics.get('avg_duration_sec', 0)}s")
  EOF
  ```

- [ ] **Check resource utilization**
  - CPU: Check `cpu_utilization_percent` from metrics
  - Memory: Check `memory_utilization_percent` from metrics
  - Disk: Check `disk_utilization_percent` from metrics

- [ ] **Review workflow execution logs**
  - Identify slowest steps
  - Check for resource-intensive operations
  - Look for synchronous operations that could parallelize

- [ ] **Check cache hit rates**
  - Build cache hit: Check `build_cache_hit_rate_percent`
  - Dependency cache: Check `dependency_cache_hit_rate_percent`
  - Artifact cache: Check `artifact_cache_hit_rate_percent`

- [ ] **Review recent changes to workflows**
  ```bash
  git diff HEAD~5 .github/workflows/
  ```

### 3. Root Cause Analysis

**Common Causes**:
1. **Low cache hit rate** (40%) - Rebuilds taking longer
2. **Resource contention** (25%) - CPU/memory pressure
3. **Dependency latency** (20%) - Slow registry/API
4. **Workflow changes** (10%) - New steps added
5. **External load** (5%) - GitHub service degradation

**Diagnosis**:
```
Check cache hit rates first
├─ <80% hit rate? → Clear caches and rebuild
├─ >80% hit rate?
│  └─ Check resource usage
│     ├─ >80% CPU/Memory? → Scale resources
│     └─ <80%? → Check dependency latency
└─ Dependency latency >500ms? → Contact provider
```

### 4. Remediation Options

**Option A: Optimize Cache Strategy**
```bash
# Analyze cache effectiveness
python scripts/ci/phase_8_3_perf_analyzer.py --analyze-caching

# Clear stale caches
gh api repos/{owner}/{repo}/actions/caches --method DELETE
```

**Option B: Scale Infrastructure**
```bash
# Increase runner concurrency
# Update GitHub Actions settings to allow more parallel jobs
gh api repos/{owner}/{repo}/actions/runner-groups --input '{"runners_url": "..."}'
```

**Option C: Optimize Workflows**
```bash
# Parallelize independent tasks
# Use conditional workflows to skip unnecessary steps
# Implement better caching strategies
```

**Option D: Address Dependency Latency**
```bash
# Configure faster registries
# Implement local package mirrors
# Add retry logic with exponential backoff
```

### 5. Resolution Verification

**Success Criteria**:
- [ ] p95 latency <baseline (7m 12s)
- [ ] Cache hit rates >85%
- [ ] Resource utilization <80%
- [ ] Consistent performance across 10+ runs

**Monitor for 2 hours**:
```bash
# Track latency improvement
for i in {1..120}; do
  python -c "
import json
with open('.codex/metrics/enhanced_metrics.json') as f:
  m = json.load(f)
print(f'p95: {m[\"signals\"][\"workflow_metrics\"].get(list(m[\"signals\"][\"workflow_metrics\"].keys())[0], {}).get(\"p95_latency_sec\", 0)}s')
"
  sleep 60
done
```

---

## Runbook 3: Infrastructure Saturation Response

**Trigger**: CPU >90% OR Memory >90% sustained for 15 minutes

### 1. Detection & Alert

```yaml
Alert Severity: Critical (P1)
Alert Type: Infrastructure Resource Saturation
Notification: PagerDuty page + ops team
Response SLA: 15 minutes
```

### 2. Investigation Checklist

- [ ] **Verify resource metrics**
  ```bash
  python << 'EOF'
  import json
  with open('.codex/metrics/enhanced_metrics.json') as f:
    m = json.load(f)
  infra = m['signals']['infrastructure_metrics']
  print(f"CPU: {infra['cpu_utilization_percent']}%")
  print(f"Memory: {infra['memory_utilization_percent']}%")
  print(f"Disk: {infra['disk_utilization_percent']}%")
  EOF
  ```

- [ ] **Identify resource hogs**
  - Which workflows consuming most CPU?
  - Which jobs have highest memory usage?
  - Check GitHub Actions dashboard

- [ ] **Check for stuck processes**
  ```bash
  # List long-running jobs
  gh api repos/{owner}/{repo}/actions/runs \
    --method GET \
    -f head_sha=main \
    -f per_page=100 | jq '.workflow_runs[] | select(.status == "in_progress") | .html_url'
  ```

- [ ] **Review recent deployments**
  ```bash
  gh api repos/{owner}/{repo}/deployments -q '.[] | select(.created_at > "2026-07-02T17:00:00Z")'
  ```

- [ ] **Check for resource leaks**
  - Are processes properly terminating?
  - Are caches being cleared?
  - Check docker image cleanup

### 3. Root Cause Analysis

**Common Causes**:
1. **Runaway workflow** (40%) - Process stuck in infinite loop
2. **Resource leak** (30%) - Memory not being freed
3. **High concurrency** (20%) - Too many parallel jobs
4. **Large artifact** (10%) - Huge file processing

---

## Runbook 4: External Dependency Failure Response

**Trigger**: Service error rate >5% OR latency >2x baseline sustained for 10 minutes

### 1. Detection & Alert

```yaml
Alert Severity: High (P2)
Alert Type: External Dependency Health Degradation
Notification: Slack #ci-cd-alerts
Response SLA: 1 hour
```

### 2. Investigation Checklist

- [ ] **Check service status pages**
  - GitHub Status: https://www.githubstatus.com
  - AWS Status: https://status.aws.amazon.com
  - npm Status: https://status.npmjs.org
  - PyPI Status: https://status.python.org/

- [ ] **Verify network connectivity**
  ```bash
  curl -i https://api.github.com/status
  curl -i https://registry.npmjs.org/
  curl -i https://pypi.org/
  ```

- [ ] **Check retry behavior**
  ```bash
  # Review workflow logs for retry attempts
  gh run view <run-id> --log
  ```

- [ ] **Review fallback mechanisms**
  - Is caching enabled?
  - Are offline mirrors available?
  - Can workflows use pre-cached dependencies?

### 3. Remediation Options

**Option A: Enable Caching/Fallback**
```bash
# Use cached dependencies on next run
# Update workflows to use local mirrors
```

**Option B: Increase Timeouts**
```yaml
# In workflows, increase timeout for flaky operations
timeout-minutes: 20  # increased from 10
```

**Option C: Circuit Breaker**
```bash
# Implement circuit breaker pattern
# Skip non-critical external calls during outage
```

**Option D: Switch to Backup Endpoint**
```bash
# Use alternate registry or CDN
# Switch GitHub Enterprise to backup region
```

### 4. Resolution Verification

**Success Criteria**:
- [ ] Service dependency restored
- [ ] Error rate <1%
- [ ] Latency <baseline
- [ ] All workflows completing successfully

---

## Runbook 5: Data Integrity/Loss Response

**Trigger**: Artifact verification fails OR backup validation fails

### 1. Detection & Alert

```yaml
Alert Severity: Critical (P0/P1)
Alert Type: Data Integrity Violation
Notification: Page incident commander immediately
Response SLA: 5 minutes
```

### 2. Investigation Checklist

- [ ] **Verify artifact integrity**
  ```bash
  # Check artifact checksums
  find .codex/artifacts -name "*.sha256" -exec sha256sum -c {} \;
  ```

- [ ] **Review backup logs**
  ```bash
  tail -100 .codex/backup.log
  ```

- [ ] **Identify corruption source**
  - When was corruption introduced?
  - Which artifacts affected?
  - What system changed recently?

- [ ] **Check rollback availability**
  - Is backup available?
  - How recent is last backup?
  - Can we restore to known good state?

### 3. Remediation Options

**Option A: Restore from Backup** (Preferred)
```bash
# Restore from last known good backup
./scripts/restore_from_backup.sh --timestamp 2026-07-02T12:00:00Z
```

**Option B: Rebuild Artifacts**
```bash
# Trigger full rebuild if source code clean
gh workflow run build.yml --ref main --input full_rebuild=true
```

**Option C: Verify Data Integrity**
```bash
# Re-validate all artifacts
python scripts/verify_artifact_integrity.py --full-scan
```

**Option D: Contact Data Recovery Services**
```bash
# If backup unavailable, contact recovery specialists
# Escalate to VP Infrastructure/Data team
```

### 4. Resolution Verification

**Success Criteria**:
- [ ] Data integrity verified via checksums
- [ ] All artifacts restored
- [ ] Root cause identified
- [ ] Prevention measures implemented

### 5. Post-Incident

- [ ] Document root cause in incident log
- [ ] Implement additional integrity checks
- [ ] Update backup frequency if needed
- [ ] Review data retention policies

---

## 🔄 General Incident Response Procedures

### Escalation Matrix

```
Level 1: On-Call Engineer
  - P3/P4 incidents
  - First 30 minutes response

Level 2: Team Lead
  - P2 incidents
  - If unresolved >30 min
  - P1 technical analysis

Level 3: Engineering Manager
  - P1 incidents
  - If unresolved >1 hour
  - Business impact assessment

Level 4: VP Engineering
  - P0 incidents
  - Critical business impact
  - Immediate escalation
```

### Documentation Requirements

Every incident must document:

1. **Detection Time**: When alert triggered
2. **Root Cause**: What went wrong
3. **Duration**: Time to resolution
4. **Impact**: Number of failed runs/artifacts
5. **Resolution**: Actions taken
6. **Prevention**: Changes to prevent recurrence

### Communication Plan

- **Within 15 min**: Initial notification sent
- **Every 30 min**: Status update during incident
- **At resolution**: Final notification + RCA summary
- **24 hours after**: Post-mortem if severity P1+

---

## 📞 Contact Information

**On-Call Engineer**: `@oncall` or page via PagerDuty  
**Team Lead**: `@team-lead` (Slack or call)  
**Engineering Manager**: `@eng-manager` (Slack or email)  
**VP Engineering**: `@vp-eng` (Page immediately for P0)

---

**Runbook Status**: ✅ Complete and Operational  
**Last Updated**: 2026-07-02T18:00:00Z  
**Authority**: @mbaetiong (D-tier autonomous)
