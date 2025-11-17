# Security Policy (Offline-First)

## Reporting Security Issues

- Please avoid committing secrets. Run `python tools/security/scan_repo.py` before PRs.
- If a secret is suspected, rotate immediately and open a **local** remediation note; do not paste secrets into issues.

## Security Scanning

```bash
# Run secret scanner
python tools/security/scan_repo.py

# Check license compliance
python tools/security/license_audit.py

# Snapshot dependencies
python tools/security/dep_snapshot.py
```text

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
