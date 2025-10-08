from __future__ import annotations

import json
import os
from pathlib import Path


def run(args) -> int:
    ml_dir = Path(args.mlflow_dir or os.environ.get("CODEX_MLFLOW_DIR", "mlruns")).resolve()
    ml_dir.mkdir(parents=True, exist_ok=True)
    ml_uri = ml_dir.as_uri()
    os.environ["MLFLOW_TRACKING_URI"] = ml_uri

    if args.wandb_disable:
        os.environ["WANDB_DISABLED"] = "true"
        wandb_mode = "disabled"
    else:
        os.environ.setdefault("WANDB_MODE", "offline")
        wandb_mode = os.environ.get("WANDB_MODE", "offline")

    mlflow_ok = False
    try:
        import mlflow

        mlflow.set_tracking_uri(ml_uri)
        mlflow_ok = True
    except Exception:
        pass

    wandb_ok = False
    try:
        if os.environ.get("WANDB_DISABLED") == "true":
            wandb_ok = True
        else:
            import wandb  # noqa: F401

            wandb_ok = True
    except Exception:
        pass

    print(
        json.dumps(
            {
                "ok": True,
                "mlflow": {"uri": ml_uri, "configured": mlflow_ok},
                "wandb": {
                    "mode": wandb_mode,
                    "disabled": os.environ.get("WANDB_DISABLED") == "true",
                    "import_ok": wandb_ok,
                },
            }
        )
    )
    return 0
