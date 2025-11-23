# Codex Status Audit Command

## Overview

The `codex-status-audit` command provides a comprehensive status update audit report for the Codex repository. It traverses the codebase, runs capability audits, and generates detailed status reports.

## Usage

```bash
codex-status-audit [OPTIONS]
```text

### Options

- `--output, -o OUTPUT`: Output directory for reports (default: `reports/`)
- `--baseline, -b BASELINE`: Path to baseline `capabilities_scored.json` for delta comparison
- `--artifacts ARTIFACTS`: Artifacts directory (default: `audit_artifacts/`)
- `--skip-audit`: Skip running the audit pipeline (use existing artifacts)
- `--quick`: Quick mode: only run essential stages

## Examples

### Generate a full status audit report

```bash
codex-status-audit
```text

This will:
1. Run the complete capability audit pipeline
2. Generate a status update report
3. Save artifacts to `audit_artifacts/`
4. Save the report to `reports/`

### Skip audit and use existing artifacts

```bash
codex-status-audit --skip-audit
```text

This is useful when you've already run the audit and just want to regenerate the report.

### Compare against a baseline

```bash
codex-status-audit --baseline audit_artifacts/capabilities_scored.json.baseline
```text

This will show improvements and regressions compared to the baseline.

### Custom output directory

```bash
codex-status-audit --output my_reports
```text

## Output

The command generates:

1. **Audit Artifacts** (in `audit_artifacts/`):
   - `context_index.json`: File index of the repository
   - `facets.json`: Categorized file facets
   - `capabilities_raw.json`: Raw capability detection results
   - `capabilities_scored.json`: Scored capabilities
   - `gaps.json`: Low maturity capabilities

2. **Status Report** (in `reports/`):
   - `codex_status_update_YYYYMMDD_HHMMSS.md`: Timestamped status report

### Report Contents

The status report includes:

- **Executive Summary**: Total capabilities, average score, low maturity count
- **Low Maturity Focus**: Capabilities below threshold with primary deficits
- **Movement Since Baseline**: Improvements and regressions (if baseline provided)
- **Weights**: Effective component weights used for scoring
- **Integrity Chain**: Repository and template checksums
- **Next Actions**: Recommended steps

## Integration

The command orchestrates two main tools:

1. `scripts/space_traversal/audit_runner.py`: Runs the capability audit pipeline (stages S1-S7)
2. `scripts/space_traversal/status_update_report.py`: Generates the status update report

## Deterministic capability-audit compilation (single reference)

Use this checklist when you need one canonical view of the capability-audit pipeline and its supporting assets:

- **Entrypoint & orchestration**: `cli/status_audit.py` (this command) calls `scripts/space_traversal/audit_runner.py` for capability detection and `scripts/space_traversal/status_update_report.py` for report assembly.
- **Schemas & templates**: `docs/templates/status/codex_status_template_v1.2.md` with schemas `docs/templates/status/codex_status_template.schema_v1.2.json` and `.yaml`; authoring guidance in `docs/templates/status/authoring_guide_v1.2.md`.
- **Detectors guidance**: `detectors/README.md` plus detector implementations under `scripts/space_traversal/detectors/` (keep outputs deterministic and side-effect free).
- **Config & validation helpers**: `tools/validate_status_report.py`, `tools/generate_status_update.py`, and schema helpers in `scripts/space_traversal/schemas/`.
- **Tests that guard production behavior**: `tests/cli/test_status_audit.py` (CLI wiring), `tests/templates/test_status_template.py` (templates/schemas present), and `tests/detectors/` (detector contract).

Recommended verification commands (use `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` for determinism):

```bash
codex-status-audit --quick --output reports --artifacts audit_artifacts
python tools/validate_status_report.py --help  # confirm validation CLI available
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests/cli/test_status_audit.py tests/templates/test_status_template.py tests/detectors
```

If optional ML dependencies are missing, run with `--skip-audit` to reuse existing artifacts while still exercising the reporting path.

## See Also

- `codex-audit-runner run`: Run the full audit pipeline directly
- `codex-audit-runner explain CAPABILITY`: Explain a capability's score breakdown
- `codex-audit-runner diff --old OLD --new NEW`: Compare two audit runs
