# Operational Procedures & Maintenance Guide
**Last Updated:** 2026-07-11
**Version:** v0.2.0

**Last Updated**: 2026-07-08
**Version**: 1.0
**Audience**: Operations teams, DevOps engineers, platform engineers
**Tier**: Production-Ready

---

## Table of Contents

1. [Daily Operational Procedures](#daily-operational-procedures)
2. [Database Management](#database-management)
3. [Backup & Recovery](#backup--recovery)
4. [Performance Tuning](#performance-tuning)
5. [Security Hardening](#security-hardening)
6. [Scaling Procedures](#scaling-procedures)
7. [Maintenance Windows](#maintenance-windows)

---

## Daily Operational Procedures

### Morning Health Check

**Duration**: 15 minutes
**Frequency**: Daily at 8:00 AM

```bash
#!/bin/bash
# morning-health-check.sh

echo "=== Codex ML Daily Health Check ==="
echo "Timestamp: $(date)"

# 1. Check cluster health
echo -e "\n[CLUSTER] Checking Kubernetes cluster health..."
kubectl get nodes
NODES=$(kubectl get nodes --no-headers | wc -l)
echo " Active nodes: $NODES"

# 2. Check pod status
echo -e "\n[PODS] Checking pod status..."
kubectl get pods --all-namespaces --field-selector=status.phase!=Running,status.phase!=Succeeded
CRASHED=$(kubectl get pods -A --field-selector=status.phase=Failed | wc -l)
if [ $CRASHED -gt 0 ]; then
 echo " WARNING: $CRASHED crashed pods found"
else
 echo " All pods running normally"
fi

# 3. Check storage
echo -e "\n[STORAGE] Checking persistent volumes..."
kubectl get pvc -A
kubectl get pv | grep -v "Bound" || echo " All PVs properly bound"

# 4. Check database
echo -e "\n[DATABASE] Checking database connectivity..."
kubectl exec -it deployment/postgres -n data-layer -- \
 psql -U codex_admin -d codex -c "SELECT count(*) FROM pg_stat_activity;"
echo " Database responding"

# 5. Check Redis
echo -e "\n[CACHE] Checking Redis cache..."
kubectl exec -it deployment/redis -n data-layer -- \
 redis-cli ping
echo " Cache responding"

# 6. Check API health
echo -e "\n[API] Checking API endpoint..."
curl -s http://codex-ml-service:80/health | jq .
echo " API responding"

# 7. Review alerts
echo -e "\n[ALERTS] Recent critical alerts..."
kubectl get events -A --sort-by='.lastTimestamp' | tail -10

echo -e "\n=== Health Check Complete ==="
```

### Weekly Review

**Duration**: 1 hour
**Frequency**: Every Monday at 9:00 AM

```bash
#!/bin/bash
# weekly-review.sh

echo "=== Weekly Operational Review ==="

# 1. Review logs for errors
echo -e "\n[LOGS] Error rate last 7 days..."
kubectl logs -f deployment/codex-ml -n codex-ml \
 --timestamps=true \
 --tail=1000 | grep -i "ERROR\|CRITICAL" | wc -l

# 2. Check resource utilization
echo -e "\n[RESOURCES] Resource utilization..."
kubectl top nodes
kubectl top pods -n codex-ml | sort -k3 -rn | head -10

# 3. Check backup status
echo -e "\n[BACKUPS] Backup status last 7 days..."
aws s3 ls s3://backup-bucket/postgres/ \
 --recursive \
 --human-readable \
 --summarize | tail -5

# 4. Review cost
echo -e "\n[COST] Cloud spending last 7 days..."
aws ce get-cost-and-usage \
 --time-period Start=2026-07-01,End=2026-07-08 \
 --granularity DAILY \
 --metrics UnblendedCost \
 --group-by Type=DIMENSION,Key=SERVICE

# 5. Check scaling metrics
echo -e "\n[SCALING] Pod scaling events last 7 days..."
kubectl get events -n codex-ml --sort-by='.lastTimestamp' | grep -i "Scaled"

# 6. Review security alerts
echo -e "\n[SECURITY] Security events last 7 days..."
kubectl logs -f siem-service -n security \
 --timestamps=true \
 --tail=100

echo -e "\n=== Review Complete ==="
```

---

## Database Management

### Connection Pool Management

**Objective**: Maintain optimal database performance

```bash
# Monitor connection usage
psql -U postgres -d codex -c \
 "SELECT datname, count(*) as connections FROM pg_stat_activity GROUP BY datname;"

# Identify long-running queries
psql -U postgres -d codex -c \
 "SELECT pid, usename, query_start, query 
 FROM pg_stat_activity 
 WHERE query_start < NOW() - INTERVAL '10 minutes';"

# Kill idle connections
psql -U postgres -d codex -c \
 "SELECT pg_terminate_backend(pid) FROM pg_stat_activity 
 WHERE state = 'idle' 
 AND query_start < NOW() - INTERVAL '1 hour';"

# Tune connection pool in PgBouncer
cat >> /etc/pgbouncer/pgbouncer.ini <<'EOF'
[databases]
codex = host=localhost port=5432 dbname=codex

[pgbouncer]
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 25
min_pool_size = 5
reserve_pool_size = 5
reserve_pool_timeout = 3
EOF

sudo systemctl restart pgbouncer
```

### Index Management

**Objective**: Maintain query performance through optimal indexing

```bash
# Find missing indexes
psql -U postgres -d codex -c \
 "SELECT schemaname, tablename, attname, n_distinct
 FROM pg_stats
 WHERE schemaname NOT LIKE 'pg_%'
 ORDER BY abs(n_distinct) DESC;"

# Create indexes for frequently accessed columns
psql -U postgres -d codex -c \
 "CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
 CREATE INDEX CONCURRENTLY idx_orders_date ON orders(created_at);
 CREATE INDEX CONCURRENTLY idx_transactions_user_id ON transactions(user_id);"

# Monitor index usage
psql -U postgres -d codex -c \
 "SELECT schemaname, tablename, indexname, idx_scan
 FROM pg_stat_user_indexes
 ORDER BY idx_scan DESC;"

# Remove unused indexes
psql -U postgres -d codex -c \
 "SELECT indexname FROM pg_stat_user_indexes 
 WHERE idx_scan = 0 
 AND indexrelname LIKE '%idx%';"

# Drop unused indexes (after verification)
# DROP INDEX CONCURRENTLY unused_index_name;
```

### Query Optimization

**Objective**: Optimize slow queries

```bash
# Enable query logging
psql -U postgres -d codex -c "
 ALTER SYSTEM SET log_min_duration_statement = 1000;
 SELECT pg_reload_conf();"

# Analyze slow query
psql -U postgres -d codex -c \
 "EXPLAIN ANALYZE SELECT * FROM orders 
 WHERE customer_id = 123 AND created_at > '2026-01-01';"

# Create optimal query plan
psql -U postgres -d codex -c "
 -- Before (slow)
 SELECT * FROM orders o
 JOIN customers c ON o.customer_id = c.id
 WHERE c.country = 'US'
 
 -- After (optimized)
 SELECT o.* FROM orders o
 WHERE o.customer_id IN (
 SELECT id FROM customers WHERE country = 'US'
 );"

# Verify improvement
EXPLAIN ANALYZE <optimized-query>;
```

---

## Backup & Recovery

### Backup Strategy

**Backup Schedule**:
```
- Full backup: Daily at 2:00 AM UTC
- Incremental backup: Every 6 hours
- WAL archiving: Continuous
- Cross-region replication: Real-time
- Retention: 30 days
```

### Automated Backups

```bash
#!/bin/bash
# backup-database.sh

BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_NAME="codex"
DB_USER="codex_admin"

# Full backup
pg_dump -h localhost -U $DB_USER -d $DB_NAME \
 | gzip > $BACKUP_DIR/full_backup_$TIMESTAMP.sql.gz

# Verify backup
gunzip -t $BACKUP_DIR/full_backup_$TIMESTAMP.sql.gz
echo " Backup verified"

# Upload to S3
aws s3 cp $BACKUP_DIR/full_backup_$TIMESTAMP.sql.gz \
 s3://backup-bucket/postgres/$TIMESTAMP/

# Cleanup local backups older than 7 days
find $BACKUP_DIR -name "full_backup_*.sql.gz" -mtime +7 -delete

# Alert if backup failed
if [ $? -ne 0 ]; then
 aws sns publish --topic-arn arn:aws:sns:region:account:alerts \
 --message "Database backup failed at $TIMESTAMP"
fi
```

### Recovery Procedure

**RTO Target**: < 15 minutes

```bash
#!/bin/bash
# recover-database.sh

BACKUP_FILE="/backups/full_backup_20260708_020000.sql.gz"

# Stop application
kubectl scale deployment codex-ml --replicas=0 -n codex-ml

# Create recovery database
psql -U postgres -d template1 -c "CREATE DATABASE codex_recovery;"

# Restore from backup
gunzip < $BACKUP_FILE | \
 psql -h localhost -U codex_admin -d codex_recovery

# Verify data integrity
psql -U postgres -d codex_recovery -c \
 "SELECT COUNT(*) FROM information_schema.tables
 WHERE table_schema NOT LIKE 'pg_%';"

# Rename databases
psql -U postgres -d template1 -c \
 "ALTER DATABASE codex RENAME TO codex_old;
 ALTER DATABASE codex_recovery RENAME TO codex;"

# Restart application
kubectl scale deployment codex-ml --replicas=3 -n codex-ml

# Verify recovery
kubectl rollout status deployment/codex-ml -n codex-ml

echo " Recovery complete"
```

---

## Performance Tuning

### Database Tuning

```bash
# Check current parameters
psql -U postgres -d codex -c "SHOW all;" | grep -E "cache|buffer|work_mem"

# Optimize PostgreSQL settings
psql -U postgres -d codex -c "
ALTER SYSTEM SET shared_buffers = '4GB';
ALTER SYSTEM SET effective_cache_size = '12GB';
ALTER SYSTEM SET work_mem = '100MB';
ALTER SYSTEM SET maintenance_work_mem = '1GB';
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_io_concurrency = 200;
SELECT pg_reload_conf();"

# Monitor cache hit ratio
psql -U postgres -d codex -c "
SELECT 
 sum(heap_blks_read) as heap_read,
 sum(heap_blks_hit) as heap_hit,
 sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) as ratio
FROM pg_statio_user_tables;"
```

### Application Performance Tuning

```bash
# Enable debug logging
kubectl set env deployment/codex-ml \
 LOG_LEVEL=DEBUG -n codex-ml

# Monitor metrics
kubectl port-forward svc/prometheus 9090:9090 -n monitoring

# Profile application
python -m cProfile -o app.prof application.py

# Analyze profile
python -m pstats app.prof

# Identify bottlenecks
grep -r "TODO\|FIXME\|XXX" src/
```

### Cache Tuning

```bash
# Check Redis memory usage
redis-cli info memory

# Configure max memory policy
redis-cli CONFIG SET maxmemory-policy allkeys-lru

# Monitor cache hit ratio
redis-cli info stats | grep -E "hits|misses"

# Verify memory is efficient
redis-cli DEBUG OBJECT <key>
```

---

## Security Hardening

### Regular Security Updates

**Frequency**: Weekly or as CVEs are announced

```bash
# Check for vulnerabilities
trivy image registry.example.com/codex-ml:latest

# Update base image
docker build --build-arg BASE_IMAGE=python:3.11-slim-bookworm .

# Scan dependencies
pip-audit
npm audit

# Apply security patches
kubectl patch deployment codex-ml \
 -p '{"spec":{"template":{"metadata":{"annotations":{"updated":"'$(date +%s)'"}}}}}' \
 -n codex-ml
```

### Access Control Review

**Frequency**: Monthly

```bash
# Review RBAC policies
kubectl get rolebindings -A
kubectl get clusterrolebindings

# Check service account permissions
kubectl get serviceaccount codex-ml -n codex-ml -o yaml

# Audit API access
kubectl logs apiserver | grep "user=" | tail -100

# Rotate API keys/credentials
./scripts/rotate-secrets.sh
```

### Network Security Review

**Frequency**: Monthly

```bash
# Check security groups
aws ec2 describe-security-groups \
 --filters "Name=group-name,Values=codex-ml-sg"

# Verify firewall rules
kubectl get networkpolicies -A

# Check ingress rules
kubectl get ingress -A
```

---

## Scaling Procedures

### Horizontal Scaling

**Objective**: Scale application to handle load

```bash
# Check current replicas
kubectl get deployment codex-ml -n codex-ml

# Scale to specific count
kubectl scale deployment codex-ml --replicas=10 -n codex-ml

# Monitor scaling
kubectl rollout status deployment/codex-ml -n codex-ml
kubectl get pods -n codex-ml -w

# Verify all pods are healthy
kubectl get pods -n codex-ml -o wide | grep -v Running

# Check load is distributed
kubectl top pods -n codex-ml
```

### Vertical Scaling

**Objective**: Increase resource limits

```bash
# Update resource requests/limits
kubectl set resources deployment codex-ml \
 --requests=cpu=2000m,memory=4Gi \
 --limits=cpu=4000m,memory=8Gi \
 -n codex-ml

# Monitor resource utilization
watch 'kubectl top pods -n codex-ml'

# Verify pods restart with new resources
kubectl rollout status deployment/codex-ml -n codex-ml
```

### Database Scaling

**Objective**: Scale database for increased load

```bash
# Add read replica
aws rds create-db-instance-read-replica \
 --db-instance-identifier codex-db-read-1 \
 --source-db-instance-identifier codex-ml-db

# Monitor replication lag
aws rds describe-db-instances \
 --db-instance-identifier codex-db-read-1 \
 --query 'DBInstances[0].StatusInfos'

# Update application to use read replica
kubectl set env deployment/codex-ml \
 READ_REPLICA_HOST=codex-db-read-1.rds.amazonaws.com \
 -n codex-ml
```

---

## Maintenance Windows

### Planned Maintenance Schedule

```
Weekly Maintenance Window
 When: Sundays 02:00-04:00 UTC
 Duration: 2 hours
 Components: Non-critical updates
 Notification: Friday email blast
 Validation: 15-minute post-maintenance testing

Monthly Maintenance Window
 When: First Saturday of month 02:00-06:00 UTC
 Duration: 4 hours
 Components: Critical updates, major upgrades
 Notification: 2-week advance notice
 Validation: 1-hour comprehensive testing

Quarterly Maintenance Window
 When: TBD (announce 1 month in advance)
 Duration: 8 hours
 Components: Major infrastructure changes
 Notification: 3-month advance notice
 Validation: Full regression test suite
```

### Database Maintenance

```bash
#!/bin/bash
# maintenance-database.sh

echo "Starting database maintenance window..."

# 1. Backup database
./backup-database.sh

# 2. Vacuum and analyze
psql -U codex_admin -d codex -c "VACUUM FULL ANALYZE;"

# 3. Reindex tables
psql -U codex_admin -d codex -c "REINDEX DATABASE codex;"

# 4. Update table statistics
psql -U codex_admin -d codex -c "ANALYZE codex;"

# 5. Check table bloat
psql -U codex_admin -d codex -c \
 "SELECT schemaname, tablename, round(100.0 * (CASE 
 WHEN live_tuples = 0 THEN 0.0 ELSE dead_tuples / live_tuples::float END), 2) as dead_ratio
 FROM pg_stat_user_tables ORDER BY dead_ratio DESC;"

# 6. Verify integrity
psql -U codex_admin -d codex -c "REINDEX TABLE CONCURRENTLY <table>;"

echo "Database maintenance complete"
```

### Application Updates

```bash
#!/bin/bash
# maintenance-application.sh

echo "Starting application maintenance..."

# 1. Drain connections gracefully
kubectl annotate pods -l app=codex-ml \
 -n codex-ml \
 drain=true --overwrite

# 2. Update deployment
kubectl set image deployment/codex-ml \
 codex-ml=registry.example.com/codex-ml:1.0.1 \
 -n codex-ml

# 3. Monitor rollout
kubectl rollout status deployment/codex-ml -n codex-ml

# 4. Run smoke tests
./scripts/smoke-test.sh

# 5. Verify metrics
./scripts/verify-metrics.sh

echo "Application maintenance complete"
```

---

## Emergency Procedures

### Service Degradation Response

```bash
# 1. Declare incident
kubectl annotate namespace codex-ml incident=true

# 2. Assess impact
kubectl get pods -n codex-ml -o wide
kubectl top nodes

# 3. Gather logs
kubectl logs -n codex-ml -l app=codex-ml --all-containers=true > /tmp/logs.txt

# 4. Execute remediation
kubectl rollout undo deployment/codex-ml -n codex-ml

# 5. Monitor recovery
watch 'kubectl get pods -n codex-ml'

# 6. Post-incident review
./scripts/generate-incident-report.sh
```

---

**Important**: Document all maintenance activities in a maintenance log for future reference.

