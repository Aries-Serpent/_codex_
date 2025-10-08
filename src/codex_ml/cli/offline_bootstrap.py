from __future__ import annotations

import json

from codex_ml.tracking.guards import enforce_offline_posture


def run(args) -> int:
    decision = enforce_offline_posture(args.mlflow_dir, wandb_disable=args.wandb_disable)

    mlflow_ok = False
    try:
        import mlflow

        mlflow.set_tracking_uri(decision["mlflow"]["uri"])
        mlflow_ok = True
    except Exception:
        pass

    wandb_ok = False
    if decision["wandb"].get("disabled"):
        wandb_ok = True
    else:
        try:
            import wandb  # noqa: F401

            wandb_ok = True
        except Exception:
            pass

    print(
        json.dumps(
            {
                "ok": True,
                "mlflow": {
                    "uri": decision["mlflow"]["uri"],
                    "configured": mlflow_ok,
                    "reason": decision["mlflow"].get("reason"),
                },
                "wandb": {
                    "mode": decision["wandb"].get("mode"),
                    "disabled": bool(decision["wandb"].get("disabled")),
                    "import_ok": wandb_ok,
                },
            }
        )
    )
    return 0
