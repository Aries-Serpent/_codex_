# Local Status Reports

*Generate a self-contained `STATUS_REPORT.md` that summarizes repository gates and (optionally) evaluates assistant candidates from a JSON summary.*

## Quick Start
```bash
python tools/status_report.py \
  --summary samples/assistant_message_summary.sample.json \
  --selected 3 \
  --out STATUS_REPORT.md
```

## Verbose & Artifacts

- Add `--verbose` to embed each gate's stdout/stderr directly in the generated markdown.
- Add `--save-logs` to persist per-tool logs under `.codex/status/` and automatically reference them at the end of the report.

```bash
python tools/status_report.py \
  --summary samples/assistant_message_summary.sample.json \
  --selected 3 \
  --verbose \
  --save-logs \
  --out STATUS_REPORT.md
```

## What it includes
- Fence integrity result
- Manifest schema validation result
- Evaluator score run (if `--summary` provided)
- Selection Guard result (if `--summary` and `--selected` provided)
- Timestamps and exit codes for reproducibility

## Notes
- This is **local-only** (no CI, no network).
- If `jsonschema` is not installed, schema checks are skipped with an info note.

## See also
- `docs/templates/status_update.md`
- `docs/ops/local_gates.md`

---

## Template Mode (rich report)

You can render the report into a fuller template that includes a **Repo Map** and a **Capability Audit Table** populated by local heuristics.

```bash
python tools/status_report.py \
  --summary samples/assistant_message_summary.sample.json \
  --selected 3 \
  --template docs/templates/status_update.md \
  --branch codex/implement-local-status-reporter_2025-10-26 \
  --pr 1916 \
  --out STATUS_REPORT.md
```

**Placeholders that will be filled:**
- `{{branch}}` — branch name passed via `--branch`
- `{{pr}}` — PR number (or short label) passed via `--pr`
- `{{gates_summary}}` — rendered bullets for the local gates
- `{{repo_map}}` — a top-level directory map with key file signals
- `{{capability_table}}` — a markdown table of capability status inferred from local files
- `{{timestamp}}` — generation time

If a placeholder is missing in the template, it is ignored. If an argument is not provided (e.g., `--pr`), the placeholder is left blank.

**Heuristics used for repo map & capability table:**
- Top-level directories and counts (`docs/`, `tools/`, `tests/`, `schemas/`, `manifests/`, etc.).
- Presence of key files (e.g., `pyproject.toml`, `Dockerfile`, `.pre-commit-config.yaml`, `tools/validate_fences.py`, `tools/codex_evaluator.py`, `tools/selection_guard.py`, `tools/schema_validate.py`, `tools/status_report.py`).
- Capabilities marked as:
  - *Implemented* when required artifacts are present,
  - *Partial* when some but not all are present,
  - *Missing* otherwise.

> Template mode remains **local-only**; no GitHub or network access is performed by the reporter.

## Selection summary (optional)

If you provide `--summary`, the status reporter will also invoke `selection_report.py` and:
- Save a standalone `SELECTION_REPORT.md` to `.codex/status/`.
- Add a brief “Selection (summary)” section with exit status and (when `--verbose`) inline output.

See `docs/ops/selection_reports.md` for details on selection signals and rationale.

## Artifacts

When `--save-logs` is used, gate logs are written to `.codex/status/` (e.g., `fences.out`, `schemas.err`) for deeper debugging, and the report footer links to the directory.
