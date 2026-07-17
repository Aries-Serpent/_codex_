# RUNBOOK: Deployment Procedures for Codex ML Platform
**Last Updated:** 2026-07-11
**Version:** v0.2.1

**Version:** 1.0.0
**Last Updated: 2026-07-10
**Audience:** DevOps, Deployment Engineers
**SLA:** Deployment should complete in 30-60 minutes

---

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Single Machine Deployment](#single-machine-deployment)
3. [Kubernetes Cluster Deployment](#kubernetes-cluster-deployment)
4. [Post-Deployment Validation](#post-deployment-validation)
5. [Rollback Procedures](#rollback-procedures)
6. [Troubleshooting](#troubleshooting)

---

## Pre-Deployment Checklist

**Before deploying, verify:**

- [ ] All tests passing locally (`pytest tests/`)
- [ ] CI pipeline green (GitHub Actions)
- [ ] Code review approved and merged to `main`
- [ ] Deployment credentials available (GitHub token, Kubernetes access)
- [ ] Target environment accessible (SSH key, kubeconfig)
- [ ] Database backups created (if applicable)
- [ ] DNS records verified (if domain changes)
- [ ] Monitoring/alerting configured for new version
- [ ] Runback plan tested (see [Rollback Procedures](#rollback-procedures))
- [ ] Team notified of deployment window

---

## Single Machine Deployment

### Prerequisites

- Python 3.12+
- 8GB RAM minimum (16GB recommended)
- 50GB free disk space
- Internet connection (for pip install)

### Deployment Steps

#### Step 1: SSH into Target Machine

```bash
ssh -i /path/to/key deployment@codex.example.com

# Verify Python version
python3 --version
# Expected: Python 3.12.x
```

#### Step 2: Clone Repository (or Pull Latest)

```bash
# First time deployment
git clone https://github.com/Aries-Serpent/_codex_.git
cd _codex_

# Subsequent deployments
cd /opt/codex
git fetch origin
git checkout main
git pull origin main
```

#### Step 3: Backup Current Installation

```bash
# Stop running services first
sudo systemctl stop codex-api
sudo systemctl stop codex-worker

# Backup database
sqlite3 /var/lib/codex/codex.db ".dump" > /var/backups/codex_backup_$(date +%Y%m%d_%H%M%S).sql

# Backup models
tar -czf /var/backups/codex_models_$(date +%Y%m%d_%H%M%S).tar.gz \
 /var/lib/codex/models/

echo " Backup complete"
```

#### Step 4: Install/Update Dependencies

```bash
# Create virtual environment (first time)
python3 -m venv /opt/codex/venv

# Activate virtual environment
source /opt/codex/venv/bin/activate

# Install dependencies (pins exact versions for reproducibility)
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Install package in development mode
pip install -e .

# Verify installation
python -c "import codex; print(codex.__version__)"
```

#### Step 5: Update Configuration

```bash
# Verify config exists
ls -la /etc/codex/config.yaml

# If not exists, copy from template
sudo cp config/defaults.yaml /etc/codex/config.yaml

# Edit configuration for target environment
sudo nano /etc/codex/config.yaml
# Update:
# - model_path
# - data_path
# - log_level
# - api_port

# Validate configuration
python -m codex.validate_config /etc/codex/config.yaml
```

#### Step 6: Load Secrets

```bash
# Create .env file (should not be committed to repo)
cat > /opt/codex/.env << EOF
OPENAI_API_KEY=your-actual-key-here
DB_PASSWORD=your-db-password-here
JWT_SECRET=your-jwt-secret-here
SENTRY_DSN=your-sentry-dsn-here
EOF

# Set permissions (readable only by codex user)
chmod 600 /opt/codex/.env

# Verify secrets loaded
source /opt/codex/.env
echo " Secrets loaded"
```

#### Step 7: Migrate Database (if needed)

```bash
# Check current schema version
python -m codex.db.migrate --status

# Run migrations
python -m codex.db.migrate --upgrade

# Verify migration
python -m codex.db.migrate --status
# Should show latest version
```

#### Step 8: Start Services

```bash
# Start API service
sudo systemctl start codex-api

# Start background worker (if applicable)
sudo systemctl start codex-worker

# Verify services running
sudo systemctl status codex-api
sudo systemctl status codex-worker

# Check logs
sudo journalctl -u codex-api -n 50 -f
```

#### Step 9: Verify Deployment

See [Post-Deployment Validation](#post-deployment-validation) below.

---

## Kubernetes Cluster Deployment

### Prerequisites

- Kubernetes 1.24+
- kubectl configured to access cluster
- Docker image built and pushed to registry
- Helm chart updated with new version

### Deployment Steps

#### Step 1: Build and Push Docker Image

```bash
# Build image
docker build -t codex-ml:v0.2.1 .

# Tag for registry
docker tag codex-ml:v0.2.1 registry.example.com/codex-ml:v0.2.1

# Push to registry
docker push registry.example.com/codex-ml:v0.2.1

# Verify push
docker pull registry.example.com/codex-ml:v0.2.1
```

#### Step 2: Update Helm Values

```yaml
# values-prod.yaml
image:
 repository: registry.example.com/codex-ml
 tag: v0.2.1
 pullPolicy: IfNotPresent

replicas: 3

resources:
 requests:
 memory: "4Gi"
 cpu: "2"
 limits:
 memory: "8Gi"
 cpu: "4"

database:
 host: postgres.default.svc.cluster.local
 port: 5432
 name: codex_prod

monitoring:
 enabled: true
 prometheus: true
```

#### Step 3: Create/Update Kubernetes Resources

```bash
# Create namespace (first time)
kubectl create namespace codex-prod

# Create secrets
kubectl create secret generic codex-secrets \
 --from-literal=db-****** \
 --from-literal=api-key=your-key \
 -n codex-prod

# Apply configuration
kubectl apply -k config/kubernetes/overlays/prod/

# Verify resources created
kubectl get pods -n codex-prod
kubectl get services -n codex-prod
```

#### Step 4: Deploy with Helm

```bash
# Add Helm repository (first time)
helm repo add codex https://charts.example.com/codex
helm repo update

# Deploy
helm upgrade --install codex-prod codex/codex \
 -f values-prod.yaml \
 --namespace codex-prod \
 --version 1.0.0

# Monitor deployment
kubectl rollout status deployment/codex-api -n codex-prod

# Watch pods starting up
kubectl get pods -n codex-prod -w
```

#### Step 5: Verify Deployment

See [Post-Deployment Validation](#post-deployment-validation).

---

## Post-Deployment Validation

### Health Checks

```bash
# 1. Check service is running
curl http://localhost:8000/health
# Expected: {"status": "healthy"}

# 2. Check API is responding
curl -X POST http://localhost:8000/api/v1/inference \
 -H "Content-Type: application/json" \
 -d '{"query": "test"}'
# Expected: 200 OK with inference result

# 3. Check database connectivity
python -c "
import sqlite3
conn = sqlite3.connect('/var/lib/codex/codex.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM models')
count = cursor.fetchone()[0]
print(f' Database connected, {count} models registered')
"

# 4. Check logs for errors
tail -n 20 /var/log/codex/api.log
tail -n 20 /var/log/codex/worker.log
```

### Performance Baseline

```bash
# Run performance test
python -m codex.perf.benchmark \
 --num_requests 100 \
 --concurrency 10 \
 --timeout 30

# Expected output:
# Mean latency: 250ms (p50), 450ms (p95)
# Throughput: 40 req/sec
# Error rate: <1%
```

### Functionality Tests

```bash
# Run smoke tests
pytest tests/smoke/ -v

# Expected: All tests pass
# test_api_health
# test_inference_basic
# test_data_ingestion
# test_model_loading
```

### Monitoring Setup

```bash
# Verify Prometheus scraping
curl http://prometheus:9090/api/v1/query?query=up
# Expected: codex_api instances show up=1

# Verify Grafana dashboard
# Go to http://grafana:3000
# Dashboard "Codex Performance" should show metrics

# Set up alerts
# In Grafana: Alerts New Rule
# Alert on: error_rate > 1% or latency_p95 > 2000ms
```

---

## Rollback Procedures

### Quick Rollback (If Critical Issue)

**Use this if deployment has critical bugs:**

```bash
# 1. Stop current service
sudo systemctl stop codex-api

# 2. Restore from backup
sqlite3 /var/lib/codex/codex.db < /var/backups/codex_backup_YYYYMMDD_HHMMSS.sql

# 3. Restore previous code version
cd /opt/codex
git checkout v0.2.1

# 4. Install previous dependencies
source venv/bin/activate
pip install -r requirements.txt

# 5. Restart service
sudo systemctl start codex-api

# 6. Verify rollback successful
curl http://localhost:8000/health
```

### Gradual Rollback (Canary Rollback)

**Use this for less critical issues:**

```bash
# 1. Check current deployment
helm list -n codex-prod

# 2. Get previous release
helm history codex-prod -n codex-prod

# 3. Rollback to previous release
helm rollback codex-prod 5 -n codex-prod
# (5 is the revision number from history)

# 4. Monitor rollback
kubectl rollout status deployment/codex-api -n codex-prod

# 5. Verify
curl http://localhost:8000/health
```

### Data Recovery

**If database was corrupted:**

```bash
# 1. Find backup
ls -ltr /var/backups/codex_backup*.sql | tail -1

# 2. Restore
sqlite3 /var/lib/codex/codex.db < /var/backups/codex_backup_YYYYMMDD.sql

# 3. Verify data integrity
python -c "
import sqlite3
conn = sqlite3.connect('/var/lib/codex/codex.db')
cursor = conn.cursor()

# Check tables exist
cursor.execute(\"SELECT name FROM sqlite_master WHERE type='table'\")
tables = cursor.fetchall()
print(f' {len(tables)} tables exist')

# Check row counts
for table in tables:
 cursor.execute(f'SELECT COUNT(*) FROM {table[0]}')
 count = cursor.fetchone()[0]
 print(f' - {table[0]}: {count} rows')
"
```

---

## Troubleshooting

### Issue: Service Won't Start

**Symptom:** `systemctl status codex-api` shows failed

**Diagnostic steps:**

```bash
# 1. Check logs
sudo journalctl -u codex-api -n 100

# 2. Try starting in foreground to see error
source /opt/codex/venv/bin/activate
python -m codex.api

# 3. Check config file
python -m codex.validate_config /etc/codex/config.yaml

# 4. Check permissions
ls -la /var/lib/codex/
ls -la /var/log/codex/

# 5. Check port availability
sudo netstat -tlnp | grep 8000
```

**Resolution:**
- Fix error shown in logs
- Ensure `/var/lib/codex` and `/var/log/codex` are writable by codex user
- Ensure port 8000 is not in use by another service

### Issue: High Latency / Slow Response

**Symptom:** API responses taking >1 second

```bash
# 1. Check CPU usage
top -p $(pgrep -f 'python -m codex.api') -n 1

# 2. Check memory usage
ps aux | grep codex | grep -v grep

# 3. Check disk I/O
iostat -x 1 5

# 4. Check database performance
python -m codex.db.analyze
# Look for slow queries

# 5. Check model loading time
python -c "
import time
from codex import ModelRegistry

start = time.time()
registry = ModelRegistry()
model = registry.load('latest')
end = time.time()
print(f'Model load time: {end - start:.2f}s')
"
```

**Resolution:**
- Increase allocated memory/CPU
- Rebuild database indexes: `python -m codex.db.optimize`
- Move old models to archive: `python -m codex.model.cleanup`
- Scale horizontally (add more instances)

### Issue: Database Connection Errors

**Symptom:** `sqlite3.OperationalError: database is locked`

```bash
# 1. Check if database is being backed up
ps aux | grep sqlite

# 2. Check for abandoned connections
lsof | grep codex.db

# 3. Check file permissions
ls -la /var/lib/codex/codex.db

# 4. Check disk space
df -h /var/lib/codex/
```

**Resolution:**
- Ensure only one process accessing database at a time
- Kill abandoned processes: `kill -9 <PID>`
- Fix permissions: `chown codex:codex /var/lib/codex/codex.db`
- Free up disk space if needed

### Issue: Out of Memory

**Symptom:** Process killed, `OOM Killer` in logs

```bash
# 1. Check available memory
free -h

# 2. Check memory usage by process
ps aux --sort=-%mem | head -10

# 3. Check for memory leaks
python -m memory_profiler -m codex.api

# 4. Check garbage collection
python -c "
import gc
gc.collect()
print(gc.get_stats())
"
```

**Resolution:**
- Increase server RAM
- Reduce batch size: `model.batch_size=16` (in config)
- Enable model quantization: `model.quantize=true`
- Reduce number of replicas temporarily

---

## Rollback Decision Matrix

| Severity | Latency | Error Rate | Decision |
|----------|---------|-----------|----------|
| CRITICAL | >5s | >10% | Immediate rollback |
| HIGH | >2s | >5% | Canary rollback |
| MEDIUM | >1s | >1% | Monitor & investigate |
| LOW | Normal | <1% | Monitor |

---

## Post-Incident Review

After any deployment issue:

```bash
# 1. Collect logs
tar -czf deployment_logs_$(date +%Y%m%d_%H%M%S).tar.gz \
 /var/log/codex/ /var/logs/kubernetes/

# 2. Document incident
# Create issue: https://github.com/Aries-Serpent/_codex_/issues
# Title: "Deployment incident: [Issue Description]"
# Include:
# - When it occurred
# - Duration
# - Impact (users affected, error rate)
# - Root cause
# - Resolution
# - Prevention

# 3. Update runbook
# If this runbook was unclear or incomplete, update it
```

---

**Maintained by:** @mbaetiong
**Last tested:** 2026-07-10
**Next review:** 2026-08-10
