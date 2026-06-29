# PHASE 9.3 PARALLEL DEPLOYMENT PLAN

**Date:** 2026-06-22  
**Track:** Phase 9.3 (Multi-Agent Parallel Execution)  
**Scope:** Canary → Regional → Full Rollout (3 phases over 3 days)  
**Status:** Ready for Deployment

---

## EXECUTIVE SUMMARY

This document outlines the phased deployment strategy for the semantic routing engine (Task 9.3.2) and parallel agent queuing system (Task 9.3.3-9.3.4). The rollout uses a 3-phase approach with strict SLA monitoring and kill switches to minimize risk.

**Timeline:**
- **Day 1 (Jun 23):** Canary deployment (5% traffic, <0.5% error threshold)
- **Day 2 (Jun 24):** Regional deployment (25% traffic, <1% error threshold)
- **Day 3+ (Jun 25+):** Full deployment (100% traffic, <0.5% error threshold)

**Go/No-Go Criteria:**
- ✅ 95%+ routing accuracy (measured on 1000+ test queries)
- ✅ <500ms p99 routing latency
- ✅ 100 concurrent PRs with stable performance
- ✅ Zero deadlocks or circular dependency failures
- ✅ All canary metrics passing for 12h minimum

---

## 1. PRE-DEPLOYMENT CHECKLIST

### 1.1 Code Readiness
- [ ] All 6 components implemented and tested
  - [ ] Task 9.3.1: Capability index built (.codex/PHASE_9_3_CAPABILITY_INDEX.json)
  - [ ] Task 9.3.2: Semantic router deployed (scripts/ci/phase_9_3_semantic_router.py)
  - [ ] Task 9.3.3: Queue manager deployed (scripts/ci/phase_9_3_agent_queue_manager.py)
  - [ ] Task 9.3.4: Workload balancer deployed (scripts/ci/phase_9_3_workload_balancer.py)
  - [ ] Task 9.3.5: Stress tests passing (4/6 minimum)
  - [ ] Documentation complete (.codex/PHASE_9_3_*.md)

### 1.2 Infrastructure Readiness
- [ ] GitHub Actions runners provisioned (m-class, 8 vCPU minimum)
- [ ] Database prepared (SQLite for routing cache + metrics)
- [ ] Monitoring dashboards deployed
- [ ] Logging infrastructure ready (CloudWatch/DataDog)
- [ ] Alert channels configured (PagerDuty, Slack)
- [ ] Kill switch controls tested
- [ ] Rollback procedures documented

### 1.3 Stakeholder Sign-Off
- [ ] Product: Requirements met
- [ ] SRE: Infrastructure approved
- [ ] Security: No vulnerabilities found
- [ ] Platform: Integration points verified
- [ ] @mbaetiong: D-tier approval obtained

### 1.4 Metrics Baseline
- [ ] Current state captured:
  - [ ] Existing routing latency (p50/p95/p99)
  - [ ] Agent utilization baseline
  - [ ] Error rate baseline
  - [ ] PR merge time baseline

---

## 2. PHASE 1: CANARY DEPLOYMENT (Day 1)

### 2.1 Traffic Allocation
```
Production CI Runs
    ↓
    ├─ 5% → NEW ROUTING ENGINE (experimental)
    └─ 95% → EXISTING SEQUENTIAL ROUTER (stable)
```

### 2.2 Deployment Steps

**Step 1: Feature Flag Activation**
```bash
export PARALLEL_ROUTING_ENABLED=true
export PARALLEL_ROUTING_TRAFFIC_PERCENTAGE=5
export PARALLEL_ROUTING_FALLBACK_TO_SEQUENTIAL=true  # Fallback on error
```

**Step 2: Deploy Router Components**
```bash
# Deploy to Lambda/ECS (or GitHub Actions runner group)
docker build -t codex-router:9.3 -f Dockerfile.router .
docker push codex-router:9.3

# Provision 1-2 router instances for 5% traffic
```

**Step 3: Enable Monitoring**
```bash
# Deploy CloudWatch dashboards
# Configure Datadog APM
# Enable CloudTrail logging
# Send metrics to time-series DB
```

**Step 4: Verify Startup**
```
✓ Capability index loaded (145 agents)
✓ FAISS index ready (if enabled)
✓ Routing cache initialized (1h TTL)
✓ Metrics collector running
✓ Health checks passing
```

### 2.3 SLA Thresholds (Canary)

| Metric | Target | Action on Breach |
|--------|--------|-----------------|
| Routing Latency (p99) | <500ms | Escalate to on-call |
| Routing Accuracy | ≥95% | Investigate false negatives |
| Error Rate | <0.5% | Trigger rollback |
| Agent Utilization | ±20% std dev | Load balancer tuning |
| Cache Hit Rate | >40% | Verify cache working |
| Deadlocks Detected | 0 | IMMEDIATE ROLLBACK |

