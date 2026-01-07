# Validation: Hydra Config Snapshot & Checks (v1.2)
> Generated: 2024-11-02 15:08:30 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Config Auditor], [Secondary: Toolsmith] ⚡ Energy: 5

Goals
- Capture active Hydra configuration in status reports and validate against schemas.

Snapshot Recipe
| Step | Command | Output |
|---|---|---|
| List groups | hydra --help (or app CLI) | config group names |
| Active overrides | Record CLI flags or defaults.yaml imports | snapshot.hydra_config_snapshot.active_overrides |
| Sweep configs | List sweep yaml files | snapshot.hydra_config_snapshot.sweep_configs |
| Validation | python tools/validate_configs.py --root configs/training --schema configs/schemas/training.schema.yaml | PASS/FAIL summary |

Report Fields
- hydra_config_snapshot.config_groups: ["model", "data", "trainer", ...]
- hydra_config_snapshot.active_overrides: ["trainer.batch_size=32", ...]
- hydra_config_snapshot.sweep_configs: ["sweeps/bs.yaml", ...]
- hydra_config_snapshot.validation_status: pass|fail|warn

Tips
- Keep config examples small; prefer inheritance via defaults.
- Align config keys with training.schema.yaml to minimize drift.
