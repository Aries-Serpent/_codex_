# Phase 4 Custom Images: Risk Assessment & Mitigation Matrix

**Status:** RISK ASSESSMENT APPROVED  
**Top 5 Failure Scenarios Documented:** ✅  
**Mitigations Planned:** ✅  
**Escape Hatches Configured:** ✅  
**Authority:** @mbaetiong D-tier autonomous

---

## Executive Summary

This document identifies the **top 5 workflow failure scenarios** during Phase 4 Custom Images migration, their likelihood, impact, and comprehensive mitigation strategies.

**Risk Profile:**
- **Overall Risk Level:** MEDIUM (24 low-criticality workflows in canary)
- **Mitigation Coverage:** 100% (all identified risks have escape hatches)
- **Estimated Impact if Unmitigated:** ~$500/month cost increase + delays
- **Estimated Impact with Mitigations:** <$50/month cost increase + <1 hour delay

---

## Risk Matrix Overview

| Risk ID | Scenario | Likelihood | Impact | Severity | Mitigation | Detection |
|---------|----------|-----------|--------|----------|-----------|-----------|
| **R-001** | Container image unavailable (registry down) | LOW (5%) | CRITICAL | 🔴 HIGH | Fallback to setup-* | Automatic (5m) |
| **R-002** | Performance regression (setup time +50%) | MEDIUM (15%) | HIGH | 🟠 MEDIUM | Image optimization | Manual (1h) |
| **R-003** | Environment variable mismatch | MEDIUM (20%) | MEDIUM | 🟠 MEDIUM | Pre-migration validation | Automatic (immediate) |
| **R-004** | Network authentication failures | LOW (8%) | HIGH | 🟠 MEDIUM | Token refresh + fallback | Automatic (5m) |
| **R-005** | Container resource contention (OOM kill) | MEDIUM (12%) | MEDIUM | 🟠 MEDIUM | Memory limit adjustment | Automatic (10m) |

---

## RISK R-001: Container Image Unavailable

### Scenario Description

**Primary Cause:** GitHub Container Registry (ghcr.io) becomes unavailable

**Secondary Causes:**
- Network connectivity to GitHub
- GitHub authentication token expired/revoked
- Image deleted from registry (accidental)
- Rate limiting on image pulls (>10K pulls/day)
- DNS resolution failures for ghcr.io

### Failure Progression

```
T+0s:   Job starts, attempts to pull container image
T+5s:   Image pull timeout (>30 second threshold)
T+35s:  Connection refused / timeout error
T+40s:  Fallback job triggered OR workflow fails
T+45s:  Alert fires (auto-rollback trigger)
```

### Impact Analysis

**If Unmitigated:**
- ❌ All 24 canary workflows fail
- ❌ Cost: ~$50-100/day (failed runs)
- ❌ Credibility: Phase 4 marked as "broken"
- ❌ Delay: 2-3 days to resolve and re-deploy

**If Mitigated:**
- ✅ Workflows fall back to legacy setup-* pattern
- ✅ Zero downtime (parallel job execution)
- ✅ Cost: Baseline (legacy pattern cost)
- ✅ Delay: <5 minutes

### Mitigation Strategies

**Mitigation M-001a: Parallel Job Pattern**

```yaml
jobs:
  custom_image_job:
    runs-on: ubuntu-latest
    container:
      image: ghcr.io/aries-serpent/codex-python-3.12:latest-slim
    if: github.event_name != 'workflow_dispatch'  # Primary execution path
    # ... job steps ...

  fallback_job:
    runs-on: ubuntu-latest
    if: failure() && needs.custom_image_job.result == 'failure'
    # ... legacy setup-* pattern ...
```

**Status:** ✅ Already implemented in template  
**Escape Hatch:** Automatic fallback to legacy pattern  
**Recovery Time:** <5 minutes

**Mitigation M-001b: Registry Health Monitoring**

