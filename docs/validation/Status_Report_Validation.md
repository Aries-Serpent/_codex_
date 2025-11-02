# Validation: Status Report v1.2 — End-to-End Gates
> Generated: 2025-11-02 15:05:03 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Validation Lead], [Secondary: CI Maintainer] ⚡ Energy: 5

Scope
- Define the complete validation flow for status reports and related schemas.

Validation Flow
| Step | Command | Purpose | Pass Criteria |
|---|---|---|---|
| 1. Skeleton | python tools/status_report.py --title "📍 `_codex_` : Status Update YYYY-MM-DD-HH:MM:UTC" --out reports/daily/YYYY-MM-DD.json | Generate base JSON | File created |
| 2. Schema test | pytest -q tests/status/test_example_report_schema.py | Ensure example conforms to schema | Test passes |
| 3. Configs | python tools/validate_configs.py --root configs/training --schema configs/schemas/training.schema.yaml | Hydra configs integrity | All PASS |
| 4. Ad-hoc | python tools/schema_validate.py --data <data> --schema <schema> | Spot-check any JSON/YAML | Exit 0 |
| 5. Audit chain | python scripts/audit/build_integrity_chain.py | Integrity manifest | audit_run_manifest.json present |

Troubleshooting Matrix
| Symptom | Likely Cause | Remediation |
|---|---|---|
| Schema test fails | Drift between example and schema | Update example or schema, re-run tests |
| Config validation fails | Missing required keys or wrong types | Fix YAML to match schema; add tests if needed |
| Audit chain missing | Script not executed | Run build_integrity_chain.py; verify write permissions |

Tips
- Keep .statusrc.json aligned with CI thresholds.
- Use CAP-/FIND-/PATCH-/REPRO- IDs consistently; validate via regex if scripting.