### 2.4 Monitoring Queries

```sql
-- Routing latency distribution
SELECT
  percentile_cont(0.50) WITHIN GROUP (ORDER BY latency_ms) as p50,
  percentile_cont(0.95) WITHIN GROUP (ORDER BY latency_ms) as p95,
  percentile_cont(0.99) WITHIN GROUP (ORDER BY latency_ms) as p99
FROM routing_decisions
WHERE created_at > now() - interval 1 hour;

-- Error rate
SELECT
  COUNT(*) as total,
  COUNT(*) FILTER (WHERE success = false) as failures,
  COUNT(*) FILTER (WHERE success = false)::float / COUNT(*) * 100 as error_rate_pct
FROM routing_decisions
WHERE created_at > now() - interval 1 hour;

-- Accuracy (correct agent selected)
SELECT
  COUNT(*) as total_decisions,
  COUNT(*) FILTER (WHERE accuracy = 1.0) as correct,
  COUNT(*) FILTER (WHERE accuracy = 1.0)::float / COUNT(*) * 100 as accuracy_pct
FROM routing_decisions
WHERE created_at > now() - interval 1 hour;

-- Agent load distribution
SELECT
  agent_id,
  COUNT(*) as tasks_assigned,
  AVG(queue_depth) as avg_queue,
  STDDEV(queue_depth) as queue_stddev
FROM routing_assignments
WHERE created_at > now() - interval 1 hour
GROUP BY agent_id;
```

### 2.5 Canary Duration & Decision
- **Duration:** 12 hours minimum
- **Go Criteria:** All SLA thresholds met for full 12h
- **No-Go Criteria:** Any SLA breach during monitoring period
- **Decision Window:** 12:00 UTC Day 1 (after 12h monitoring)

### 2.6 Canary Rollback (if needed)
```bash
# Immediate rollback to sequential router
export PARALLEL_ROUTING_ENABLED=false
export PARALLEL_ROUTING_FALLBACK_TO_SEQUENTIAL=true

# Drain in-flight routing requests (max 5 min timeout)
# Wait for graceful shutdown
# Verify sequential router serving 100% traffic
# Post-mortem: Analyze logs for root cause
```

---

## 3. PHASE 2: REGIONAL DEPLOYMENT (Day 2)

**Prerequisite:** Canary canary passing for 12h ✓

### 3.1 Traffic Allocation
```
Production CI Runs
    ↓
    ├─ 25% → NEW ROUTING ENGINE (expanding)
    └─ 75% → EXISTING SEQUENTIAL ROUTER (fallback)
```

### 3.2 Deployment Steps

**Step 1: Scale Router Instances**
```bash
# Provision 4-5 router instances for 25% traffic
# Verify load balancing across instances
# Health checks on all instances
```

**Step 2: Update Monitoring Thresholds**
```
Error rate threshold: <1% (increased from 0.5%)
Other thresholds unchanged
```

**Step 3: Monitor for 6 Hours**
- Extended monitoring window (6h minimum)
- Gradual traffic shift (5% → 10% → 15% → 25% over 1h)
- Continuous SLA verification

### 3.3 SLA Thresholds (Regional)

| Metric | Target | Action on Breach |
|--------|--------|-----------------|
| Routing Latency (p99) | <500ms | Investigate |
| Routing Accuracy | ≥95% | Investigate |
| Error Rate | <1% | Escalate (higher threshold for expansion) |
| Deadlocks Detected | 0 | IMMEDIATE ROLLBACK |

### 3.4 Regional Decision
- **Duration:** 6 hours minimum on 25% traffic
- **Go Criteria:** All SLA thresholds met
- **No-Go Criteria:** Any breach or escalation needed
- **Decision Window:** 18:00 UTC Day 2 (after 6h monitoring)

---

## 4. PHASE 3: FULL DEPLOYMENT (Day 3+)

**Prerequisite:** Regional deployment passing for 6h ✓

### 4.1 Traffic Allocation
```
Production CI Runs
    ↓
    └─ 100% → NEW ROUTING ENGINE (full rollout)
```

### 4.2 Deployment Steps

**Step 1: Scale to Full Capacity**
```bash
# Provision router instances for 100% traffic
# Typically: 8-12 instances depending on throughput
# Enable auto-scaling rules
```

**Step 2: Disable Sequential Fallback**
```bash
export PARALLEL_ROUTING_FALLBACK_TO_SEQUENTIAL=false
export PARALLEL_ROUTING_ENABLED=true
```