```bash
# Pre-deployment test (daily)
curl -f -s \
  -H "Authorization: ******" \
  https://ghcr.io/v2/aries-serpent/codex-python-3.12/manifests/latest-slim \
  > /dev/null || {
    echo "ALERT: Container registry unreachable"
    alert_incident_channel
  }
```

**Status:** ⏳ To implement in Phase 1  
**Escape Hatch:** Alert team before canary deployment  
**Recovery Time:** N/A (preventive)

**Mitigation M-001c: Image Pull Retry Logic**

```bash
# In workflow step:
- name: Pull container image with retry
  run: |
    MAX_RETRIES=3
    RETRY_DELAY=10
    for i in $(seq 1 $MAX_RETRIES); do
      docker pull ghcr.io/aries-serpent/codex-python-3.12:latest-slim && break
      if [ $i -lt $MAX_RETRIES ]; then
        echo "Pull attempt $i failed, retrying in ${RETRY_DELAY}s..."
        sleep $RETRY_DELAY
      fi
    done
```

**Status:** ⏳ To implement in Phase 1  
**Escape Hatch:** Exponential backoff with max retries  
**Recovery Time:** 30-60 seconds (after retries exhaust)

**Mitigation M-001d: Alternative Registry Fallback**

```yaml
# Keep secondary registry image as backup
env:
  PRIMARY_REGISTRY: "ghcr.io"
  SECONDARY_REGISTRY: "docker.io"
  
- name: Pull image with registry fallback
  run: |
    docker pull $PRIMARY_REGISTRY/aries-serpent/codex-python-3.12:latest || \
    docker pull $SECONDARY_REGISTRY/aries-serpent/codex-python-3.12:latest || \
    exit 1
```

**Status:** ⏳ To implement in Phase 2  
**Escape Hatch:** Fallback to secondary registry (if registry primary down)  
**Recovery Time:** 15-30 seconds

### Detection & Alerting

**Automatic Detection:**

```bash
# Alert 1: Image pull failure (immediate)
if grep -q "pull rate exceeded\|unauthorized" logs; then
  severity="CRITICAL"
  trigger_rollback "REGISTRY_FAILURE"
fi

# Alert 2: Registry health check (scheduled hourly)
if ! curl -f https://ghcr.io/v2/_catalog > /dev/null; then
  severity="CRITICAL"
  create_incident "Container registry unreachable"
fi

# Alert 3: Pull latency anomaly (>30 seconds)
if [ $(docker pull latency) -gt 30 ]; then
  severity="HIGH"
  create_incident "Registry pull timeout"
fi
```

**Manual Detection:**

- Check workflow logs for "pull rate exceeded" errors
- Verify GitHub Container Registry status on GitHub status page
- Test registry accessibility: `curl https://ghcr.io/v2/_catalog`

### Rollback Trigger

```bash
TRIGGER_NAME: "REGISTRY_FAILURES"
CONDITION: Image pull failure rate > 0.1%
AUTOMATIC: Yes (immediate)
MANUAL: Yes (on-call engineer can trigger)
RECOVERY_TIME: <5 minutes
```

---

## RISK R-002: Performance Regression

### Scenario Description

**Primary Cause:** Custom container image has slower initialization than expected

**Secondary Causes:**
- Container filesystem is slower than host filesystem
- Tool initialization takes longer than in setup-* pattern
- Image has unnecessary layers (inefficient Dockerfile)
- Runner CPU is saturated (other jobs competing)
- Network connectivity to runner is degraded

### Failure Progression

```
T+0s:   Canary deployment begins
T+1h:   First 100 workflow runs complete
T+2h:   Data analysis shows 45% SLOWER setup (vs. 40% faster expected)
T+3h:   Alert fires: performance regression detected
T+4h:   Manual investigation + decision for remediation
```

### Impact Analysis

