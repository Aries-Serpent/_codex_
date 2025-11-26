# Configuration Validation Guide

This guide explains how to validate Codex configuration files against the bundled schemas and how the checks run locally and in CI.

## Quick Start

Validate all default config groups with strict enforcement:

```bash
python tools/validate_configs.py --group all --strict --quiet
```

Generate a JSON report for auditing (includes timestamps and duration):

```bash
python tools/validate_configs.py \
  --group tracking \
  --report artifacts/config_validation_report.json \
  --quiet
```

Validate every YAML file under a directory against a specific schema:

```bash
python tools/validate_configs.py --root configs/training --schema configs/schemas/training.schema.yaml --strict
```

## Groups

Use `--group` to target specific config families. Multiple groups may be provided, and `all` is the default.

- `training` – `configs/training/base.yaml`, `configs/training/profiles/default.yaml`
- `evaluation` – `configs/evaluation/default.yaml`
- `logging` – `configs/base/logging/base.yaml`
- `tracking` – `configs/tracking/base.yaml`, `configs/tracking/offline.yaml`
- `deployment` – `configs/deployment/interfaces.yaml`, `configs/deploy/reasoning_pod.yaml`
- `monitoring` – `configs/deployment/hhg_logistics/monitor/default.yaml`

## Strict vs Partial

- `--strict` enforces all required fields, even for partial overlays.
- Without `--strict`, required-field errors are filtered when using `--root` to accommodate overlay configs.

## CI Integration

The GitHub Actions workflow runs the `config_validation` nox session with `--strict` and generates a JSON report artifact. Failures block merges.

## Troubleshooting

- Ensure `jsonschema` and `PyYAML` are installed (provided via `requirements-dev.txt`).
- Use `--report` to inspect which files failed and why.
- For partial configs, run without `--strict` to identify required-field gaps incrementally.
