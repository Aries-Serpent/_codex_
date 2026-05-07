# Dependabot Security Alert Summary — PR #4323

**Generated:** 2026-05-06T22:45Z  
**Repo:** Aries-Serpent/_codex_  
**Branch:** copilot/fix-timeline-structure

## Master Summary Table

| ID | Package | Severity | File | Vuln Version | Fixed In | Advisory | Status |
|----|---------|----------|------|-------------|---------|----------|--------|
| 241 | Mako | High | requirements/lock.txt | 1.3.10 | ≥1.3.11 | GHSA-v92g-xgxw-vvmm | ✅ FIXED → 1.3.12 |
| 242 | Mako | High | uv.lock | (already 1.3.12) | ≥1.3.11 | GHSA-v92g-xgxw-vvmm | ✅ STALE — already patched |
| 239 | GitPython | High | requirements/lock.txt | 3.1.45 | ≥3.1.48 | GHSA-7545-fcxq-7j24 | ✅ FIXED → 3.1.50 |
| 240 | GitPython | High | uv.lock | 3.1.49 | ≥3.1.48 | GHSA-7545-fcxq-7j24 | ✅ FIXED → 3.1.50 |
| 244 | GitPython | High | requirements/lock.txt | 3.1.45 | ≥3.1.44 | GHSA-cwvm-v4w8-q58c | ✅ FIXED → 3.1.50 (same bump as #239) |
| 246 | GitPython | High | uv.lock | 3.1.49 | ≥3.1.44 | GHSA-cwvm-v4w8-q58c | ✅ FIXED → 3.1.50 (same bump as #240) |
| 245 | python-multipart | High | uv.lock | — | ≥0.0.27 | GHSA-59g5-xgcq-4qw3 | ✅ SAFE — `multipart 1.3.1` (renamed pkg, >> fix version) |

## Alert Details

- **#239/#240**: GitPython reference API path traversal — arbitrary file write/delete outside repo. Fixed ≥ 3.1.48.
- **#241/#242**: Mako path traversal via backslash URI on Windows in TemplateLookup. Fixed ≥ 1.3.11.
- **#244/#246**: GitPython newline injection in `config_writer().set_value()` enabling RCE via `core.hooksPath`. Fixed ≥ 3.1.44.
- **#245**: python-multipart DoS via unbounded multipart part headers. Fixed ≥ 0.0.27. `uv.lock` uses `multipart 1.3.1` (the renamed successor package — safe).

## Remediation PRs

All fixes applied to branch `copilot/fix-timeline-structure` (PR #4323):
- Alerts #239, #240, #244, #246 (GitPython): single bump to `gitpython==3.1.50` covers all four
- Alerts #241, #242 (Mako): bump to `mako==1.3.12`
- Alert #245 (python-multipart): `multipart 1.3.1` in uv.lock (renamed pkg) + `python-multipart==0.0.27` in requirements/lock.txt (cherry-pick from PR #4330)

## Investigation Reports

- [reports/investigation_alert_239.md](investigation_alert_239.md) — GitPython requirements/lock.txt (path traversal)
- [reports/investigation_alert_240.md](investigation_alert_240.md) — GitPython uv.lock (path traversal)
- [reports/investigation_alert_241.md](investigation_alert_241.md) — Mako requirements/lock.txt
- [reports/investigation_alert_242.md](investigation_alert_242.md) — Mako uv.lock
- [reports/investigation_alert_244.md](investigation_alert_244.md) — GitPython requirements/lock.txt (newline injection RCE)
- [reports/investigation_alert_245.md](investigation_alert_245.md) — python-multipart uv.lock (DoS)
- [reports/investigation_alert_246.md](investigation_alert_246.md) — GitPython uv.lock (newline injection RCE)

## Artifact Files

Raw Dependabot alert data was not exported to artifact files during this session.
All findings are summarized in the table and investigation reports above.
