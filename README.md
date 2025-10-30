# Documentation Moved

All primary documentation now lives in the [`docs/`](docs/) directory.

- Start with [`docs/README_ROOT.md`](docs/README_ROOT.md)
- Contribution guidelines: [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md)
- Changelog: [`docs/CHANGELOG.md`](docs/CHANGELOG.md)
- Operational templates: [`docs/templates/README.md`](docs/templates/README.md)

Legacy references should update to the new paths under `docs/`.

> This repo is designed for **local-only** workflows. No CI is enabled by default.

## Local Gates & Status Reports

This repository ships **local-only** quality gates (no CI) and a local status reporter:

- See **docs/ops/local_gates.md** for running fences, evaluator, schema checks, and the selection guard.
- See **docs/ops/status_reports.md** for generating a reusable **STATUS_REPORT.md** (including template mode, `--verbose`, and `--save-logs`).

Quick start:
```bash
python tools/status_report.py --summary samples/assistant_message_summary.sample.json --selected 3 --out STATUS_REPORT.md
```

### Repository Status Audit

Generate a comprehensive status update audit report for the Codex repository:

```bash
# Full audit and report
codex-status-audit

# Quick regeneration with existing artifacts
codex-status-audit --skip-audit

# Compare against baseline
codex-status-audit --baseline audit_artifacts/capabilities_scored.json.baseline
```

See **[docs/cli/status_audit.md](docs/cli/status_audit.md)** for detailed usage.

## Candidate Selection (local-only)

You can generate a local selection recommendation across 1–4 assistant variants:

```bash
python tools/selection_report.py \
  --summary samples/assistant_message_summary.sample.json \
  --out SELECTION_REPORT.md
```

This runs the evaluator and enforces required selection-guard signals, then explains the tie-break.

## Quickstart

```bash
codex-train experiment=debug training.max_epochs=1 training.batch_size=2 \
  data.train_path=data/train.jsonl data.eval_path=data/eval.jsonl \
  logging.tensorboard=false logging.mlflow_enable=false \
  training.output_dir=artifacts/runs/quickstart
codex reasoning-templates list
codex-train +reasoning=baseline curriculum.phase_schedule=starter \
  logging.reasoning_trace=true training.output_dir=artifacts/runs/reasoning-starter
codex evaluate --config configs/evaluation/reasoning.yaml --metrics-only
```

### Offline-first environment bootstrap

```bash
# 1) Create and activate a virtualenv (any tool)
python -m venv .venv && . .venv/bin/activate

# 2) Install dev tools
pip install -r requirements-dev.txt

# 3) (Optional) Sync minimal runtime deps from a lockfile if provided
if [ -f requirements/lock.txt ]; then
  pip install -r requirements/lock.txt
fi

# 4) Sanity gates
python tools/validate_fences.py
python tools/schema_validate.py \
  --data manifests/selection_guard_rules.json --schema schemas/selection_guard_rules.schema.json \
  --data manifests/codex_eval_rules.v3.json --schema schemas/codex_eval_rules.v3.schema.json

# Optional: selection and status one-liners
python tools/selection_report.py --summary samples/assistant_message_summary.sample.json --out SELECTION_REPORT.md
python tools/status_report.py    --summary samples/assistant_message_summary.sample.json --selected 3 \
                                 --template docs/templates/status_update.md \
                                 --branch my/branch --pr 1234 --verbose --save-logs --out STATUS_REPORT.md
```
