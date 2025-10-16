# Zendesk Admin Runbook

Codex ships offline-first utilities for Zendesk administrators. This runbook
summarizes the happy path for promoting configuration changes with evidence and
version tracking.

## Environment
Export per-environment credentials (never commit secrets):

```bash
export ZENDESK_DEV_SUBDOMAIN=...
export ZENDESK_DEV_EMAIL=...
export ZENDESK_DEV_TOKEN=...
```

Validate:
```bash
python -m codex.cli zendesk env-check --env dev
python -m codex.cli zendesk deps-check
```

## Dry-run → Plan → Apply

```bash
# Diff & plan (resource example: triggers)
python -m codex.cli zendesk diff triggers desired.json current.json > diff.json
python -m codex.cli zendesk plan diff.json > plan.json
# Dry-run (no mutations, writes evidence)
python -m codex.cli zendesk apply triggers plan.json --env dev --dry-run
# Apply (mutations + version bump)
python -m codex.cli zendesk apply triggers plan.json --env dev
```

## Evidence & Metrics

Dry-run and apply operations append JSONL evidence under `.codex/evidence/` for
post-change review. After applies, consult metrics:

```bash
python -m codex.cli zendesk metrics
```
