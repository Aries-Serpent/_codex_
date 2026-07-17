# Infrastructure Operations Manual - Codex ML
**Last Updated:** 2026-07-11
**Version:** v0.2.0

**Document Version:** 1.0.0
**Last Updated: 2026-07-08
**Authority:** Phase 12 WS3 Documentation Lane 8
**Audience:** SREs, DevOps Engineers, Operations Team
**Status:** Production Guide

---

## Table of Contents

1. [Daily Operations](#daily-operations)
2. [Scaling Procedures](#scaling-procedures)
3. [Maintenance Procedures](#maintenance-procedures)
4. [Backup & Recovery](#backup--recovery)
5. [Incident Response](#incident-response)
6. [Health Checks](#health-checks)
7. [Performance Tuning](#performance-tuning)

---

## Daily Operations

### Morning Health Check (08:00 UTC)

```bash
#!/bin/bash
# Run daily health check

echo "=== System Health Check ==="

# 1. Kubernetes cluster status
kubectl cluster-info
kubectl get nodes
kubectl get pods --all-namespaces --field-selector=status.phase!=Running

# 2. Service status
kubectl get services -n codex

# 3. Database health
kubectl exec postgres-0 -- pg_isready -U postgres

# 4. Storage status
kubectl get pvc --all-namespaces

# 5. Metrics pipeline
curl http://prometheus:9090/-/healthy

# 6. Alert status
curl http://alertmanager:9093/api/v1/alerts | jq '.data[] | select(.status.state=="firing")'

# 7. Recent errors in logs
kubectl logs -n codex deployment/api-server --tail=100 | grep -i error
```

### Metrics Dashboard Review

**Daily metrics to monitor:**

| Metric | Normal Range | Alert Threshold |
|--------|--------------|-----------------|
| API Error Rate | <1% | >5% for 5min |
| Model Server Latency (p50) | <200ms | >500ms for 5min |
| GPU Utilization | 60-90% | >95% sustained |
| Memory Usage | 50-80% | >90% for 10min |
| Disk Usage | <70% | >80% for 30min |
| Control Plane API Latency | <100ms | >500ms for 5min |

### Log Review

```bash
# Check for errors in past hour
kubectl logs -n codex --since=1h --timestamps=true \
 -l app=api-server | grep -i error

# Check training job logs
kubectl logs -n codex job/training-job-123

# Real-time log tail
kubectl logs -f -n codex deployment/api-server
```

### Backup Verification

```bash
# Verify database backups completed
aws s3 ls s3://codex-backups/postgres/ --recursive \
 | tail -10

# Check backup size and timestamps
aws s3 ls s3://codex-backups/postgres/daily/ --recursive
```

---

## Scaling Procedures

### Horizontal Pod Autoscaling (HPA)

#### Check Current Scaling Status

```bash
# View HPA status
kubectl get hpa -n codex

# Detailed HPA metrics
kubectl describe hpa api-server-hpa -n codex

# View metrics
kubectl get --raw /apis/custom.metrics.k8s.io/v1beta1/namespaces/codex/pods/*/cpu_usage
```

#### Manual Scaling

```bash
# Scale API servers to 5 replicas
kubectl scale deployment api-server -n codex --replicas=5

# Scale model server to 3 replicas
kubectl scale deployment model-server -n codex --replicas=3

# Verify scaling
kubectl rollout status deployment/api-server -n codex
```

#### HPA Configuration

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
 name: api-server-hpa
 namespace: codex
spec:
 scaleTargetRef:
 apiVersion: apps/v1
 kind: Deployment
 name: api-server
 minReplicas: 2
 maxReplicas: 10
 metrics:
 - type: Resource
 resource:
 name: cpu
 target:
 type: Utilization
 averageUtilization: 70
 - type: Resource
 resource:
 name: memory
 target:
 type: Utilization
 averageUtilization: 80
 behavior:
 scaleDown:
 stabilizationWindowSeconds: 300
 policies:
 - type: Percent
 value: 50
 periodSeconds: 15
 scaleUp:
 stabilizationWindowSeconds: 0
 policies:
 - type: Percent
 value: 100
 periodSeconds: 15
 - type: Pods
 value: 2
 periodSeconds: 15
```

### Vertical Scaling (Node Upgrade)

```bash
# 1. Drain node to reschedule pods
kubectl drain node-1 --ignore-daemonsets --delete-emptydir-data

# 2. Upgrade node instance type (cloud console)
# - Stop instance
# - Change instance type
# - Start instance

# 3. Uncordon node to re-enable scheduling
kubectl uncordon node-1

# 4. Verify node is ready
kubectl get nodes node-1 -o wide
```

### Database Scaling

#### PostgreSQL Scaling

```sql
-- Check current connections
SELECT datname, count(*) as connections 
FROM pg_stat_activity 
GROUP BY datname;

-- Increase max connections (requires restart)
ALTER SYSTEM SET max_connections = 400;

-- Apply configuration
SELECT pg_reload_conf();
```

#### Redis Scaling (Cluster)

```bash
# Check cluster status
redis-cli --cluster info localhost:6379

# Add node to cluster
redis-cli --cluster add-node 192.168.1.100:6379 192.168.1.1:6379

# Rebalance cluster
redis-cli --cluster rebalance 192.168.1.1:6379
```

---

## Maintenance Procedures

### Rolling Updates

#### Update API Service

```bash
# 1. Update image
kubectl set image deployment/api-server \
 api-server=codex/api-server:v0.2.0 \
 -n codex

# 2. Monitor rollout
kubectl rollout status deployment/api-server -n codex

# 3. Verify endpoints
kubectl get endpoints api-server -n codex

# 4. Rollback if needed
kubectl rollout undo deployment/api-server -n codex
```

#### Update Models

```bash
# 1. Create new model deployment
kubectl apply -f model-server-v2.yaml

# 2. Test with canary (5% traffic)
kubectl patch virtualservice api-traffic -n codex \
 --type merge -p '{"spec":{"hosts":[{"name":"model-server","subsets":[{"name":"v1","weight":95},{"name":"v2","weight":5}]}]}}'

# 3. Monitor metrics for v2
kubectl logs -n codex deployment/model-server-v2 --follow

# 4. Gradually increase traffic
# 5% 25% 50% 100% (over 30 minutes)
kubectl patch virtualservice...

# 6. Remove old version
kubectl delete deployment model-server-v1 -n codex
```

### Node Maintenance

#### OS Patching

```bash
# 1. Mark node for maintenance
kubectl cordon node-1

# 2. Drain pods
kubectl drain node-1 --ignore-daemonsets --delete-emptydir-data --timeout=10m

# 3. Apply patches (cloud console or SSH)
# ssh node-1 'sudo yum update -y'

# 4. Reboot if needed
# ssh node-1 'sudo reboot'

# 5. Verify node readiness
kubectl get nodes node-1 -o wide

# 6. Uncordon node
kubectl uncordon node-1
```

### Database Maintenance

#### PostgreSQL Vacuum & Analyze

```bash
# Connected to PostgreSQL container
kubectl exec -it postgres-0 -n codex -- psql -U postgres

-- Run maintenance
VACUUM ANALYZE;

-- Check table bloat
SELECT schemaname, tablename, 
 pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Rebuild indexes if needed
REINDEX DATABASE codex;
```

#### Index Maintenance

```bash
# Check unused indexes
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;

-- Drop unused indexes
DROP INDEX CONCURRENTLY unused_index_name;
```

---

## Backup & Recovery

### Backup Strategy

#### Automated Daily Backups

```bash
# Kubernetes cron job for database backups
kubectl apply -f - <<EOF
apiVersion: batch/v1
kind: CronJob
metadata:
 name: postgres-backup
 namespace: codex
spec:
 schedule: "0 2 * * *" # 02:00 UTC daily
 jobTemplate:
 spec:
 template:
 spec:
 containers:
 - name: backup
 image: codex/backup:latest
 command:
 - /bin/bash
 - -c
 - |
 pg_dump -U postgres codex | gzip | \
 aws s3 cp - s3://codex-backups/postgres/daily/\$(date +%Y-%m-%d).sql.gz
 restartPolicy: OnFailure
EOF
```

#### Point-in-Time Recovery

```bash
# Enable WAL archiving (configure once)
ALTER SYSTEM SET wal_level = replica;
ALTER SYSTEM SET max_wal_senders = 3;
ALTER SYSTEM SET wal_keep_size = '1GB';

-- WAL archiving to S3
ALTER SYSTEM SET archive_mode = on;
ALTER SYSTEM SET archive_command = 
 'aws s3 cp pg_wal/%f s3://codex-backups/wal/';

-- Reload configuration
SELECT pg_reload_conf();
```

### Recovery Procedures

#### Database Recovery from Backup

```bash
# 1. Identify backup to restore
aws s3 ls s3://codex-backups/postgres/daily/

# 2. Download backup
aws s3 cp s3://codex-backups/postgres/daily/2024-07-05.sql.gz - | gunzip > backup.sql

# 3. Stop applications
kubectl scale deployment api-server -n codex --replicas=0

# 4. Create temporary database for restoration
kubectl exec -it postgres-0 -n codex -- psql -U postgres -c "CREATE DATABASE codex_restore;"

# 5. Restore backup
kubectl exec -it postgres-0 -n codex -- psql -U postgres codex_restore < backup.sql

# 6. Verify restored data
kubectl exec -it postgres-0 -n codex -- psql -U postgres codex_restore -c "SELECT COUNT(*) FROM models;"

# 7. Swap databases (if successful)
# Rename codex codex_old, codex_restore codex

# 8. Restart applications
kubectl scale deployment api-server -n codex --replicas=3
```

#### Model Artifacts Recovery

```bash
# 1. List available model versions
aws s3 ls s3://codex-ml-artifacts/models/ --recursive

# 2. Restore specific model
aws s3 cp s3://codex-ml-artifacts/models/model-v1.0/weights.pt ./

# 3. Verify integrity
md5sum weights.pt
aws s3 cp s3://codex-ml-artifacts/models/model-v1.0/weights.pt.md5 ./
md5sum -c weights.pt.md5
```

---

## Incident Response

### Incident Severity Levels

| Severity | Impact | Response Time | SLA |
|----------|--------|----------------|-----|
| **P1** | Complete service outage | <15 min | 4 hours resolution |
| **P2** | Degraded service (>5% errors) | <30 min | 8 hours resolution |
| **P3** | Minor issues, workarounds exist | <2 hours | 24 hours resolution |
| **P4** | Low-impact, no immediate fix needed | Best effort | 1 week |

### P1 Incident: API Service Down

```bash
# 1. Confirm incident
kubectl get deployment api-server -n codex
kubectl get pods -n codex -l app=api-server

# 2. Check logs
kubectl logs -n codex deployment/api-server --tail=200

# 3. Check resources
kubectl describe nodes
kubectl top pods -n codex

# 4. Restart deployment
kubectl rollout restart deployment/api-server -n codex

# 5. If restart doesn't help, rollback
kubectl rollout undo deployment/api-server -n codex

# 6. If still down, check database
kubectl exec -it postgres-0 -n codex -- psql -U postgres -c "SELECT 1;"

# 7. Verify DNS/networking
kubectl run -it --rm debug --image=nicolaka/netshoot -- /bin/bash
nslookup api-server.codex.svc.cluster.local
curl http://api-server:8080/health
```

### P2 Incident: High Error Rate (>5%)

```bash
# 1. Query error metrics
curl 'http://prometheus:9090/api/v1/query?query=rate(api_errors_total[5m])'

# 2. Check specific error messages
kubectl logs -n codex deployment/api-server --grep=error | tail -50

# 3. Check recent changes
git log --oneline -20 | head -10

# 4. Check resource contention
kubectl top pods -n codex | grep -E "api-server|model-server"

# 5. If resource issue, scale up
kubectl scale deployment api-server -n codex --replicas=8

# 6. Monitor recovery
watch -n 5 'curl http://prometheus:9090/api/v1/query?query=rate(api_errors_total[5m]) | jq'
```

### Incident Communication

```
---
# Incident Report Template

**Incident ID:** INC-2024-07-08-001
**Start Time:** 2024-07-08 14:30:00 UTC
**Severity:** P2

**Description:**
API service showing elevated error rate (8.5%), affecting ~2% of users

**Root Cause:**
Model server replica ran out of GPU memory due to longer inference chains

**Resolution Timeline:**
- 14:30: Error rate detected (alerts fired)
- 14:32: On-call engineer acknowledged
- 14:35: Identified GPU memory exhaustion
- 14:38: Restarted model-server pods
- 14:42: Error rate returned to normal (<1%)
- 15:00: RCA initiated

**Impact:**
- Duration: 12 minutes
- Affected Users: ~2% (estimated)
- Requests Failed: 847/98,234
- Revenue Impact: Minimal

**Prevention:**
1. Lower GPU memory alert threshold from 95% to 85%
2. Add GPU memory pre-checks in request handler
3. Implement request queuing with backpressure

---
```

---

## Health Checks

### Application Health Check Endpoints

```bash
# Liveness probe (Is service running?)
curl http://api-server:8080/health/live
# Response: 200 OK

# Readiness probe (Is service ready for traffic?)
curl http://api-server:8080/health/ready
# Response: 200 OK if ready, 503 if draining

# Detailed health status
curl http://api-server:8080/health/status
# Response:
# {
# "status": "healthy",
# "timestamp": "2024-07-08T15:30:00Z",
# "checks": {
# "database": "ok",
# "cache": "ok",
# "storage": "ok"
# }
# }
```

### Infrastructure Health Checks

```bash
# Kubernetes API server
kubectl cluster-info

# etcd health
kubectl exec -it etcd-0 -n kube-system -- etcdctl endpoint health

# Kubelet
curl -k https://localhost:10250/healthz

# Scheduler and controller manager
kubectl get componentstatus

# Network connectivity
kubectl run -it --rm netcheck --image=nicolaka/netshoot -- \
 bash -c "for i in {1..5}; do curl -s http://api-server:8080/health; done"
```

### Database Health Checks

```sql
-- Connection pool status
SELECT datname, count(*) as connections 
FROM pg_stat_activity 
WHERE state = 'active'
GROUP BY datname;

-- Replication lag (for replicas)
SELECT slot_name, restart_lsn, confirmed_flush_lsn 
FROM pg_replication_slots;

-- Query performance
SELECT query, mean_time, max_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC LIMIT 10;

-- Table bloat
SELECT schemaname, tablename, 
 round(100 * (pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) / pg_total_relation_size(schemaname||'.'||tablename)) AS bloat_percent
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY bloat_percent DESC;
```

---

## Performance Tuning

### API Server Optimization

```yaml
# Tuning parameters
performance_tuning:
 # Connection pooling
 database:
 pool_size: 20
 max_overflow: 10
 pool_recycle: 3600
 
 # HTTP settings
 http:
 worker_threads: 8
 keepalive_timeout: 30
 request_timeout: 60
 
 # Caching
 cache:
 enabled: true
 backend: redis
 ttl: 3600
 max_size: 1000000
 
 # Compression
 compression:
 enabled: true
 min_size_bytes: 1024
 level: 6
```

### Database Optimization

```sql
-- Create missing indexes
CREATE INDEX idx_models_status ON models(status) 
WHERE status != 'archived';

CREATE INDEX idx_requests_created_user ON inference_requests(created_at DESC, user_id)
WHERE status = 'completed';

-- Analyze table statistics
ANALYZE models;
ANALYZE inference_requests;

-- Vacuum full (maintenance window only)
VACUUM FULL ANALYZE models;

-- Enable query parallelization
ALTER SYSTEM SET max_parallel_workers_per_gather = 4;
ALTER SYSTEM SET max_parallel_maintenance_workers = 4;
SELECT pg_reload_conf();
```

### GPU Optimization

```bash
# Check GPU utilization per process
nvidia-smi --query-compute-apps=gpu_uuid,pid,gpu_memory_usage --format=csv

# Monitor GPU performance
watch -n 1 nvidia-smi

# Set GPU clock scaling (persistence mode)
nvidia-smi -pm 1
nvidia-smi -lmc 1215 # Lock memory clock to 1215 MHz
nvidia-smi -lgc 1410 # Lock GPU clock to 1410 MHz

# Monitor GPU memory fragmentation
nvidia-smi --query-gpu=memory.used,memory.free --format=csv --loop=1
```

### Network Optimization

```bash
# Check for packet loss
ping -c 100 <target> | grep loss

# Monitor network interface
iftop -n # Interface top

# Check TCP metrics
netstat -s | grep -E "retransmit|dropped"

# Optimize network settings
sysctl -w net.core.somaxconn=65535
sysctl -w net.ipv4.tcp_max_syn_backlog=65535
```

---

## On-Call Runbook

### Escalation Contacts

```
Level 1 (Triage): @platform-on-call
 - Verify incident impact
 - Check dashboards
 - Restart services
 
Level 2 (Debugging): @platform-lead
 - Root cause analysis
 - Database debugging
 - Infrastructure changes
 
Level 3 (Executive): @vp-engineering
 - Major data loss
 - Complete outage >30min
 - Customer communication
```

### Quick Fixes Checklist

```
[ ] Check if it's a known issue
 - Review incidents list
 - Check #incidents Slack channel

[ ] Try standard troubleshooting
 - Restart service: kubectl rollout restart deployment/...
 - Check logs: kubectl logs -f deployment/...
 - Check resources: kubectl top pods
 
[ ] Monitor recovery
 - Watch dashboards
 - Check error rates
 - Verify customer impact

[ ] Document if resolved
 - Create post-mortem
 - Update runbook
 - Notify stakeholders
```

---

## See Also

- [Infrastructure Architecture](INFRASTRUCTURE_ARCHITECTURE.md)
- [Technical Reference](TECHNICAL_REFERENCE.md)
- [Deployment Guides](../deployment/)
- [Troubleshooting Guide](../deployment/TROUBLESHOOTING_GUIDE.md)

---

**Document Maintenance:**
- Review quarterly
- Update after each incident
- Test procedures annually

