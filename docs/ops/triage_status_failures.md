# Ops: Triage Guide for Status/Validation Failures (v1.2)
> Generated: 2024-11-02 15:10:07 UTC | Author: mbaetiong  
🧠 Roles: [Primary: On-call], [Secondary: CI Maintainer] ⚡ Energy: 5

Matrix
| Failure | Signal | First Action | Next Steps |
|---|---|---|---|
| Schema test fails | pytest red | Open example JSON; align with schema | Run tools/schema_diff.py to inspect drift |
| Configs fail | validate_configs FAIL lines | Identify offending YAML | Fix types/required keys; re-run tool |
| Secrets scan | new findings | Audit .secrets.baseline | Rotate secret; commit baseline update |
| SAST | bandit high/medium | Review path | Add fix or inline ignore with rationale |
| Audit chain | manifest missing | Rerun build script | Check write perms; re-run workflow |
