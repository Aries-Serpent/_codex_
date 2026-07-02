# Session and Artifact Retention Policy

**Version**: 1.0  
**Last Updated**: 2026-07-15  
**Authority**: Phase D Tier 2 Documentation  
**Status**: ✅ Active

---

## 📋 Policy Overview

This document defines the retention schedule and lifecycle management for all artifacts generated during the Codex AI codebase analysis, optimization, and governance workflows. The policy ensures data is retained long enough for verification and compliance while managing storage and operational overhead.

### Guiding Principles

1. **Compliance**: Maintain records required for audit trails and governance
2. **Efficiency**: Archive or delete data once operational value expires
3. **Recovery**: Preserve sufficient historical data for debugging and forensic analysis
4. **Optimization**: Reduce operational overhead through predictable cleanup cycles
5. **Flexibility**: Support extended retention for critical analyses with archival options

---

## 📁 Artifact Type Retention Schedule

### 1. Session Logs (NDJSON Format)

**Location**: `memory/sessions/` (or configured session directory)  
**Format**: Newline-delimited JSON (NDJSON)  
**Retention Period**: **90 days**

**Rationale**:
- Contains real-time decision logs, tool invocations, and interaction records
- Required for debugging session behavior and understanding agent decisions
- Sufficient for post-incident analysis and pattern identification
- Reduces storage overhead after 90 days (most active analysis windows < 30 days)

**Lifecycle**:
1. **Days 0-90**: Hot storage (immediately accessible)
2. **Day 90**: Automatic deletion (no archive)
3. **Before deletion**: Optional manual backup via `archive_old_sessions.py`

**Content Examples**:
```
turn_index | timestamp | user_message | assistant_response | tool_calls | metadata
```

---

### 2. SQLite Session Database

**Location**: `.codex/sessions.db` (or configured database path)  
**Format**: SQLite database  
**Retention Period**: **90 days**

**Rationale**:
- Stores indexed session metadata (turn history, checkpoints, events)
- Supports rapid querying of session state and event sequences
- Can be recreated from raw logs if needed
- 90-day window aligns with NDJSON log retention

**Lifecycle**:
1. **Days 0-90**: Active database (indexed, queryable)
2. **Day 90**: Archive to compressed backup or delete
3. **Archive trigger**: Automatic via `archive_old_sessions.py`

**Tables Managed**:
- `sessions` - session metadata
- `turns` - turn-by-turn records
- `checkpoints` - workflow checkpoints
- `events` - session events
- `tool_requests` - tool invocation records
- `attachments` - uploaded file references

---

### 3. Test Skeletons & Coverage Reports

**Location**: `coverage_reports/`, `tests/`, `.codex/test_skeletons/`  
**Format**: JSON, YAML, Python, HTML  
**Retention Period**: **365 days (1 year)**

**Rationale**:
- Test infrastructure is long-lived; coverage trends are analyzed across releases
- Gap-fill test skeletons inform long-term coverage strategy
- Annual retention allows trend analysis (e.g., "coverage improvement YoY")
- These are relatively small files and high-value for planning

**Lifecycle**:
1. **Days 0-365**: Active retention (reference and analysis)
2. **Day 365**: Archive to compressed backup
3. **Day 730**: Delete archived copies (2-year retention option available)
4. **Archive format**: Compressed YAML/JSON bundles with date prefix

**Content Examples**:
```
- coverage_report_2026-07-15.json
- test_skeleton_gaps_phase_12.yaml
- mutation_test_results_2026-Q3.html
```

---

### 4. Checkpoint Files

**Location**: `.codex/checkpoints/`, `.codex/plans/`, session-specific checkpoint dirs  
**Format**: YAML, JSON, Markdown  
**Retention Period**: **180 days with archive option**

**Rationale**:
- Checkpoints represent key decision points and validation states
- Needed for understanding workflow progression and rollback capability
- Can be archived for historical reference beyond 180 days
- Archive provides insurance against unexpected rework

**Lifecycle**:
1. **Days 0-180**: Hot storage (immediately accessible for rollback)
2. **Day 180**: Move to archive (compressed tarball)
3. **Day 365**: Option to delete archived checkpoints (keep or extend)
4. **Archive format**: `checkpoints_archive_YYYY-MM-DD.tar.gz`

**Checkpoint Types Covered**:
- Workflow state checkpoints (YAML format)
- Phase delivery checkpoints (JSON metadata)
- Approval/sign-off checkpoints (Markdown + metadata)
- Recovery checkpoints (binary state snapshots)

---

### 5. Campaign Execution Reports

