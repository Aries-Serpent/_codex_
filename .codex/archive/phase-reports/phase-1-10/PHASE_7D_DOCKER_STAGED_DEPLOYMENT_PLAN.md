# 🚀 STAGED DEPLOYMENT PLAN: v0.1.0-final Production Release
**Multi-Environment Rollout with Health Verification & Rollback Procedures**

**Generated:** 2026-06-20T07:54:04Z  
**Authority:** @mbaetiong (D-level autonomy)  
**Release Version:** v0.1.0-final  
**Status:** READY FOR EXECUTION

---

## EXECUTIVE SUMMARY

This document outlines the staged deployment procedure for v0.1.0-final across three environments (dev, staging, production). Each stage includes specific health checks, success criteria, and rollback procedures. The deployment is designed to minimize risk through gradual rollout with continuous verification.

**Timeline:** ~6-8 hours total (including waiting periods)
- Dev environment: 30-45 minutes
- Staging environment: 1-2 hours
- Production environment: 2-3 hours
- Monitoring period: 2-4 hours

---

## STAGE 1: DEVELOPMENT ENVIRONMENT DEPLOYMENT

### 1.1 Pre-Deployment Checklist

**Duration:** 15 minutes

```
□ Verify development cluster is operational
  - Check Kubernetes cluster health: kubectl cluster-info
  - Verify node status: kubectl get nodes
  - Confirm persistent volumes available
  - Check resource quotas: kubectl describe resourcequota

□ Backup current development state
  - Snapshot all databases: pg_dump, mongodump as applicable
  - Export environment variables
  - Capture current service versions for rollback

□ Verify image availability in registry
  - Confirm all 8 Docker variants built and pushed
  - Verify image digests match expected values
  - Check image sizes are within expected ranges

□ Prepare rollback artifacts
  - Document previous service versions
  - Save previous configuration manifests
  - Prepare rollback scripts
```

### 1.2 Development Deployment Steps

**Duration:** 20-30 minutes

#### Step 1.2.1: Update Image References
```yaml
# Update deployment manifests to reference v0.1.0-final images
# File: k8s/dev/deployment.yaml

spec:
  containers:
  - name: codex-api
    image: ghcr.io/aries-serpent/codex:v0.1.0-final  # Updated
    imagePullPolicy: Always
    resources:
      limits:
        cpu: 2000m
        memory: 2Gi
      requests:
        cpu: 500m
        memory: 512Mi
```

#### Step 1.2.2: Apply Configuration Updates
```bash
# 1. Update ConfigMaps for environment-specific settings
kubectl apply -f k8s/dev/configmap.yaml

# 2. Apply database migrations if needed
kubectl apply -f k8s/dev/migrations/
kubectl rollout status deployment/codex-migration -n development

# 3. Update secrets (from GitHub Secrets)
kubectl create secret generic codex-secrets \
  --from-literal=DATABASE_URL=${{ secrets.DEV_DATABASE_URL }} \
  --from-literal=API_KEY=${{ secrets.DEV_API_KEY }} \
  -n development \
  --dry-run=client -o yaml | kubectl apply -f -
```

#### Step 1.2.3: Deploy New Version
```bash
# 1. Update deployment with new image
kubectl set image deployment/codex-api \
  codex-api=ghcr.io/aries-serpent/codex:v0.1.0-final \
  -n development

# 2. Monitor rollout
kubectl rollout status deployment/codex-api -n development --timeout=5m

# 3. Verify pod status
kubectl get pods -n development -l app=codex-api
kubectl logs deployment/codex-api -n development --tail=50
```

#### Step 1.2.4: Execute Data Migration (if needed)
```bash
# Run migration job if there are schema changes
kubectl create job --from=cronjob/codex-migration-nightly \
  codex-migration-$(date +%s) \
  -n development

# Monitor migration status
kubectl logs -f job/codex-migration-$(date +%s) -n development
```

### 1.3 Development Health Checks