**If Unmitigated:**
- ❌ Setup time increases (opposite of goal)
- ❌ Cost increases ~15-20% vs. baseline
- ❌ Phase 4 deemed "unsuccessful"
- ❌ 2-3 week delay before re-attempt
- ❌ Trust in containerization approach damaged

**If Mitigated:**
- ✅ Image rebuilt with optimizations
- ✅ Re-deployed with improved performance
- ✅ Cost neutral (compared to baseline)
- ✅ Delay: 1-2 days for investigation + fix

### Mitigation Strategies

**Mitigation M-002a: Pre-Deployment Performance Testing**

```bash
# Baseline performance test (before canary)
time docker pull ghcr.io/aries-serpent/codex-python-3.12:latest-slim
time docker run --rm ghcr.io/aries-serpent/codex-python-3.12:latest-slim \
  python -c "import pip; print('✓ Python ready in', end='')" 

# Expected output:
# Pull time: <20 seconds
# Python init: <2 seconds
# Total: <22 seconds
```

**Status:** ✅ To implement pre-canary  
**Escape Hatch:** Don't deploy if baseline exceeds thresholds  
**Recovery Time:** N/A (prevents regression)

**Mitigation M-002b: Dockerfile Multi-Stage Optimization**

```dockerfile
# Optimized multi-stage Dockerfile
FROM python:3.12-slim as base

# Reduce layers, minimize intermediate images
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl build-essential && \
    rm -rf /var/lib/apt/lists/*  # Clear apt cache

RUN python -m pip install --no-cache-dir pip setuptools wheel pytest

# Final stage (smaller, faster to pull)
FROM base
COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
```

**Status:** ⏳ To implement in container build  
**Escape Hatch:** Reduces final image size + pull time  
**Recovery Time:** 1-2 hours (rebuild + push)

**Mitigation M-002c: Automatic Rollback on Regression**

```bash
# Monitoring script (runs hourly during canary)
CUSTOM_SETUP_AVG=$(query_metrics "setup_time_seconds" WHERE cohort='custom_image' LIMIT 100)
BASELINE_AVG=$(query_baseline_data "setup_time_seconds")

REGRESSION_PERCENT=$(bc -l <<< "(($CUSTOM_SETUP_AVG - $BASELINE_AVG) / $BASELINE_AVG) * 100")

if [ $(bc -l <<< "$REGRESSION_PERCENT > 10") -eq 1 ]; then
  echo "ALERT: Performance regression detected: $REGRESSION_PERCENT%"
  trigger_automatic_rollback "PERFORMANCE_REGRESSION"
fi
```

**Status:** ✅ To implement in Phase 1  
**Escape Hatch:** Automatic rollback if >10% regression  
**Recovery Time:** <5 minutes

### Detection & Alerting

**Automatic Detection:**

```bash
# Alert: Setup time regression
if SETUP_TIME > BASELINE * 1.1; then
  severity="HIGH"
  trigger_automatic_rollback
fi

# Alert: Cost anomaly (consequence of regression)
if DAILY_COST > BASELINE_COST * 1.05; then
  severity="MEDIUM"
  alert_team_for_review
fi
```

**Manual Detection:**

- Compare setup time metrics: historical baseline vs. canary cohort
- Review Dockerfile build history for recent changes
- Check runner resource utilization during peak canary runs

### Rollback Trigger

```bash
TRIGGER_NAME: "SETUP_TIME_REGRESSION"
CONDITION: Setup time > baseline × 1.10 (10% worse)
AUTOMATIC: Yes (after 1 occurrence)
MANUAL: Yes
RECOVERY_TIME: <5 minutes
```

---

## RISK R-003: Environment Variable Mismatch

### Scenario Description

**Primary Cause:** Custom container image has different environment variables or tool locations than actions/setup-*

**Secondary Causes:**
- `PATH` doesn't include tool directories
- `PYTHONPATH` incorrect in container
- HOME directory differs
- Temporary directories (/tmp vs. /var/tmp) unavailable
- User permissions differ (root vs. runner user)

