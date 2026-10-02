# Phase 4 Custom Images: Comprehensive Rollback Procedure

**Status:** ROLLBACK PLAN APPROVED  
**Activation Authority:** D-tier autonomous (@mbaetiong) OR automated trigger  
**Implementation:** <5 minutes for full rollback  
**Authority:** @mbaetiong D-tier autonomous

---

## Executive Summary

This document defines the **automatic and manual rollback procedures** for Phase 4 Custom Images migration. Rollback can be triggered automatically by monitoring alerts or manually by authorized personnel.

**Rollback Guarantees:**
- ⏱️ Full system recovery in <5 minutes
- ✅ Zero data loss
- 🔄 Transparent to end users
- 📊 Automatic incident reporting

---

## Automatic Rollback Triggers

### Trigger 1: Setup Time Regression

**Condition:** Custom image setup time > baseline × 1.10 (10% worse)

```bash
# Monitoring check (runs every 5 minutes during canary)
CUSTOM_AVG=$(query_last_100_runs "setup_time_seconds" WHERE cohort='custom_image')
BASELINE_AVG=$(query_baseline_data "setup_time_seconds")

if [ $(bc -l <<< "$CUSTOM_AVG > $BASELINE_AVG * 1.1") -eq 1 ]; then
  echo "TRIGGER: Setup time regression detected"
  trigger_rollback "SETUP_TIME_REGRESSION"
fi
```

**Severity:** HIGH  
**Action:** Automatic rollback after 1 occurrence (no delay)

---

### Trigger 2: Success Rate Drop

**Condition:** Custom image success rate < 95%

```bash
SUCCESS_RATE=$(query_last_100_runs "success_count / total_runs" WHERE cohort='custom_image')

if [ $(bc -l <<< "$SUCCESS_RATE < 0.95") -eq 1 ]; then
  echo "TRIGGER: Success rate drop below 95%"
  trigger_rollback "LOW_SUCCESS_RATE"
fi
```

**Severity:** CRITICAL  
**Action:** Automatic immediate rollback + alert on-call

---

### Trigger 3: Container Registry Failures

**Condition:** Image pull failure rate > 0.1% (10 per 10,000 pulls)

```bash
# Monitor container registry health
PULL_FAILURES=$(grep -c "pull rate exceeded\|unauthorized\|image not found" workflow_logs)
TOTAL_PULLS=$(count_canary_runs_in_window)

FAILURE_RATE=$(bc -l <<< "$PULL_FAILURES / $TOTAL_PULLS * 100")

if [ $(bc -l <<< "$FAILURE_RATE > 0.1") -eq 1 ]; then
  echo "TRIGGER: Container registry failure rate too high"
  trigger_rollback "REGISTRY_FAILURES"
fi
```

**Severity:** CRITICAL  
**Action:** Automatic immediate rollback + page SRE team

---

### Trigger 4: Cost Anomaly

**Condition:** Daily custom image cost > baseline daily cost × 1.05 (5% more expensive)

```bash
CUSTOM_DAILY_COST=$(query_billing "date=today" WHERE cohort='custom_image')
BASELINE_DAILY_COST=$(query_baseline_billing "daily_average")

if [ $(bc -l <<< "$CUSTOM_DAILY_COST > $BASELINE_DAILY_COST * 1.05") -eq 1 ]; then
  echo "TRIGGER: Cost anomaly detected"
  trigger_rollback "COST_ANOMALY"
fi
```

**Severity:** MEDIUM  
**Action:** Alert team + manual review (wait 2 hours for human decision)

---

### Trigger 5: P1 Incident Correlation

**Condition:** P1 incident opened within 30 minutes of canary deployment OR during canary window

```bash
# Check for P1 incidents in the last 30 minutes
P1_INCIDENTS=$(gh issue list --label "p1-incident" --state "open" --created ">=$(date -d '30 minutes ago' +%Y-%m-%dT%H:%M:%S)")

if [ ! -z "$P1_INCIDENTS" ]; then
  echo "TRIGGER: P1 incident detected during canary"
  trigger_rollback "P1_INCIDENT"
fi
```

**Severity:** CRITICAL  
**Action:** Immediate rollback + escalate to on-call manager

---

### Trigger 6: Network Performance Degradation