**Step 3: Monitor Continuously**
- 24/7 monitoring (at least 1 week)
- Daily automated reports to platform team
- Weekly review with @mbaetiong

### 4.3 SLA Thresholds (Production)

| Metric | Target | Action on Breach |
|--------|--------|-----------------|
| Routing Latency (p99) | <500ms | Tuning required |
| Routing Accuracy | ≥95% | Investigation required |
| Error Rate | <0.5% | Escalation to SRE |
| Deadlocks Detected | 0 | IMMEDIATE ROLLBACK |
| Agent Utilization | ±20% std dev | Rebalancing needed |

### 4.4 Production Rollout Decision
- **Duration:** 7 days minimum
- **Go Criteria:** All SLA thresholds met + no user complaints
- **Success Criteria:** Officially sunset sequential router after 2 weeks stable

---

## 5. KILL SWITCHES & EMERGENCY PROCEDURES

### 5.1 Feature Flags

```python
# .github/runners/router_config.yaml
PARALLEL_ROUTING_ENABLED: boolean
  - true: Route tasks to semantic engine
  - false: Fallback to sequential router

PARALLEL_ROUTING_TRAFFIC_PERCENTAGE: 0-100
  - 5 (canary), 25 (regional), 100 (full)

PARALLEL_ROUTING_FALLBACK_TO_SEQUENTIAL: boolean
  - true: Any error → fallback to sequential
  - false: Any error → fail fast

PARALLEL_ROUTING_CACHE_ENABLED: boolean
  - true: Use 1h TTL cache
  - false: Bypass cache (for debugging)

PARALLEL_ROUTING_LATENCY_SLA_MS: number
  - 500 (default), 1000 (relaxed SLA during debugging)
```

### 5.2 Emergency Rollback Procedure

**Trigger:** Any of:
- Error rate > SLA threshold for >5 min
- Deadlock detected
- Agent utilization > 95% for >10 min
- P99 latency > 2x SLA for >5 min

**Steps:**
```bash
# Step 1: Enable fallback to sequential
export PARALLEL_ROUTING_FALLBACK_TO_SEQUENTIAL=true

# Step 2: Monitor transition (5 min)
# Verify sequential router handling all traffic

# Step 3: If still failing, disable parallel routing completely
export PARALLEL_ROUTING_ENABLED=false

# Step 4: Post-mortem within 1 hour
# Analyze logs and metrics
# Identify root cause
# Plan fix
```

### 5.3 Graceful Degradation

```python
# If router unavailable:
# 1. Fall back to category-based selection
# 2. Use simple round-robin
# 3. Use first-available agent
# 4. Error and escalate to human
```

---

## 6. MONITORING & ALERTING

### 6.1 Dashboard Metrics

**Real-time Dashboard (updated every 10s):**
- Routing latency (p50/p95/p99)
- Accuracy percentage
- Error rate
- Active tasks
- Queue depth
- Agent utilization by agent
- Cache hit rate
- Throughput (tasks/sec)

**Hourly Report:**
- Aggregated latencies
- Accuracy trends
- Error trends
- Agent load distribution
- Most common routing decisions
- Failed routing attempts

### 6.2 Alerts

```yaml
alerts:
  - name: High Routing Latency
    condition: p99_latency_ms > 500
    severity: warning
    action: page_on_call

  - name: Low Routing Accuracy
    condition: accuracy < 0.95
    severity: warning
    action: escalate_to_platform

  - name: High Error Rate
    condition: error_rate > 0.01  # 1%
    severity: critical
    action: trigger_rollback

  - name: Deadlock Detected
    condition: circular_dependency_count > 0
    severity: critical
    action: immediate_rollback + page_cto

  - name: Agent Queue Overflow
    condition: max_queue_depth > 10
    severity: warning
    action: scale_agents + investigate
```

### 6.3 Metrics Export

```bash
# Prometheus metrics endpoint
/metrics/routing

# Datadog custom metrics
routing.latency_ms (gauge, p50/p95/p99)
routing.accuracy_ratio (gauge, 0-1)
routing.error_rate (gauge, 0-1)
routing.throughput_tasks_per_sec (gauge)
routing.queue_depth (gauge)
routing.cache_hit_rate (gauge, 0-1)
```

---

## 7. SUCCESS CRITERIA & SIGN-OFF

### 7.1 Canary Success (Day 1 12:00 UTC)
- [x] 95%+ routing accuracy
- [x] <500ms p99 latency
- [x] <0.5% error rate
- [x] Zero deadlocks
- [x] 12h stable monitoring

**Approval:** @mbaetiong or SRE lead

