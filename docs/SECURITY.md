# Security Policy (Offline-First)
**Last Updated:** 2026-07-14
**Version:** v0.2.0

## Phase 4 CodeQL Security Resolution (2026-07-14)

**Status:** COMPLETE - All CodeQL security alerts resolved

Phase 4 has successfully eliminated all CodeQL security vulnerabilities through comprehensive remediation of untrusted code patterns in `workflow_run` privileged contexts. All 2 CRITICAL + 1 MEDIUM alerts have been definitively resolved.

### Workflow_run Privileged Context Security Pattern

**Key Security Principle:** Do not use git operations in `workflow_run` contexts; use GitHub API validation instead.

**Why This Matters:**
- CodeQL performs YAML-level dataflow analysis on `workflow_run` triggered jobs
- Git operations (`git fetch`, `git checkout`) create untrusted code dataflow patterns
- LGTM pragmas and code comments do NOT suppress workflow-level analysis
- Only structural changes (removing git operations) eliminate the vulnerability

**Recommended Pattern - Before (Vulnerable):**
```yaml
- name: Validate and sync
  run: |
    git fetch origin main --depth=1
    git checkout -fB _autogen_sync_ origin/main
    git add changes
    git push origin HEAD
```

**Recommended Pattern - After (Secure):**
```yaml
- name: Validate and sync  
  run: |
    # Validate branch exists via API (no git fetch/checkout)
    gh api repos/${{ github.repository }}/branches/main --silent 2>/dev/null
    # (files already prepared, git operations only on trusted main branch)
    git add changes
    git push origin HEAD
```

**Workflows Fixed in Phase 4:**
1. `iterative-self-healing-ci.yml` - Removed 3 git fetch operations from workflow_run jobs
2. `cognitive-analysis-feed.yml` - Removed 2 git fetch + 2 git checkout operations
3. `vars-guide-sync.yml` - Removed 1 git fetch + 1 git checkout operation

**For Complete Details:** See [CodeQL Alert Resolution Final Report](.codex/CODEQL_ALERT_RESOLUTION_FINAL_REPORT_2026_07_14.md)

---

## Reporting Security Issues

- Please avoid committing secrets. Run `python tools/security/scan_repo.py` before PRs.
- If a secret is suspected, rotate immediately and open a **local** remediation note; do not paste secrets into issues.

## File Permissions Policy

### Logging & Tracking Files

All log files and ML tracking artifacts use **owner-only permissions** (`0o600`) by default:

| File Type | Default Mode | Rationale |
|-----------|--------------|-----------|
| NDJSON Logs | `0o600` | may contain API keys, connection strings |
| Tracking Summaries | `0o600` | Contains model hyperparameters, system metadata |
| Rotated Backups | `0o600` | Inherits sensitivity from active logs |

**Override for Shared Monitoring**:
```bash
export CODEX_LOG_FILE_MODE=0o640  # Group-readable for monitoring agents
```

**Security Note**: Never use world-readable permissions (`0o644`) for production logs.

### Implementation Details

The permission policy is enforced through:
- `src/codex_ml/logging/permissions.py` - Central permission constants
- `src/codex_ml/logging/ndjson_logger.py` - Structured log files
- `src/codex_ml/tracking/writers.py` - ML tracking summaries

All `os.open()` calls use `get_log_file_mode()` to ensure consistent permissions across the codebase.

## Security Scanning

```bash
# Run secret scanner
python tools/security/scan_repo.py

# Check license compliance
python tools/security/license_audit.py

# Snapshot dependencies
python tools/security/dep_snapshot.py
```

All scans are offline and output to `audit_artifacts/` directory.

## Dependency Management

- Use `requirements/lock.txt` for reproducible installs
- Run `make deps` to audit licenses and dependencies
- Review `audit_artifacts/license_audit.json` periodically

## Secret Handling

See `docs/security/secret_handling.md` for detailed guidance on:
- Secret detection patterns
- Incident response
- Best practices