**Location**: `reports/`, `.codex/campaigns/`, `artifacts/`  
**Format**: Markdown, JSON, CSV  
**Retention Period**: **365 days (1 year)**

**Rationale**:
- Executive summaries and campaign results inform future planning
- Required for accountability and post-mortem analysis
- Help identify recurring issues and process improvements
- Small file sizes; high-value retention relative to storage cost

**Lifecycle**:
1. **Days 0-365**: Active retention (reference and analysis)
2. **Day 365**: Archive to compressed backup
3. **Day 730**: Delete archived copies (2-year retention available)
4. **Archive format**: `campaign_reports_archive_YYYY.tar.gz`

**Report Types Covered**:
- Campaign execution summaries
- Phase delivery reports
- QA validation results
- Incident post-mortems
- Metrics and KPI snapshots

---

### 6. Artifact Types Summary Table

| Artifact Type | Location | Format | Retention | Archive | Notes |
|---------------|----------|--------|-----------|---------|-------|
| Session logs | `memory/sessions/` | NDJSON | 90 days | Optional | Auto-cleanup |
| Session DB | `.codex/sessions.db` | SQLite | 90 days | Optional | Indexed access |
| Test skeletons | `tests/`, `.codex/test_skeletons/` | JSON/YAML | 365 days | After day 365 | Trend analysis |
| Coverage reports | `coverage_reports/` | JSON/HTML | 365 days | After day 365 | Planning input |
| Checkpoints | `.codex/checkpoints/` | YAML/JSON | 180 days | After day 180 | Rollback support |
| Campaign reports | `reports/`, `artifacts/` | Markdown/JSON | 365 days | After day 365 | Accountability |

---

## 🔄 Lifecycle Stages

```
┌─────────────────────────────────────────────────────────────────┐
│ ARTIFACT LIFECYCLE FLOW                                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  CREATION           ACTIVE USE           RETENTION              │
│  ────────           ──────────           ─────────              │
│     │                  │                      │                 │
│  [File Created] ──> [Days 0-N] ──> [Day N+1] ──> Archive/Delete│
│                    (Hot Storage)    (Cool Storage)              │
│                                           │                     │
│                                    ┌──────┴──────┐              │
│                                    │             │              │
│                            [Archive Tarball] [Delete]          │
│                                    │             │              │
│                            [S3 Upload]    [Local Cleanup]     │
│                            [Optional]      [Automatic]         │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Stage Definitions

1. **Creation** (Day 0)
   - File generated during normal operations
   - Timestamp recorded for age calculation
   - Added to hot storage location

2. **Active Use** (Days 0-N)
   - Immediately accessible for queries/analysis
   - Indexed for rapid retrieval (if applicable)
   - Updated with new data as sessions continue

3. **Retention** (Day N+1 onward)
   - No longer modified; available for reference only
   - Moved to cool storage or archive
   - May be deleted if no archive requested

4. **Archive** (Optional)
   - Compressed and date-stamped
   - Uploaded to S3 (if configured)
   - Retained for compliance/historical reference

5. **Deletion** (Policy expiry)
   - Automatic deletion via cleanup script
   - Audit trail recorded before deletion
   - No recovery available after deletion

---

## 🧹 Automated Cleanup & Archival

### Overview

The lifecycle is managed by automated scripts that:
- Identify artifacts exceeding retention windows
- Optionally archive to compressed tarballs
- Delete expired artifacts
- Log all cleanup actions
- Verify integrity before deletion

### Cleanup Script

**Location**: `scripts/maintenance/archive_old_sessions.py`

**Features**:
- Multi-threaded archive generation
- S3 upload support (optional)
- Dry-run mode for validation
- Audit trail logging
- Checksum verification
- Rollback capability

### Automation Triggers

1. **Manual Trigger**: `python scripts/maintenance/archive_old_sessions.py`
2. **Cron Schedule**: Daily at 02:00 UTC (configurable)
3. **CI/CD Pipeline**: Post-merge cleanup stage
4. **Webhook**: External trigger via GitHub Actions

---

## ⚙️ Configuration

### Environment Variables

```bash
# Retention windows (days)
RETENTION_SESSIONS=90
RETENTION_CHECKPOINTS=180
RETENTION_REPORTS=365
RETENTION_TESTS=365

# Archive configuration
ARCHIVE_ENABLED=true
ARCHIVE_FORMAT=tar.gz  # or tar.bz2
ARCHIVE_S3_ENABLED=false
ARCHIVE_S3_BUCKET=codex-archives
ARCHIVE_S3_PREFIX=retention/

