# Ops Index

Operational docs live under `docs/ops/`. Use this page as a landing index for on-call and runbooks in this tree.

## Quick links

* [Runbook](ops/RUNBOOK.md)
* [Deployment checklist](ops/deployment.md)
* [Monitoring guide](ops/monitoring.md)
* [Experiment tracking SOP](ops/experiment_tracking.md)
* [Retention policy](ops/retention.md)
* [Security notes](ops/security.md)
* [Secrets scanning workflow](#secrets-scanning)

## Secrets scanning

Use the repository-provided helper to perform on-demand scans without relying on external services:

```bash
python tools/scan_secrets.py --path . --formats all
```

The script supports dry-run and diff modes. See `python tools/scan_secrets.py --help` for full options.
