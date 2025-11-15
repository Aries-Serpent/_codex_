# [Doc]: Copilot Instruction — Security Session (pip-audit, Bandit, gitleaks)

## Objective
Produce three artifacts and a summary in the security session:
- artifacts/security_report.json (pip-audit JSON)
- artifacts/bandit_report.txt (Bandit text)
- artifacts/gitleaks_report.json (gitleaks JSON)
- artifacts/security_summary.json (aggregated counts for PR)

## How it works
- pip-audit JSON is parsed; HIGH/CRITICAL not in security_allowlist.json (and not expired) will fail the session.
- Bandit runs with optional .bandit.yaml; we upload its text report (does not fail the session by itself).
- gitleaks runs with optional .gitleaks.toml; we upload JSON report (does not fail the session by itself).
- The aggregated summary is stored in security_summary.json.

## Commands (CI)
```bash
nox -s security
```

## Accept/Fail Criteria
- ACCEPT: No HIGH/CRITICAL dependency vulns OR only allowlisted with valid future expiry.
- FAIL: Any HIGH/CRITICAL remaining after allowlist check.

## Files to maintain
- .bandit.yaml: Bandit config (exclude tests/docs; set skips)
- .gitleaks.toml: gitleaks config (allowlist paths, entropy tuning if needed)
- security_allowlist.json: Controlled exceptions with explicit expiry

— End —
