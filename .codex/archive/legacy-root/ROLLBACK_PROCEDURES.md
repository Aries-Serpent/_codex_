# Rollback Procedures & Failure Recovery Guide

**Version:** 1.0  
**Last Updated:** 2026-07-09  
**Target Audience:** Deployment Engineers, SREs, Incident Responders  
**Status:** Production-Ready  

---

## Overview

This guide provides comprehensive failure detection and recovery procedures for production deployments. It covers 8 specific failure scenarios with decision trees, bash commands, state verification, and post-incident procedures.

**Quick Reference:**
- **Decision Tree:** Determine failure type and affected phase/lane
- **8 Recovery Procedures:** Pre-deployment through full rollback
- **Recovery Time Estimate:** 5-45 minutes depending on failure type
- **Escalation Trigger:** Any unrecoverable failure escalates to @mbaetiong

---

## Failure Detection Decision Tree

```
┌─────────────────────────────────────────────────────────┐
│        DEPLOYMENT FAILURE DETECTED                       │
└─────────────────────────────────────────────────────────┘
                          ↓
        ┌─────────────────────────────────┐
        │ Which phase failed?              │
        └─────────────────────────────────┘
         ↙        ↙        ↙         ↙        ↙
    Phase 1    Phase 2    Phase 3    Phase 4   Phase 5
      ↓          ↓          ↓         ↓         ↓
   [RP-001]   [RP-002]   Which?    [RP-007]  [RP-008]
             (PLAN)     (PRE-CHK)  (DEPLOY) (POST-M)  (VERIFY)
                                     ↓
                        ┌────────────┼────────────┐
                        ↓            ↓            ↓
                    Lane A       Lane B/C      Lane D
                  [RP-003]      [RP-004-005]   [RP-006]
```

---

## Recovery Procedure 1: Pre-Deployment Check Failures (RP-001)

**Affected Phase:** Phase 1 (Planning)  
**Failure Signal:** DEPLOYMENT_PREREQUISITES_CHECKLIST.md returns >0 failures  
**Recovery Time:** 5-15 minutes  
**Impact Scope:** No production systems affected (pre-flight)  

### Detection

```bash
#!/bin/bash
# Detection script for pre-deployment failures

CHECKLIST_RESULT=$(.codex/scripts/deployment_prerequisites_check.sh all 2>&1)
FAILED_COUNT=$(echo "$CHECKLIST_RESULT" | grep -c "FAIL")

if [ $FAILED_COUNT -gt 0 ]; then
  echo "❌ PRE-DEPLOYMENT CHECK FAILURE DETECTED"
  echo "Failed checks: $FAILED_COUNT"
  echo "$CHECKLIST_RESULT" | grep "FAIL"
  exit 1
fi
```

### Recovery Procedure

**Step 1: Identify Failed Checks**
```bash
# Run checklist and save failures
.codex/scripts/deployment_prerequisites_check.sh all > /tmp/checklist-failures.txt 2>&1

# Extract failed sections
grep "❌ CHECK" /tmp/checklist-failures.txt | awk -F: '{print $2}' | sort -u

# Display failure details
grep -A 5 "❌ CHECK" /tmp/checklist-failures.txt
```

**Step 2: Apply Remediation (by section)**

```bash
# Authorization failures (Section 1)
if grep -q "CHECK 1\." /tmp/checklist-failures.txt; then
  echo "REMEDIATION: Authorization failures"
  echo "  1. Check governance gates: .codex/DEPLOYMENT_SIGN_OFF_*.md"
  echo "  2. Request @mbaetiong signature if needed"
  echo "  3. Update deployment window if required"
fi

# Code state failures (Section 2)
if grep -q "CHECK 2\." /tmp/checklist-failures.txt; then
  echo "REMEDIATION: Code quality failures"
  ruff check --fix .
  black .
  mypy src/
  nox -s tests
fi

# Version failures (Section 3)
if grep -q "CHECK 3\." /tmp/checklist-failures.txt; then
  echo "REMEDIATION: Version/artifact failures"
  python -m build
  git tag -a v$(grep version pyproject.toml | head -1 | cut -d'"' -f2) -m "Release v$(grep version pyproject.toml | head -1 | cut -d'"' -f2)"
  git push --tags
fi

# Security failures (Section 5)
if grep -q "CHECK 5\." /tmp/checklist-failures.txt; then
  echo "REMEDIATION: Security failures"
  echo "  1. Run CodeQL remediation agent"
  echo "  2. Update vulnerable dependencies"
  echo "  3. Rotate exposed secrets"
fi
```

