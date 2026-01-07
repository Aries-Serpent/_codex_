# Guide: Copilot Security Gates & Scans (v1.2)
> Generated: 2025-11-02 14:59:25 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Security Gatekeeper], [Secondary: CI Maintainer] ⚡ Energy: 5  
⚛️ Physics: Path🛤️ Fields🔄 Patterns👁️ Redundancy🔀 Balance⚖️

Purpose
- Standardize security validation steps aligned to the v1.2 status template.
- Ensure repeatable, offline-friendly scans with clear pass/fail criteria.

Tools and Commands
| Category | Tool | Command | Pass Criteria |
|---|---|---|---|
| SAST (Python) | bandit | bandit -q -r src | No medium/high issues or documented exceptions |
| Secrets | detect-secrets | detect-secrets scan > .secrets.baseline && detect-secrets audit .secrets.baseline | Baseline audited; no new findings |
| Dependencies | pip-audit | pip-audit -r requirements.txt | 0 critical/high, or accepted with rationale |
| Schema Validation | schema_validate.py | python tools/schema_validate.py --data D --schema S | Exit code 0 |
| Audit Chain | build_integrity_chain.py | python scripts/audit/build_integrity_chain.py | Creates audit_run_manifest.json |

DoD (Definition of Done)
- Bandit finds 0 high-severity issues or all are triaged with inline comments and references.
- detect-secrets baseline committed and audited in PRs.
- pip-audit shows 0 critical/high unless accepted with tracked issue.
- Status JSON example validates against schema in CI.
- Audit chain artifacts built and uploaded as workflow artifacts.

Notes
- For offline modes, cache PyPI mirrors or vendor minimal wheels.
- Avoid printing secrets in CI logs; scrub with GitHub Actions masking.
