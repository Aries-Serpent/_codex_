# [Validation]: Security Gate — pip-audit, Bandit, gitleaks

## Acceptance Criteria
- pip-audit JSON exists, parsed; 0 HIGH/CRITICAL unless in security_allowlist.json and not expired.
- bandit report exists (text).
- gitleaks report exists (JSON).
- Combined summary artifacts/security_summary.json present.

## Commands
```bash
nox -s security
python tools/security/merge_security_reports.py  # optional; nox already aggregates
```text

## Files
- .bandit.yaml — exclude noisy paths; skip B101; configure severity/confidence
- .gitleaks.toml — workspace allowlist; add rules for test fixtures if needed
- security_allowlist.json — explicit, time-bound exceptions

— End —
