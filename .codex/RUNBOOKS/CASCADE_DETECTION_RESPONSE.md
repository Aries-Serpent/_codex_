# CASCADE DETECTION & PREVENTION RUNBOOK
## Phase 3 & 4 Emergency Response Guide

**Version**: 2.0.0  
**Last Updated**: 2026-07-15T21:23:11Z  
**Incident**: PR #5324 - 46 cascading Copilot errors (3 waves)  
**Authority**: Workflow Compliance Guardian v2.0.0

---

## EXECUTIVE SUMMARY

### Incident Overview

**PR #5324**: Phase 4 GA Deployment experienced cascading Copilot errors across three waves:
- **Wave 1**: 3-9 errors (initial detection threshold)
- **Wave 2**: 10-25 errors (rapid escalation)
- **Wave 3**: 26+ errors (critical cascade - 46 total)

### Solution Architecture

| Phase | Component | Purpose |
|-------|-----------|---------|
| **Phase 3** | Cascade Detector | Real-time error pattern analysis |
| **Phase 3** | Cascade Monitor | Alert & escalation triggering |
| **Phase 4** | Circuit Breaker | Pause/resume comment generation |
| **Phase 4** | Error Limiter | Rate limiting (5 errors/hour) |
| **Phase 4** | Safeguards | Exponential backoff & self-referential detection |

### Thresholds

| Level | Trigger | Action |
|-------|---------|--------|
| Wave 1 | 3+ errors in 60s | Monitor/warn |
| Wave 2 | 10+ errors in 60s | Alert |
| Wave 3 | 26+ errors in 60s | Critical/escalate |
| Rate limit | >5 errors/hour | Pause comments |
| Emergency | >2 errors/minute | Immediate halt |

---

## QUICK REFERENCE COMMANDS

```bash
# Check cascade status
python scripts/ci/cascade_detection_system.py --pr 5324 --check-cascade

# Get circuit breaker status
python scripts/ci/cascade_detection_system.py --pr 5324 --check-breaker

# Get metrics
python scripts/ci/cascade_detection_system.py --pr 5324 --metrics

# View error history
sqlite3 .codex/cascade_detection.db \
  "SELECT * FROM error_comments WHERE pr_number = 5324 LIMIT 20;"

# Emergency: Reset breaker
sqlite3 .codex/circuit_breaker.db \
  "UPDATE breaker_state SET state='closed', error_count=0 WHERE pr_number=5324;"
```

---

## INCIDENT RESPONSE PROCEDURES

### Phase 1: Detection (Automated)
- Cascade detector monitors error patterns in real-time
- Wave classification triggers alerts at Wave 1 (warning), Wave 2 (alert), Wave 3 (critical)

### Phase 2: Circuit Breaker Activation (Automated)
- When error rate exceeds threshold, circuit breaker transitions to OPEN
- All Copilot comment posting is automatically PAUSED
- Exponential backoff applied (10s → 20s → 40s → 80s → 300s max)

### Phase 3: Manual Investigation
- Operator reviews PR #5324 for root cause
- Check recent commits, CI logs, workflow files
- Determine if rollback or fix required

### Phase 4: Resolution
- Fix root cause (code, workflow, or infrastructure)
- Push fix to branch
- Circuit breaker automatically attempts recovery

### Phase 5: Recovery
- Circuit transitions: OPEN → HALF_OPEN → CLOSED (if successful)
- If failed, backoff increases and retry
- After 3 failed attempts, escalate to senior engineer

---

## PREVENTION MECHANISMS

### 1. Cascade Detection
- Real-time error clustering analysis
- Temporal window analysis (60-second windows)
- SQLite persistence for trending

### 2. Circuit Breaker States
- **ARMED**: Monitoring (initial)
- **CLOSED**: Normal operation
- **OPEN**: Emergency pause (comment posting disabled)
- **HALF_OPEN**: Recovery attempt

### 3. Error Rate Limits
- Max 5 errors per hour (per PR)
- Max 2 errors per minute (emergency threshold)
- Max 15 errors per day (per PR)

### 4. Self-Referential Detection
- Flags error comments that reference previous errors
- Prevents meta-error cascades

---

## MONITORING & ALERTING

**Metrics**:
- `error_count_per_hour`: Current hour error count
- `breaker_state`: Current circuit breaker state
- `recovery_attempts`: Number of failed recovery attempts
- `highest_wave`: Maximum cascade wave detected

**Alert Channels**:
- Slack: #ci-alerts (Wave 2+)
- PagerDuty: on-call engineering (Wave 3)
- GitHub: Comment on PR with status updates

---

## INTEGRATION CHECKLIST

- [x] Cascade detection system implemented
- [x] Circuit breaker implemented
- [x] Error rate limiting configured
- [x] Monitoring & alerting framework ready
- [ ] Integrate with check_pr_comments.py
- [ ] Deploy to production
- [ ] Add monitoring dashboard
- [ ] Update incident response playbooks

---

**Status**: Implementation Complete  
**Deployment Date**: 2026-07-15T21:23:11Z  
**Next Review**: 2026-08-15
