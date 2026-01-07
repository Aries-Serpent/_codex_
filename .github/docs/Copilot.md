# [Copilot]: PR2208 — Unblock CI by removing types-tomli and finalizing security gate
> Generated: 2024-11-12 04:07:40 UTC | Author: mbaetiong  
🧠 Roles: [Primary: CI Orchestrator], [Secondary: Security Gatekeeper] ⚡ Energy: 4  
⚛️ Physics: Path🛤️ [Normalize deps → Install binary → Sanity assert → Collect → Enforce] Fields🔄 [Coverage, Security, Types] Patterns👁️ [Binary tool install, Soft-fail Optionals, Determinism] Redundancy🔀 [pip-audit + bandit + gitleaks] Balance⚖️ [Reliability vs Speed]

## Summary
- Fixed gitleaks: moved from pip dependency to CI-installed binary (v8.18.0).
- New failure: types-tomli is not available on PyPI and is unnecessary on Python ≥3.11 (tomli included as stdlib tomllib). Remove it from requirements-dev.txt.

## Required Actions
| Step | File/Area | Action | Why |
|---|---|---|---|
| 1 | requirements-dev.txt | Remove `types-tomli` | Not a valid package; unnecessary on Python 3.12 |
| 2 | requirements-dev.txt | (Optional) Add `tomli; python_version < '3.11'` | Compatibility for local py<3.11 if needed |
| 3 | Security job | Keep installing gitleaks via curl | gitleaks is a binary, not on PyPI |
| 4 | noxfile.py (security) | Keep using shutil.which("gitleaks") | Run binary if present; write empty report otherwise |
| 5 | TOML imports | Use toml_compat helper (provided) | Uniform API for tomllib/tomli across versions |
| 6 | Re-run CI | Trigger workflow | Validate coverage, security, typing gates |

## Quick Checks (after commit)
- Coverage gate: artifacts/coverage.xml exists; repo ≥95%, targets ≥96%.
- Security gate: artifacts/security_report.json, bandit/gitleaks reports, summary; High/Critical unallowlisted = 0.
- Typing gate: artifacts/mypy_summary.txt shows success.

— End —