**Step 3: Re-validate**
```bash
# Re-run checklist after remediation
.codex/scripts/deployment_prerequisites_check.sh all

# Verify all checks pass
if [ $? -eq 0 ]; then
  echo "✅ All pre-deployment checks passed. Ready to proceed."
else
  echo "❌ Some checks still failing. Escalating to @mbaetiong"
  exit 1
fi
```

### Escalation

If >2 checks fail after remediation:

```bash
# Create escalation issue
gh issue create \
  --title "PRE-DEPLOYMENT FAILURE: $(date +%Y-%m-%d)" \
  --body "$(cat /tmp/checklist-failures.txt)" \
  --label deployment,critical \
  --assignee mbaetiong

# Notify team
echo "ESCALATION: Pre-deployment checks failed. Issue created."
```

---

## Recovery Procedure 2: Agent Dispatch Failures (RP-002)

**Affected Phase:** Phase 2 (Pre-Deployment → Deployment)  
**Failure Signal:** DeploymentGateway fails to dispatch lanes or orchestration error  
**Recovery Time:** 10-20 minutes  
**Impact Scope:** No production systems affected (dispatch layer)  

### Detection

```bash
# Check deployment gateway status
if grep -q "PHASE_FAILED.*pre_deployment" .codex/deployment-*.log; then
  echo "❌ AGENT DISPATCH FAILURE DETECTED"
  grep -B5 -A5 "PHASE_FAILED.*pre_deployment" .codex/deployment-*.log
  exit 1
fi
```

### Recovery Procedure

**Step 1: Diagnose Dispatch Error**
```bash
# Retrieve dispatch logs
LOG_FILE=.codex/deployment-$(ls -t .codex/deployment-*.log | head -1 | sed 's/.*deployment-//;s/.log//')-events.jsonl

# Find dispatch failures
jq 'select(.event_type == "escalation_triggered")' $LOG_FILE

# Extract error messages
jq '.message' $LOG_FILE | grep -i "dispatch\|fail" | head -10
```

**Step 2: Validate Orchestrator Configuration**
```bash
# Check Python class availability
python -c "from .codex.orchestrator import DeploymentGateway; print('✅ Orchestrator loaded')" 2>&1

# Verify lane handlers registered
python -c "
from .codex.orchestrator import Lane
lanes = [Lane.LANE_A, Lane.LANE_B, Lane.LANE_C, Lane.LANE_D]
print(f'✅ {len(lanes)} lanes defined')
"
```

**Step 3: Clear Dispatch State**
```bash
# Remove stale checkpoint
rm -f .codex/deployment-*-checkpoint.json

# Clear event log (archive first)
mv .codex/deployment-*.jsonl .codex/archive/

# Verify clean state
if [ ! -f .codex/deployment-*-checkpoint.json ]; then
  echo "✅ Dispatch state cleared"
fi
```

**Step 4: Retry Dispatch**
```bash
# Run orchestrator with fresh state
python -m codex.cli deploy --deployment-id "v0.1.0-final-retry" --phase "pre_deployment"

# Monitor for success
tail -f .codex/deployment-*.jsonl | jq 'select(.event_type == "phase_complete")'
```

### Escalation

If dispatch continues to fail:

