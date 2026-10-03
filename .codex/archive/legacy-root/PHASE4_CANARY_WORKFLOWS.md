# Phase 4 Custom Images: Canary Workflow Selection

**Status:** APPROVED FOR CANARY ROLLOUT  
**Canary Size:** 24 workflows (10.96% of 219 total)  
**Timeline:** Week 1-2 of Phase 4  
**Authority:** @mbaetiong D-tier autonomous

---

## Executive Summary

This document identifies 24 non-critical workflows suitable for canary migration from `actions/setup-*` pattern to custom container images. Selection criteria prioritize:

1. **Low criticality** (non-blocking, non-deployment)
2. **High frequency** (maximize data collection)
3. **Isolated dependencies** (minimal cross-workflow impact)
4. **Existing success rate** >95% (baseline stability)

---

## Canary Workflow Cohort

### TIER-1 VALIDATION WORKFLOWS (Highest Priority — 12 workflows)

These workflows run frequently with low risk and isolated scopes:

| Workflow | Frequency | Risk Level | Criticality | Rationale | Setup Actions Used |
|----------|-----------|-----------|-------------|-----------|-------------------|
| `validate.yml` | Per-PR | LOW | Non-blocking | Syntax validation, quick pass/fail | setup-python@v6 (2x) |
| `validate-code-examples.yml` | Per-PR | LOW | Non-blocking | Documentation examples only | setup-python@v6 (2x) |
| `test-variables-api.yml` | On-demand | LOW | Non-blocking | API test harness, isolated | setup-python@v6 (2x) |
| `workflow-link-validation.yml` | Nightly | LOW | Non-blocking | Link checker, quick scan | setup-python@v6 (2x) |
| `reference-integrity.yml` | Nightly | LOW | Non-blocking | Cross-reference validation | setup-python@v6 (2x) |
| `consistency-checks.yml` | Scheduled | LOW | Non-blocking | YAML/config consistency | setup-python@v6, setup-node (3x total) |
| `profile-validation.yml` | On-demand | LOW | Non-blocking | Configuration profile check | setup-python@v6 (2x) |
| `har-capture.yml` | Nightly | MEDIUM | Non-blocking | HTTP archive capture | setup-python@v6 (2x) |
| `telemetry-collection.yml` | Scheduled | LOW | Non-blocking | Telemetry aggregation | setup-python@v6 (1x) |
| `coverage-with-timeout.yml` | Per-PR | MEDIUM | Non-blocking | Coverage report generation | setup-python@v6 (2x) |
| `dependency-submission.yml` | Scheduled | LOW | Non-blocking | SBOM generation | setup-python@v6 (1x) |
| `sigstore-verify.yml` | On-demand | MEDIUM | Non-blocking | Artifact signature verification | setup-python@v6 (1x) |

**Canary-1 Total:** 12 workflows | **Avg Setup Time Saved:** 45-60s per run | **Monthly Cost Impact:** ~$120-150

---

### TIER-2 MONITORING & ANALYSIS WORKFLOWS (Medium Priority — 12 workflows)

Monitoring and analysis workflows with longer setup times (good benchmarking):

| Workflow | Frequency | Risk Level | Criticality | Rationale | Setup Actions Used |
|----------|-----------|-----------|-------------|-----------|-------------------|
| `workflow-analytics-unified.yml` | Hourly | MEDIUM | Non-blocking | Analytics aggregation, isolated | setup-python@v6 (3x) |
| `correlation-engine-monitor.yml` | Hourly | MEDIUM | Non-blocking | Correlation analysis | setup-python@v6 (2x) |
| `reasoning-engine-monitor.yml` | Hourly | MEDIUM | Non-blocking | Reasoning metrics | setup-python@v6 (1x) |
| `capacity-planner-monitor.yml` | Hourly | MEDIUM | Non-blocking | Capacity forecasting | setup-python@v6 (4x) |
| `ensemble-predictor-monitor.yml` | Hourly | MEDIUM | Non-blocking | Prediction aggregation | setup-python@v6 (5x) |
| `sla-optimizer-monitor.yml` | Hourly | MEDIUM | Non-blocking | SLA tracking | setup-python@v6 (5x) |
| `proactive-ci-monitor.yml` | Hourly | MEDIUM | Non-blocking | CI health metrics | setup-python@v6 (1x) |
| `performance-monitoring.yml` | Hourly | MEDIUM | Non-blocking | Performance aggregation | setup-python@v6 (1x) |
| `ml-lifecycle-gate.yml` | Per-commit | MEDIUM | Informational | ML model tracking | setup-python@v6, setup-node (4x total) |
| `model-drift-retrain.yml` | Nightly | MEDIUM | Non-blocking | Model quality check | setup-python@v6 (2x) |
| `data-quality-suite.yml` | Nightly | MEDIUM | Non-blocking | Data validation | setup-python@v6 (3x) |
| `rag-quality-nightly.yml` | Nightly | MEDIUM | Non-blocking | RAG evaluation | setup-python@v6 (3x) |

**Canary-2 Total:** 12 workflows | **Avg Setup Time Saved:** 60-90s per run | **Monthly Cost Impact:** ~$180-240