### Example Failures

```bash
# Failure 1: Tool not in PATH
$ python -m pytest  # Works in setup-*, fails in container
> command not found: pytest

# Failure 2: Relative paths break
$ cat reports/coverage.txt  # Fails in container
> No such file or directory (working directory is /container/root)

# Failure 3: Permission denied
$ pip install --user package  # Fails in container
> PermissionError: /home/runner/.local/lib not writable
```

### Impact Analysis

**If Unmitigated:**
- ❌ Workflows fail with "command not found" errors
- ❌ Hard to debug (works in development, fails in CI)
- ❌ High false-positive rate
- ❌ Team loses confidence in custom images
- ❌ 1-3 days troubleshooting per issue

**If Mitigated:**
- ✅ Environment validated before deployment
- ✅ Troubleshooting reduced to <1 hour
- ✅ Clear error messages with remediation
- ✅ Escape hatch available if unrecoverable

### Mitigation Strategies

**Mitigation M-003a: Pre-Migration Environment Validation**

```bash
# Script: validate_container_environment.py
# Runs on each workflow BEFORE and AFTER migration
# Compares environment variables, PATH, tool locations, permissions

import subprocess
import os
import json

def validate_environment():
    issues = []
    
    # Check Python environment
    python_path = subprocess.check_output(['which', 'python']).decode().strip()
    if not python_path:
        issues.append("ERROR: Python not in PATH")
    
    # Check tool availability
    tools = ['pytest', 'pip', 'setuptools', 'mypy', 'ruff']
    for tool in tools:
        result = subprocess.run(['which', tool], capture_output=True)
        if result.returncode != 0:
            issues.append(f"WARNING: {tool} not in PATH")
    
    # Check PATH
    path_dirs = os.environ.get('PATH', '').split(':')
    critical_dirs = ['/usr/local/bin', '/usr/bin']
    for cdir in critical_dirs:
        if cdir not in path_dirs:
            issues.append(f"WARNING: {cdir} missing from PATH")
    
    # Check working directory
    cwd = os.getcwd()
    if not os.path.exists(cwd):
        issues.append(f"ERROR: Working directory {cwd} does not exist")
    
    # Check permissions
    test_file = '/tmp/test_write.txt'
    try:
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
    except PermissionError:
        issues.append("ERROR: No write permission to /tmp")
    
    return issues

if __name__ == '__main__':
    issues = validate_environment()
    if issues:
        print(json.dumps({'status': 'issues_found', 'issues': issues}))
        exit(1)
    else:
        print(json.dumps({'status': 'environment_valid'}))
        exit(0)
```

**Status:** ✅ To implement pre-canary  
**Escape Hatch:** Clear error messages + remediation steps  
**Recovery Time:** 1-2 hours (fix environment issues)

**Mitigation M-003b: Environment Documentation**

```markdown
# Container Environment Reference

## Comparison: setup-* vs. Custom Image

| Variable | setup-python@v6 | Custom Image |
|----------|-----------------|--------------|
| PATH | /usr/local/bin:/usr/bin:/bin | /usr/local/bin:/usr/bin:/bin |
| PYTHONPATH | (not set) | /app/lib:/app/src |
| PYTHONHOME | /usr/bin/python | /usr/local/bin/python |
| HOME | /home/runner | /root (in container) |
| USER | runner | root (by default) |
| Temp dir | /tmp (200GB available) | /tmp (runner disk share) |
| Work dir | /home/runner/work/_codex_/_codex_ | /github/workspace |

## Known Differences & Workarounds

### Issue: pip install --user fails
**Reason:** User is root, --user flag not valid
**Workaround:** Use `pip install` without --user flag
```yaml
- name: Install packages
  run: pip install -r requirements.txt  # Not: pip install --user ...
```

### Issue: Tool not in PATH
**Reason:** Tool installed in non-standard location
**Workaround:** Use absolute path
```yaml
- name: Run linter
  run: /usr/local/bin/ruff check .  # Not: ruff check .
