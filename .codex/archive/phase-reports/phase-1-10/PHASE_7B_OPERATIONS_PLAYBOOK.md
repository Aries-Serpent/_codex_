# 📖 PHASE 7B OPERATIONS PLAYBOOK

**Document:** PHASE_7B_OPERATIONS_PLAYBOOK.md  
**Version:** v0.1.0-final  
**Release Date:** 2026-06-21  
**Authority:** @mbaetiong (COPILOT_AGENT_AUTH_ENABLED=true)  
**Status:** ✅ **PRODUCTION-GRADE OPERATIONS MANUAL**

---

## 📋 TABLE OF CONTENTS

1. [Pre-Deployment Verification](#pre-deployment-verification)
2. [Deployment Procedures](#deployment-procedures)
3. [Post-Deployment Validation](#post-deployment-validation)
4. [Monitoring & Alerting](#monitoring--alerting)
5. [Incident Response Procedures](#incident-response-procedures)
6. [Performance Baselines & SLAs](#performance-baselines--slas)
7. [Rollback Procedures](#rollback-procedures)
8. [Security Operations](#security-operations)

---

## 1. PRE-DEPLOYMENT VERIFICATION

### 1.1 Release Artifact Verification

Before deploying v0.1.0-final, verify all release artifacts:

```bash
# Step 1: Verify tarball integrity
cd /opt/releases
sha256sum -c codex-0.1.0-final.tar.gz.sha256
# Expected: codex-0.1.0-final.tar.gz: OK

# Step 2: Verify SBOM signature
gpg --verify codex-0.1.0-final.sbom.json.sig
# Expected: Good signature from [release-key]

# Step 3: Verify Docker image
docker image inspect ghcr.io/aries-serpent/codex:v0.1.0-final
# Check: SHA256 digest matches release notes

# Step 4: Verify dependencies
pip install --dry-run codex==0.1.0-final
# Expected: No conflicts, all dependencies resolvable
```

### 1.2 Environment Readiness Checklist

Before proceeding with deployment:

- [ ] **Backup Current State:**
  ```bash
  # Backup production database
  pg_dump codex_prod > /backups/codex_prod_$(date +%Y%m%d_%H%M%S).sql

  # Backup configuration
  cp -r /etc/codex /backups/codex_config_$(date +%Y%m%d_%H%M%S)

  # Backup current installation
  cp -r /opt/codex /backups/codex_current_$(date +%Y%m%d_%H%M%S)
  ```

- [ ] **Verify System Resources:**
  ```bash
  # Check disk space (50GB minimum)
  df -h / | grep -E '/(Avail|^/'

  # Check memory (8GB minimum)
  free -h

  # Check CPU availability
  nproc
  ```

- [ ] **Verify Network Connectivity:**
  ```bash
  # Test GitHub API access
  curl -I https://api.github.com

  # Test package repository
  curl -I https://pypi.org/project/codex/

  # Test DNS resolution
  nslookup github.com
  ```

- [ ] **Notify Stakeholders:**
  ```bash
  # Send notification to operations team
  echo "Scheduled deployment of v0.1.0-final on $(date)" | \
    mail -s "CODEX v0.1.0-final Deployment Notice" ops@company.com
  ```

### 1.3 Security Pre-Checks

```bash
# Verify no secrets in release artifacts
tar tzf codex-0.1.0-final.tar.gz | grep -E '\.(key|token|secret|password|pem|crt)$'
# Expected: No output (zero matches)

# Verify file permissions (no world-writable files)
tar tzf codex-0.1.0-final.tar.gz | \
  tar xzOf codex-0.1.0-final.tar.gz | \
  find . -perm -002
# Expected: No output (zero world-writable files)

# Verify CodeQL compliance
codex-security-check --release v0.1.0-final
# Expected: PASS (CodeQL HIGH ≤1, Risk 0.2/10)
```

---

## 2. DEPLOYMENT PROCEDURES

### 2.1 Standard Deployment (Recommended)

**Duration:** 15-20 minutes  
**Downtime:** 2-3 minutes (graceful shutdown + restart)  
**Rollback Time:** <2 minutes

```bash
#!/bin/bash
# Standard Deployment Script for v0.1.0-final

set -euo pipefail

# Configuration
RELEASE_VERSION="0.1.0-final"
INSTALL_PATH="/opt/codex"
SERVICE_NAME="codex"
BACKUP_PATH="/backups"

# Step 1: Pre-deployment validation
echo "[$(date)] Starting deployment of v${RELEASE_VERSION}..."
echo "[$(date)] Verifying release artifacts..."

cd /tmp
wget -q https://github.com/Aries-Serpent/_codex_/releases/download/v${RELEASE_VERSION}/codex-${RELEASE_VERSION}.tar.gz
sha256sum -c codex-${RELEASE_VERSION}.tar.gz.sha256 || { echo "Checksum verification failed"; exit 1; }

# Step 2: Backup current installation
echo "[$(date)] Backing up current installation..."
cp -r ${INSTALL_PATH} ${BACKUP_PATH}/codex_$(date +%Y%m%d_%H%M%S)

# Step 3: Stop service
echo "[$(date)] Stopping ${SERVICE_NAME} service..."
systemctl stop ${SERVICE_NAME}

# Step 4: Extract and install
echo "[$(date)] Installing v${RELEASE_VERSION}..."
cd /tmp
tar xzf codex-${RELEASE_VERSION}.tar.gz
cd codex-${RELEASE_VERSION}
pip install --upgrade -e .

# Step 5: Restart service
echo "[$(date)] Starting ${SERVICE_NAME} service..."
systemctl start ${SERVICE_NAME}

# Step 6: Verify deployment
echo "[$(date)] Verifying deployment..."
sleep 5
if systemctl is-active --quiet ${SERVICE_NAME}; then
  echo "[$(date)] ✅ Deployment successful!"
  codex --version
else
  echo "[$(date)] ❌ Deployment failed - rolling back"
  systemctl stop ${SERVICE_NAME}
  rm -rf ${INSTALL_PATH}
  cp -r ${BACKUP_PATH}/codex_previous ${INSTALL_PATH}
  systemctl start ${SERVICE_NAME}
  exit 1
fi
```

### 2.2 Kubernetes Deployment

**Duration:** 5-10 minutes  
**Downtime:** 0 (rolling update)  
**Rollback Time:** <1 minute

```yaml
# deployment-v0.1.0-final.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: codex
  namespace: production
  labels:
    app: codex
    version: v0.1.0-final
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: codex
  template:
    metadata:
      labels:
        app: codex
        version: v0.1.0-final
    spec:
      containers:
      - name: codex
        image: ghcr.io/aries-serpent/codex:v0.1.0-final
        imagePullPolicy: IfNotPresent

        # Port configuration
        ports:
        - name: http
          containerPort: 8080
          protocol: TCP

        # Environment variables
        env:
        - name: CODEX_LOG_LEVEL
          value: "INFO"
        - name: CODEX_METRICS_ENABLED
          value: "true"
        - name: CODEX_SECURITY_MODE
          value: "strict"

        # Resource limits
        resources:
          requests:
            cpu: 500m
            memory: 512Mi
          limits:
            cpu: 2000m
            memory: 2Gi

        # Health checks
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 30
          timeoutSeconds: 5
          failureThreshold: 3

        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3

        # Security context
        securityContext:
          runAsNonRoot: true
          runAsUser: 1000
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL

      # Pod disruption budget
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - codex
              topologyKey: kubernetes.io/hostname

---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: codex-pdb
  namespace: production
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: codex
```

**Deployment Steps:**

```bash
# Step 1: Apply new deployment
kubectl apply -f deployment-v0.1.0-final.yaml

# Step 2: Monitor rolling update
kubectl rollout status deployment/codex -n production --timeout=5m

# Step 3: Verify new replicas
kubectl get pods -n production -l app=codex

# Step 4: Check service endpoints
kubectl get endpoints codex -n production

# Step 5: Validate application readiness
kubectl exec -it $(kubectl get pod -l app=codex -n production -o jsonpath='{.items[0].metadata.name}') -n production -- \
  curl localhost:8080/health
```

### 2.3 Docker Compose Deployment

**Duration:** 5 minutes  
**Downtime:** 1-2 minutes  
**Rollback Time:** <2 minutes

```yaml
# docker-compose.yml

version: '3.9'

services:
  codex:
    image: ghcr.io/aries-serpent/codex:v0.1.0-final
    container_name: codex
    restart: unless-stopped

    environment:
      CODEX_LOG_LEVEL: INFO
      CODEX_METRICS_ENABLED: "true"
      CODEX_SECURITY_MODE: "strict"
      POSTGRES_HOST: db
      POSTGRES_PORT: "5432"
      POSTGRES_DB: codex
      POSTGRES_USER: codex
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-changeme}

    ports:
      - "8080:8080"

    volumes:
      - ./config:/etc/codex:ro
      - ./data:/var/lib/codex
      - ./logs:/var/log/codex

    depends_on:
      db:
        condition: service_healthy

    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s

    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "10"

  db:
    image: postgres:14-alpine
    container_name: codex-db
    restart: unless-stopped

    environment:
      POSTGRES_DB: codex
      POSTGRES_USER: codex
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-changeme}

    volumes:
      - ./postgres_data:/var/lib/postgresql/data

    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U codex"]
      interval: 10s
      timeout: 5s
      retries: 5
```

**Deployment Steps:**

```bash
# Step 1: Pull latest images
docker-compose pull

# Step 2: Stop current services
docker-compose stop codex

# Step 3: Backup database
docker-compose exec -T db pg_dump codex > backup_$(date +%Y%m%d_%H%M%S).sql

# Step 4: Start new services
docker-compose up -d codex

# Step 5: Verify services
docker-compose ps
docker-compose logs -f codex --tail=20
```

---

## 3. POST-DEPLOYMENT VALIDATION

### 3.1 Health Check Procedures

```bash
#!/bin/bash
# Post-Deployment Validation Script

echo "=== POST-DEPLOYMENT VALIDATION ==="

# Check service status
echo "[1] Checking service status..."
systemctl is-active --quiet codex && echo "✅ Service running" || echo "❌ Service not running"

# Check application health
echo "[2] Checking application health..."
curl -s http://localhost:8080/health | jq .
# Expected: {"status": "healthy", "timestamp": "2026-06-21T..."}

# Check database connectivity
echo "[3] Checking database connectivity..."
curl -s http://localhost:8080/ready | jq .
# Expected: {"ready": true, "database": "connected"}

# Check version
echo "[4] Checking deployed version..."
curl -s http://localhost:8080/version | jq .
# Expected: {"version": "0.1.0-final"}

# Check critical modules
echo "[5] Checking critical modules..."
curl -s http://localhost:8080/metrics | grep module_load_failures
# Expected: Low or zero failures

# Performance baseline
echo "[6] Recording performance baseline..."
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8080/
# Expected: Response time < 200ms

# Check logs for errors
echo "[7] Checking logs for errors..."
journalctl -u codex -n 50 | grep -E "ERROR|CRITICAL" || echo "✅ No errors found"

# Verify security posture
echo "[8] Verifying security posture..."
curl -s http://localhost:8080/security/status | jq .
# Expected: {"security_mode": "strict", "codeql_status": "approved"}

echo "=== VALIDATION COMPLETE ==="
```

### 3.2 Integration Testing

```bash
#!/bin/bash
# Integration Test Suite

echo "=== RUNNING INTEGRATION TESTS ==="

# Test 1: API endpoint functionality
echo "[Test 1] API endpoints..."
pytest tests/integration/test_api_v0_1_0.py -v

# Test 2: Database operations
echo "[Test 2] Database operations..."
pytest tests/integration/test_database.py -v

# Test 3: Security operations
echo "[Test 3] Security operations..."
pytest tests/integration/test_security.py -v

# Test 4: Performance benchmarks
echo "[Test 4] Performance benchmarks..."
pytest tests/performance/test_benchmarks.py -v

# Test 5: Error recovery
echo "[Test 5] Error recovery..."
pytest tests/integration/test_resilience.py -v

echo "=== TESTS COMPLETE ==="
```

---

## 4. MONITORING & ALERTING

### 4.1 Prometheus Configuration

```yaml
# prometheus.yml

global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    monitor: 'codex-v0.1.0-final'

scrape_configs:
  - job_name: 'codex'
    static_configs:
      - targets: ['localhost:8080']
    metrics_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'codex-detailed'
    static_configs:
      - targets: ['localhost:8080']
    metrics_path: '/metrics/detailed'
    scrape_interval: 30s
```

### 4.2 Grafana Dashboards

**Key Metrics to Monitor:**

```
Application Health:
├─ Uptime percentage (target: ≥99.9%)
├─ Request latency (p95: <200ms)
├─ Error rate (target: <0.1%)
└─ Active connections

Resource Usage:
├─ CPU utilization (target: <80%)
├─ Memory usage (target: <70%)
├─ Disk I/O (target: <100 IOPS)
└─ Network I/O

Security:
├─ CodeQL alert status
├─ CVE scan results
├─ Failed authentication attempts
└─ Unauthorized API calls

Tests:
├─ Test pass rate (target: 100%)
├─ Coverage percentage
├─ Mutation score
└─ New test failures
```

### 4.3 Alert Rules

```yaml
# alerting_rules.yml

groups:
  - name: codex_v0.1.0_final
    rules:

      # Critical alerts
      - alert: CodexServiceDown
        expr: up{job="codex"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Codex service down"

      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.01
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"

      # High priority alerts
      - alert: HighCPUUsage
        expr: process_cpu_seconds_total > 80
        for: 10m
        labels:
          severity: high
        annotations:
          summary: "High CPU usage"

      - alert: HighMemoryUsage
        expr: process_resident_memory_bytes / 1024 / 1024 > 1500
        for: 10m
        labels:
          severity: high
        annotations:
          summary: "High memory usage"

      # Medium priority alerts
      - alert: SlowResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 0.2
        for: 10m
        labels:
          severity: medium
        annotations:
          summary: "Slow response times"
```

### 4.4 Alerting Channels

- **PagerDuty:** Critical alerts (immediate page)
- **Slack:** High/Medium alerts (channel notification)
- **Email:** Daily summary report
- **Dashboard:** Real-time monitoring interface

---

## 5. INCIDENT RESPONSE PROCEDURES

### 5.1 Common Issues & Solutions

#### Issue 1: Service Fails to Start

**Symptoms:** Service exits immediately, systemctl shows `Failed`

**Diagnosis:**
```bash
# Check systemd status
systemctl status codex

# Check recent logs
journalctl -u codex -n 100

# Check configuration validity
codex --config /etc/codex/config.yaml --validate
```

**Resolution:**
```bash
# Option 1: Reload configuration
systemctl reload codex

# Option 2: Restart with clean state
systemctl stop codex
rm -rf /var/lib/codex/cache/*
systemctl start codex

# Option 3: Check dependencies
pip check
pip install --upgrade -e .
```

#### Issue 2: High Memory Usage

**Symptoms:** Memory gradually increases, OOM killer triggered

**Diagnosis:**
```bash
# Check memory trends
ps aux | grep codex | grep -v grep

# Profile memory usage
python -m memory_profiler codex

# Check for memory leaks
python -m tracemalloc codex
```

**Resolution:**
```bash
# Restart service (restart schedule daily during off-peak)
systemctl restart codex

# Increase available memory (if possible)
# Edit /etc/default/codex, add JAVA_OPTS or similar

# Enable memory monitoring and alerting
curl -X POST http://localhost:8080/config/memory_limit?threshold=80
```

#### Issue 3: Slow Response Times

**Symptoms:** API response time >500ms, user timeouts

**Diagnosis:**
```bash
# Check database query performance
curl http://localhost:8080/metrics/db_queries?top=10

# Check slow log
tail -100 /var/log/codex/slow.log

# Profile application
python -m cProfile -s cumtime codex
```

**Resolution:**
```bash
# Increase number of worker processes
# Edit /etc/codex/config.yaml: workers: 4 → 8

# Enable query caching
curl -X POST http://localhost:8080/config/cache?ttl=3600

# Optimize database indexes
codex-admin migrate --optimize-indexes

# Restart service
systemctl restart codex
```

### 5.2 Escalation Matrix

| Issue | Severity | On-Call | Escalation | SLA |
|-------|----------|---------|-----------|-----|
| Service down | Critical | DevOps | VP Eng, CTO | 15min |
| High error rate | High | Senior DevOps | Director | 30min |
| Performance degradation | High | SRE | Team Lead | 1hour |
| Memory leak | Medium | Backend Dev | Team Lead | 4hours |
| Configuration drift | Low | Junior | Team Lead | 8hours |

### 5.3 Post-Incident Procedure

```bash
#!/bin/bash
# Post-Incident Review Procedure

INCIDENT_ID=$1
INCIDENT_TIME=$2

echo "=== POST-INCIDENT REVIEW ==="

# Step 1: Collect logs
echo "Collecting logs..."
journalctl -u codex --since "$INCIDENT_TIME" -n 500 > incident_logs_${INCIDENT_ID}.txt

# Step 2: Collect metrics
echo "Collecting metrics..."
curl -s http://localhost:8080/metrics/incident_report?id=${INCIDENT_ID} > metrics_${INCIDENT_ID}.json

# Step 3: Document timeline
echo "Document incident timeline in: incident_report_${INCIDENT_ID}.md"

# Step 4: Create remediation tasks
echo "Create remediation PRs if needed"

# Step 5: Schedule post-mortem
echo "Schedule post-mortem meeting for team review"

echo "=== REVIEW COMPLETE ==="
```

---

## 6. PERFORMANCE BASELINES & SLAs

### 6.1 Service Level Objectives

```
Performance SLAs (v0.1.0-final):

Availability:
  ├─ Uptime target: 99.9% (±8h 45m downtime/month)
  └─ Recovery time: <2 minutes

Response Time:
  ├─ p50 (median): <50ms
  ├─ p95 (95th): <200ms
  ├─ p99 (99th): <500ms
  └─ p99.9 (99.9th): <2 seconds

Throughput:
  ├─ Minimum: 100 req/sec
  ├─ Target: 1,000 req/sec
  └─ Maximum: 5,000 req/sec

Error Rates:
  ├─ 4xx errors: <1%
  ├─ 5xx errors: <0.1%
  └─ Timeouts: <0.05%

Resource Usage:
  ├─ CPU: <80% under peak load
  ├─ Memory: <2GB per instance
  ├─ Disk: <80% utilization
  └─ Network: <50% capacity
```

### 6.2 Performance Baseline Tests

```bash
#!/bin/bash
# Performance Baseline Measurement

echo "=== PERFORMANCE BASELINE TEST ==="

# Warmup
echo "Warmup (30s)..."
ab -n 1000 -c 10 http://localhost:8080/ > /dev/null 2>&1

# Test 1: Latency
echo "Test 1: Latency (10k requests, 50 concurrent)..."
ab -n 10000 -c 50 -g latency_baseline.tsv http://localhost:8080/ | grep "Requests per second"

# Test 2: Throughput
echo "Test 2: Throughput (30 second duration)..."
ab -t 30 -c 100 http://localhost:8080/ | grep "Requests per second"

# Test 3: Memory usage
echo "Test 3: Memory usage under load..."
ps aux | grep codex | grep -v grep

# Test 4: CPU usage
echo "Test 4: CPU usage under load..."
top -b -n 1 -p $(pidof codex) | grep codex

echo "=== BASELINE COMPLETE ==="
```

---

## 7. ROLLBACK PROCEDURES

### 7.1 Quick Rollback (Emergency)

**Duration:** <2 minutes  
**Prerequisites:** Recent backup available

```bash
#!/bin/bash
# Emergency Rollback Script

echo "INITIATING EMERGENCY ROLLBACK"
echo "Current version: $(codex --version)"

# Step 1: Stop current service
echo "[1] Stopping service..."
systemctl stop codex

# Step 2: Restore previous installation
echo "[2] Restoring previous installation..."
BACKUP_DIR=$(ls -td /backups/codex_* | head -1)
rm -rf /opt/codex
cp -r ${BACKUP_DIR} /opt/codex

# Step 3: Restore previous database (if needed)
echo "[3] Restoring database..."
BACKUP_SQL=$(ls -td /backups/*.sql | head -1)
psql codex < ${BACKUP_SQL}

# Step 4: Restart service
echo "[4] Restarting service..."
systemctl start codex

# Step 5: Verify rollback
echo "[5] Verifying rollback..."
sleep 5
if systemctl is-active --quiet codex; then
  echo "✅ Rollback successful - $(codex --version)"
else
  echo "❌ Rollback failed - MANUAL INTERVENTION REQUIRED"
  exit 1
fi
```

### 7.2 Kubernetes Rollback

```bash
# Check rollout history
kubectl rollout history deployment/codex -n production

# Rollback to previous revision
kubectl rollout undo deployment/codex -n production

# Verify rollback
kubectl rollout status deployment/codex -n production
```

### 7.3 Database Rollback

```bash
# For minor data corruption (keep application version)
psql codex < /backups/codex_YYYYMMDD_HHMMSS.sql

# For major issues (restore from backup point)
systemctl stop codex
pg_dropdb codex
pg_restore -C -d postgres /backups/codex_YYYYMMDD_HHMMSS.backup
systemctl start codex
```

---

## 8. SECURITY OPERATIONS

### 8.1 Security Monitoring

```bash
#!/bin/bash
# Security Monitoring Check

echo "=== SECURITY MONITORING ==="

# Check 1: CodeQL status
echo "[1] CodeQL alert status..."
curl -s http://localhost:8080/security/codeql_status | jq .

# Check 2: Dependency vulnerabilities
echo "[2] Checking dependencies for CVEs..."
pip-audit --desc

# Check 3: Failed authentication attempts
echo "[3] Failed authentication attempts..."
grep "authentication failed" /var/log/codex/security.log | wc -l

# Check 4: Unauthorized API access
echo "[4] Unauthorized API access..."
grep "unauthorized" /var/log/codex/security.log | tail -10

# Check 5: File integrity
echo "[5] File integrity check..."
find /opt/codex -type f -exec sha256sum {} \; > /tmp/codex_hashes.txt
diff -q /tmp/codex_hashes.txt /tmp/codex_hashes_baseline.txt

echo "=== SECURITY CHECK COMPLETE ==="
```

### 8.2 Secrets Management

```bash
# Store secrets in environment
export CODEX_DB_PASSWORD=$(aws secretsmanager get-secret-value --secret-id codex/db/password)
export CODEX_API_KEY=$(aws secretsmanager get-secret-value --secret-id codex/api/key)

# Never store secrets in:
# - Configuration files
# - Environment files (.env)
# - Source code
# - Logs or debug output

# Use HashiCorp Vault for centralized secrets
vault kv get secret/codex/credentials
```

### 8.3 Access Control

```yaml
# RBAC Configuration

roles:
  admin:
    permissions:
      - read
      - write
      - delete
      - configure
      - deploy

  operator:
    permissions:
      - read
      - write
      - restart

  viewer:
    permissions:
      - read

users:
  devops_team:
    role: admin

  sre_team:
    role: operator

  management:
    role: viewer
```

---

## 📞 SUPPORT & ESCALATION

### Support Contacts

- **On-Call DevOps:** Page via PagerDuty
- **SRE Team:** #sre-oncall Slack channel
- **Engineering Manager:** manager@company.com
- **VP Engineering:** vp-eng@company.com

### Emergency Procedures

**For CRITICAL incidents (service down):**
1. Page on-call DevOps immediately
2. Declare incident in #incidents Slack channel
3. Start incident bridge (Zoom/Teams)
4. Execute appropriate runbook (Section 5)
5. Document timeline and post-mortem

---

## 🎯 REFERENCE DOCUMENTS

- `PHASE_7B_FINAL_METRICS_DASHBOARD.md` — Metrics consolidation
- `v0.1.0-FINAL_RELEASE_NOTES.md` — Release documentation
- `PHASE_7B_PRODUCTION_READINESS_SUMMARY.md` — Approval checklist

---

**Operations Playbook Created:** 2026-06-21  
**Authority:** @mbaetiong (COPILOT_AGENT_AUTH_ENABLED=true)  
**Status:** ✅ **PRODUCTION-GRADE, READY FOR OPERATIONS TEAM**
