# Artifact Lifecycle Automation

**Version**: 1.0  
**Last Updated**: 2026-07-15  
**Authority**: Phase D Tier 2 Documentation  
**Status**: ✅ Active

---

## 📋 Overview

The Artifact Lifecycle Automation system provides automated, scheduled cleanup and archival of session logs, artifacts, and governance records. This document describes the automation architecture, setup procedures, and operational considerations.

---

## 🎯 Objectives

1. **Automated Cleanup**: Reduce manual intervention for artifact lifecycle management
2. **Data Preservation**: Maintain archives for compliance and historical analysis
3. **Storage Optimization**: Free up disk space by removing expired artifacts
4. **Audit Trail**: Record all lifecycle actions for compliance and debugging
5. **Safety**: Verification and rollback capabilities to prevent accidental data loss

---

## 🔧 Automation Components

### 1. Main Archive Script

**Location**: `scripts/maintenance/archive_old_sessions.py`

**Purpose**:
- Identify artifacts exceeding retention windows
- Create compressed archives of identified artifacts
- Delete expired artifacts after archival
- Log all actions to audit trail
- Verify integrity via checksums

**Capabilities**:
- Multi-threaded parallel processing
- Dry-run mode for safe validation
- S3 backup support (optional)
- Checksum verification before deletion
- Automatic rollback on errors

### 2. Configuration File

**Location**: `.codex/retention_config.yaml`

**Purpose**:
- Define retention windows for each artifact type
- Configure archive format and storage
- Control cleanup behavior (dry-run, parallel workers, etc.)
- S3 integration settings (optional)

**Example**:
```yaml
retention:
  sessions:
    window_days: 90
    archive: true
    locations:
      - memory/sessions/
  
  database:
    window_days: 90
    archive: true
    paths:
      - .codex/sessions.db

archive:
  format: tar.gz
  s3_enabled: false
  verify_checksums: true

cleanup:
  dry_run: false
  verify_before_delete: true
  parallelism: 4
```

### 3. Audit Logging

**Locations**:
- `.codex/cleanup_audit.log` - Human-readable log file
- `.codex/cleanup_audit.json` - Structured audit entries

**Entry Format**:
```json
{
  "timestamp": "2026-07-15T02:15:00Z",
  "action": "archive|delete|skip|error",
  "artifact_type": "session_logs|session_database|checkpoints|reports|tests",
  "path": "/path/to/artifact",
  "details": {
    "retention_days": 90,
    "checksum": "sha256:...",
    "size_bytes": 1024000
  },
  "dry_run": false,
  "status": "success|failed"
}
```

### 4. Preservation List

**Location**: `.codex/preserved_artifacts.json`

**Purpose**: Mark specific artifacts for protection from deletion

**Format**:
```json
{
  "preserved_paths": [
    "memory/sessions/important_session.ndjson",
    "reports/critical_analysis.md"
  ],
  "preserved_until": {
    "memory/sessions/important_session.ndjson": "2026-12-31"
  }
}
```

---

## 🚀 Setup & Deployment

### Step 1: Create Directory Structure

```bash
# Create maintenance scripts directory
mkdir -p scripts/maintenance

# Create archive storage directory
mkdir -p .codex/archives

# Create configuration directory
mkdir -p .codex
```

### Step 2: Deploy Archive Script

```bash
# Copy script to location
cp scripts/maintenance/archive_old_sessions.py scripts/maintenance/

# Make executable
chmod +x scripts/maintenance/archive_old_sessions.py

# Verify installation
python scripts/maintenance/archive_old_sessions.py --help
```

### Step 3: Configure Retention Policy

Create `.codex/retention_config.yaml`:

```yaml
retention:
  sessions:
    window_days: 90
    archive: true
    locations:
      - memory/sessions/
  
  database:
    window_days: 90
    archive: true
    paths:
      - .codex/sessions.db
  
  checkpoints:
    window_days: 180
    archive: true
    archive_after_days: 180
    locations:
      - .codex/checkpoints/
  
  reports:
    window_days: 365
    archive: true
    locations:
      - reports/
      - artifacts/
  
  tests:
    window_days: 365
    archive: true
    locations:
      - coverage_reports/
      - .codex/test_skeletons/

archive:
  format: tar.gz
  compression: gzip
  s3_enabled: false
  s3_bucket: codex-archives
  s3_prefix: retention/
  verify_checksums: true

cleanup:
  dry_run: false
  verify_before_delete: true
  log_all_actions: true
  parallelism: 4
  timeout_seconds: 3600
```

### Step 4: Test in Dry-Run Mode

```bash
# Run in dry-run mode to preview changes
python scripts/maintenance/archive_old_sessions.py --dry-run

# Review audit log
cat .codex/cleanup_audit.log
```

### Step 5: Enable Automated Execution

#### Option A: Cron Schedule (Linux/macOS)

