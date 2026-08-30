# Residual Root Cleanup — Wave A/B/C

## Scope
This pass is intentionally limited to the remaining non-canonical root artifacts that are clearly generated or stale. It leaves all live source, docs, and root-governance directories in place, including `.github/` and `.codex/`.

## Wave A — Inventory and classification

### Kept at root (active config / governance)
- `.github/` — root governance; not touched.
- `.codex/` — root governance; not touched.
- `.statusrc.json` — active status/config metadata for repo health tooling.
- `.fencefixer.yml` — active fence-fixer configuration; used by tooling.
- `.secrets.baseline`, `.mypy_baseline`, `.coveragerc`, and other root config files — canonical project metadata and active tooling inputs.

### Moved to archive (stale generated artifacts)
- `.coverage_baseline.json` — empty baseline snapshot; generated state, not canonical project metadata. It was not a live source/config artifact and had no meaningful contents.
- `.secrets.new.baseline` — empty runtime artifact for secret scanning; generated interim output, not a canonical baseline file.

## Wave B — Archive move

Moved the stale residuals into the repo archive taxonomy:

- `.codex/archive/root-consolidation/temp-outputs/residual-root-cleanup/.coverage_baseline.json`
- `.codex/archive/root-consolidation/temp-outputs/residual-root-cleanup/.secrets.new.baseline`

This keeps the working root free of placeholder/generated artifacts while preserving the repo’s archive/report taxonomy and review trail.

## Wave C — Validation

Validated that the root remains minimal and stable:
- `.github/` and `.codex/` remain at the top level and retain governance control.
- Live project source/doc/config directories were not touched.
- Only clearly stale generated artifacts were moved.
- The remaining root is composed of canonical repo metadata and active project entry points.

## Result
The root is now cleaner without broad or risky reorganization, while preserving the project’s active tooling and governance structure.