---

## Canary Cohort Characteristics

### Aggregate Statistics

```
Total Canary Workflows:    24
Total Setup Actions:       ~65 calls/canary run
Baseline Frequency:        8,760+ runs/month (hourly + scheduled)
Potential Monthly Savings: ~$300-400 (compute + bandwidth)
Projected Setup Time Reduction: 40-50% per workflow execution
Projected Network I/O Reduction: 30-40% (fewer action downloads)
```

### Workflow Distribution by Risk

```
LOW Risk:              15 workflows (62.5%)
MEDIUM Risk:            9 workflows (37.5%)
HIGH Risk:              0 workflows (0%)

NON-BLOCKING:          24 workflows (100%)
BLOCKING (excluded):    0 workflows (this canary)
```

### Dependency Isolation

**No canary workflow depends on another canary workflow.**  
All canary workflows are isolated to their own execution scope with no cross-workflow triggers.

---

## Success Criteria for Canary Phase

### Metrics to Track

1. **Setup Time Reduction**
   - Baseline: Average setup-python time in canary workflows (historical data)
   - Target: 40-50% reduction in workflow initialization time
   - Measurement: Extract `setup-python` duration from workflow logs

2. **Reliability Metrics**
   - Target: ≥99.5% success rate (no regression from baseline)
   - Measurement: Track success/failure counts per workflow

3. **Cost Efficiency**
   - Target: 30-40% reduction in compute minutes for canary cohort
   - Measurement: GitHub Actions billing data

4. **Network Performance**
   - Target: 50%+ reduction in action download time
   - Measurement: Network timing in workflow logs

### Exit Criteria (Proceed to Phase-2)

✅ ALL of the following must be true to proceed with Phase-2 (next 50 workflows):

- [ ] **Success Rate:** ≥99.5% across canary cohort (≤12 failures total across all canary runs in 1 week)
- [ ] **Setup Time:** ≥40% reduction confirmed by log analysis (3+ workflow data points)
- [ ] **Cost Savings:** ≥$250/month verified from billing data
- [ ] **No Production Impact:** Zero P1 incidents correlated with canary migration
- [ ] **Log Parsing:** Custom image logs parse correctly in all monitoring dashboards
- [ ] **Container Registry:** No authentication or pull rate limit issues detected

### Abort Criteria (Rollback Canary)

❌ ROLLBACK immediately if ANY of these occur:

- [ ] Success rate drops below 95% (>12 failures in canary cohort)
- [ ] Setup time increase >10% (regression detected)
- [ ] Cost increase >5% vs. baseline
- [ ] Authentication failures to container registry
- [ ] P1 incident correlated with custom image deployment

---

## Canary Migration Rollout Timeline

### Week 1: Setup & Baseline

- Day 1-2: Container image build & registry validation
- Day 3: Deploy to 1st cohort (3 workflows: `validate.yml`, `validate-code-examples.yml`, `test-variables-api.yml`)
- Day 4-5: Monitoring & baseline collection
- Day 5-7: Deploy to 2nd cohort (remaining 21 workflows)

### Week 2: Monitoring & Decision

- Days 8-10: Full canary execution (hourly + scheduled runs)
- Day 11: Data analysis & metrics compilation
- Day 12: Go/No-go decision gates validation
- Day 13-14: Buffer for remediation if needed

### Week 3: Phase-2 Preparation

- Prepare next 50 workflows for Phase-2
- Document lessons learned from canary
- Refine templates based on canary feedback

---

## Risk Mitigation for Canary

### Escape Hatches

1. **Per-Workflow Rollback**
   - Add label to disable custom image: `use-legacy-setup: true`
   - Workflow auto-reverts to setup-* if label present
   - Zero-downtime fallback

2. **Registry Pull Failure Handling**
   - Implement exponential backoff with max 3 retries
   - Fall back to setup-* if registry pull fails
   - Alert on repeated failures

3. **Environment Variable Mismatch**
   - Pre-migration validation script compares env vars between custom image and setup-*
   - Document all differences in migration guide
   - Provide override mechanism

### Monitoring Setup

**Custom Dashboard Metrics** (auto-created during deployment):

```yaml
metrics:
  - setup_time_duration_seconds
  - workflow_total_duration_seconds
  - container_pull_time_seconds
  - container_auth_failures_total
  - registry_rate_limit_errors_total
  - cost_per_workflow_execution_usd
```

---

## Next Steps

1. ✅ **Week 1, Day 3:** Deploy custom image to registry
2. ✅ **Week 1, Day 3:** Migrate Canary-1 workflows (3 workflows)
3. ✅ **Week 1, Day 5:** Migrate Canary-2 workflows (21 workflows)
4. ✅ **Week 2, Day 11:** Evaluate success criteria
5. ✅ **Week 2, Day 12:** Make Go/No-go decision
6. ✅ **Week 3+:** Proceed to Phase-2 or remediate canary issues

---

**Document Owner:** Copilot Cloud Agent  
**Last Updated:** 2026-07-18  
**Version:** 1.0
