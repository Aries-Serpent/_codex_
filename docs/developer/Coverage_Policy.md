# [Doc]: Coverage Policy and Canonical Test Session
> Generated: 2025-10-14 20:23:38 UTC | Author: mbaetiong  
Energy: 5/5 

## Canonical Path
- Canonical session: `nox -s coverage` (branch coverage, HTML/XML artifacts).
- Convenience aliases (tests, cov, coverage_html) delegate to the canonical path or are marked deprecated.

## Fail-under Source of Truth
- Coverage floor is defined in `pyproject.toml` under `[tool.coverage.report].fail_under`.
- Nox resolves the floor from pyproject; runtime override: `CODEX_COV_FLOOR`.

## Artifacts
| Type | Location |
|------|----------|
| JSON (timestamped) | artifacts/coverage/<ts>/coverage.json |
| HTML | artifacts/coverage_html/ |
| XML | artifacts/coverage.xml |

## Quick Run
```bash
nox -s coverage
```

*End*