```bash
# Add to crontab
crontab -e

# Insert daily cleanup at 2:00 AM UTC (adjust timezone as needed)
0 2 * * * cd /path/to/_codex_ && python scripts/maintenance/archive_old_sessions.py >> /tmp/cleanup.log 2>&1
```

#### Option B: GitHub Actions Workflow

Create `.github/workflows/retention-cleanup.yml`:

```yaml
name: Artifact Lifecycle Cleanup

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC
  workflow_dispatch:

jobs:
  cleanup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install pyyaml
      
      - name: Run artifact lifecycle cleanup
        run: |
          python scripts/maintenance/archive_old_sessions.py
      
      - name: Upload audit log
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: cleanup-audit-log
          path: .codex/cleanup_audit.json
```

#### Option C: Manual Trigger

```bash
# Run cleanup manually
python scripts/maintenance/archive_old_sessions.py

# With specific config
python scripts/maintenance/archive_old_sessions.py --config .codex/retention_config.yaml

# In preview mode only
python scripts/maintenance/archive_old_sessions.py --dry-run --archive-only
```

---

## 📊 Usage Examples

### Basic Cleanup (Production)

```bash
# Run standard cleanup with defaults
python scripts/maintenance/archive_old_sessions.py
```

**Output**:
```
2026-07-15 02:15:00,123 [INFO] Starting artifact lifecycle management (dry_run=False)
2026-07-15 02:15:01,234 [INFO] ARCHIVE: memory/sessions/session_abc.ndjson
2026-07-15 02:15:02,345 [INFO] DELETE: memory/sessions/session_abc.ndjson
2026-07-15 02:15:15,456 [INFO] Lifecycle management complete: 5 archived, 5 deleted

============================================================
ARTIFACT LIFECYCLE MANAGEMENT SUMMARY
============================================================
Archived: 5
Deleted:  5
Errors:   0
============================================================
```

### Dry-Run Preview

```bash
# Preview what would be done
python scripts/maintenance/archive_old_sessions.py --dry-run

# Combine with archive-only to see archival without deletion
python scripts/maintenance/archive_old_sessions.py --dry-run --archive-only
```

### Custom Configuration

```bash
# Use alternate configuration file
python scripts/maintenance/archive_old_sessions.py --config custom_retention.yaml

# Override parallelism
python scripts/maintenance/archive_old_sessions.py --parallel 8

# Force delete without verification
python scripts/maintenance/archive_old_sessions.py --force-delete
```

### Preserve Critical Artifacts

Create `.codex/preserved_artifacts.json`:

```json
{
  "preserved_paths": [
    "reports/phase_12_final_report.md",
    "artifacts/campaign_execution_results.json"
  ]
}
```

Run cleanup - preserved artifacts will be skipped:

```bash
python scripts/maintenance/archive_old_sessions.py
# Outputs: [INFO] SKIP (preserved): reports/phase_12_final_report.md
```

---

## ⚙️ Configuration Options

### Command-Line Arguments

```
--dry-run                 Show what would be done without making changes
--config FILE             Use custom config file (default: .codex/retention_config.yaml)
--archive-only            Archive without deleting
--force-delete            Skip verification before deletion
--parallel N              Number of parallel workers (default: 4)
--preserve PATH           Mark specific artifact for preservation
--repo-root PATH          Repository root directory (default: .)
```

### Environment Variables

```bash
# Retention windows (days)
export RETENTION_SESSIONS=90
export RETENTION_CHECKPOINTS=180
export RETENTION_REPORTS=365
export RETENTION_TESTS=365

# Archive configuration
export ARCHIVE_ENABLED=true
export ARCHIVE_FORMAT=tar.gz
export ARCHIVE_S3_ENABLED=false
export ARCHIVE_S3_BUCKET=codex-archives

# Cleanup behavior
export CLEANUP_DRY_RUN=false
export CLEANUP_VERIFY_BEFORE_DELETE=true
export CLEANUP_PARALLELISM=4
```

### Config File Sections

#### `retention` Section

Defines retention window for each artifact type:

```yaml
retention:
  sessions:
    window_days: 90        # Days before cleanup
    archive: true          # Create archive before deleting
    locations: [...]       # Directories to scan

  database:
    window_days: 90
    archive: true
    paths: [...]           # Specific files to monitor

  checkpoints:
    window_days: 180
    archive: true
    archive_after_days: 180

  reports:
    window_days: 365
    archive: true

  tests:
    window_days: 365
    archive: true
```

#### `archive` Section

Controls archival behavior:

```yaml
archive:
  format: tar.gz           # tar.gz or tar.bz2
  compression: gzip        # gzip or bzip2
  s3_enabled: false        # Upload to S3
  s3_bucket: codex-archives
  s3_prefix: retention/
  verify_checksums: true   # Verify archive integrity
```

#### `cleanup` Section

Controls cleanup execution:

```yaml
cleanup:
  dry_run: false           # Test without changes
  verify_before_delete: true
  log_all_actions: true
  parallelism: 4           # Parallel workers
  timeout_seconds: 3600    # Max execution time
```

---

