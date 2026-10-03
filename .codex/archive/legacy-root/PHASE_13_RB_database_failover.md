# PHASE 13 OPERATIONAL RUNBOOK - DATABASE FAILOVER
# Primary → Backup Failover Procedures
# Version: 1.0.0
# Last Updated: 2026-07-16T20:51Z
# Severity: CRITICAL
# RTO: 5 minutes
# RPO: 0 (replication lag < 1 second)

---

## SCENARIO DESCRIPTION

Primary PostgreSQL database has become unresponsive or degraded. This runbook handles:
- Primary database connectivity loss
- Primary database CPU/memory exhaustion
- Primary database disk space exhaustion
- Cascading failure detection
- Managed failover to replica

**Trigger Conditions:**
- `pg_is_in_recovery()` = false AND primary not responding for >2 minutes
- Primary CPU utilization >95% for >5 minutes
- Primary disk space <5% available
- Replication lag >30 seconds detected

---

## PRE-INCIDENT CHECKLIST

- [ ] Review current replication lag (should be <1s)
  ```bash
  psql -h primary.db.internal -U postgres -c "SELECT now() - pg_last_wal_receive_lsn()::text::timestamp AS replication_lag;"
  ```

- [ ] Verify backup replica is healthy
  ```bash
  psql -h replica.db.internal -U postgres -c "SELECT version();"
  ```

- [ ] Check standby WAL receiver status
  ```bash
  psql -h replica.db.internal -U postgres -c "SELECT * FROM pg_stat_replication;"
  ```

- [ ] Verify alerting is enabled
  ```bash
  curl http://alertmanager:9093/api/v1/alerts | grep -i "database"
  ```

- [ ] Confirm application connection pool configuration
  - Location: `/etc/codex/database_config.yml`
  - Read replicas: replica1, replica2, replica3
  - Write endpoint: primary.db.internal
  - Failover timeout: 30s

- [ ] Document current time and status in incident log
  ```bash
  echo "DB Failover started: $(date -u +'%Y-%m-%dT%H:%M:%SZ')" >> /var/log/incidents.log
  ```

---

## STEP-BY-STEP TROUBLESHOOTING

### Step 1: Confirm Primary Database Issue (5 min)

**Action 1.1:** Test primary database connectivity
```bash
pg_isready -h primary.db.internal -p 5432 -U postgres
# Expected: accepting connections
# Actual: [record actual status]
```

**Action 1.2:** Check database logs for errors
```bash
tail -50 /var/log/postgresql/postgresql.log | grep ERROR
# Look for: connection refused, out of memory, disk full
```

**Action 1.3:** Verify network connectivity to primary
```bash
ping -c 3 primary.db.internal
nslookup primary.db.internal
# Expected: responses within 5ms
```

**Decision Point:**
- If primary is responding: Proceed to "Performance Degradation Response" (Step 2)
- If primary is unreachable: Proceed to "Emergency Failover" (Step 3)

### Step 2: Performance Degradation Response (10 min)

**Action 2.1:** Check primary database status
```bash
psql -h primary.db.internal -U postgres -c "
  SELECT
    datname,
    usename,
    application_name,
    state,
    query,
    query_start,
    state_change
  FROM pg_stat_activity
  WHERE state != 'idle'
  ORDER BY query_start;
"
```

**Action 2.2:** Identify slow queries
```bash
psql -h primary.db.internal -U postgres -c "
  SELECT
    query,
    calls,
    total_time,
    mean_time,
    max_time
  FROM pg_stat_statements
  ORDER BY total_time DESC
  LIMIT 10;
"
```

**Action 2.3:** Monitor replication lag
```bash
watch -n 5 "psql -h replica.db.internal -U postgres -c \"SELECT now() - pg_last_wal_receive_lsn()::text::timestamp AS replication_lag;\""
# Expected: < 1 second
# Alert threshold: > 30 seconds
```

