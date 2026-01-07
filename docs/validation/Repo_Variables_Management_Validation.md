# [Validation]: Repo Actions variables — create/update/delete/list via Codex
> Generated: Previous Cycle-10-21 03:27:15 UTC | Author: mbaetiong

Goal
- Validate full lifecycle management of GitHub Actions repository variables using Codex with GH_PAT/_CODEX_BOT_RUNNER.

Steps
1) Ensure token:
```bash
export GH_PAT="*****"  # or: export _CODEX_BOT_RUNNER="*****"
```text

2) Create/update variables:
```bash
# Curated + generic
make runner-vars OWNER=Aries-Serpent REPO=_codex_ RUNS_ON='["self-hosted","linux"]' SETS="FEATURE_FLAG=1 DEPLOY_ENV=staging"
```text

3) List variables:
```bash
make vars-list OWNER=Aries-Serpent REPO=_codex_
# Or JSON:
make vars-list OWNER=Aries-Serpent REPO=_codex_ FORMAT=json
```text

4) Update existing:
```bash
make runner-vars OWNER=Aries-Serpent REPO=_codex_ SETS="FEATURE_FLAG=0"
```text

5) Delete variables:
```bash
make runner-vars OWNER=Aries-Serpent REPO=_codex_ DELETE="FEATURE_FLAG DEPLOY_ENV"
# or
make vars-delete OWNER=Aries-Serpent REPO=_codex_ NAMES="FEATURE_FLAG DEPLOY_ENV"
```text

6) Evidence:
- .codex/evidence/runner_ops.jsonl should include configure_repo_vars entries with created/updated/deleted arrays reflecting your actions.

Troubleshooting
- 401/403: token must have repo admin + actions variables permissions.
- Values with spaces: quote appropriately, e.g., SETS=$'MESSAGE=Hello World' → SETS="MESSAGE=Hello World".
- Pagination: list_repo_vars fetches up to 100 variables per call (sufficient for most repos). Repeat if needed.