## 🔍 Monitoring & Alerts

### Audit Log Monitoring

```bash
# View recent cleanup actions
tail -f .codex/cleanup_audit.log

# Count deleted artifacts
grep '"action": "delete"' .codex/cleanup_audit.json | wc -l

# Find errors
grep '"status": "failed"' .codex/cleanup_audit.json
```

### Metrics Extraction

```bash
# Total storage freed (in MB)
jq '[.[] | select(.action == "delete") | .details.size_bytes] | add / 1024 / 1024' .codex/cleanup_audit.json

# Archive count by type
jq 'group_by(.artifact_type) | map({type: .[0].artifact_type, count: length})' .codex/cleanup_audit.json
```

### Alert Conditions

Configure alerts for:
- Cleanup script timeout (> 1 hour)
- Archive creation failure
- S3 upload failure (if enabled)
- Checksum mismatch on archive

---

## 🛡️ Safety & Recovery

### Verification Procedures

The script performs automatic verification:

1. **Age Verification**: Confirm artifact exceeds retention window
2. **Archive Integrity**: Calculate checksums before deletion
3. **Dry-Run Validation**: Preview all actions before execution
4. **Duplicate Check**: Ensure archive copy exists (if enabled)

### Rollback Procedures

If cleanup fails:

1. **Automatic Detection**: Script validates each step
2. **Partial Cleanup**: Stops on first error; preserves state
3. **Error Logging**: Records exact failure points
4. **Recovery**: Restore from archive if needed

**Manual Recovery**:

```bash
# Extract from archive if needed
cd .codex/archives
tar -xzf session_logs_archive_20260715_021500.tar.gz

# Copy back to original location
cp -r sessions/* ../../memory/sessions/

# Verify restoration
ls -la ../../memory/sessions/
```

### Backup Strategy

Before enabling automatic cleanup in production:

1. **Manual Test**: Run `--dry-run` and review output
2. **Archive Backup**: Create offline copy of archives
3. **Database Snapshot**: Export session database to CSV
4. **Audit Log Snapshot**: Save audit trail to external storage

---

## 📈 Performance Considerations

### Parallelization

Default: 4 parallel workers

```bash
# Increase for faster processing (machine with 8+ cores)
python scripts/maintenance/archive_old_sessions.py --parallel 8

# Reduce for low-resource environments
python scripts/maintenance/archive_old_sessions.py --parallel 2
```

### Memory Usage

- Each archive operation: ~100-500 MB RAM
- Typical cleanup: < 2 GB total

Monitor via:

```bash
# Watch memory during cleanup
watch -n 1 'ps aux | grep archive_old_sessions'
```

### Execution Time

Typical cleanup duration:

| Scenario | Duration |
|----------|----------|
| 100 files (~1 GB) | 5-10 minutes |
| 500 files (~5 GB) | 20-30 minutes |
| 1000 files (~10 GB) | 45-60 minutes |

Optimize with parallelism or schedule during off-peak hours.

---

## 🔐 Security Considerations

### Sensitive Data in Archives

Archives are unencrypted by default. If handling sensitive data:

```bash
# Option 1: Encrypt archives
tar czf - sessions/ | openssl enc -aes-256-cbc -out archive.tar.gz.enc

# Option 2: Use S3 with encryption
export ARCHIVE_S3_ENABLED=true
export AWS_S3_ENCRYPTION=AES256
```

### Access Control

```bash
# Restrict script execution
chmod 700 scripts/maintenance/archive_old_sessions.py

# Protect audit logs
chmod 600 .codex/cleanup_audit.*

# Protect config with secrets
chmod 600 .codex/retention_config.yaml
```

### Audit Trail Protection

Ensure audit logs are:
- Not deleted
- Retained longer than artifacts
- Exported to external system regularly
- Signed/verified if compliance-critical

---

## 📚 Related Documentation

- [Retention Policy](./RETENTION_POLICY.md)
- [Retention Policy Operations Guide](../docs/RETENTION_POLICY_OPERATIONS_GUIDE.md)
- [Archive & Recovery Procedures](./ARCHIVE_RECOVERY_PROCEDURES.md)

---

## ✅ Deployment Checklist

- [ ] Script installed at `scripts/maintenance/archive_old_sessions.py`
- [ ] Configuration file created at `.codex/retention_config.yaml`
- [ ] Directory structure created (`.codex/archives`, etc.)
- [ ] Tested in dry-run mode; output reviewed
- [ ] Cron schedule configured OR GitHub Actions workflow deployed
- [ ] Monitoring configured (log tails, alerts)
- [ ] Recovery procedures documented and tested
- [ ] Team notified of cleanup schedule
- [ ] Audit log access restricted appropriately
- [ ] First cleanup run executed successfully

---

**Document Authority**: Phase D Tier 2  
**Approved By**: @mbaetiong (D-mode autonomous)  
**Status**: ✅ Active  
**Last Review**: 2026-07-15  
**Next Review**: 2026-10-15 (quarterly)
