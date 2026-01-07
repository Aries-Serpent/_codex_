# Security Policy (Offline-First)

## Reporting Security Issues

- Please avoid committing secrets. Run `python tools/security/scan_repo.py` before PRs.
- If a secret is suspected, rotate immediately and open a **local** remediation note; do not paste secrets into issues.

## File Permissions Policy

### Logging & Tracking Files

All log files and ML tracking artifacts use **owner-only permissions** (`0o600`) by default:

| File Type | Default Mode | Rationale |
|-----------|--------------|-----------|
| NDJSON Logs | `0o600` | Phase 5 contain API keys, connection strings |
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