**Condition:** Average network I/O > baseline × 1.50 (50% more bandwidth)

```bash
CUSTOM_NETWORK=$(query_metrics "network_bytes_downloaded" WHERE cohort='custom_image' LIMIT 100)
BASELINE_NETWORK=$(query_baseline_data "network_bytes_downloaded")

ACTUAL_AVG=$(python -c "import statistics; print(statistics.mean($CUSTOM_NETWORK))")
BASELINE_AVG=$(python -c "import statistics; print(statistics.mean($BASELINE_NETWORK))")

if [ $(bc -l <<< "$ACTUAL_AVG > $BASELINE_AVG * 1.5") -eq 1 ]; then
  echo "TRIGGER: Network performance degradation"
  trigger_rollback "NETWORK_DEGRADATION"
fi
```

**Severity:** MEDIUM  
**Action:** Alert team + wait for manual decision (4-hour review window)

---

## Manual Rollback Triggers

### Trigger 7: Manual Request (Authorized Personnel)

**Authority:** 
- @mbaetiong (repo owner)
- On-call SRE engineer
- Copilot Cloud Agent (D-tier autonomous)

**Procedure:**

```bash
# Option 1: Via GitHub issue
gh issue create \
  --title "ROLLBACK: Phase 4 Custom Images — Manual Request" \
  --body "Reason: [reason_here]\nRequester: [name]" \
  --label "p1-incident,phase4-rollback"

# Option 2: Via chat/Slack (if issue creation unavailable)
# Post message to #incidents channel with reason and authority

# Option 3: Via script (D-tier autonomous only)
python scripts/phase4/trigger_rollback.py --reason="[reason]" --authority="autonomous"
```

**Severity:** DEPENDS  
**Action:** Rollback after 1-minute review window (allow for abort if false alarm)

---

### Trigger 8: Scheduled Maintenance Window

**Timing:** Friday 02:00 UTC (low-traffic window)

**Procedure:**

```bash
# If canary week overlaps maintenance window, rollback before maintenance
if date_matches("Friday 02:00 UTC +/- 4 hours"); then
  trigger_rollback "SCHEDULED_MAINTENANCE"
fi
```

**Severity:** LOW  
**Action:** Scheduled rollback (no emergency protocol)

---

## Rollback Execution Procedures

### QUICK ROLLBACK (Per-Workflow, <5 min)

**Use Case:** One specific canary workflow is failing

**Steps:**

1. **Identify failing workflow**
   ```bash
   FAILING_WORKFLOW="validate.yml"  # Example
   ```

2. **Set fallback flag in workflow**
   ```bash
   # Edit workflow file: .github/workflows/validate.yml
   
   # Add/modify step:
   - name: "Disable custom image"
     run: echo "PHASE4_MIGRATION=disabled" >> $GITHUB_ENV
   
   # OR set label:
   # Add label to job:
   if: !contains(github.event.inputs.use_legacy_setup, 'true')
   ```

3. **Commit and push**
   ```bash
   git add .github/workflows/validate.yml
   git commit -m "phase4: temporary fallback for validate.yml"
   git push origin current-branch
   ```

4. **Monitor next run**
   - Workflow should execute with legacy setup-* pattern
   - Verify success in next scheduled run
   - Check cost returned to baseline

5. **Restore custom image** (after root cause analysis)
   ```bash
   # Re-enable custom image:
   git revert [commit_hash]
   git push origin current-branch
   ```

**Rollback Time:** ~3-5 minutes

---

### FULL CANARY ROLLBACK (All 24 workflows, <5 min)

**Use Case:** Multiple canary workflows failing OR performance degradation across cohort

**Steps:**

1. **Prepare rollback commit**
   ```bash
   # Checkout all 24 canary workflow files
   for workflow in \
     validate.yml \
     validate-code-examples.yml \
     test-variables-api.yml \
     workflow-link-validation.yml \
     reference-integrity.yml \
     consistency-checks.yml \
     profile-validation.yml \
     har-capture.yml \
     telemetry-collection.yml \
     coverage-with-timeout.yml \
     dependency-submission.yml \
     sigstore-verify.yml \
     workflow-analytics-unified.yml \
     correlation-engine-monitor.yml \
     reasoning-engine-monitor.yml \
     capacity-planner-monitor.yml \
     ensemble-predictor-monitor.yml \
     sla-optimizer-monitor.yml \
     proactive-ci-monitor.yml \
     performance-monitoring.yml \
     ml-lifecycle-gate.yml \
     model-drift-retrain.yml \
     data-quality-suite.yml \
     rag-quality-nightly.yml; do
     
     # For each workflow: remove container definition, restore setup-* steps
     git checkout HEAD -- ".github/workflows/$workflow"
   done
   ```

