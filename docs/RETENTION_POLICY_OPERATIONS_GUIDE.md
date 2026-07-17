# Retention Policy Operations Guide
**Last Updated:** 2026-07-11
**Version:** v0.2.0

**Version**: 1.0 
**Last Updated**: 2026-07-15 
**Audience**: DevOps, Infrastructure, Maintenance Teams 
**Authority**: Phase D Tier 2 Documentation 
**Status**: Active

---

## Overview

This guide provides operational procedures for managing the artifact retention lifecycle in the Codex repository. It covers manual cleanup, emergency procedures, monitoring, and troubleshooting.

---

## Quick Start

### One-Time Manual Cleanup

```bash
# Test what would be cleaned
cd /path/to/_codex_
python scripts/maintenance/archive_old_sessions.py --dry-run

# Execute cleanup
python scripts/maintenance/archive_old_sessions.py
```

### Schedule Automatic Cleanup

**Option A: Cron (Linux/macOS)**

```bash
# Edit crontab
crontab -e

# Add line for daily 2 AM UTC cleanup
0 2 * * * cd /path/to/_codex_ && python scripts/maintenance/archive_old_sessions.py >> /var/log/codex_cleanup.log 2>&1
```

**Option B: GitHub Actions**

Push `.github/workflows/retention-cleanup.yml`:

```yaml
name: Artifact Lifecycle Cleanup
on:
 schedule:
 - cron: '0 2 * * *'
jobs:
 cleanup:
 runs-on: ubuntu-latest
 steps:
 - uses: actions/checkout@v3
 - uses: actions/setup-python@v4
 with:
 python-version: '3.11'
 - run: pip install pyyaml && python scripts/maintenance/archive_old_sessions.py
```

---

## Common Operations

### View Cleanup Status

```bash
# Check latest cleanup audit entries
tail -20 .codex/cleanup_audit.log

# View structured audit data (requires jq)
jq '.[0:5]' .codex/cleanup_audit.json

# Count operations by type
jq 'group_by(.action) | map({action: .[0].action, count: length})' .codex/cleanup_audit.json
```

### Check Storage Usage

```bash
# Size of session directory
du -sh memory/sessions/

# Size of archive directory
du -sh .codex/archives/

# Total artifact storage
du -sh memory/ reports/ artifacts/ .codex/

# Find largest files
find . -type f -size +100M -printf '%s %p\n' | sort -rn | head -20
```

### Preserve Critical Artifacts

To prevent deletion of specific artifacts:

**1. Create preservation list**

```json
{
 "preserved_paths": [
 "reports/phase_12_final_report.md",
 "memory/sessions/critical_session.ndjson"
 ],
 "preserved_until": {
 "reports/phase_12_final_report.md": "2026-12-31"
 }
}
```

**2. Save to file**

```bash
cat > .codex/preserved_artifacts.json << 'EOF'
{
 "preserved_paths": [
 "reports/phase_12_final_report.md"
 ]
}
EOF
```

**3. Run cleanup**

```bash
# Preserved artifacts will be skipped
python scripts/maintenance/archive_old_sessions.py
```

### Extend Retention Window

**Temporary Extension** (Override for specific run):

```bash
# Create temporary config with extended windows
cat > /tmp/extended_retention.yaml << 'EOF'
retention:
 sessions:
 window_days: 180 # Extended from 90
 database:
 window_days: 180
 checkpoints:
 window_days: 365 # Extended from 180
EOF

# Run with extended config
python scripts/maintenance/archive_old_sessions.py --config /tmp/extended_retention.yaml
```

**Permanent Extension**:

Edit `.codex/retention_config.yaml`:

```yaml
retention:
 sessions:
 window_days: 180 # Changed from 90
```

---

## Monitoring & Alerting

### Setup Log Monitoring

```bash
# Real-time log monitoring
tail -f .codex/cleanup_audit.log

# Watch for errors
grep ERROR .codex/cleanup_audit.log

# Daily summary
cat .codex/cleanup_audit.log | grep "Lifecycle management complete"
```

### Key Metrics

```bash
# Total artifacts archived
jq '[.[] | select(.action == "archive")] | length' .codex/cleanup_audit.json

# Total artifacts deleted
jq '[.[] | select(.action == "delete")] | length' .codex/cleanup_audit.json

# Storage freed (in MB)
jq '[.[] | select(.action == "delete") | .details.size_bytes] | add / 1024 / 1024' .codex/cleanup_audit.json

# Failed operations
jq '[.[] | select(.status == "failed")] | length' .codex/cleanup_audit.json
```