```bash
# Escalate with full logs
python scripts/ci/gather_deployment_diagnostics.py \
  --output-file .codex/dispatch-failure-diagnostics.tar.gz

# Create issue
gh issue create \
  --title "DISPATCH FAILURE: DeploymentGateway orchestration error" \
  --body "Attach: .codex/dispatch-failure-diagnostics.tar.gz" \
  --label deployment,critical \
  --assignee mbaetiong
```

---

## Recovery Procedure 3: Lane A Execution Failures (RP-003)

**Affected Phase:** Phase 3 (Deployment) - Lane A (Feature & Integration Validation)  
**Failure Signal:** Lane A timeout or exception, test failures, feature validation fails  
**Recovery Time:** 15-30 minutes  
**Impact Scope:** Code/tests affected; no production deployment  

### Detection

```bash
# Check for Lane A failure
LOG_FILE=$(ls -t .codex/deployment-*.jsonl | head -1)
if jq 'select(.lane == "lane_a" and .event_type == "lane_failed")' $LOG_FILE | grep -q .; then
  echo "❌ LANE A FAILURE DETECTED"
  jq 'select(.lane == "lane_a")' $LOG_FILE | tail -5
  exit 1
fi
```

### Recovery Procedure

**Step 1: Analyze Lane A Failure**
```bash
# Extract Lane A error
LANE_ERROR=$(jq 'select(.lane == "lane_a" and .event_type == "lane_failed") | .message' \
  $LOG_FILE | head -1)
echo "Lane A Error: $LANE_ERROR"

# Check for specific failure types
if echo "$LANE_ERROR" | grep -q "test.*fail"; then
  echo "Failure Type: TEST FAILURE"
elif echo "$LANE_ERROR" | grep -q "timeout"; then
  echo "Failure Type: TIMEOUT"
elif echo "$LANE_ERROR" | grep -q "validation"; then
  echo "Failure Type: FEATURE VALIDATION FAILURE"
fi
```

**Step 2: Recovery by Failure Type**

```bash
# TYPE A: Test Failure
if echo "$LANE_ERROR" | grep -q "test.*fail"; then
  echo "RECOVERY: Test failure - debugging and retry"
  
  # Run tests with verbose output
  nox -s tests -- -vv --tb=short
  
  # Fix failing tests
  # ... (manual debugging)
  
  # Retry Lane A
  python -c "
  import asyncio
  from .codex.orchestrator import Lane, DeploymentGateway
  gw = DeploymentGateway('v0.1.0-final-recovery')
  asyncio.run(gw.execute_lane(Lane.LANE_A))
  "
fi

# TYPE B: Timeout
if echo "$LANE_ERROR" | grep -q "timeout"; then
  echo "RECOVERY: Lane A timeout - likely long-running tests"
  
  # Check for slow tests
  nox -s tests -- --durations=10
  
  # Optimize or split tests
  # ... (performance improvement)
  
  # Retry with increased timeout (if needed, adjust PHASE_ORCHESTRATOR_SPEC.md)
  python -c "
  import asyncio
  from .codex.orchestrator import Lane, DeploymentGateway
  gw = DeploymentGateway('v0.1.0-final-recovery')
  gw.LANE_TIMEOUTS[Lane.LANE_A] = 600  # 10 minutes
  asyncio.run(gw.execute_lane(Lane.LANE_A))
  "
fi

# TYPE C: Feature Validation Failure
if echo "$LANE_ERROR" | grep -q "validation"; then
  echo "RECOVERY: Feature validation failure"
  
  # Validate features against spec
  python -m codex.cli validate-features --strict
  
  # Fix feature issues
  # ... (manual remediation)
  
  # Retry validation
  python -c "
  import asyncio
  from .codex.orchestrator import Lane, DeploymentGateway
  gw = DeploymentGateway('v0.1.0-final-recovery')
  asyncio.run(gw.execute_lane(Lane.LANE_A))
  "
fi
```

