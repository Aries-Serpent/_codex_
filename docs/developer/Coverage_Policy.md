# [Doc]: Coverage Policy and Canonical Test Session
> Generated: 2025-10-14 02:46:01 UTC | Author: mbaetiong
🧠 Roles: [Audit Orchestrator], [Capability Cartographer] ⚡ Energy: 5

## Canonical Path
- Canonical session: `nox -s coverage` (branch coverage, HTML/XML artifacts).
- Convenience aliases (`tests`, `cov`, `coverage_html`) are retained for local ergonomics but delegate to the canonical path or are marked deprecated.

## Fail-under
- The coverage floor is defined in `pyproject.toml` under `[tool.coverage.report].fail_under`.
- `nox` reads this value automatically; override at runtime via `CODEX_COV_FLOOR`.

## Artifacts
| Type | Location |
|------|----------|
| JSON (timestamped) | `artifacts/coverage/<ts>/coverage.json` |
| HTML | `artifacts/coverage_html/` |
| XML | `artifacts/coverage.xml` |

*End*