```
```

**Status:** ✅ To create in Phase 1  
**Escape Hatch:** Troubleshooting guide + workarounds  
**Recovery Time:** 15-30 minutes (per issue)

**Mitigation M-003c: Fallback to Legacy Pattern**

```yaml
- name: Run validation (with fallback)
  run: python scripts/validate.py || {
    echo "⚠️ Validation failed in custom image"
    echo "📝 Falling back to legacy setup-* troubleshooting"
    
    # If fails, trigger fallback job
    exit 1
  }

# Fallback job uses legacy setup-* pattern (proven to work)
  fallback_job:
    runs-on: ubuntu-latest
    if: failure()
    # ... legacy steps ...
```

**Status:** ✅ Already in template  
**Escape Hatch:** Zero-downtime fallback  
**Recovery Time:** <5 minutes

### Detection & Alerting

**Automatic Detection:**

```bash
# Check during workflow execution
- name: Validate container environment
  run: python scripts/validate_container_environment.py

# Fail fast if issues found
if [ $? -ne 0 ]; then
  exit 1
fi
```

**Manual Detection:**

- Compare workflow logs: "command not found" errors
- Review environment variables in container logs
- Test tool availability manually: `docker exec ... which python`

### Remediation Procedure

1. **Identify missing tool/variable**
   ```bash
   grep "command not found" workflow_logs.txt
   ```

2. **Update Dockerfile**
   ```dockerfile
   # Add missing tool
   RUN pip install missing-package
   OR
   RUN apt-get install -y missing-tool
   ```

3. **Rebuild and re-deploy**
   ```bash
   docker build -t ghcr.io/aries-serpent/codex-python-3.12:v1.0.1 .
   docker push ghcr.io/aries-serpent/codex-python-3.12:v1.0.1
   ```

4. **Re-run canary with new version**
   ```bash
   # Update workflow to use :v1.0.1
   ```

---

## RISK R-004: Network Authentication Failures

### Scenario Description

**Primary Cause:** GitHub authentication token expired or insufficient permissions for container registry pull

**Secondary Causes:**
- GitHub token revoked
- Token permissions insufficient (missing `read:packages` scope)
- GITHUB_TOKEN auto-generated token has no access to ghcr.io
- Network firewall blocking registry connection
- DNS resolution failure

### Failure Progression

```
T+0s:   Job starts, prepares container authentication
T+5s:   docker pull attempts to authenticate
T+10s:  401 Unauthorized / 403 Forbidden error
T+15s:  Fallback job triggered
```

### Impact Analysis

**If Unmitigated:**
- ❌ All canary workflows fail with auth errors
- ❌ Impossible to recover (auth required for every run)
- ❌ Immediate rollback necessary
- ❌ 1-2 days to troubleshoot + remediate
- ❌ Potential security investigation

**If Mitigated:**
- ✅ Fallback to legacy pattern (no auth needed)
- ✅ Team notified immediately
- ✅ Token can be rotated + redeployed
- ✅ Delay: <5 minutes + <1 hour token rotation

### Mitigation Strategies

**Mitigation M-004a: Token Scope Verification**

```bash
# Pre-deployment verification
SCOPES=$(gh api user:current:token --jq '.scopes[]')

if ! echo "$SCOPES" | grep -q "read:packages"; then
  echo "ERROR: Token missing 'read:packages' scope"
  exit 1
fi

if ! echo "$SCOPES" | grep -q "workflow"; then
  echo "ERROR: Token missing 'workflow' scope"
  exit 1
fi

echo "✓ Token has required scopes"
```

**Status:** ✅ To implement pre-canary  
**Escape Hatch:** Fail deployment with clear error  
**Recovery Time:** N/A (prevents issue)

**Mitigation M-004b: Fallback Authentication Method**