# Cleanup behavior
CLEANUP_DRY_RUN=false
CLEANUP_VERIFY_BEFORE_DELETE=true
CLEANUP_LOG_LEVEL=INFO
```

### Configuration File

**Location**: `.codex/retention_config.yaml`

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
    archive_after_days: 365
    locations:
      - reports/
      - artifacts/
  
  tests:
    window_days: 365
    archive: true
    locations:
      - coverage_reports/
      - tests/

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

---

## 🔐 Safety & Compliance

### Verification Procedures

Before any deletion:

1. **Checksum Verification**: Confirm archive integrity
2. **Age Confirmation**: Verify retention window exceeded
3. **Duplicate Check**: Ensure archive copy exists (if enabled)
4. **Dry-Run Validation**: Test without actual deletion
5. **Audit Log**: Record all deletion decisions

### Rollback Procedures

If cleanup error occurs:

1. **Automatic Detection**: Script validates each step
2. **Partial Cleanup**: Stop on first error; preserve state
3. **Audit Trail**: Log exact deletion points
4. **Recovery**: Restore from archive if available
5. **Alert**: Notify operators of failure

### Compliance & Audit

**Audit Trail Locations**:
- `.codex/cleanup_audit.log` - All cleanup actions
- `.codex/archive_manifest.json` - Archive inventory
- `reports/retention_monthly_report.md` - Summary reports

**Audit Entry Format**:
```json
{
  "timestamp": "2026-07-15T02:15:00Z",
  "action": "delete",
  "artifact_type": "session_logs",
  "path": "memory/sessions/session_abc123.ndjson",
  "age_days": 91,
  "checksum": "sha256:...",
  "status": "success",
  "operator": "automatic_cleanup"
}
```

---

## 📊 Monitoring & Reporting

### Metrics Tracked

- **Total artifacts**: Count by type
- **Storage usage**: Bytes by artifact type
- **Archive operations**: Count, duration, success rate
- **Cleanup actions**: Deleted artifacts, recovery requests
- **Policy violations**: Artifacts exceeding window

### Monthly Reports

**Location**: `reports/retention_monthly_report.md`

**Contents**:
- Artifacts processed
- Storage freed
- Archive operations completed
- Any policy violations or exceptions
- Recommendations for retention adjustments

### Alerting

**Alert Conditions**:
- Cleanup script failure or timeout
- Checksum verification failure
- S3 upload failure (if enabled)
- Storage threshold exceeded
- Archive missing for critical artifacts

---

## 🚀 Implementation Timeline

| Phase | Timeframe | Action |
|-------|-----------|--------|
| Phase 1 | Week 1 | Policy adoption; configure retention windows |
| Phase 2 | Week 2 | Deploy cleanup script; validate in dry-run mode |
| Phase 3 | Week 3 | Enable automatic cleanup; monitor results |
| Phase 4 | Week 4+ | Continuous operation; monthly review |

---

## 📝 Exceptions & Extensions

### Long-Retention Request

For artifacts exceeding standard retention windows:

1. **Executive Decision**: Approval from project lead
2. **Duration**: Specify extension period (e.g., +6 months)
3. **Justification**: Document business case
4. **Location**: Update `RETENTION_POLICY_EXCEPTIONS.md`
5. **Notification**: Alert cleanup script via config

### Critical Artifact Preservation

For mission-critical analyses:

1. **Manual Archive**: `scripts/maintenance/archive_old_sessions.py --preserve <path>`
2. **S3 Backup**: Upload to dedicated S3 bucket
3. **Versioning**: Maintain multiple snapshots
4. **Metadata**: Document version history

---

## 📚 Related Documentation

- [Artifact Lifecycle Automation](./ARTIFACT_LIFECYCLE_AUTOMATION.md)
- [Retention Policy Operations Guide](../docs/RETENTION_POLICY_OPERATIONS_GUIDE.md)
- [Session Log Format Specification](./SESSION_LOG_FORMAT.md)
- [Archive & Recovery Procedures](./ARCHIVE_RECOVERY_PROCEDURES.md)

---

## ✅ Approval & Authority

**Document Authority**: Phase D Tier 2  
**Approved By**: @mbaetiong (D-mode autonomous)  
**Status**: ✅ Active  
**Last Review**: 2026-07-15  
**Next Review**: 2026-10-15 (quarterly)

---

**Version History**:
- v1.0 (2026-07-15): Initial policy document
  - 90-day retention for session logs and databases
  - 180-day retention for checkpoints with archive
  - 365-day retention for test skeletons, coverage reports, campaign reports
  - Automated cleanup and archival procedures
  - S3 backup support (optional)
