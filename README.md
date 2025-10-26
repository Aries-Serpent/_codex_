# Documentation Moved

All primary documentation now lives in the [`docs/`](docs/) directory.

- Start with [`docs/README_ROOT.md`](docs/README_ROOT.md)
- Contribution guidelines: [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md)
- Changelog: [`docs/CHANGELOG.md`](docs/CHANGELOG.md)
- Operational templates: [`docs/templates/README.md`](docs/templates/README.md)

Legacy references should update to the new paths under `docs/`.

## Local Gates & Status Reports

This repository ships **local-only** quality gates (no CI) and a local status reporter:

- See **docs/ops/local_gates.md** for running fences, evaluator, schema checks, and the selection guard.
- See **docs/ops/status_reports.md** for generating a reusable **STATUS_REPORT.md** (including a template mode).

Quick start:
```bash
python tools/status_report.py --summary samples/assistant_message_summary.sample.json --selected 3 --out STATUS_REPORT.md
```
