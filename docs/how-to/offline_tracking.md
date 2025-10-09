# [How-to]: Offline Tracking Guards (MLflow + W&B)  
> Generated: 2025-10-09 20:04:41 UTC | Author: mbaetiong  
Roles: [Audit Orchestrator], [Capability Cartographer]  Energy: 5

Purpose
- Enforce offline-by-default tracking for MLflow and Weights & Biases in airgapped or cost-controlled environments.
- Allow explicit opt-in to remote hosts via an allowlist.

Defaults
- MLflow: file://<artifacts_dir>/mlruns (coerced unless remote host is allowlisted)
- W&B: WANDB_MODE=offline unless explicitly set by user

Environment toggles
| Var | Meaning | Example |
|-----|---------|---------|
| CODEX_ALLOWLIST_HOSTS | Comma-separated allowlisted hosts | mlflow.mycorp.local,api.github.com |
| MLFLOW_TRACKING_URI | MLflow tracking URI | file:///.../mlruns |
| WANDB_MODE | W&B mode | offline (default) |

Python API
```python
from src.codex_utils.tracking.guards import ensure_mlflow_offline, ensure_wandb_offline
uri = ensure_mlflow_offline("artifacts")
mode = ensure_wandb_offline()
print(uri, mode)
```

Notes
- No network calls are made by these guards; they operate via environment variables.
- When remote URIs are provided and not allowlisted, they are coerced to a local file:// store.

*End*