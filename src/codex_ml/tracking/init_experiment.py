from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict

try:  # Optional TensorBoard
    from torch.utils.tensorboard import SummaryWriter  # type: ignore
except Exception:  # pragma: no cover - optional dependency missing
    SummaryWriter = None  # type: ignore

try:  # Optional MLflow
    import mlflow  # type: ignore

    HAS_MLFLOW = True
except Exception:  # pragma: no cover - optional dependency missing
    HAS_MLFLOW = False
    mlflow = None  # type: ignore

try:  # Optional Weights & Biases
    import wandb  # type: ignore

    HAS_WANDB = True
except Exception:  # pragma: no cover - optional dependency missing
    HAS_WANDB = False
    wandb = None  # type: ignore


def init_experiment(
    name: str,
    *,
    log_dir: str | Path = "runs",
    use_tensorboard: bool = False,
    use_mlflow: bool = False,
    use_wandb: bool = False,
) -> Dict[str, Any]:
    """Initialise experiment tracking backends.

    Parameters
    ----------
    name:
        Experiment name.
    log_dir:
        Directory for local artifacts and NDJSON metrics.
    use_tensorboard, use_mlflow, use_wandb:
        Enable respective tracking integrations when possible.

    Returns
    -------
    Dict[str, Any]
        Dictionary containing a ``log_metrics`` callable and metadata such as
        ``ndjson_path`` and the TensorBoard writer (if active).
    """

    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    ndjson_path = log_path / f"{name}.ndjson"

    writer = None
    if use_tensorboard and SummaryWriter is not None:
        try:  # pragma: no cover - depends on tensorboard availability
            tb_dir = log_path / "tensorboard" / name
            tb_dir.mkdir(parents=True, exist_ok=True)
            writer = SummaryWriter(log_dir=str(tb_dir))
        except Exception:
            writer = None

    if use_mlflow and HAS_MLFLOW:
        try:  # pragma: no cover - optional backend
            mlflow.set_experiment(name)
            mlflow.start_run(run_name=name)
        except Exception:
            pass

    if use_wandb and HAS_WANDB:
        try:  # pragma: no cover - optional backend
            wandb.init(project=name, name=name, mode=os.getenv("WANDB_MODE", "offline"))
        except Exception:
            pass

    def log_metrics(step: int, metrics: Dict[str, Any]) -> None:
        rec = {"step": int(step), **metrics}
        with ndjson_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec) + "\n")
        if writer is not None:
            for k, v in metrics.items():
                if isinstance(v, (int, float)):
                    try:
                        writer.add_scalar(k, v, step)
                    except Exception:
                        pass

    return {"log_metrics": log_metrics, "ndjson_path": ndjson_path, "tensorboard": writer}