**Duration:** 10-15 minutes after deployment**

#### Health Check #1: Pod Status Verification
```bash
# Verify all pods are running
kubectl get pods -n development -l app=codex-api -o wide

# Expected output: All pods in Running state with Ready 1/1
# Action if failed: Check logs → Rollback if startup errors detected
```

#### Health Check #2: Service Endpoints
```bash
# Verify service is reachable
kubectl get svc codex-api -n development

# Test endpoint connectivity
curl -X GET http://codex-api.development.svc.cluster.local:8000/health
# Expected: 200 OK with { "status": "healthy" }
```

#### Health Check #3: Application Functionality
```bash
# Test core functionality endpoints
curl -X POST http://codex-api.development/api/v1/models/predict \
  -H "Content-Type: application/json" \
  -d '{"input": "test"}'
# Expected: 200 OK with valid model output

# Test CLI commands if applicable
kubectl exec deployment/codex-api -n development -- \
  codex --version
# Expected: v0.1.0-final
```

#### Health Check #4: Database Connectivity
```bash
# Verify database connection
kubectl exec deployment/codex-api -n development -- \
  python -c "from codex.db import SessionLocal; \
             db = SessionLocal(); \
             print('DB OK' if db.execute('SELECT 1') else 'DB FAIL')"
# Expected: DB OK
```

#### Health Check #5: Metrics Export
```bash
# Verify Prometheus metrics are available
curl http://codex-api.development:8000/metrics
# Expected: 200 OK with Prometheus metrics format
```

### 1.4 Development Validation Criteria

| Criterion | Target | Action if Failed |
|-----------|--------|------------------|
| All pods Running | 3/3 running | Inspect logs, investigate pending state |
| Health endpoint responds | 200 OK | Restart pod, check configuration |
| API endpoints functional | All working | Rollback to previous version |
| Database queries successful | 100% success | Check database connectivity, run migrations |
| No error rate spike | <1% error rate | Monitor for 5 minutes, rollback if persists |
| Memory usage normal | <500MB average | Monitor GC, check for memory leaks |

### 1.5 Development Rollback Procedure (if needed)

```bash
# If any health check fails:

# 1. Scale down broken deployment
kubectl scale deployment codex-api --replicas=0 -n development

# 2. Restore previous image
kubectl set image deployment/codex-api \
  codex-api=ghcr.io/aries-serpent/codex:v0.0.9-stable \
  -n development

# 3. Scale back up
kubectl scale deployment codex-api --replicas=3 -n development

# 4. Verify rollback completed
kubectl rollout status deployment/codex-api -n development

# 5. Report issue and halt pipeline
# escalate to @mbaetiong with full logs
```

**Success Criteria for Stage 1:** All health checks pass, no errors observed for 5 minutes → PROCEED TO STAGE 2

---

## STAGE 2: STAGING ENVIRONMENT DEPLOYMENT

### 2.1 Pre-Deployment Checklist

**Duration:** 20-30 minutes

```
□ Review development environment results
  - Confirm all Stage 1 health checks passed
  - Review any warnings or performance metrics
  - Confirm no production impact from dev testing

□ Backup current staging state
  - Create staging database snapshot
  - Export staging configurations
  - Document current service versions

□ Load test preparation
  - Configure load testing tools (k6, locust)
  - Prepare realistic traffic patterns
  - Set up monitoring dashboards

□ Staging infrastructure verification
  - Verify staging cluster has sufficient resources
  - Check persistent volume capacity
  - Verify backup systems operational
```

### 2.2 Staging Deployment Steps

**Duration:** 30-45 minutes (similar to Stage 1)**

#### Step 2.2.1-2.4: Same as Stage 1
- Update image references in `k8s/staging/deployment.yaml`
- Apply configuration updates and secrets
- Deploy new version using canary strategy (see 2.3)
- Execute data migrations if applicable

