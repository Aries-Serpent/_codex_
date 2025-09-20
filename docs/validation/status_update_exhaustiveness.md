# Validation Checklist: Exhaustive Status Update
> Updated: 2025-09-20

Use this checklist to confirm that the daily status update produced by
`tools/status/generate_status_update.py` is complete, deterministic, and scoped
to all required coverage areas.

## Preflight

| Check | Status | Notes |
| --- | --- | --- |
| Generator invoked offline (`python tools/status/generate_status_update.py --author "<name>" --date YYYY-MM-DD --write`) |  |  |
| UTC date in filename matches invocation date |  |  |
| Report stored under `.codex/status/_codex_status_update-YYYY-MM-DD.md` |  |  |
| `.codex/status_scan.json` regenerated from the same run |  |  |
| No network calls or CI integrations triggered |  |  |

## Coverage & Inventory

| Area | Requirement | Status | Notes |
| --- | --- | --- | --- |
| Stub inventory | NotImplementedError raises, placeholder raises, and trivial bodies itemised with file, symbol, and line |  |  |
| TODO density | Per-file counts for TODO/FIXME/XXX, summarised in report and JSON |  |  |
| Empty packages | All directories containing only `.gitkeep` or trivial `__init__.py` recorded |  |  |
| CLI discovery | Every click/Typer command/group listed with status classification and doc references |  |  |
| Registries | Each `*registry.py` enumerates registered keys, implementation targets, and unresolved entries |  |  |
| Tests mapping | Module count vs. detected tests summarised; modules lacking references listed in details block |  |  |
| Docs cross-references | Docs mentioning incomplete/high-risk features captured with topic keywords and line numbers |  |  |
| Packaging | Presence of pyproject, requirements*, lock artefacts, and duplicate dependency specs summarised |  |  |
| Compliance | License file inventory, `.secrets.baseline`, and `.pre-commit-config.yaml` status reported |  |  |
| Reproducibility | Data manifests, seed utilities/calls, and checkpoint artefacts surfaced |  |  |

## Determinism & Storage

| Check | Status | Notes |
| --- | --- | --- |
| Lists and tables sorted alphabetically/deterministically |  |  |
| `.codex/errors.ndjson` only updated on handled failures |  |  |
| Summary counts in Markdown match `.codex/status_scan.json` |  |  |

## Sign-off

| Role | Name | Date | Notes |
| --- | --- | --- | --- |
| Reviewer |  |  |  |
| Maintainer |  |  |  |

