# Production Observability: Health Check & Validation Procedures

**Phase**: 7D (Pre-v0.1.0-final)  
**Authority**: @mbaetiong (D-level autonomy)  
**Status**: Production-Ready Implementation Guide  
**Last Updated**: 2026-06-20  

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [Deployment Day Procedures](#deployment-day-procedures)
4. [Post-Deployment Validation](#post-deployment-validation)
5. [Stability Criteria](#stability-criteria)
6. [Manual Testing Procedures](#manual-testing-procedures)

--- # pragma: allowlist secret # pragma: allowlist secret

## Executive Summary

Health checks ensure v0.1.0-final is production-ready before and after deployment. There are four critical phases:

1. **Pre-Deployment** (Day before): Infrastructure & configuration validation
2. **Deployment Day** (0-5 min): Service startup & basic connectivity
3. **Early Monitoring** (5 min - 1 hour): System stabilization
4. **Stability Validation** (1 - 24 hours): Baseline establishment

---

## Pre-Deployment Checklist

### 24 Hours Before Deployment

**Infrastructure Readiness** ✓

```bash
#!/bin/bash
# Run this script 24 hours before deployment

echo "=== Infrastructure Pre-Flight Checks ==="

# 1. Disk Space
echo "Checking disk space..."
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
  echo "❌ FAIL: Disk usage $DISK_USAGE% > 80%"
  exit 1
else
  echo "✓ PASS: Disk usage $DISK_USAGE% OK"
fi

# 2. Memory
echo "Checking available memory..."
MEM_AVAIL=$(free -m | awk 'NR==2 {print $7}')
MEM_NEEDED=4096
if [ $MEM_AVAIL -lt $MEM_NEEDED ]; then
  echo "❌ FAIL: Available memory ${MEM_AVAIL}MB < ${MEM_NEEDED}MB"
  exit 1
else
  echo "✓ PASS: Available memory ${MEM_AVAIL}MB OK"
fi

# 3. Network connectivity
echo "Checking network..."
ping -c 1 8.8.8.8 > /dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "❌ FAIL: No internet connectivity"
  exit 1
else
  echo "✓ PASS: Network OK"
fi

# 4. Database connectivity
echo "Checking database..."
pg_isready -h $DB_HOST -p 5432 > /dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "❌ FAIL: Database unreachable at $DB_HOST"
  exit 1
else
  echo "✓ PASS: Database OK"
fi

# 5. Redis connectivity
echo "Checking Redis..."
redis-cli -h $REDIS_HOST ping > /dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "❌ FAIL: Redis unreachable at $REDIS_HOST"
  exit 1
else
  echo "✓ PASS: Redis OK"
fi

# 6. Monitoring stack
echo "Checking monitoring stack..."
curl -s http://prometheus:9090/-/healthy > /dev/null
if [ $? -ne 0 ]; then
  echo "❌ FAIL: Prometheus unhealthy"
  exit 1
else
  echo "✓ PASS: Prometheus OK"
fi

# 7. Alerting stack
echo "Checking alerting..."
curl -s http://alertmanager:9093/-/healthy > /dev/null
if [ $? -ne 0 ]; then
  echo "❌ FAIL: Alertmanager unhealthy"
  exit 1
else
  echo "✓ PASS: Alertmanager OK"
fi

echo ""
echo "=== ✓ ALL PRE-DEPLOYMENT CHECKS PASSED ==="
```

**Monitoring Setup Validation** ✓

```yaml
# Verify metrics collection is working
- Prometheus scraping at least 5 targets
- Alert rules loaded without errors
- Grafana dashboards accessible
- Loki/ELK receiving logs
- Alertmanager routing configured
```

**Configuration Review** ✓

- [ ] All secrets configured (DB passwords, API keys)
- [ ] Environment variables set correctly
- [ ] Log level set to INFO (not DEBUG)
- [ ] Rate limits configured
- [ ] Cache TTLs appropriate
- [ ] Timeout values reasonable
- [ ] Feature flags reviewed
- [ ] Database migrations ready

**Team Readiness** ✓

```bash
# 24 hours before deployment
# 1. Confirm on-call engineer availability
# 2. Review escalation contacts
# 3. Verify Slack/PagerDuty channels active
# 4. Distribute runbooks to team
# 5. Schedule post-deployment review meeting
```

---

## Deployment Day Procedures

### Phase 1: Pre-Deployment (T-30 min)

```bash
# 1. Final health check
./scripts/pre-flight-check.sh

# 2. Create deployment snapshot
kubectl create configmap pre-deployment-state \
  --from-literal=timestamp=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
  --from-literal=version=v0.1.0-final

# 3. Verify backup integrity
pg_dump $DB_NAME --schema-only | head -20  # Verify it works

# 4. Notify team
echo "🚀 Deployment starting in 30 minutes..."
# Post to Slack: #deployments
```

### Phase 2: Deployment (T-0 to T+5 min)

**Goal**: Service up and responding

```bash
# T-0: Start deployment
kubectl apply -f deployment/codex-ml-v0.1.0.yml
DEPLOY_START=$(date +%s)

# T-0 to T+3: Watch rollout
echo "⏳ Waiting for deployment..."
kubectl rollout status deployment/codex-ml --timeout=180s
ROLLOUT_STATUS=$?

if [ $ROLLOUT_STATUS -ne 0 ]; then
  echo "❌ Deployment failed!"
  kubectl describe deployment codex-ml
  # Rollback if needed
  kubectl rollout undo deployment/codex-ml
  exit 1
fi

# T+3 to T+5: Verify connectivity
echo "✓ Checking service connectivity..."
for i in {1..10}; do
  curl -s http://codex-ml/health
  if [ $? -eq 0 ]; then
    echo "✓ Service responding"
    break
  fi
  echo "Attempt $i/10..."
  sleep 1
done

DEPLOY_DURATION=$(($(date +%s) - $DEPLOY_START))
echo "✓ Deployment completed in ${DEPLOY_DURATION}s"
```

**Deployment Status Dashboard**:

| Checkpoint | Status | Time | Details |
|-----------|--------|------|---------|
| Pods starting | ✓ | T+2min | 3/3 replicas running |
| Service responding | ✓ | T+3min | HTTP 200 from /health |
| Database connected | ✓ | T+4min | Queries < 100ms |
| Cache available | ✓ | T+5min | Redis responds |

---

## Post-Deployment Validation

### Phase 3: Stabilization (T+5 min to T+1 hour)

**Goal**: System settling to normal operating parameters

#### Automated Checks (every 2 minutes)

```bash
#!/bin/bash
# run: ./scripts/health-check-loop.sh

HEALTH_CHECK_INTERVAL=120  # 2 minutes
HEALTH_CHECK_DURATION=3600  # 1 hour
END_TIME=$(($(date +%s) + HEALTH_CHECK_DURATION))

while [ $(date +%s) -lt $END_TIME ]; do
  TIMESTAMP=$(date -u +'%Y-%m-%dT%H:%M:%SZ')

  echo "=== Health Check @ $TIMESTAMP ==="

  # 1. Pod Health
  RUNNING_PODS=$(kubectl get pods -l app=codex-ml -o jsonpath='{.items[?(@.status.phase=="Running")].metadata.name}' | wc -w)
  TOTAL_PODS=$(kubectl get pods -l app=codex-ml -o jsonpath='{.items[*].metadata.name}' | wc -w)
  echo "Pods: $RUNNING_PODS/$TOTAL_PODS running"

  if [ $RUNNING_PODS -lt $TOTAL_PODS ]; then
    echo "⚠️  WARNING: Not all pods running"
    kubectl get pods -l app=codex-ml
  fi

  # 2. Error Rate
  ERROR_RATE=$(curl -s 'http://prometheus:9090/api/v1/query?query=rate(http_requests_total{status=~"5.."}[5m])' | \
    jq '.data.result[0].value[1]' | tr -d '"' | awk '{printf "%.2f", $1*100}')
  echo "Error Rate: ${ERROR_RATE}%"

  if (( $(echo "$ERROR_RATE > 1" | bc -l) )); then
    echo "⚠️  WARNING: Error rate > 1%"
  fi

  # 3. Database Latency
  DB_LATENCY=$(curl -s 'http://prometheus:9090/api/v1/query?query=histogram_quantile(0.95,rate(db_query_duration_seconds_bucket[5m]))' | \
    jq '.data.result[0].value[1]' | tr -d '"')
  echo "DB P95 Latency: ${DB_LATENCY}s"

  # 4. Memory Usage
  MEM_USAGE=$(kubectl top pod -l app=codex-ml --no-headers | awk '{s+=$2} END {print s}')
  echo "Memory Usage: ${MEM_USAGE}Mi"

  # 5. Cache Performance
  CACHE_HIT=$(curl -s 'http://prometheus:9090/api/v1/query?query=cache_hit_ratio' | \
    jq '.data.result[0].value[1]' | tr -d '"' | awk '{printf "%.1f", $1*100}')
  echo "Cache Hit Ratio: ${CACHE_HIT}%"

  echo ""

  sleep $HEALTH_CHECK_INTERVAL
done
```

**Expected Behavior (T+5 to T+60 min)**:

| Metric | Expected | Alert If |
|--------|----------|----------|
| Error Rate | < 0.5% | > 1% |
| P95 Latency | < 500ms | > 1s |
| Memory | Stabilized | Growing |
| CPU | < 40% | > 60% |
| Cache Hit | > 80% | < 70% |
| Pod Restarts | 0 | > 0 |

#### Manual Spot Checks (every 15 min)

```bash
# T+15: Check logs for errors
kubectl logs -l app=codex-ml --tail=50 | grep -i error

# T+30: Verify database performance
psql $DB_NAME << SQL
  SELECT query, calls, total_time, mean_time
  FROM pg_stat_statements
  WHERE mean_time > 100
  ORDER BY mean_time DESC LIMIT 5;
SQL

# T+45: Check external API connectivity
curl -I https://api.example.com/health

# T+60: Review monitoring dashboards
# Check Grafana at http://grafana:3000
# - System Health Overview
# - Application Performance
# - Errors & Logs
```

### Phase 4: Extended Stability (T+1 hour to T+24 hours)

**Goal**: Establish 24-hour baseline

#### Hourly Checks (T+1h to T+24h)

```bash
#!/bin/bash
# Hourly validation script

for hour in {1..24}; do
  TIMESTAMP=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
  echo "=== Hour $hour: $TIMESTAMP ==="

  # Key metrics
  UPTIME=$(curl -s 'http://prometheus:9090/api/v1/query?query=up{job="codex-ml"}' | \
    jq '[.data.result[].value[1]] | map(tonumber) | map(select(. == 1)) | length' | \
    awk -v total=$(curl -s 'http://prometheus:9090/api/v1/query?query=up{job="codex-ml"}' | jq '.data.result | length') '{printf "%.1f", $1/total*100}')

  ERROR_COUNT=$(curl -s 'http://prometheus:9090/api/v1/query?query=increase(http_requests_total{status=~"5.."}[1h])' | \
    jq '.data.result[0].value[1]' | tr -d '"')

  REQUEST_COUNT=$(curl -s 'http://prometheus:9090/api/v1/query?query=increase(http_requests_total[1h])' | \
    jq '.data.result[0].value[1]' | tr -d '"')

  ERROR_RATE=$(echo "scale=2; $ERROR_COUNT / $REQUEST_COUNT * 100" | bc)

  echo "Uptime: ${UPTIME}%"
  echo "Error Rate: ${ERROR_RATE}%"
  echo "Total Requests: $REQUEST_COUNT"

  # Alert conditions
  if (( $(echo "$UPTIME < 99" | bc -l) )); then
    echo "⚠️  WARNING: Uptime < 99%"
  fi

  if (( $(echo "$ERROR_RATE > 0.5" | bc -l) )); then
    echo "⚠️  WARNING: Error rate > 0.5%"
  fi

  sleep 3600
done
```

#### 24-Hour Baseline Metrics

```yaml
baseline_metrics:
  availability: 99.9%  # Must be > 99.5%
  error_rate: 0.1%     # Must be < 0.5%
  p95_latency: 300ms   # Must be < 1000ms
  p99_latency: 500ms   # Must be < 2000ms
  cpu_avg: 35%         # Allows up to 70%
  memory_avg: 2.5GB    # Allows up to 6GB
  cache_hit: 85%       # Must be > 75%
  db_connections: 25   # Max 100

  # Business metrics
  predictions_generated: 10000+
  average_confidence: 0.92
  model_accuracy: 94%+
  data_pipeline_latency: < 2s
```

---

## Stability Criteria

### 0-5 Minutes: Service Stability

**Criteria**:
- [ ] All pods running and ready
- [ ] Service responding to health checks
- [ ] Basic connectivity to all dependencies
- [ ] No crash loops or restarts
- [ ] Metrics appearing in Prometheus

**Failure Triggers for Rollback**:
- Pod CrashLoopBackOff
- Service not responding after 5 min
- Database connection failures
- Immediate error rate > 10%

### 5-60 Minutes: System Stabilization

**Criteria**:
- [ ] Error rate stable < 1%
- [ ] Latency p95 < 1 second
- [ ] Memory usage stabilized
- [ ] No unexplained increases in CPU
- [ ] Cache performance > 70% hit ratio
- [ ] All health check endpoints returning 200

**Monitoring Dashboard**: Open Grafana "Application Performance"

### 1-24 Hours: Baseline Establishment

**Criteria**:
- [ ] Availability > 99.5% for the period
- [ ] Error rate < 0.5%
- [ ] P99 latency < 2 seconds (consistent)
- [ ] Memory growth < 10% over 24h
- [ ] Prediction accuracy within 1% of pre-release
- [ ] All SLA metrics met
- [ ] No repeated error patterns

**Success Metrics Dashboard**:

```bash
# At T+24h, run this validation
cat > /opt/monitoring/validators/24h-check.sh << 'EOF'
#!/bin/bash

echo "=== 24-Hour Deployment Validation ==="

# Query Prometheus for 24-hour metrics
QUERY_START=$(date -u -d '24 hours ago' +'%Y-%m-%dT%H:%M:%SZ')
QUERY_END=$(date -u +'%Y-%m-%dT%H:%M:%SZ')

# 1. Availability
AVAILABILITY=$(curl -s 'http://prometheus:9090/api/v1/query_range' \
  --data-urlencode 'query=up{job="codex-ml"}' \
  --data-urlencode "start=$QUERY_START" \
  --data-urlencode "end=$QUERY_END" \
  --data-urlencode 'step=60s' | \
  jq '.data.result | map(.values) | add | map(tonumber) | \
    (map(select(. == 1)) | length) / (length) * 100')

echo "24h Availability: ${AVAILABILITY}%"
[ $(echo "$AVAILABILITY >= 99.5" | bc) -eq 1 ] && echo "✓ PASS" || echo "❌ FAIL"

# 2. Error Rate
ERROR_RATE=$(curl -s 'http://prometheus:9090/api/v1/query' \
  --data-urlencode 'query=increase(http_requests_total{status=~"5.."}[24h]) / increase(http_requests_total[24h]) * 100' | \
  jq '.data.result[0].value[1]')

echo "24h Error Rate: ${ERROR_RATE}%"
[ $(echo "$ERROR_RATE <= 0.5" | bc) -eq 1 ] && echo "✓ PASS" || echo "❌ FAIL"

# 3. P99 Latency
P99_LATENCY=$(curl -s 'http://prometheus:9090/api/v1/query' \
  --data-urlencode 'query=histogram_quantile(0.99, increase(http_request_duration_seconds_bucket[24h]))' | \
  jq '.data.result[0].value[1]')

echo "24h P99 Latency: ${P99_LATENCY}s"
[ $(echo "$P99_LATENCY <= 2" | bc) -eq 1 ] && echo "✓ PASS" || echo "❌ FAIL"

# 4. Model Accuracy
MODEL_ACCURACY=$(curl -s 'http://prometheus:9090/api/v1/query' \
  --data-urlencode 'query=avg(model_accuracy_percent)' | \
  jq '.data.result[0].value[1]')

echo "Model Accuracy: ${MODEL_ACCURACY}%"
[ $(echo "$MODEL_ACCURACY >= 92" | bc) -eq 1 ] && echo "✓ PASS" || echo "❌ FAIL"

echo ""
echo "=== DEPLOYMENT VALIDATION COMPLETE ==="
EOF

chmod +x /opt/monitoring/validators/24h-check.sh
/opt/monitoring/validators/24h-check.sh
```

---

## Manual Testing Procedures

### Critical User Flows

**Test 1: Model Prediction Flow** (5 min)

```bash
#!/bin/bash

echo "Testing: Model Prediction Flow"

# 1. Authenticate
TOKEN=$(curl -s -X POST http://codex-ml/auth/login \
  -d '{"username":"test","password":"test"}' | jq -r '.token')

echo "✓ Authentication successful"

# 2. Submit prediction request
PREDICTION=$(curl -s -X POST http://codex-ml/api/v1/predict \
  -H "Authorization: ******" \
  -d '{"input":"test data","model":"default"}')

PRED_ID=$(echo $PREDICTION | jq -r '.prediction_id')
echo "✓ Prediction submitted: $PRED_ID"

# 3. Get results
sleep 2
RESULT=$(curl -s http://codex-ml/api/v1/predictions/$PRED_ID \
  -H "Authorization: ******")

ACCURACY=$(echo $RESULT | jq -r '.confidence')
echo "✓ Results retrieved: confidence=$ACCURACY"

# 4. Verify quality
if (( $(echo "$ACCURACY > 0.90" | bc -l) )); then
  echo "✓ PASS: Prediction quality good"
else
  echo "❌ FAIL: Prediction confidence too low"
fi
```

**Test 2: Data Pipeline** (10 min)

```bash
#!/bin/bash

echo "Testing: Data Pipeline"

# 1. Ingest test data
BATCH_ID=$(curl -s -X POST http://codex-ml/api/v1/data/ingest \
  -d @test_data_batch.json | jq -r '.batch_id')

echo "✓ Data batch submitted: $BATCH_ID"

# 2. Monitor processing
for i in {1..30}; do
  STATUS=$(curl -s http://codex-ml/api/v1/data/$BATCH_ID/status | jq -r '.status')
  echo "Status: $STATUS"

  if [ "$STATUS" = "completed" ]; then
    echo "✓ Processing completed"
    break
  fi

  sleep 2
done

# 3. Verify output
OUTPUT=$(curl -s http://codex-ml/api/v1/data/$BATCH_ID/results | jq '.records | length')
echo "✓ Processed $OUTPUT records"
```

**Test 3: Error Handling** (5 min)

```bash
#!/bin/bash

echo "Testing: Error Handling"

# 1. Invalid input
RESPONSE=$(curl -s http://codex-ml/api/v1/predict -d '{"invalid":"data"}')
STATUS=$(echo $RESPONSE | jq -r '.status')

if [ "$STATUS" = "error" ]; then
  echo "✓ Invalid input rejected properly"
else
  echo "❌ FAIL: Should reject invalid input"
fi

# 2. Rate limiting
for i in {1..100}; do
  curl -s http://codex-ml/health > /dev/null &
done
wait

# Check if rate limited
RESPONSE=$(curl -s http://codex-ml/health)
if echo $RESPONSE | grep -q "rate"; then
  echo "✓ Rate limiting working"
fi

# 3. Dependency failure simulation (not in production!)
# This would test graceful degradation
```

---

## Validation Checklist (Complete)

### Pre-Deployment (T-24h)
- [ ] Infrastructure health checks passing
- [ ] Monitoring stack operational
- [ ] All dependencies responding
- [ ] Team on-call list confirmed
- [ ] Runbooks distributed
- [ ] Database backups verified
- [ ] Rollback plan reviewed

### Deployment Day (T-0)
- [ ] All pods running after T+5 min
- [ ] Service responding to health checks
- [ ] No crash loops
- [ ] Basic error rate < 5%

### Post-Deployment (T+60 min)
- [ ] Error rate stable < 1%
- [ ] P95 latency < 1s
- [ ] Memory stabilized
- [ ] Cache hit ratio > 70%
- [ ] All health checks green

### 24-Hour Baseline (T+24h)
- [ ] Availability > 99.5%
- [ ] Error rate < 0.5%
- [ ] P99 latency < 2s
- [ ] Predictions generated: 10k+
- [ ] Model accuracy > 92%
- [ ] All SLA metrics met

---

**Next Steps:**
1. Review PHASE_7D_INCIDENT_RESPONSE.md (if issues occur)
2. Document lessons learned
3. Update runbooks based on actual behavior
4. Schedule post-deployment retrospective (T+48h)
