# Database Recovery Runbook

**Audience**: Production operators, DevOps engineers, SREs  
**Scope**: SQLite databases in Codex production deployment  
**Last Updated**: 2026-06-22  
**Version**: 1.0  

---

## Table of Contents

1. [Quick Reference](#quick-reference)
2. [Database Locations](#database-locations)
3. [Common Recovery Scenarios](#common-recovery-scenarios)
4. [Backup Procedures](#backup-procedures)
5. [Disaster Recovery](#disaster-recovery)
6. [Performance Recovery](#performance-recovery)
7. [Troubleshooting](#troubleshooting)

---

## Quick Reference

### Emergency Contacts
- **Database Owner**: Codex Admin
- **On-Call**: Check PagerDuty
- **Escalation**: Engineering Lead

### Database Status Check
```bash
# Check all databases exist and are accessible
ls -lh /var/data/codex_*.db
ls -lh .codex/*.db

# Quick integrity check
sqlite3 /var/data/codex_users.db "PRAGMA integrity_check;"
sqlite3 .codex/session_logs.db "PRAGMA integrity_check;"
```

## Critical Alert Thresholds
| Condition | Action |
|-----------|--------|
| Integrity check FAILED | **STOP ALL TRAFFIC** - Escalate immediately |
| DB file size > 10GB | Execute WAL checkpoint |
| Connection pool size > 10 | Check for connection leak |
| Query p95 > 500ms | Check for long-running queries |

---

## Database Locations

### Development Environment
```
.codex/session_logs.db       # Session logging
.codex/agent_memory.db       # Agent state (local only)
```

### Production Environment
```
/var/data/codex_users.db           # User authentication (CRITICAL)
/var/data/codex_session_logs.db   # Session logging (HIGH)
/var/data/codex_archive.db        # Artifact storage (MEDIUM)
```

### Environment Variables
```bash
CODEX_LOG_DB_PATH=/var/data/codex_session_logs.db
CODEX_USERSTORE_DB_PATH=/var/data/codex_users.db
CODEX_ARCHIVE_DB_PATH=/var/data/codex_archive.db
CODEX_SQLITE_POOL=1  # Enable connection pooling
```

---

## Common Recovery Scenarios

### Scenario 1: Database Becomes Unresponsive

**Symptoms**:
- Requests timing out
- "database is locked" errors
- High CPU on SQLite process

**Recovery Steps**:

1. **Identify the blocking process**:
```bash
# Check open file descriptors
lsof /var/data/codex_users.db

# Check for long-running queries
sqlite3 /var/data/codex_users.db ".tables"
```

2. **Force WAL checkpoint** (for session_logs):
```bash
sqlite3 /var/data/codex_session_logs.db "PRAGMA wal_checkpoint(RESTART);"
```

3. **Restart affected service** (graceful):
```bash
# Use systemd for graceful restart
systemctl restart codex-api
```

**Prevention**:
- Monitor query execution times
- Implement query timeout (30 seconds for non-analytics queries)
- Use connection pooling to limit concurrent connections

## Scenario 2: "Disk I/O Error" on WAL

**Symptoms**:
- `sqlite3.OperationalError: disk I/O error`
- Cannot write to .db-wal file
- Filesystem is full or has permissions issues

**Recovery Steps**:

1. **Check disk space**:
```bash
df -h /var/data/
# If full, clean up old logs or archives
```

2. **Check file permissions**:
```bash
ls -l /var/data/codex_*.db*
# Should be readable/writable by codex user
chmod 660 /var/data/codex_*.db*
```

3. **Force WAL checkpoint to merge**:
```bash
sqlite3 /var/data/codex_session_logs.db "PRAGMA wal_checkpoint(TRUNCATE);"
```

4. **Verify integrity**:
```bash
sqlite3 /var/data/codex_session_logs.db "PRAGMA integrity_check;"
```

## Scenario 3: Corrupted Database File

**Symptoms**:
- `sqlite3.DatabaseError: database disk image is malformed`
- Application startup fails
- Integrity check returns errors

**Recovery Steps**:

1. **Verify corruption**:
```bash
sqlite3 /var/data/codex_users.db "PRAGMA integrity_check;"
# Output will detail corruption issues
```

2. **Attempt recovery with integrity check**:
```bash
# Create recovery query
sqlite3 /var/data/codex_users.db << SQL
PRAGMA integrity_check;
REINDEX;
PRAGMA optimize;
SQL
```

3. **If recovery fails, restore from backup**:
```bash
# Restore from backup
cp /backups/codex_users.db.backup.$(date +%Y%m%d) /var/data/codex_users.db
chmod 660 /var/data/codex_users.db
```

4. **Verify restored database**:
```bash
sqlite3 /var/data/codex_users.db "SELECT COUNT(*) FROM users;"
```

5. **Test application**:
```bash
# Run smoke tests
pytest tests/auth/test_sqlite_user_repository.py -v
```

## Scenario 4: Connection Pool Exhaustion

**Symptoms**:
- "connection pool exhausted" errors
- Requests queuing up
- Memory usage climbing

**Recovery Steps**:

1. **Check pool status**:
```bash
# In Python console
from codex.logging.db_manager import DBManager
db_manager = DBManager()
print(db_manager._CONNECTION_POOL)
```

2. **Identify long-lived connections**:
```bash
# Check for processes holding connections
lsof /var/data/codex_users.db | grep -v "codex-api"
```

3. **Graceful restart of connection pool**:
```bash
# Use systemd
systemctl reload codex-api  # Send SIGHUP instead of SIGTERM
```

---

## Backup Procedures

### Automated Backup (Recommended)

**Backup Strategy**:
- **Frequency**: Hourly (session_logs), Daily (users, archive)
- **Retention**: 7 days (session_logs), 30 days (users, archive)
- **Location**: /backups/codex/

**Setup Backup Scripts**:

```bash
#!/bin/bash
# /usr/local/bin/backup_codex_dbs.sh

BACKUP_DIR="/backups/codex"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup each database with WAL checkpoint
for db in /var/data/codex_*.db; do
    db_name=$(basename $db)
    
    # Checkpoint WAL
    sqlite3 $db "PRAGMA wal_checkpoint(TRUNCATE);"
    
    # Copy database
    cp $db $BACKUP_DIR/${db_name}.backup.$TIMESTAMP
    
    # Verify backup
    sqlite3 $BACKUP_DIR/${db_name}.backup.$TIMESTAMP "PRAGMA integrity_check;" > /tmp/check_$TIMESTAMP.txt
    if ! grep -q "ok" /tmp/check_$TIMESTAMP.txt; then
        echo "ALERT: Backup verification failed for $db_name"
        exit 1
    fi
done

echo "✅ Backup completed at $TIMESTAMP"
```

**Cron Job**:
```bash
# Add to /etc/cron.d/codex_backup
0 */6 * * * /usr/local/bin/backup_codex_dbs.sh >> /var/log/codex_backup.log 2>&1
```

## Manual Backup

```bash
# Quick backup before maintenance
sqlite3 /var/data/codex_users.db "PRAGMA wal_checkpoint(TRUNCATE);"
cp /var/data/codex_users.db /backups/manual_backup_$(date +%s).db

# Verify
sqlite3 /backups/manual_backup_*.db "PRAGMA integrity_check;"
```

## Restore from Backup

```bash
# Stop application
systemctl stop codex-api

# Restore database
cp /backups/codex_users.db.backup.20250120_010000 /var/data/codex_users.db
chmod 660 /var/data/codex_users.db

# Verify
sqlite3 /var/data/codex_users.db "SELECT COUNT(*) FROM users;"

# Restart application
systemctl start codex-api

# Test
curl http://localhost:8000/health
```

---

## Disaster Recovery

### Full Database Loss Scenario

**Procedure**:

1. **Stop all services**:
```bash
systemctl stop codex-api
systemctl stop codex-workers
```

2. **Restore all databases**:
```bash
# Get latest backup timestamp
LATEST_BACKUP=$(ls -t /backups/codex_users.db.backup.* | head -1 | sed 's/.*backup\.//')

# Restore each database
cp /backups/codex_users.db.backup.$LATEST_BACKUP /var/data/codex_users.db
cp /backups/codex_session_logs.db.backup.$LATEST_BACKUP /var/data/codex_session_logs.db
cp /backups/codex_archive.db.backup.$LATEST_BACKUP /var/data/codex_archive.db

chmod 660 /var/data/codex_*.db
```

3. **Verify all databases**:
```bash
for db in /var/data/codex_*.db; do
    result=$(sqlite3 $db "PRAGMA integrity_check;")
    if [[ $result != "ok" ]]; then
        echo "❌ FAILED: $db - $result"
        exit 1
    else
        echo "✅ PASSED: $db"
    fi
done
```

4. **Restart services**:
```bash
systemctl start codex-api
systemctl start codex-workers
```

5. **Run smoke tests**:
```bash
pytest tests/integration/test_full_stack_integration.py -v --tb=short
```

6. **Monitor logs** (30 minutes):
```bash
tail -f /var/log/codex-api.log | grep -i "error\|exception"
```

---

## Performance Recovery

### Scenario: Slow Queries

**Detection**:
```bash
# Enable query timing
sqlite3 /var/data/codex_users.db ".timer on"

# Run slow query
SELECT * FROM users WHERE email LIKE '%@example.com%';
```

**Recovery**:

1. **Analyze query plan**:
```bash
sqlite3 /var/data/codex_users.db "EXPLAIN QUERY PLAN SELECT * FROM users WHERE email LIKE '%@example.com%';"
```

2. **Run optimization**:
```bash
sqlite3 /var/data/codex_users.db "PRAGMA optimize;"
```

3. **Reindex tables**:
```bash
sqlite3 /var/data/codex_users.db "REINDEX;"
```

## Scenario: Database Size Growing Too Fast

**Detection**:
```bash
# Check database size
du -sh /var/data/codex_*.db

# Check WAL file size
du -sh /var/data/codex_*.db-wal
```

**Recovery**:

1. **Force WAL checkpoint**:
```bash
sqlite3 /var/data/codex_session_logs.db "PRAGMA wal_checkpoint(TRUNCATE);"
```

2. **Archive old events** (for session_logs):
```bash
# Backup and purge events older than 30 days
sqlite3 /var/data/codex_session_logs.db << SQL
-- Create archive table
CREATE TABLE session_events_archive AS
SELECT * FROM session_events
WHERE ts < strftime('%s', 'now', '-30 days');

-- Delete archived events
DELETE FROM session_events
WHERE ts < strftime('%s', 'now', '-30 days');

-- Optimize
PRAGMA optimize;
SQL
```

---

## Troubleshooting

### Common Error Messages and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `database is locked` | Writer blocking reader | Force WAL checkpoint or restart |
| `disk I/O error` | Filesystem issue | Check disk space and permissions |
| `database disk image is malformed` | Corruption | Restore from backup |
| `UNIQUE constraint failed` | Duplicate key | Check data for duplicates, fix integrity |
| `FOREIGN KEY constraint failed` | Referential integrity | Verify related records exist |

### Health Check Procedure

**Run weekly**:

```bash
#!/bin/bash
# Health check script

echo "=== CODEX DATABASE HEALTH CHECK ==="
echo "Time: $(date)"
echo

for db in /var/data/codex_*.db; do
    db_name=$(basename $db)
    echo "Checking $db_name..."
    
    # Integrity check
    integrity=$(sqlite3 $db "PRAGMA integrity_check;")
    if [[ $integrity == "ok" ]]; then
        echo "  ✅ Integrity: PASS"
    else
        echo "  ❌ Integrity: FAIL - $integrity"
    fi
    
    # Size check
    size=$(du -h $db | cut -f1)
    echo "  📊 Size: $size"
    
    echo
done

echo "=== END HEALTH CHECK ==="
```

---

## Recovery Time Objectives (RTO) and Recovery Point Objectives (RPO)

| Database | RTO | RPO | Recovery Method |
|----------|-----|-----|-----------------|
| users.db | 5 min | 1 hour | Restore from hourly backup |
| session_logs.db | 15 min | 6 hours | Restore or truncate/restart |
| archive.db | 30 min | 24 hours | Restore or rebuild from git |

---

## Appendix: Useful SQL Commands

```sql
-- Check database integrity
PRAGMA integrity_check;

-- Optimize and analyze
PRAGMA optimize;
ANALYZE;

-- Force WAL checkpoint
PRAGMA wal_checkpoint(RESTART);  -- Restart mode (blocks during checkpoint)
PRAGMA wal_checkpoint(TRUNCATE);  -- Truncate mode (truncates WAL file)

-- Show query performance
.timer on
SELECT * FROM users;

-- Show indexes on table
PRAGMA index_list(users);
PRAGMA index_info(idx_users_email);
```

