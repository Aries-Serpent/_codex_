# Security Baseline (Local-only)

This document summarizes the lightweight security utilities available in the repository for local use. The tools are offline-first and are intended to prevent common mistakes (committing secrets or shipping unpinned dependencies) without requiring external services.

## Secret Scanner

`tools/codex_secret_scan.py` searches the repository tree for credential-shaped strings using conservative regexes (AWS keys, bearer tokens, Slack tokens, generic API keys, and private key blocks). Binary assets and common vendor directories (`.git`, `venv`, `node_modules`, `.codex`) are skipped.

Usage:

```bash
python tools/codex_secret_scan.py --repo-root . \
  --json-out codex_secret_scan_report.json \
  --md-out codex_secret_scan_report.md
```

Outputs include a JSON payload with hit details and a Markdown summary for quick review.

## Dependency Pinning Checker

`tools/codex_dep_pin_check.py` inspects common manifest files for unpinned dependencies:

- `requirements.txt` and `requirements-dev.txt`
- `pyproject.toml` (`project.dependencies` block)
- `environment.yml` (both Conda and pip sections)

Requirements missing explicit version operators are reported.

Usage:

```bash
python tools/codex_dep_pin_check.py --repo-root . \
  --json-out codex_dep_pin_report.json \
  --md-out codex_dep_pin_report.md
```

Both tools are safe to rerun and designed for offline environments.

## Relationship to Reproducibility & Gap Registry

The security reports can be incorporated into reproducibility manifests and referenced from gap registry entries when closing security-related gaps. Task sequence steps trigger these utilities so artifacts exist for downstream aggregation.