**Step 3: Verify Recovery**
```bash
# Check Lane A status
jq 'select(.lane == "lane_a") | {timestamp, event_type, message}' \
  .codex/deployment-*.jsonl | tail -3

# Confirm success
if jq 'select(.lane == "lane_a" and .event_type == "lane_complete")' \
  .codex/deployment-*.jsonl | grep -q .; then
  echo "✅ Lane A recovery successful"
  exit 0
else
  echo "❌ Lane A still failing - escalate to @mbaetiong"
  exit 1
fi
```

---

## Recovery Procedure 4-5: Lane B/C Execution Failures

**Affected Phase:** Phase 3 (Deployment) - Lanes B/C  
**Failure Signal:** Docker/K8s failure (Lane B) or Security/Docs failure (Lane C)  
**Recovery Time:** 10-25 minutes  

### Lane B (Infrastructure) Recovery

```bash
# Step 1: Diagnose Docker/K8s failure
LANE_ERROR=$(jq 'select(.lane == "lane_b" and .event_type == "lane_failed") | .metadata' \
  .codex/deployment-*.jsonl | jq -r '.exception' | head -1)

# Step 2: Recover Docker build
if echo "$LANE_ERROR" | grep -iq "docker"; then
  docker system prune -f
  RELEASE_TAG=$(git describe --tags --abbrev=0 | sed 's/^v//')
  docker build -t codex:${RELEASE_TAG} . --no-cache
  docker run --rm codex:${RELEASE_TAG} python -m codex --help
fi

# Step 3: Recover K8s manifest
if echo "$LANE_ERROR" | grep -iq "kubernetes"; then
  kubectl apply --dry-run=client -f .codex/k8s-manifests/
fi

# Retry Lane B
python -c "
import asyncio
from .codex.orchestrator import Lane, DeploymentGateway
gw = DeploymentGateway('v0.1.0-final-recovery')
asyncio.run(gw.execute_lane(Lane.LANE_B))
"
```

### Lane C (Security) Recovery

```bash
# Step 1: Check security failures
if jq '.message' .codex/deployment-*.jsonl | grep -iq "codeql\|security"; then
  echo "RECOVERY: Security finding - remediate"
  gh code-scanning list --state open
fi

# Step 2: Check documentation failures
if jq '.message' .codex/deployment-*.jsonl | grep -iq "doc\|link"; then
  echo "RECOVERY: Documentation - validate and fix"
  python -m codex.cli validate-docs --strict
fi

# Retry Lane C
python -c "
import asyncio
from .codex.orchestrator import Lane, DeploymentGateway
gw = DeploymentGateway('v0.1.0-final-recovery')
asyncio.run(gw.execute_lane(Lane.LANE_C))
"
```

---

## Recovery Procedure 6: Lane D Execution Failures (RP-006)

**Affected Phase:** Phase 3 (Deployment) - Lane D (Release & Publishing)  
**Failure Signal:** PyPI upload fails, GitHub release fails, package index error  
**Recovery Time:** 5-15 minutes  

### Recovery Procedure

```bash
# Step 1: Check PyPI upload failure
LANE_ERROR=$(jq 'select(.lane == "lane_d") | .message' \
  .codex/deployment-*.jsonl | tail -1)

if echo "$LANE_ERROR" | grep -iq "pypi\|twine"; then
  # Clean and rebuild
  rm -rf dist/ build/ *.egg-info/
  python -m build
  
  # Verify credentials
  [ -f ~/.pypirc ] || { echo "Missing PyPI credentials"; exit 1; }
  
  # Retry upload
  twine upload dist/* --verbose
fi

# Step 2: Check GitHub release failure
if echo "$LANE_ERROR" | grep -iq "github"; then
  RELEASE_TAG=$(git describe --tags --abbrev=0)
  gh release create $RELEASE_TAG --title "Release $RELEASE_TAG" --notes-from-tag || true
  gh release upload $RELEASE_TAG dist/* --clobber
fi

# Retry Lane D
python -c "
import asyncio
from .codex.orchestrator import Lane, DeploymentGateway
gw = DeploymentGateway('v0.1.0-final-recovery')
asyncio.run(gw.execute_lane(Lane.LANE_D))
"
```