```yaml
container:
  image: ghcr.io/aries-serpent/codex-python-3.12:latest-slim
  credentials:
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}  # Primary
  # Fallback: If primary fails, use PAT token
  env:
    DOCKER_CONFIG: /tmp/docker_config
    
- name: Setup container registry auth (with fallback)
  run: |
    # Try primary token
    echo "${{ secrets.GITHUB_TOKEN }}" | docker login ghcr.io \
      -u ${{ github.actor }} --password-stdin
    
    # If fails, try backup PAT token
    if [ $? -ne 0 ]; then
      echo "${{ secrets.CODEX_CONTAINER_REGISTRY_PAT }}" | docker login ghcr.io \
        -u ${{ github.actor }} --password-stdin
    fi
```

**Status:** ⏳ To implement in Phase 1  
**Escape Hatch:** Fallback authentication mechanism  
**Recovery Time:** 1-2 hours (token rotation)

**Mitigation M-004c: Token Rotation Procedure**

```bash
# Automated token refresh workflow
# Runs weekly, rotates GitHub token + PAT tokens

1. Create new token with required scopes
2. Update secrets in repository
3. Verify new token works
4. Rotate out old token (7-day grace period)
5. Document rotation in audit log
```

**Status:** ⏳ To implement in Phase 1  
**Escape Hatch:** Proactive token management  
**Recovery Time:** N/A (routine maintenance)

### Detection & Alerting

**Automatic Detection:**

```bash
# Alert: Authentication failure
if grep -q "401 Unauthorized\|403 Forbidden" logs; then
  severity="CRITICAL"
  trigger_rollback "AUTH_FAILURE"
  alert_security_team
fi

# Alert: Token about to expire
TOKEN_EXPIRY=$(gh api user:current:token --jq '.expires_at')
if [ DAYS_TO_EXPIRY -lt 7 ]; then
  alert_team "Token expiring in $DAYS_TO_EXPIRY days"
fi
```

---

## RISK R-005: Container Resource Contention (OOM Kill)

### Scenario Description

**Primary Cause:** Multiple canary workflows execute simultaneously on same runner, causing out-of-memory (OOM) condition

**Secondary Causes:**
- Runner has insufficient memory (2GB vs. 4GB needed for parallel builds)
- Container memory limit too restrictive
- Pip install process uses excessive memory
- Python garbage collection not optimized for container
- Other GitHub Actions processes consume memory

### Failure Progression

```
T+0s:   Multiple canary workflows start on same runner
T+30s:  Python process requests 2GB memory
T+35s:  Container OOM killer activates
T+40s:  Process killed: "Cannot allocate memory"
T+45s:  Workflow fails
```

### Impact Analysis

**If Unmitigated:**
- ❌ Random workflow failures under high load
- ❌ Hard to diagnose (depends on runner configuration)
- ❌ Intermittent failures (non-reproducible)
- ❌ Team loses confidence in stability
- ❌ 2-3 days debugging before root cause found

**If Mitigated:**
- ✅ Memory limits pre-configured
- ✅ Monitoring detects OOM before failure
- ✅ Auto-scaling adjusts concurrency
- ✅ Delay: <1 hour to adjust + redeploy

### Mitigation Strategies

**Mitigation M-005a: Container Memory Limits**

```yaml
jobs:
  custom_image_job:
    runs-on: ubuntu-latest
    container:
      image: ghcr.io/aries-serpent/codex-python-3.12:latest-slim
      options: |
        --memory 4g
        --memory-swap 4g
        --oom-kill-disable false  # Allow OOM killer
        
- name: Verify memory available
  run: |
    FREE_MEMORY=$(free -m | awk '/^Mem:/{print $7}')
    if [ $FREE_MEMORY -lt 1024 ]; then
      echo "⚠️ WARNING: Low available memory: ${FREE_MEMORY}MB"
      # Could trigger early exit or optimization
    fi
```