2. **Verify rollback commit**
   ```bash
   # Ensure all 24 workflows use legacy setup-* pattern
   grep -r "actions/setup-python\|actions/setup-node" .github/workflows/ | \
     wc -l  # Should show 24+ occurrences
   
   # Ensure no custom image definitions remain
   grep -r "container:" .github/workflows/ | \
     grep -v "# container:" | \
     wc -l  # Should be 0
   ```

3. **Push rollback immediately**
   ```bash
   git commit -m "phase4: ROLLBACK canary workflows to legacy pattern

   - Reason: [automatic_trigger_reason]
   - 24 workflows reverted to actions/setup-* pattern
   - Emergency rollback completed at [timestamp]
   - Monitoring threshold: [threshold_value] exceeded
   "
   
   git push origin current-branch --force-with-lease
   ```

4. **Monitor post-rollback**
   - All canary workflows should resume legacy pattern within 5 minutes
   - Verify cost returned to baseline
   - Check success rate returned to >99.5%
   - Confirm no errors in latest runs

5. **Root cause analysis**
   ```bash
   # Investigate what triggered rollback
   
   # If setup time regression:
   docker image inspect ghcr.io/aries-serpent/codex-python-3.12:latest-slim
   
   # If registry failures:
   gh api rate_limit  # Check GitHub rate limits
   curl -I https://ghcr.io/token  # Check registry health
   
   # If cost anomaly:
   gh api repos/Aries-Serpent/_codex_/actions/runners  # Check runner configuration
   ```

**Rollback Time:** <5 minutes (push to all canary runs using legacy pattern immediately)

---

### FULL PHASE-4 ROLLBACK (All 219 workflows, ~30 min)

**Use Case:** Fundamental issue with custom images (e.g., container registry permanently unavailable)

**Steps:**

1. **Declare emergency**
   ```bash
   # Create high-priority incident issue
   gh issue create \
     --title "PHASE 4 EMERGENCY ROLLBACK: Container Registry Unavailable" \
     --body "Full Phase 4 rollback in progress due to registry failure" \
     --label "p1-incident,emergency,phase4"
   ```

2. **Disable Phase 4 globally**
   ```bash
   # Set repo variable to disable all Phase 4 workflows
   gh variable set CODEX_PHASE4_CUSTOM_IMAGES_ENABLED --body "disabled"
   ```

3. **Trigger rollback for all active workflows**
   ```bash
   # Run rollback script for all 219 workflows
   python scripts/phase4/rollback_all_workflows.py
   
   # This script:
   # - Reverts all workflow files to pre-migration state
   # - Removes all container definitions
   # - Restores all actions/setup-* steps
   # - Creates single rollback commit
   ```

4. **Push emergency fix**
   ```bash
   git commit -m "EMERGENCY: Phase 4 rollback — all 219 workflows

   - Full rollback to legacy actions/setup-* pattern
   - CODEX_PHASE4_CUSTOM_IMAGES_ENABLED=disabled
   - Reason: Container registry permanent failure
   - All workflows reverted to pre-Phase-4 state
   - Deployed at [timestamp] by [authority]
   "
   
   git push origin current-branch --force-with-lease
   ```

5. **Verify full rollback**
   ```bash
   # Ensure all workflows use legacy pattern
   grep -r "container:" .github/workflows/ | grep -v "# container:" | wc -l
   # Should show 0
   
   # Ensure all setup-* actions present
   grep -r "actions/setup-" .github/workflows/ | wc -l
   # Should show 165+ (setup-python, setup-node, etc.)
   ```

6. **Communicate rollback status**
   ```bash
   # Post status in incidents channel
   # Expected: All 219 workflows resume legacy pattern within 15 minutes
   # Cost: Return to baseline (~$2,000-2,500/month)
   ```