#### Step 2.2.5: Canary Deployment (10% traffic initially)
```yaml
# Use Istio/Flagger for canary deployment
# File: k8s/staging/canary.yaml

apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: codex-api-canary
  namespace: staging
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: codex-api

  service:
    port: 8000

  analysis:
    interval: 1m
    threshold: 5  # max 5% error rate
    maxWeight: 100
    stepWeight: 20  # increase traffic by 20% every minute

  metrics:
  - name: request-success-rate
    thresholdRange:
      min: 99
    interval: 1m
  - name: request-duration
    thresholdRange:
      max: 500
    interval: 1m
```

### 2.3 Staging Health Checks

**Duration:** 45-60 minutes (extended monitoring for canary)**

Same as Stage 1, plus:

#### Extended Check #1: Load Testing
```bash
# Run synthetic load test
k6 run tests/load-tests/api-endpoint-load.js \
  --vus 50 \
  --duration 10m \
  --stage "1m:10" --stage "5m:50" --stage "4m:10"

# Expected: <1% error rate, p95 response time <500ms
```

#### Extended Check #2: Error Rate Monitoring (20 minutes)
```bash
# Monitor Prometheus for errors
# Query: rate(http_requests_total{status=~"5.."}[1m])
# Expected: <0.01 (less than 0.01 errors/sec)

# Check application logs for exceptions
kubectl logs -f deployment/codex-api -n staging --all-containers=true
# Expected: Only info/warn level logs, no errors
```

#### Extended Check #3: Database Performance
```bash
# Monitor slow queries
# Connect to staging DB and check query logs
# Expected: All queries complete in <500ms (p95)

# Verify no connection pool exhaustion
psql $STAGING_DATABASE_URL -c \
  "SELECT count(*) FROM pg_stat_activity WHERE state = 'active';"
# Expected: <80 active connections
```

### 2.4 Staging Validation Criteria

| Criterion | Target | Action if Failed |
|-----------|--------|------------------|
| Canary error rate | <1% | Increase monitoring interval, may halt rollout |
| Load test p95 response | <500ms | Check for performance regressions, may rollback |
| Database connections stable | <80 active | Monitor for connection leaks, may rollback |
| Memory growth | <5% per hour | Check for memory leaks, may rollback |
| No new exceptions | 0 new errors | Investigate and fix before production |

### 2.5 Staging Rollback Procedure

Same as Stage 1, with additional:
```bash
# Reset canary weight to 0
kubectl patch canary codex-api-canary \
  -p '{"spec":{"skipAnalysis":true}}' -n staging

# Complete rollback
# (same scale-down, restore image, scale-up procedure)
```

**Success Criteria for Stage 2:**
- Canary health checks pass for full duration
- No performance regressions detected
- Load test completes successfully → PROCEED TO STAGE 3

---

## STAGE 3: PRODUCTION ENVIRONMENT DEPLOYMENT

### 3.1 Pre-Deployment Checklist

**Duration:** 30-45 minutes**

```
□ Final production readiness review
  - Confirm all Stage 1 and 2 checks passed
  - Review all monitoring dashboards configured
  - Verify incident response team on standby

□ Create comprehensive backups
  - Full production database backup with verification
  - Export all production configurations
  - Create filesystem snapshots if applicable

□ Communication plan
  - Notify status page of scheduled maintenance (if needed)
  - Brief customer support on changes
  - Prepare rollback communication template

□ Post-deployment monitoring setup
  - Verify all alerting rules configured
  - Check dashboard visibility for on-call engineer
  - Verify incident escalation paths active

□ Blue-Green Deployment Preparation
  - Ensure both blue and green environments ready
  - Verify traffic switching mechanism functional
  - Test failover procedure (non-disruptive)
```

### 3.2 Production Deployment Strategy: Blue-Green

**Duration:** 60-90 minutes (with extended monitoring)**

Due to production criticality, use Blue-Green deployment strategy:

#### Strategy Overview
- **Blue Environment:** Current v0.0.9-stable (running, handling traffic)
- **Green Environment:** New v0.1.0-final (deployed, not receiving traffic initially)
- **Switch:** Traffic routed from blue to green using load balancer
- **Rollback:** Reverse traffic back to blue if issues detected