### Create Alert Rules

**For Prometheus/AlertManager:**

```yaml
groups:
 - name: codex_retention
 rules:
 - alert: CleanupScriptFailure
 expr: increase(codex_cleanup_errors_total[1h]) > 0
 annotations:
 summary: "Codex cleanup script failed"
 
 - alert: CleanupTimeout
 expr: codex_cleanup_duration_seconds > 3600
 annotations:
 summary: "Codex cleanup took too long"
 
 - alert: ArchiveChecksum Mismatch
 expr: increase(codex_archive_checksum_failures_total[1h]) > 0
 annotations:
 summary: "Archive integrity check failed"
```

### Manual Health Check

Run monthly to verify cleanup health:

```bash
#!/bin/bash
# Monthly cleanup health check

echo "=== Cleanup Health Check ==="
echo "Last cleanup:"
tail -1 .codex/cleanup_audit.log

echo "\nErrors in last 30 days:"
grep ERROR .codex/cleanup_audit.log | tail -30 | wc -l

echo "\nStorage by type:"
du -sh memory/sessions/ reports/ artifacts/ .codex/ 2>/dev/null | tail -4

echo "\nArchive directory:"
ls -lh .codex/archives/ | tail -10

echo "\nAudit log size:"
ls -lh .codex/cleanup_audit.*

echo "\nDone!"
```

---

## Emergency Procedures

### Cleanup Script Hanging

If script appears hung (no output for > 30 minutes):

```bash
# Find process
ps aux | grep archive_old_sessions

# Kill if necessary
kill -9 <PID>

# Check for partial state
ls -la .codex/archives/*.tmp

# Cleanup temp files
rm -f .codex/archives/*.tmp

# Restart cleanup
python scripts/maintenance/archive_old_sessions.py
```

### Out of Disk Space

If cleanup fails due to disk space:

```bash
# Check current usage
df -h

# Find largest artifacts
find . -size +1G -type f | head -10

# Manually delete very old files
find memory/sessions/ -mtime +90 -delete

# Free cache directories
rm -rf .pytest_cache/ __pycache__/ .mypy_cache/

# Run cleanup again
python scripts/maintenance/archive_old_sessions.py
```

### Archive Corruption

If archive verification fails:

```bash
# List suspicious archives
jq '[.[] | select(.action == "archive" and .details.checksum == null)]' .codex/cleanup_audit.json

# Validate existing archives
for f in .codex/archives/*.tar.gz; do
 echo "Checking $f..."
 tar -tzf "$f" > /dev/null && echo " OK" || echo " CORRUPTED"
done

# Remove corrupted archives
rm .codex/archives/corrupted_*.tar.gz

# Re-run cleanup to regenerate
python scripts/maintenance/archive_old_sessions.py --archive-only
```

### Data Recovery

If data is accidentally deleted:

```bash
# 1. Check for archive
ls -la .codex/archives/ | grep session

# 2. Extract from archive
cd .codex/archives
tar -xzf session_logs_archive_*.tar.gz

# 3. Copy back to original location
cp -v sessions/*.ndjson ../../memory/sessions/

# 4. Verify restoration
ls -lh ../../memory/sessions/ | grep -E 'ndjson$' | wc -l

# 5. Update audit log
echo "Data recovered from archive: $(date)" >> .codex/cleanup_audit.log
```

---

## Backup & Recovery

### Pre-Cleanup Backup

Before enabling automatic cleanup:

```bash
# Create backup of current state
mkdir -p backups/pre_cleanup_$(date +%Y%m%d)

# Backup session logs
cp -r memory/sessions/ backups/pre_cleanup_$(date +%Y%m%d)/

# Backup database
cp .codex/sessions.db backups/pre_cleanup_$(date +%Y%m%d)/

# Backup audit logs
cp .codex/cleanup_audit.* backups/pre_cleanup_$(date +%Y%m%d)/

# Verify backup
du -sh backups/pre_cleanup_*/
```

### Archive Backup to External Storage

```bash
# Create tarball of all archives
cd .codex
tar -czf archives_backup_$(date +%Y%m%d).tar.gz archives/

# Upload to external storage (e.g., S3, GCS)
aws s3 cp archives_backup_*.tar.gz s3://backup-bucket/codex/

# Verify upload
aws s3 ls s3://backup-bucket/codex/ --recursive
```

---

## Troubleshooting

### Problem: Cleanup Deletes Wrong Files

