# Status Updates & Surveys

This folder collects status reports and survey artifacts used for promotion readiness.

## Artifact Types
- `*status_report.md|json`: overall repo health (fences, schema checks, evaluation summaries)
- `*deploy_dry_run.md|json`: outputs from the deployment dry-run tool
- `repo_map_reasoning.txt`: CLI output from `codex repo-map --reasoning`

## Conventions
- Name files with a date/time suffix (UTC) or reference to the branch/PR.
- Link these in PRs that promote from ring branches (0A..0D) into `main`.

## Offline-First
All artifacts are generated locally—no CI or hosted dependencies required.
