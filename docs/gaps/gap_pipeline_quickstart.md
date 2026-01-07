# Gap Pipeline Quickstart

This guide shows how to run the _codex_ gap pipeline end-to-end using the
unified CLI.

## 1. Prerequisites

- A recent audit file, e.g.:

  - `_codex_: Status Update (2025-11-27)` saved as
    `_codex_status_update-Previous Cycle-11-27.md`

- Local environment with:
  - Python 3.10+ (or similar)
  - `pyyaml` installed

## 2. Optional metadata files

The pipeline will automatically use these files if they exist:

- `codex_hardship.yaml`
  - Gap-level risk and notes metadata.
  - Validated by `tools/codex_hardship_validate.py`.

- `codex_capability_map.yaml`
  - Capability → locations mapping (code / tests / docs).
  - Validated by `tools/codex_capability_map_validate.py`.

## 3. Run the gap pipeline

From the repository root:

```bash
python tools/codex_gap_pipeline.py \
  --audit _codex_status_update-Previous Cycle-11-27.md \
  --registry codex_gap_registry.yaml
```

On success you should see:
- `codex_gap_registry.yaml`
- `codex_yaml_gap_report.md`
- `codex_gap_trends.md`
- (Existing) `codex_change_log.md`
- (Existing) `codex_error_questions.md`

## 4. Next steps
- Use codex_gap_bootstrap.py <gap_id> to create per-gap docs under
  docs/gaps/.
- Use the registry and capability map to identify where to implement code,
  tests, and docs for each gap.
- Re-run the pipeline after each implementation round to keep the registry
  and reports up to date.
