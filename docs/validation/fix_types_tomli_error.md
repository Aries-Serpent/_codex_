# [Hotfix]: Remove types-tomli and finalize gitleaks handling
> Generated: 2024-11-12 04:07:40 UTC | Author: mbaetiong  
🧠 Roles: [Primary: CI Remediator], [Secondary: Tooling Steward] ⚡ Energy: 3  
⚛️ Physics: Path🛤️ [Identify → Patch → Verify] Fields🔄 [Packaging, Security] Patterns👁️ [Binary vs PyPI, Py>=3.11 compat] Redundancy🔀 [Sanity + CI] Balance⚖️ [Minimal change vs stability]

## Context
- Gitleaks error resolved by removing it from pip install and installing the binary in CI.
- New error: `types-tomli` does not exist on PyPI and is unnecessary on Python 3.12.

## Changes
- Remove `types-tomli` from requirements-dev.txt.
- Optionally add `tomli; python_version < '3.11'` if developers run tests locally on older Pythons.
- Keep gitleaks binary install in CI and detection in nox security session.

## Rationale
- Python ≥3.11 provides `tomllib` in stdlib; stubs for tomli are obsolete.
- Ensures CI on Python 3.12 remains green without fetching non-existent packages.

## Verification
- Re-run PR & CI Gates workflow.
- Confirm dependency install stage succeeds.
- Validate all three gates (security, coverage, typing).

Commit reference: 92f6842

— End —