**Rollback Time:** 20-30 minutes (comprehensive verification required)

---

## Version Pinning Strategy

### Container Image Versioning

**Format:** `ghcr.io/aries-serpent/codex-python-3.12:VERSION`

```
Version Schema:
  - latest-slim         # Auto-update to latest stable slim build
  - latest              # Auto-update to latest full build
  - latest-debug        # Auto-update to latest debug build
  - v1.0.0-slim         # Specific release version (for canary)
  - v1.0.0              # Specific release version (full)
  - main-ubuntu-2404    # Development build (branch-specific)
```

**Pinning Strategy:**

```yaml
# Canary Phase (Week 1-2): PIN to specific version for rollback control
container:
  image: ghcr.io/aries-serpent/codex-python-3.12:v1.0.0-slim
  # Allows immediate revert to v1.0.0 if issues detected

# Phase-2 (Week 3+): Switch to latest-slim (auto-update)
container:
  image: ghcr.io/aries-serpent/codex-python-3.12:latest-slim
  # Automatically gets latest security patches, performance improvements
```

**Rollback via Version Pin:**

```bash
# If issues detected with latest-slim, immediately revert to v1.0.0-slim
sed -i 's/:latest-slim/:v1.0.0-slim/g' .github/workflows/*.yml
git commit -m "phase4: rollback to v1.0.0-slim"
git push
```

---

## Disaster Recovery Procedures

### DR Scenario 1: Container Registry Down (Network Isolation)

**Symptoms:**
- Image pull timeout (>30s)
- "Connection refused" errors in workflow logs
- All canary workflows stuck at "Waiting for runner"

**Recovery Steps:**

1. **Immediate action:** Fallback to legacy setup-*
   ```bash
   # Trigger automatic rollback (already configured)
   # Workflows will use built-in fallback job
   ```

2. **Container registry restoration:**
   ```bash
   # Check registry status
   curl -I https://ghcr.io/
   
   # If GitHub Container Registry is down:
   # - Switch to alternative registry (Docker Hub, ECR)
   # - Update all workflow files with new registry
   # - Re-push custom images to alternative
   ```

3. **Resume Phase 4:**
   ```bash
   # Once registry restored and verified:
   git revert [rollback_commit]
   git push
   ```

**Recovery Time:** 15-30 minutes (depending on registry availability)

---

### DR Scenario 2: Corrupted Container Image