### 7.2 Regional Success (Day 2 18:00 UTC)
- [x] 95%+ routing accuracy on 25% traffic
- [x] <500ms p99 latency
- [x] <1% error rate
- [x] Zero deadlocks
- [x] 6h stable monitoring

**Approval:** @mbaetiong or SRE lead

### 7.3 Production Success (Day 3 onwards)
- [x] 95%+ routing accuracy on 100% traffic
- [x] <500ms p99 latency
- [x] <0.5% error rate
- [x] Zero deadlocks
- [x] 7 days stable operation
- [x] No user complaints
- [x] Agent utilization balanced (±20% std dev)

**Approval:** @mbaetiong + Platform Team

### 7.4 Official Completion
After 14 days stable operation on 100% traffic:
- [ ] Sunset sequential router (keep as fallback only)
- [ ] Archive unused code
- [ ] Update documentation
- [ ] Post retrospective to team
- [ ] Mark Task 9.3.6 COMPLETE

---

## 8. ROLLBACK & RECOVERY PROCEDURES

### 8.1 Emergency Rollback (Anytime)
```bash
# Immediate rollback to sequential router
kubectl set env deployment/router-engine \
  PARALLEL_ROUTING_ENABLED=false \
  PARALLEL_ROUTING_FALLBACK_TO_SEQUENTIAL=true

# Verify all traffic on sequential
curl https://router.internal/health
# Expected: { status: "fallback_sequential_active" }

# Drain in-flight requests (wait max 5 min)
# Kill old router pods
kubectl delete pods -l app=router-engine
```

### 8.2 Data Recovery
- All routing decisions logged to append-only log
- Cache can be rebuilt from log (replay capability)
- Agent metrics persisted to time-series DB
- No data loss expected

### 8.3 Post-Mortem Process
1. **Immediate:** Rollback and stabilize (0-15 min)
2. **Investigation:** Root cause analysis (15 min - 2 hours)
3. **Fix:** Code fix or config adjustment (2-6 hours)
4. **Testing:** Regression tests on fix (1-2 hours)
5. **Redeployment:** Re-enter at Canary phase
6. **Review:** Team retrospective within 24 hours

---

## 9. CONTACTS & ESCALATION

### 9.1 Escalation Chain
```
On-Call Engineer (Router Component)
  ↓ (unresolved in 15 min)
SRE Lead (@platform-sre)
  ↓ (unresolved in 30 min)
@mbaetiong (D-tier approval authority)
```

### 9.2 Key Contacts
- **Product:** @product-lead
- **Platform/SRE:** @platform-sre
- **Security:** @security-lead
- **Authority:** @mbaetiong

### 9.3 Communication
- **Slack:** #codex-deployments (real-time)
- **Status Page:** status.internal.codex.com
- **Incident:** Use GitHub Issues with label "phase-9-3-incident"

---

## 10. APPENDIX: CONFIG FILES & SCRIPTS

### 10.1 Feature Flag Configuration

```yaml
# .github/runners/phase_9_3_router.yaml
version: 1
router:
  enabled: true
  traffic_percentage: 5  # Canary phase
  fallback_to_sequential: true

  # Performance tuning
  routing_timeout_ms: 500
  cache_ttl_seconds: 3600
  max_queue_depth: 100
  max_agents_per_task: 3

  # SLA thresholds
  sla:
    latency_p99_ms: 500
    accuracy_min: 0.95
    error_rate_max: 0.005

  # Logging
  logging:
    level: INFO
    log_all_decisions: true
    log_errors: true

```

### 10.2 Deployment Script

```bash
#!/bin/bash
# deploy_phase_9_3.sh

PHASE=$1  # canary, regional, production
TRAFFIC=$2  # 5, 25, 100

echo "Deploying Phase 9.3 ($PHASE, $TRAFFIC% traffic)"

# Update config
kubectl set env deployment/router-engine \
  PARALLEL_ROUTING_TRAFFIC_PERCENTAGE=$TRAFFIC

# Verify health
sleep 10
curl https://router.internal/health

echo "Deployment complete. Monitoring for SLA compliance..."
```

---

## SIGN-OFF

- **Prepared by:** @mbaetiong (D-tier)
- **Reviewed by:** SRE Lead
- **Approved by:** @mbaetiong
- **Date:** 2026-06-22
- **Ready for Deployment:** YES ✓

---

**Next Steps:**
1. Obtain stakeholder sign-off on pre-deployment checklist
2. Execute Canary phase (Day 1)
3. Monitor and report daily
4. Execute Regional phase (Day 2)
5. Execute Production phase (Day 3+)
6. Complete Phase 9.3 by 2026-07-05