#### Phase 1: Deploy to Green Environment (30-40 minutes)
```bash
# 1. Deploy new version to green environment (isolated)
kubectl apply -f k8s/production/green/deployment.yaml

# 2. Wait for all green pods to reach Ready state
kubectl rollout status deployment/codex-api-green \
  -n production --timeout=10m

# 3. Run health checks against green environment
curl http://codex-api-green.production.svc.cluster.local:8000/health
```

#### Phase 2: Verify Green Environment (15-20 minutes)
```bash
# 1. Execute smoke tests against green endpoints
pytest tests/smoke/ -v --target=green --environment=production

# 2. Monitor green pod metrics (CPU, memory, errors)
kubectl top pods -l app=codex-api,version=green -n production

# 3. Check green application logs for errors
kubectl logs -l app=codex-api,version=green -n production \
  --tail=200 --timestamps=true
```

#### Phase 3: Traffic Switch to Green (5-10 minutes)
```bash
# 1. Update service selector to point to green
kubectl patch service codex-api \
  -p '{"spec":{"selector":{"version":"green"}}}' \
  -n production

# 2. Verify traffic switched (should see connections on green)
kubectl exec pod/codex-api-green-xxxxx -n production -- \
  curl localhost:8000/metrics | grep http_requests_total

# 3. Monitor error rate during switch (should remain <0.1%)
# Wait 2 minutes to allow connection pool warmup
```

#### Phase 4: Production Health Checks (15-20 minutes)
Perform comprehensive health checks with production traffic:

```bash
# Check 1: Error rate monitoring
# Expected: <0.1% error rate (verify for 5 minutes)

# Check 2: Response time monitoring
# Expected: p95 <1000ms, p99 <2000ms

# Check 3: Database query performance
# Expected: All queries complete in <2s (p99)

# Check 4: Real user monitoring (if applicable)
# Expected: Core Web Vitals within SLA

# Check 5: Third-party service integrations
# Verify all external APIs responding correctly
```

### 3.3 Production Validation Criteria

| Criterion | Target | Monitoring Period |
|-----------|--------|------------------|
| Error rate | <0.1% | 10 minutes post-switch |
| Response time (p95) | <1000ms | 10 minutes post-switch |
| Database performance | p99 <2s | Continuous 30 min |
| CPU utilization | <70% | Continuous 30 min |
| Memory utilization | <75% | Continuous 30 min |
| Exception rate | 0 new errors | Continuous 30 min |
| Third-party APIs | 100% success | Continuous 30 min |

### 3.4 Production Rollback Procedure (if needed)

```bash
# **CRITICAL: Execute immediately if any health check fails**

# 1. Assess the issue (severity, scope, affected users)
# 2. If critical (error rate >1% or availability <99.9%), trigger rollback:

# Switch traffic back to blue (v0.0.9-stable)
kubectl patch service codex-api \
  -p '{"spec":{"selector":{"version":"blue"}}}' \
  -n production

# 3. Monitor blue environment (should stabilize immediately)
# Expected: Error rate drops to <0.1% within 30 seconds

# 4. Verify blue environment stable (5 minutes)
kubectl logs -l app=codex-api,version=blue -n production \
  --tail=100 | grep -i "error" | wc -l
# Expected: Minimal errors

# 5. Report incident and begin root cause analysis
# Create incident ticket with full logs and metrics
# Escalate to @mbaetiong immediately
```

### 3.5 Production Success Criteria

**Do NOT complete production deployment unless ALL criteria met:**

✅ All health checks pass  
✅ Error rate <0.1% for 10 minutes  
✅ Response times normal  
✅ Database stable  
✅ No new errors in logs  
✅ All integrations responding  
✅ Blue environment ready for rollback (just in case)

**Success Criteria Met:** v0.1.0-final deployed to production → PROCEED TO MONITORING