**Symptoms:**
- Tool version mismatch (e.g., Python 3.11 instead of 3.12)
- Missing dependencies (pip, setuptools not in PATH)
- Permission errors (workflow can't write to /tmp)

**Recovery Steps:**

1. **Identify corruption**
   ```bash
   # Check image history and recent builds
   docker history ghcr.io/aries-serpent/codex-python-3.12:latest-slim
   
   # Verify image layers
   docker image inspect ghcr.io/aries-serpent/codex-python-3.12:latest-slim
   ```

2. **Rebuild image**
   ```bash
   # Rebuild from Dockerfile
   cd .github/actions/container-build
   docker build -t ghcr.io/aries-serpent/codex-python-3.12:v1.0.1-slim -f Dockerfile.python-3.12 .
   docker push ghcr.io/aries-serpent/codex-python-3.12:v1.0.1-slim
   ```

3. **Switch to new image version**
   ```bash
   sed -i 's/:latest-slim/:v1.0.1-slim/g' .github/workflows/*.yml
   git commit -m "phase4: use fixed image v1.0.1-slim"
   git push
   ```

**Recovery Time:** 20-40 minutes (rebuild + deployment)

---

### DR Scenario 3: Runner Out of Disk Space (Container Image Size Issue)

**Symptoms:**
- "No space left on device" errors
- Docker pull failures mid-extraction
- Workflows timeout during image pull

**Recovery Steps:**

1. **Check runner disk space**
   ```bash
   df -h /  # Check root partition
   docker images | grep codex  # Check image sizes
   ```

2. **Use slim image variant**
   ```bash
   # Switch from full (~500MB) to slim (~200MB)
   sed -i 's/:latest/:latest-slim/g' .github/workflows/*.yml
   git commit -m "phase4: use slim image to reduce disk usage"
   git push
   ```

3. **Clean up old images on runner**
   ```bash
   # GitHub Actions runner self-cleanup:
   # - Automatically removes images older than 7 days
   # - Clears cache every 24 hours
   # (No manual action needed)
   ```

**Recovery Time:** 5-10 minutes (image switch)

---

## Testing Rollback Before Production

### Rollback Test Plan (Pre-Canary)

**Objective:** Verify all rollback procedures work correctly

**Test Steps:**

```bash
# 1. Test automatic trigger simulation
pytest tests/phase4/test_rollback_triggers.py -v

# 2. Test quick rollback (single workflow)
python scripts/phase4/test_quick_rollback.py --workflow validate.yml

# 3. Test full canary rollback
python scripts/phase4/test_full_rollback.py --workflows-count 24

# 4. Test disaster recovery scenarios
pytest tests/phase4/test_dr_scenarios.py -v
  # Includes:
  # - Registry down
  # - Corrupted image
  # - Disk space issues
  # - Network timeout
```

**Expected Results:**
- ✅ All rollback procedures complete in <5 minutes
- ✅ Workflows return to legacy setup-* pattern
- ✅ No data loss
- ✅ Cost returns to baseline
- ✅ Incident reports auto-generated

---

## Rollback Communication Protocol

### Automated Notifications

**When rollback triggers automatically:**

```yaml
Notification Channels:
  - GitHub Issue: Create P1 issue with rollback reason
  - Slack: Post to #incidents with severity + reason
  - Email: Alert on-call engineer
  - PagerDuty: Alert if P1 incident + rollback
  - Metrics Dashboard: Flag rollback event + timestamp
```

**Notification Template:**

```markdown
🚨 PHASE 4 ROLLBACK ACTIVATED

**Trigger:** [ROLLBACK_REASON]
**Time:** [TIMESTAMP]
**Workflows Affected:** [N workflows]
**Status:** In progress (ETA 5 minutes for full rollback)

**What happened:**
- [1-2 sentence explanation]

**Action taken:**
- [Automatic rollback to legacy pattern]
- [All workflows reverted]

**Next steps:**
1. Investigate root cause
2. Fix issue
3. Re-deploy canary

**Questions?** Contact: [on-call engineer]
```

---

## Post-Rollback Procedures

### After Any Rollback

1. **Root cause analysis** (within 2 hours)
   - [ ] Identify what triggered rollback
   - [ ] Document findings
   - [ ] Create remediation plan

2. **Fix issues** (within 24 hours)
   - [ ] Update container image
   - [ ] Update workflow templates
   - [ ] Re-test before re-deployment

3. **Re-deployment** (within 48 hours or reschedule)
   - [ ] Deploy fixed version
   - [ ] Start with smaller cohort (5-10 workflows)
   - [ ] Monitor closely

4. **Lessons learned**
   - [ ] Document what failed
   - [ ] Update this procedure
   - [ ] Add new automatic triggers if needed

---

## Version Control & Audit Trail

### Rollback Audit Log

```
.codex/phase4/rollback_audit.log

Format: [TIMESTAMP] [TRIGGER] [AUTHORITY] [RESULT] [RECOVERY_TIME]

Example entries:
2026-07-18T14:32:00Z [SETUP_TIME_REGRESSION] [AUTOMATIC] [SUCCESS] 4m15s
2026-07-18T09:15:00Z [MANUAL_REQUEST] [mbaetiong] [SUCCESS] 3m42s
2026-07-17T23:45:00Z [REGISTRY_FAILURE] [AUTOMATIC] [SUCCESS] 5m00s
```

### Git Commit History

All rollback commits are tagged for easy reference:

```bash
git tag -l phase4/rollback/*

# Review all rollbacks
git log --grep="ROLLBACK" --oneline | head -20
```

---

## Key Contacts

**On-Call SRE:** [SRE_ENGINEER_NAME]  
**Repository Owner:** @mbaetiong  
**Cloud Infrastructure Team:** [CONTACT_EMAIL]  
**Container Registry Admin:** [CONTACT_EMAIL]

---

**Document Owner:** Copilot Cloud Agent  
**Last Updated:** 2026-07-18  
**Version:** 1.0
