# _codex Status Update — Post-Iteration

## Evidence checklist
- [ ] audit_artifacts/capabilities_scored.json
- [ ] audit_artifacts/gaps.json
- [ ] reports/capability_audit.md
- [ ] reports/_codex_status_update-0D_base_-2025-10-10.md

## Capability coverage to test markers/sessions

| Capability area | Marker or session to exercise |
| --- | --- |
| Pipeline | `pytest -m "training"` |
| Templates | `pytest -m "templates"` |
| Detectors | `pytest -k detector -m smoke` |
| Configuration | `pytest -m "infra"` |
| Tests/health gates | `pytest -m "smoke"` or `nox -s tests` |