**Decision Point:**
- If lag < 30s and queries responding: Wait 5 more minutes, monitor closely
- If lag > 30s or queries timing out: Proceed to Emergency Failover (Step 3)

### Step 3: Emergency Failover (5 min)

**Action 3.1:** Notify team immediately
```bash
# Post to #oncall-alerts Slack channel
curl -X POST $SLACK_WEBHOOK_URL \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "🚨 DATABASE FAILOVER IN PROGRESS",
    "blocks": [
      {
        "type": "section",
        "text": {
          "type": "mrkdwn",
          "text": "*Database Failover Initiated*\nPrimary: UNRESPONSIVE\nFailover Target: replica.db.internal\nETA: 5 minutes"
        }
      }
    ]
  }'
```

**Action 3.2:** Promote standby replica to primary
```bash
# SSH to replica host
ssh replica.db.internal

# Promote to primary
sudo /usr/lib/postgresql/15/bin/pg_ctl promote -D /var/lib/postgresql/15/main

# Verify promotion (may take 30-60 seconds)
sleep 30
psql -U postgres -c "SELECT pg_is_in_recovery();"
# Expected: f (not in recovery = primary)
```

**Action 3.3:** Update DNS/connection strings immediately
```bash
# Update primary endpoint to point to promoted replica
# Method depends on environment:

# Option A: Update /etc/hosts
ssh app-server "echo 'replica.db.internal primary.db.internal' >> /etc/hosts"

# Option B: Update AWS RDS endpoint
aws rds modify-db-instance \
  --db-instance-identifier codex-primary \
  --preferred-backup-window "03:00-04:00"

# Option C: Update service discovery
curl -X PUT http://consul.service.consul:8500/v1/kv/codex/db/primary \
  -d "replica.db.internal:5432"
```

**Action 3.4:** Verify application connectivity
```bash
# Test application can connect to promoted primary
psql -h primary.db.internal -U codex_app -d codex_prod -c "SELECT COUNT(*) FROM users;"
# Expected: [row count]

# Check application health
curl http://app:8080/health | jq '.database'
# Expected: { "status": "healthy", "latency_ms": <100 }
```

**Action 3.5:** Monitor for cascading failures
```bash
# Watch for connection pool exhaustion
psql -h primary.db.internal -U postgres -c "
  SELECT count(*) FROM pg_stat_activity;
" 
# Alert: > 300 connections (pool saturation)

# Monitor write latency
watch -n 5 "curl http://prometheus:9090/api/v1/query?query=db_write_latency_p95 | jq '.data.result[0].value[1]'"
# Expected: < 50ms
# Alert: > 500ms (indicates persistence issues)
```

---

## ESCALATION PROCEDURES

### If Promoted Replica Also Fails:

1. **Immediate Actions:**
   - Stop all write traffic immediately
   - Switch to read-only mode
   - Notify VP of Engineering: @mbaetiong

2. **Recovery Steps:**
   ```bash
   # Check backup from 24h ago
   ls -lh /backups/postgresql/

   # Restore to temporary database
   pg_restore -d codex_recovery /backups/postgresql/daily_2026-07-16_03-00.dump

   # Verify data integrity
   psql -d codex_recovery -c "SELECT COUNT(*) FROM users;"

   # If valid, promote to primary
   # (Follow Step 3.2 above)
   ```

3. **Communication:**
   - Update status page: "Degraded - Read-Only Mode"
   - Post to #operations every 15 minutes

### If Failover Takes >10 minutes:

1. **Escalation:**
   - Page database team lead
   - Notify @mbaetiong
   - Begin customer communication

2. **Alternative Strategy:**
   - Check if old primary can be revived
   - Consider activating read replicas as temporary primaries

---

## ROLLBACK PROCEDURES

**If Primary Recovers Within 1 Hour:**

