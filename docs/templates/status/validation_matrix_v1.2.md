# Matrix: Validations Required/Optional (v1.2)
> Generated: 2024-11-02 15:29:01 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Validation Matrix Author], [Secondary: Reviewer] ⚡ Energy: 5

| Area | Tool | Required | Pass Criteria | Artifact |
|---|---|---:|---|---|
| Status Schema | pytest (example JSON) | Yes | Test passes | test log |
| Configs (Hydra) | tools/validate_configs.py | Yes (if configs exist) | All PASS | terminal log |
| Ad-hoc Schema | tools/schema_validate.py | Optional | Exit 0 | PASS/FAIL |
| Cross-Refs | tools/link_id_crossref.py | Optional | Exit 0 | terminal log |
| Audit Chain | build_integrity_chain.py | Optional | Manifest written | audit_run_manifest.json |
| Security (SAST) | bandit | Yes | No disallowed severity | report |
| Secrets | detect-secrets | Yes | Baseline present/audited | .secrets.baseline |
| Dependencies | pip-audit | Yes | <= policy caps | report |
| Coverage | coverage json | Optional | >= fail-under (if set) | .coverage.json |
