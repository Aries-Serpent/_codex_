# ADR: "Open Entropy" Decisions — Local Gates, Reporting, and UX

## Status
Accepted — 2024-10-26

## Context
We captured several ambiguous choices ("Areas of Open Entropy") around local gates, report generation, and developer experience. This ADR records the defaults so contributors have a single reference.

## Decisions
1. **Selection precedence** — Selection Guard is authoritative; Evaluator informs tie-breaks.
2. **Template placeholders** — Unset placeholders render blank; do not fail the report.
3. **Schema checks** — If `jsonschema` is not installed, schema validation is skipped with an informational note.
4. **Smoke test data** — Tests skip if sample JSON inputs are missing.
5. **Report verbosity** — Default summarizes; `--verbose` includes gate outputs; `--save-logs` writes artifacts and the report links them.
6. **Noise/chatter** — Default suppresses connection chatter; `--verbose` reveals it for debugging.
7. **Guard signals** — Driven by `manifests/selection_guard_rules.json`.
8. **Traceability** — The chosen candidate ID must appear in `STATUS_REPORT.md` and PR bodies.
9. **Remote fetching** — Local-only by default; optional future `--fetch` remains out of scope.

## Consequences
- Clean default UX and reproducible reports.
- Optional depth without CI or network dependencies.

## Rollback
Revert this ADR and remove the extra flags from the reporter if tighter defaults are desired.
