# [InstructionEnhancement]: PR #2208 CI Gates — Operator Notes
> Generated: 2025-11-11 22:40:08 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Operator], [Secondary: Reviewer] ⚡ Energy: 5  
⚛️ Physics: Path🛤️ [Trigger → Observe → Act] Fields🔄 [Security, Coverage, Typing] Patterns👁️ [Fail-fast, Schema-validated] Redundancy🔀 [Artifacts + Summary] Balance⚖️ [Strict vs Practical]

## Quick Commands
- Security: `nox -s security`
- Coverage: `nox -s coverage`
- Typing: `nox -s typecheck`
- Env/Docs: `nox -s env && python scripts/generate_docs_manifest.py`

## Env Filters (speed up PR loops)
- `PYTEST_MARK_EXPR="smoke or determinism"`
- `PYTEST_K_EXPR="cli and not slow"`

## Allowlist Management
- File: security_allowlist.json
- Schema: configs/schemas/security_allowlist.schema.json
- Validate: `python tools/security/validate_allowlist.py`
- Rules: Each entry must include id, rationale, expiry_date (YYYY-MM-DD). Expired entries are ignored automatically.

## Outputs (must appear in artifacts/)
- security_report.json, bandit_report.txt, gitleaks_report.json, security_summary.json
- coverage.xml (+ htmlcov/), mypy_summary.txt
- env_snapshot.json, docs_manifest.sha

— End —
