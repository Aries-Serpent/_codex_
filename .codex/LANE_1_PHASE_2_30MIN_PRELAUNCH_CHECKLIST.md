# LANE 1 PHASE 2 - 30-MINUTE PRE-LAUNCH CHECKLIST

**Execute at:** 2026-07-20T01:30:00Z (30 minutes before Phase 2 launch)

---

## ✅ PRE-LAUNCH VERIFICATION STEPS

### Step 1: Verify All Preconditions (PRODUCTION_TRAFFIC_RAMP_FRAMEWORK.md §2)

**Confirm:**
- [ ] Phase 1 GitHub Release marked complete (check release notes)
- [ ] v0.2.0 release artifact checksum verified (compare against release artifact)
- [ ] Rollback target (v0.1.0-final) warm and health-checked (verify via load balancer)
- [ ] Load balancer / ingress weight change path validated (test control path)
- [ ] Phase 12 monitoring dashboards live (check all 13 metric dashboards)
- [ ] Incident commander and on-call coverage confirmed (@mbaetiong + tier-2 on-call)
- [ ] Database replicas healthy; replication lag <100ms baseline (check metrics)
- [ ] Cache layer healthy; cache hit rate ≥97% baseline (check metrics)
- [ ] Telemetry pipeline healthy; metric drop rate 0% (verify ingestion)

**If ANY precondition is not met:** STOP and escalate to @mbaetiong immediately.

### Step 2: Record Pre-Ramp Baseline Metrics

Create a baseline snapshot in the execution report template:

```markdown
## Pre-Ramp Baseline (Recorded at 2026-07-20T01:50:00Z)

| Metric | Baseline Value | Unit | Notes |
|--------|---|---|---|
| Request rate (RPS) | [fill] | req/s | |
| Error rate (%) | [fill] | % | Current value from v0.1.0-final |
| Latency p50 (ms) | [fill] | ms | |
| Latency p95 (ms) | [fill] | ms | Record for Stage 1 variance comparison |
| Latency p99 (ms) | [fill] | ms | Target: <750ms PASS threshold |
| CPU utilization (%) | [fill] | % | |
| Memory utilization (%) | [fill] | % | |
| Cache hit rate (%) | [fill] | % | Expected: ≥97% |
| DB connections active | [fill] | conn | |
| DB replication lag (ms) | [fill] | ms | Expected: <100ms |
| Healthy instances | [fill] / 32 | % | Expected: 100% |
| Active Sev-1/2 incidents | [fill] | count | Expected: 0 |
| Telemetry coverage | [fill] | % | Expected: 100% |
```

**Action:** Retrieve these from live dashboards and record in `.codex/PRODUCTION_RAMP_EXECUTION_REPORT.md`.

### Step 3: Annotate All Dashboards

Add dashboard annotations:
- **Tag:** `stage=0-baseline` (pre-ramp)
- **Timestamp:** 2026-07-20T01:50:00Z
- **Event:** "Phase 2 production traffic ramp starting in 10 minutes"

This creates a clear visual marker on all time-series graphs.

### Step 4: Notify Incident Commander

**Send to @mbaetiong:**

> @mbaetiong — Phase 2 production traffic ramp launching in 10 minutes (2026-07-20T02:00:00Z).
> 
> **Pre-launch verification:** All preconditions armed ✅  
> **Baseline metrics:** Recorded and archived  
> **Gate 1 target:** Stage 1 PASS/HOLD/FAIL decision at 2026-07-20T02:30:00Z (+30m)  
> **Escalation threshold:** HOLD >30m or any FAIL → immediate escalation  
> 
> Executing per PRODUCTION_TRAFFIC_RAMP_FRAMEWORK.md. Will update orchestration coordination artifact on gate decisions.

### Step 5: Confirm Phase 3 (Incident Response) Armed

Verify with phase-12-incident-coordinator or ci-emergency-response-agent:
- [ ] Incident dashboards standing by
- [ ] Alerting rules active and paging hot
- [ ] On-call schedule verified
- [ ] SLA timers armed (<30s Sev-1 acknowledgment)
- [ ] Runbook links accessible

If Phase 3 is NOT ready, DELAY Phase 2 launch and escalate.

### Step 6: Final Systems Check

- [ ] Load balancer weight control system responsive
- [ ] Monitoring scraper polling data successfully
- [ ] Log aggregation pipeline ingesting cleanly
- [ ] No ongoing incidents or maintenance windows
- [ ] Network path to production load balancers clear

---

## 🚀 GO/NO-GO DECISION

At 2026-07-20T01:50:00Z, make final GO/NO-GO decision:

**GO** if:
- All preconditions verified ✅
- All baseline metrics recorded ✅
- Dashboards annotated ✅
- Incident commander notified ✅
- Phase 3 confirmed armed ✅
- All systems checks passed ✅

**NO-GO** if:
- Any precondition not met
- Any baseline metric unavailable
- Phase 3 not armed
- Incident or maintenance window active
- Any systems check failed

---

## 📋 IMMEDIATE NEXT ACTIONS (If GO)

1. **At 2026-07-20T02:00:00Z:** Execute Stage 1 load balancer shift (0% → 10% v0.2.0)
2. **Observe for 30 minutes:** Collect metrics at 5m, 15m, 30m checkpoints
3. **At 2026-07-20T02:30:00Z:** Evaluate Stage 1 gate (PASS / HOLD / FAIL)
4. **Record decision** in execution report with timestamp and reasoning
5. **Advance** to next stage or escalate per gate outcome

---

**Pre-Launch Checklist Status:** [TO BE COMPLETED AT T-1]  
**Scheduled Execution:** 2026-07-20T02:00:00Z  
**Expected Completion:** 2026-07-20T08:00:00Z (~6 hours)