**Symptoms**: Files modified recently are deleted

**Causes**:
- Clock skew on system
- Incorrect retention window configuration
- File timestamps corrupted

**Resolution**:

```bash
# 1. Verify system time
date

# 2. Check file timestamps
stat memory/sessions/session_*.ndjson | grep Modify

# 3. Review retention config
cat .codex/retention_config.yaml | grep window_days

# 4. Run in dry-run to preview
python scripts/maintenance/archive_old_sessions.py --dry-run

# 5. Adjust retention windows if needed
```

### Problem: Cleanup Script Crashes

**Symptoms**: Script exits with error

**Resolution**:

```bash
# 1. Check error message
python scripts/maintenance/archive_old_sessions.py 2>&1 | tail -50

# 2. Verify permissions
ls -la scripts/maintenance/archive_old_sessions.py
ls -la .codex/

# 3. Check Python environment
python --version
pip list | grep pyyaml

# 4. Run with verbose logging
python -u scripts/maintenance/archive_old_sessions.py 2>&1 | tee debug_cleanup.log

# 5. Check system resources
free -h
df -h
```

### Problem: Archives Not Created

**Symptoms**: Files deleted but no archives

**Causes**:
- Archive disabled in config
- Insufficient disk space
- Archive directory permission issue

**Resolution**:

```bash
# 1. Check archive config
grep archive_enabled .codex/retention_config.yaml

# 2. Check archive directory permissions
ls -ld .codex/archives/
chmod 755 .codex/archives/

# 3. Check disk space
df -h .codex/

# 4. Test archive creation manually
tar -czf .codex/archives/test.tar.gz memory/sessions/sample.ndjson
```

---

## Operational Checklists

### Daily

- [ ] Check cleanup completed successfully (if scheduled)
 ```bash
 tail -1 .codex/cleanup_audit.log | grep "complete"
 ```
- [ ] Verify disk space adequate
 ```bash
 df -h / | tail -1
 ```
- [ ] Check for any errors in audit log
 ```bash
 grep -c "ERROR\|FAILED" .codex/cleanup_audit.log
 ```

### Weekly

- [ ] Review artifact storage trends
 ```bash
 du -sh memory/sessions/ reports/ artifacts/
 ```
- [ ] Verify archive integrity
 ```bash
 find .codex/archives/ -name "*.tar.gz" -exec tar -tzf {} \; > /dev/null
 ```
- [ ] Check audit log size (rotate if > 100 MB)
 ```bash
 ls -lh .codex/cleanup_audit.log
 ```

### Monthly

- [ ] Generate cleanup summary report
 ```bash
 jq 'group_by(.action) | map({action: .[0].action, count: length})' .codex/cleanup_audit.json
 ```
- [ ] Review and adjust retention windows if needed
- [ ] Backup archives to external storage
- [ ] Test data recovery procedure

### Quarterly

- [ ] Review retention policy with team
- [ ] Audit preserved artifacts list
- [ ] Update documentation if needed
- [ ] Plan for next quarter's cleanup requirements

---

## Related Resources

- [Retention Policy](../.codex/RETENTION_POLICY.md)
- [Artifact Lifecycle Automation](../.codex/ARTIFACT_LIFECYCLE_AUTOMATION.md)
- [Archive & Recovery Procedures](../.codex/ARCHIVE_RECOVERY_PROCEDURES.md)

---

## Support & Escalation

### Common Support Issues

| Issue | Contact | Resolution Time |
|-------|---------|-----------------|
| Cleanup failed | DevOps Team | 2 hours |
| Data recovery | Infrastructure Team | 4 hours |
| Policy adjustment | Project Lead | 1 business day |
| Emergency retention | CTO | Immediate |

### Escalation Path

1. **First Response**: DevOps Team (check logs, restart script)
2. **Investigation**: Infrastructure Team (check resources, verify backups)
3. **Decision**: Project Lead (approve exceptions, policy changes)
4. **Emergency**: CTO (emergency override, data preservation decisions)

---

## Sign-Off

**Document Authority**: Phase D Tier 2 
**Approved By**: @mbaetiong (D-mode autonomous) 
**Date**: 2026-07-15 
**Team Acknowledgment**: _______________ (Date: _________)

---

**Version History**:
- v1.0 (2026-07-15): Initial operations guide
 - Quick start procedures
 - Common operations
 - Monitoring and alerting setup
 - Emergency procedures
 - Troubleshooting guide
 - Operational checklists
