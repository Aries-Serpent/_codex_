# [Validation]: types-tomli removal and TOML compatibility
> Generated: 2025-11-12 04:07:40 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Validation Architect], [Secondary: CI Reviewer] ⚡ Energy: 3  
⚛️ Physics: Path🛤️ [Assess → Patch → Verify] Fields🔄 [Packaging, TOML] Patterns👁️ [Stdlib over vendor, Compat shim] Redundancy🔀 [Unit test + CI] Balance⚖️ [Simplicity vs portability]

## Why change
- Python ≥3.11 includes `tomllib`; `types-tomli` is obsolete and not on PyPI.
- CI uses Python 3.12; removal avoids resolution failures.

## What changed
- Removed `types-tomli` from requirements-dev.txt.
- Added `toml_compat` helper to unify usage across Python versions.
- Added minimal tests to validate loader behavior.

## Acceptance checks
| Check | Command | Pass criteria |
|---|---|---|
| Dev deps install | pip install -r requirements-dev.txt | No error for types-tomli |
| TOML compat unit tests | pytest -q tests/unit/test_toml_compat.py | 2 tests pass |
| CI coverage run | nox -s coverage | coverage.xml generated; no import errors |
| Security gate | nox -s security | gitleaks via binary, pip-audit policy enforced |
| Typing | nox -s typecheck | mypy passes or summary attached |

## Notes
- For local environments on Python <3.11, enable `tomli` via environment marker in requirements (comment provided).
- Prefer importing `toml_compat` wrapper in modules that parse TOML.

— End —
