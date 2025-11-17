# Local Status Reports

*Generate status reports for the repository using various tools and formats.*

## New: JSON-Based Status Update Generator (v1.2)

The repository now includes a comprehensive, schema-driven status update generator that provides automated analysis and JSON-formatted reports.

### Quick Start
```bash
# Generate JSON status update
codex-status-audit --generate

# Or directly
python tools/generate_status_update.py

# Output: .codex/status/_codex_status_update-YYYY-MM-DD.json
```text

### What it includes
- **Metadata**: Git context, environment info, timestamps
- **Snapshot**: Repository map, 8 capability checks, findings, test status
- **Reproducibility**: 4 core controls (dependencies, lockfiles, seeds, provenance)
- **Automation**: Dependency audit, security status
- **Security**: Security assessment and findings
- **Questions & Decisions**: Tracking open questions and architectural decisions

### See also
- **[tools/README_status_update.md](../../tools/README_status_update.md)** - Complete usage guide
- **[schemas/codex_status_update.schema.json](../../schemas/codex_status_update.schema.json)** - JSON Schema v1.2
- **[tests/test_status_update_generator.py](../../tests/test_status_update_generator.py)** - Test suite

---

## Legacy: Markdown Status Reports

*Generate a self-contained `STATUS_REPORT.md` that summarizes repository gates and (optionally) evaluates assistant candidates from a JSON summary.*

### Quick Start
```bash
python tools/status_report.py \
  --summary samples/assistant_message_summary.sample.json \
  --selected 3 \
  --out STATUS_REPORT.md
```text

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
```text

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
```text

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