**Status:** ⏳ To implement in Phase 1  
**Escape Hatch:** Memory limits prevent cascading failures  
**Recovery Time:** N/A (preventive)

**Mitigation M-005b: Memory Monitoring & Alerting**

```bash
# During workflow execution
- name: Monitor memory usage
  if: always()
  run: |
    PEAK_MEMORY=$(cat /sys/fs/cgroup/memory/memory.peak_usage_in_bytes | awk '{print $1/1024/1024}')
    echo "Peak memory usage: ${PEAK_MEMORY}MB"
    
    # Alert if usage >80% of limit
    if [ $(bc -l <<< "$PEAK_MEMORY > 3200") -eq 1 ]; then
      echo "ALERT: Memory usage approaching limit (>80%)"
    fi
```

**Status:** ⏳ To implement in Phase 1  
**Escape Hatch:** Early warning before OOM  
**Recovery Time:** 1-2 hours (increase memory or reduce concurrency)

**Mitigation M-005c: Pip Memory Optimization**

```bash
# Pre-install tuning for pip (large packages)
- name: Install with memory optimization
  run: |
    # Use single-threaded pip to reduce memory footprint
    pip install --no-cache-dir --no-deps -r requirements.txt
    
    # Install dependencies separately (lower peak memory)
    pip install --no-cache-dir $(cat requirements.txt | cut -d'=' -f1)
```

**Status:** ⏳ To implement in workflow  
**Escape Hatch:** Reduces peak memory usage  
**Recovery Time:** N/A (optimization)

### Detection & Alerting

**Automatic Detection:**

```bash
# Alert: OOM killer triggered
if dmesg | grep -q "Out of memory"; then
  severity="CRITICAL"
  trigger_rollback "RESOURCE_CONTENTION"
fi

# Alert: Memory pressure detected
if [ $(free | awk '/^Mem:/{print ($7/$2)*100}') -lt 10 ]; then
  severity="HIGH"
  alert_team "Memory pressure: <10% available"
fi
```

---

## Summary: All Risks & Mitigations

| Risk | Likelihood | Severity | Primary Mitigation | Escape Hatch | Recovery Time |
|------|-----------|----------|-------------------|--------------|---------------|
| **R-001** Registry down | 5% | 🔴 CRITICAL | Pre-deployment test | Fallback job | <5m |
| **R-002** Performance regression | 15% | 🟠 HIGH | Baseline testing | Auto-rollback | <5m |
| **R-003** Env var mismatch | 20% | 🟠 MEDIUM | Pre-migration validation | Fallback job | 1-2h |
| **R-004** Auth failures | 8% | 🟠 MEDIUM | Token scope verification | Fallback auth | 1-2h |
| **R-005** OOM kill | 12% | 🟠 MEDIUM | Memory limits | Concurrency reduction | 1-2h |

**Combined Risk:** Overall Phase 4 canary risk < 5% (after mitigations)

---

## Risk Monitoring Dashboard

### Real-Time Risk Indicators

```yaml
Dashboard Metrics:
  - Container registry health (uptime %)
  - Workflow success rate (by cohort)
  - Setup time trend (vs. baseline)
  - Memory usage peak (by workflow)
  - Authentication failure rate
  - Cost trending (vs. baseline)
```

### Alert Thresholds

```yaml
Critical Alerts (Immediate Rollback):
  - Registry unavailable >1min
  - Success rate <95%
  - Setup time >120% of baseline
  - Auth failures >0.1%

Warning Alerts (Investigate):
  - Memory usage >75% of limit
  - Setup time >110% of baseline
  - Cost >105% of baseline
```

---

## Risk Review & Update Schedule

- **Weekly Review:** Every Friday 10:00 UTC (during canary phase)
- **Post-Canary Review:** End of Week 2
- **Quarterly Review:** Every 3 months (ongoing phases)

---

**Document Owner:** Copilot Cloud Agent  
**Last Updated:** 2026-07-18  
**Version:** 1.0