```bash
# 1. Re-add original primary as standby
pg_basebackup -h primary.db.internal \
  -D /mnt/backup/primary_base \
  -Fp -Xs -P

# 2. Configure as standby
echo "standby_mode = on" >> /mnt/backup/primary_base/recovery.conf

# 3. Start standby
pg_ctl -D /mnt/backup/primary_base start

# 4. Verify replication
psql -U postgres -c "SELECT * FROM pg_stat_replication;"
```

**If Primary Cannot Recover:**

- Decommission failed node
- Provision replacement with same specs
- Re-establish replication from promoted primary

---

## POST-INCIDENT REVIEW TEMPLATE

**Incident ID:** [auto-generated YYYY-MM-DD-NNN]
**Date/Time:** [fill in UTC]
**Duration:** [minutes]
**Severity:** P1 (critical)

**Timeline:**
- T+0min: [event that triggered failover]
- T+Xmin: [when detected]
- T+Ymin: [when resolved]

**Root Cause:**
- [ ] Hardware failure (disk/memory/CPU)
- [ ] Software crash (out of memory, segfault)
- [ ] Network issue
- [ ] Configuration error
- [ ] Other: ___________

**Impact:**
- [ ] Data loss: [0 / X rows]
- [ ] Downtime: [duration]
- [ ] Affected services: [list]
- [ ] Customer-facing: [yes/no]

**Lessons Learned:**
1. [What worked well]
2. [What could improve]
3. [Action items for prevention]

**Action Items:**
- [ ] Update monitoring thresholds
- [ ] Improve runbook clarity
- [ ] Upgrade hardware
- [ ] Other: ___________

**Sign-Off:**
- Incident Commander: _________
- Date: _________

---

## SUCCESS CRITERIA (POST-FAILOVER)

- [x] Primary promoted within 5 minutes
- [x] Application connectivity restored
- [x] Replication lag < 1 second
- [x] No data loss (RPO = 0)
- [x] Write latency < 50ms
- [x] Error rate < 0.1%
- [x] Incident logged and reviewed

---

## CONTACTS & ESCALATION

| Role | Name | Slack | Phone |
|------|------|-------|-------|
| DB Lead | [name] | @db-lead | +1-555-0101 |
| On-Call | [rotation] | @oncall | [PagerDuty] |
| VP Eng | mbaetiong | @mbaetiong | [emergency] |
| SRE Team | [list] | @sre-team | [escalation] |

---

## APPENDIX: USEFUL COMMANDS

**Quick Health Check:**
```bash
echo "=== Primary Status ===" && \
psql -h primary.db.internal -U postgres -c "SELECT now(), pg_is_in_recovery();" && \
echo "=== Replica Status ===" && \
psql -h replica.db.internal -U postgres -c "SELECT now(), pg_is_in_recovery();" && \
echo "=== Replication Lag ===" && \
psql -h replica.db.internal -U postgres -c "SELECT now() - pg_last_wal_receive_lsn()::text::timestamp AS lag;"
```

**Monitoring Failover Progress:**
```bash
# In one terminal (watch primary)
watch -n 2 "psql -h primary.db.internal -U postgres -c 'SELECT version();' 2>&1 || echo 'DISCONNECTED'"

# In another terminal (watch replica)
watch -n 2 "psql -h replica.db.internal -U postgres -c 'SELECT pg_is_in_recovery();' 2>&1 || echo 'DISCONNECTED'"
```

**Connection Pool Status:**
```bash
psql -h primary.db.internal -U postgres -c "
  SELECT datname, usename, count(*) as connections
  FROM pg_stat_activity
  GROUP BY datname, usename
  ORDER BY connections DESC;
"
```

---

## REFERENCES

- PostgreSQL High Availability Guide: https://www.postgresql.org/docs/15/warm-standby.html
- Streaming Replication: https://www.postgresql.org/docs/15/streaming-replication.html
- Physical Replication: https://www.postgresql.org/docs/15/physical-replication.html
- Runbook Version: 1.0.0
- Last Validated: 2026-07-16