---

## STAGE 4: IMMEDIATE POST-DEPLOYMENT MONITORING (30-60 minutes)

### 4.1 Real-Time Dashboards

**Duration:** Continuous for 1 hour

```
┌─────────────────────────────────────────┐
│     LIVE PRODUCTION METRICS DASHBOARD    │
├─────────────────────────────────────────┤
│                                         │
│  Request Rate (req/sec)        [Graph]  │
│  Error Rate (%)                [Graph]  │
│  Response Time (p95)           [Graph]  │
│  Active Users                  [Gauge]  │
│  Database Connections          [Gauge]  │
│  Memory Usage                  [Gauge]  │
│                                         │
│  Key Alerts: [NONE EXPECTED]            │
│                                         │
│  Last Updated: NOW                      │
└─────────────────────────────────────────┘
```

### 4.2 Automated Alert Thresholds

| Alert | Threshold | Severity | Action |
|-------|-----------|----------|--------|
| Error Rate High | >0.5% | CRITICAL | Page on-call engineer immediately |
| Response Time High | p95 >2s | WARNING | Investigate, may need scaling |
| Database Slow | query p99 >3s | WARNING | Check query plans, indexes |
| Memory Growing | +10% per 5min | WARNING | Investigate memory leak |
| Pod Crashing | >2 restarts/min | CRITICAL | Rollback immediately |

### 4.3 Checklist: Every 5 Minutes for 30 Minutes

```
Time 00:05 - Error rate check, Response time check, Pod health check
Time 00:10 - Database connection check, Memory trend check
Time 00:15 - Third-party API check, Log review for errors
Time 00:20 - Error rate check, Response time check, Pod health check
Time 00:25 - Database connection check, Memory trend check
Time 00:30 - Review overall stability, confirm no issues detected
```

---

## DEPLOYMENT TIMELINE SUMMARY

```
Stage 1: Development          0:00 - 1:15 UTC
  Pre-checks:                 0:00 - 0:15
  Deployment:                 0:15 - 0:45
  Health checks & validation: 0:45 - 1:15

Stage 2: Staging             1:15 - 3:00 UTC
  Pre-checks:                 1:15 - 1:45
  Deployment & canary:        1:45 - 2:30
  Extended health checks:     2:30 - 3:00

Stage 3: Production          3:00 - 5:00 UTC
  Pre-checks:                 3:00 - 3:45
  Blue-green deployment:      3:45 - 4:30
  Health checks & validation: 4:30 - 5:00

Stage 4: Monitoring          5:00 - 6:00 UTC
  Intensive monitoring:       5:00 - 6:00

**Total Duration: ~6 hours**
**Go-Live: v0.1.0-final in production by 6:00 UTC**
```

---

## CONTINGENCY: FULL ROLLBACK PROCEDURE

If production deployment fails catastrophically:

```bash
# 1. IMMEDIATE: Switch traffic back to blue
kubectl patch service codex-api \
  -p '{"spec":{"selector":{"version":"blue"}}}' \
  -n production

# 2. Monitor blue stabilization (should be 30 seconds)

# 3. Alert all stakeholders
# - Send incident notification
# - Post status page update
# - Notify customer support

# 4. Investigate failure
# - Collect all logs from green environment
# - Review metrics from failure period
# - Create incident ticket with root cause

# 5. Post-mortem
# - Schedule 24-hour post-mortem meeting
# - Document lessons learned
# - Update deployment procedures if needed
```

---

## SUCCESS DEFINITION

✅ **Deployment is SUCCESSFUL if:**
- v0.1.0-final running in production
- <0.1% error rate sustained for 1 hour
- All health checks passing
- Production users not experiencing degradation
- All integrations working correctly
- Rollback plan remains ready (in case)

✅ **Ready to proceed to post-deployment verification phase**

---

**Next Document:** `.codex/PHASE_7D_DOCKER_POST_DEPLOYMENT_CHECKLIST.md`