---

## Recovery Procedure 7: Post-Merge Automation Failures (RP-007)

**Affected Phase:** Phase 4 (Post-Deployment)  
**Failure Signal:** Post-merge workflows fail, community notifications fail  
**Recovery Time:** 10-25 minutes  

```bash
# Step 1: Check workflow status
gh run list --limit 5 --json conclusion,name

# Step 2: Re-trigger post-merge automation
gh workflow run post-merge-automation.yml \
  --ref main \
  --inputs deployment_id=v0.1.0-final

# Step 3: Re-send community notifications (if needed)
python -m codex.cli notify-community \
  --deployment-id "v0.1.0-final" \
  --notify-slack
```

---

## Recovery Procedure 8: Full Rollback to Previous Version (RP-008)

**Affected Phase:** Emergency Rollback (Any Phase)  
**Failure Signal:** Critical bug, data compromise, >5 lane failures  
**Recovery Time:** 20-60 minutes  

### Full Rollback Procedure

```bash
#!/bin/bash
set -e

PREVIOUS_VERSION=$(git describe --tags --abbrev=0 --skip=1)
CURRENT_VERSION=$(git describe --tags --abbrev=0)

echo "════════════════════════════════════════════"
echo "  FULL ROLLBACK: $CURRENT_VERSION → $PREVIOUS_VERSION"
echo "════════════════════════════════════════════"

# Step 1: Freeze current deployment
echo "[1/6] Freezing deployment..."
gh run cancel --silent || true
git tag v${CURRENT_VERSION}-rolled-back

# Step 2: Revert code
echo "[2/6] Reverting code..."
git revert --no-edit HEAD
git push origin main

# Step 3: Rollback database (if applicable)
echo "[3/6] Rolling back database..."
# alembic downgrade -1 || true

# Step 4: Rollback container images
echo "[4/6] Rolling back images..."
REGISTRY="ghcr.io/aries-serpent"
PREV_TAG=${PREVIOUS_VERSION#v}
docker pull ${REGISTRY}/codex:${PREV_TAG}
docker tag ${REGISTRY}/codex:${PREV_TAG} ${REGISTRY}/codex:latest
docker push ${REGISTRY}/codex:latest

# Step 5: Rollback K8s
echo "[5/6] Rolling back Kubernetes..."
kubectl rollout undo deployment/codex -n production
kubectl rollout status deployment/codex -n production

# Step 6: Verify
echo "[6/6] Verifying..."
sleep 10
curl -s https://api.example.com/health | grep -q "ok" && echo "✅ Rollback successful" || exit 1

# Notify
gh issue create \
  --title "ROLLBACK: $CURRENT_VERSION → $PREVIOUS_VERSION" \
  --body "Full rollback completed. Investigation required." \
  --label incident,critical \
  --assignee mbaetiong

echo "════════════════════════════════════════════"
```

---

## State Verification

```bash
# Check orchestrator state
jq '.' .codex/deployment-*-checkpoint.json

# Check lane status
jq '.lanes' .codex/deployment-*-checkpoint.json

# Check production health
curl -s https://api.example.com/health
kubectl get deployment codex -n production

# Verify version
curl -s https://api.example.com/version
```

---

## Quick Reference

| Failure | Command |
|---------|---------|
| Pre-deploy checks | `.codex/scripts/deployment_prerequisites_check.sh all` |
| Lane retry | `python -c "asyncio.run(gw.execute_lane(Lane.X))"` |
| Rollback | `.codex/scripts/full-rollback.sh` |
| State check | `jq '.' .codex/deployment-*-checkpoint.json` |

---

**Version:** 1.0 | **Last Updated:** 2026-07-09 | **Contact:** @mbaetiong
