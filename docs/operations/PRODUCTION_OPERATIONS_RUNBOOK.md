# Production Operations Runbook

**Last Updated:** 2026-06-22

**Version:** 1.0.0  
**Date:** 2026-06-14T04:05:00Z  
**Owner:** Operations Team  
**Status:** Ready for Production Deployment  

---

## 📖 Table of Contents

1. [Daily Operations](#daily-operations)
2. [Scaling & Performance](#scaling--performance)
3. [Backup & Recovery](#backup--recovery)
4. [Incident Response](#incident-response)
5. [Secrets & Access Management](#secrets--access-management)
6. [Monitoring & Alerts](#monitoring--alerts)

---

## Daily Operations

### Health Checks (Every 4 hours)

```bash
#!/bin/bash
# Health check script

echo "=== Service Health Check ==="
curl -s https://api.codex.io/health | jq .
echo "Status: $(curl -s -o /dev/null -w '%{http_code}' https://api.codex.io/health)"

echo "\n=== Database Check ==="
psql $DATABASE_URL -c "SELECT NOW();" && echo "✓ Database responding"

echo "\n=== Cache Check ==="
redis-cli -h $REDIS_HOST PING && echo "✓ Redis responding"

echo "\n=== Metrics Check ==="
curl -s https://monitoring.codex.io/api/health | jq .

echo "\n=== Log Aggregation Check ==="
# Query ELK/Splunk to ensure logs flowing
curl -s $ELASTICSEARCH_URL/_cat/health && echo "✓ Log aggregation healthy"
```

## Daily Backup Verification

```bash
#!/bin/bash
# Verify backups from previous 24 hours

echo "=== Daily Backup Verification ==="

# Check database backup completed
BACKUP_TIME=$(stat -c %y /var/backups/postgres_backup.sql.gz | cut -d' ' -f1)
CURRENT_TIME=$(date +%Y-%m-%d)

if [[ $BACKUP_TIME == $CURRENT_TIME ]]; then
  echo "✓ Database backup completed today"
  echo "  Backup size: $(du -h /var/backups/postgres_backup.sql.gz)"
  echo "  Backup time: $(stat -c %y /var/backups/postgres_backup.sql.gz)"
else
  echo "✗ ALERT: Database backup not completed today!"
  # Send alert
  send_alert "critical" "Database backup failed"
fi

# Check filesystem backup
BACKUP_COUNT=$(find /var/backups -mtime -1 -type f | wc -l)
echo "✓ Filesystem backups completed: $BACKUP_COUNT files"

# Verify backup integrity
sha256sum -c /var/backups/BACKUP_CHECKSUMS.txt && echo "✓ All backup checksums valid"
```

## Routine Maintenance

```bash
# Weekly: Update dependencies
pip install --upgrade pip setuptools wheel
npm update

# Weekly: Review logs for errors
grep -i "error\|warning" /var/log/codex/*.log | tail -20

# Monthly: Certificate check
for cert in /etc/ssl/certs/*.pem; do
  openssl x509 -enddate -noout -in $cert | \
    awk -v cert=$cert '{ \
      cmd="date +%s -d \"" $0 "\""; \
      cmd | getline exp; \
      close(cmd); \
      days_left=(exp-systime())/86400; \
      if(days_left<30) \
        print "⚠️  " cert " expires in " days_left " days" \
    }'
done

# Monthly: Disk space check
du -sh /*/ | sort -rh | head -10
```

---

## Scaling & Performance

### Horizontal Scaling (Add Replicas)

```bash
# Check current replica count
kubectl get deployment codex-api -o jsonpath='{.spec.replicas}'

# Scale up
kubectl scale deployment codex-api --replicas=5

# Monitor scaling
kubectl rollout status deployment/codex-api

# Verify all pods healthy
kubectl get pods -l app=codex-api --watch
```

## Vertical Scaling (Increase Resources)

```bash
# Edit deployment
kubectl edit deployment codex-api

# Find 'resources:' section and update:
# limits:
# cpu: "4"
# memory: "8Gi"
# requests:
# cpu: "2"
# memory: "4Gi"

# Apply changes
kubectl rollout restart deployment/codex-api

# Monitor
kubectl top pods -l app=codex-api
```

## Database Performance Optimization

```bash
# Check slow queries
mysql -h $DB_HOST -u root -p$DB_PASSWORD -e \
  "SELECT * FROM mysql.slow_log ORDER BY query_time DESC LIMIT 10;"

# Analyze table
mysql -h $DB_HOST -u root -p$DB_PASSWORD -e \
  "ANALYZE TABLE codex_sessions;"

# Optimize table
mysql -h $DB_HOST -u root -p$DB_PASSWORD -e \
  "OPTIMIZE TABLE codex_sessions;"

# Add index if needed
mysql -h $DB_HOST -u root -p$DB_PASSWORD -e \
  "CREATE INDEX idx_session_created ON codex_sessions(created_at);"
```

## Cache Optimization

```bash
# Check cache hit rate
redis-cli INFO stats | grep -E "hits|misses"

# Clear cache (if needed)
redis-cli FLUSHALL  # USE WITH CAUTION

# Monitor cache keys
redis-cli --scan --pattern "*" | head -20

# Check memory usage
redis-cli INFO memory | grep used_memory_human
```

---

## Backup & Recovery

### On-Demand Backup

```bash
#!/bin/bash
# Manual backup procedure

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/manual_$TIMESTAMP"
mkdir -p $BACKUP_DIR

# Backup database
echo "Backing up database..."
pg_dump -h $DB_HOST -U $DB_USER $DB_NAME | \
  gzip > $BACKUP_DIR/database_$TIMESTAMP.sql.gz

# Backup configuration
echo "Backing up configuration..."
tar czf $BACKUP_DIR/config_$TIMESTAMP.tar.gz \
  /etc/codex /etc/systemd /home/*/.*config

# Backup application data
echo "Backing up data..."
tar czf $BACKUP_DIR/data_$TIMESTAMP.tar.gz \
  /var/lib/codex /var/log/codex

# Checksum all backups
cd $BACKUP_DIR
sha256sum * > CHECKSUMS.txt

# Copy to backup storage
aws s3 cp $BACKUP_DIR s3://backups.codex.io/manual/$TIMESTAMP/ --recursive

echo "✓ Backup completed: $BACKUP_DIR"
```

## Recovery Procedure

```bash
#!/bin/bash
# Restore from backup

BACKUP_DATE=$1  # Pass YYYYMMDD_HHMMSS

echo "Recovering from backup: $BACKUP_DATE"

# Stop services
systemctl stop codex-api codex-worker

# Restore database
echo "Restoring database..."
gunzip < /var/backups/manual_$BACKUP_DATE/database_$BACKUP_DATE.sql.gz | \
  psql -h $DB_HOST -U $DB_USER $DB_NAME

# Restore configuration
echo "Restoring configuration..."
tar xzf /var/backups/manual_$BACKUP_DATE/config_$BACKUP_DATE.tar.gz -C /

# Restore data
echo "Restoring data..."
tar xzf /var/backups/manual_$BACKUP_DATE/data_$BACKUP_DATE.tar.gz -C /

# Verify recovery
echo "Verifying recovery..."
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT COUNT(*) FROM codex_sessions;"

# Restart services
systemctl start codex-api codex-worker

echo "✓ Recovery completed"
```

---

## Incident Response

### Incident Classification

| Severity | Impact | Response Time | Escalation |
|----------|--------|---|---|
| **P1 - Critical** | Service down, data loss risk | <15 min | CTO + Team |
| **P2 - High** | Degraded service, <1% error rate | <30 min | Team Lead |
| **P3 - Medium** | Minor issues, no user impact | <2 hours | On-Call |
| **P4 - Low** | Documentation, non-urgent | <24 hours | Backlog |

### P1 Incident: Service Down

```bash
#!/bin/bash
# P1 Response: Service completely down

echo "=== P1 INCIDENT: Service Down ==="
date
echo "Time: $(date -u +'%Y-%m-%dT%H:%M:%SZ')"

# 1. Declare incident
echo "Declaring P1 incident in PagerDuty..."
# pagerduty create-incident service=codex-api severity=critical

# 2. Check service status
echo "\n=== Service Status ==="
kubectl get pods -l app=codex-api
kubectl describe pod <pod-name> | tail -20

# 3. Check logs
echo "\n=== Recent Logs ==="
kubectl logs -l app=codex-api --tail=50

# 4. Check resource usage
echo "\n=== Resource Usage ==="
kubectl top pods -l app=codex-api
kubectl top nodes

# 5. Check database
echo "\n=== Database Status ==="
psql -h $DB_HOST -U $DB_USER -c "SELECT NOW();"

# 6. Initiate recovery
echo "\n=== Attempting Recovery ==="

# Restart service
kubectl rollout restart deployment/codex-api
kubectl rollout status deployment/codex-api

# If restart fails, check recent deployments
kubectl rollout history deployment/codex-api

# Rollback if needed
kubectl rollout undo deployment/codex-api

# 7. Verify service
echo "\n=== Verifying Service ==="
for i in {1..10}; do
  curl -s https://api.codex.io/health && echo "✓ Service responding" && break
  echo "Attempt $i failed, retrying..."
  sleep 5
done

# 8. Update incident
# Update PagerDuty incident with status and resolution
```

## P2 Incident: High Error Rate

```bash
#!/bin/bash
# P2 Response: Error rate elevated

ERROR_RATE=$(curl -s https://monitoring.codex.io/api/metrics/error_rate | jq .value)
echo "Current error rate: $ERROR_RATE%"

# 1. Identify error source
echo "\n=== Identifying Error Source ==="
curl -s https://logs.codex.io/search -d '{
  "query": "status:error",
  "timerange": "1h",
  "limit": 100
}' | jq '.errors | group_by(.type) | sort_by(length) | reverse'

# 2. Check recent deployments
echo "\n=== Recent Deployments ==="
kubectl rollout history deployment/codex-api

# 3. If caused by recent deploy, rollback
kubectl rollout undo deployment/codex-api

# 4. Monitor recovery
kubectl rollout status deployment/codex-api

# 5. Verify error rate decreasing
watch "curl -s https://monitoring.codex.io/api/metrics/error_rate | jq .value"
```

---

## Secrets & Access Management

### Rotating Secrets

```bash
#!/bin/bash
# Rotate all secrets

echo "=== Rotating Secrets ==="

# 1. Rotate database password
echo "Rotating database password..."
NEW_PASSWORD=$(openssl rand -base64 24)
psql -h $DB_HOST -U postgres -c \
  "ALTER USER $DB_USER WITH PASSWORD '$NEW_PASSWORD';"
# Update .env and redeploy

# 2. Rotate API tokens
echo "Rotating API tokens..."
for token in $(vault list secret/codex/api_tokens); do
  vault delete secret/codex/api_tokens/$token
  NEW_TOKEN=$(openssl rand -hex 32)
  vault write secret/codex/api_tokens/$token value=$NEW_TOKEN
done

# 3. Rotate encryption keys (with caution)
echo "Rotating encryption keys..."
# This typically requires coordination with all services

# 4. Restart services to pick up new secrets
kubectl rollout restart deployment/codex-api

echo "✓ Secrets rotation complete"
```

## Access Control Audit

```bash
#!/bin/bash
# Audit access permissions

echo "=== Access Control Audit ==="

# 1. List all service accounts
echo "Service Accounts:"
kubectl get serviceaccounts --all-namespaces

# 2. Check RBAC policies
echo "\nRBAC Policies:"
kubectl get clusterrolebindings
kubectl get rolebindings --all-namespaces

# 3. Audit user access
echo "\nUser Access:"
gcloud projects get-iam-policy codex-prod

# 4. Review VPN access logs
echo "\nVPN Access (last 24h):"
grep "$(date +%Y-%m-%d)" /var/log/vpn/access.log | tail -20

# 5. Check for unused credentials
echo "\nUnused Credentials (>90 days):"
aws iam get-credential-report | \
  jq '.[] | select(.password_last_used < now - 7776000)'
```

---

## Monitoring & Alerts

### Alert Response Guide

| Alert | Likely Cause | Action | Escalation |
|-------|--------------|--------|-----------|
| High Error Rate | Bad deployment, DB issue | Check logs, rollback if recent | P1 if persistent |
| High Latency | Load spike, DB slow queries | Scale up, optimize queries | Page on-call |
| High CPU | Inefficient code, runaway process | Check top processes, scale | Escalate if >95% |
| High Memory | Memory leak, cache bloat | Restart service, clear cache | Page lead |
| Low Disk Space | Logs filling up, backups too large | Archive logs, cleanup backups | Critical if <10% |
| DB Replication Lag | Network issue, primary overload | Check network, scale DB | Page DBA |

### Creating Custom Alerts

```bash
# Add alert rule to Prometheus
cat > /etc/prometheus/rules/custom.yaml << 'EOF'
groups:
  - name: custom_alerts
    interval: 30s
    rules:
      - alert: HighMemoryUsage
        expr: container_memory_usage_bytes > 1e9
        for: 5m
        annotations:
          summary: "High memory usage detected"
          description: "Memory usage is {{ $value | humanize }}"

      - alert: SlowQuery
        expr: mysql_slow_queries > 10
        for: 5m
        annotations:
          summary: "Slow queries detected"
          description: "{{ $value }} slow queries in last 5 minutes"
EOF

# Reload Prometheus
systemctl reload prometheus
```

---

## 📞 Escalation Contacts

**On-Call Rotation:**
- Week 1: Alice (alice@codex.io, +1-555-0001)
- Week 2: Bob (bob@codex.io, +1-555-0002)
- Week 3: Charlie (charlie@codex.io, +1-555-0003)
- Week 4: Diana (diana@codex.io, +1-555-0004)

**Escalation Chain:**
1. On-Call Engineer (first response)
2. On-Call Manager (if unresolved in 15 min)
3. Engineering Lead (if unresolved in 30 min)
4. CTO (if unresolved in 60 min)

**Incidents:**
- Slack: #incidents-production
- Email: incidents@codex.io
- PagerDuty: https://codex.pagerduty.com/

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-06-14 | Initial production runbook |

---

## Review Schedule

- **Monthly:** Review all procedures and update as needed
- **Quarterly:** Run full incident response drills
- **Annually:** Complete runbook audit and refresh
