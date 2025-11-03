# Ops: Status/Validation CI Matrix (v1.2)
> Generated: 2025-11-02 15:21:24 UTC | Author: mbaetiong  
🧠 Roles: [Primary: CI Matrix Curator], [Secondary: Reviewer] ⚡ Energy: 5

Matrix
| Workflow | Purpose | Key Steps | Artifacts |
|---|---|---|---|
| status_validation.yml | Status schema + config validation | pytest schema test; validate_configs | audit_run_manifest.json |
| security_gates.yml | SAST, secrets, deps | bandit; detect-secrets; pip-audit | .secrets.baseline, secrets_audit.json |
| nox_gates.yml | Lint/type/tests gates | nox sessions | logs |
| report_publish.yml | Validate & bundle | validate_and_publish.py | status_validation_summary.json |
| coverage_report.yml | Coverage JSON + modules | coverage run/json; coverage_extract | .coverage.json, coverage_modules.json |
| cache_hf_models.yml | Tokenizer cache warm | hf_cache_prepare.py | cached model files (runner) |
| semgrep.yml | Deep SAST | semgrep-action | SARIF (internal) |
