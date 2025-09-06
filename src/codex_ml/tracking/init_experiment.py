from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

try:  # Optional dependency
    from torch.utils.tensorboard import SummaryWriter  # type: ignore
except Exception:  # pragma: no cover - optional
    SummaryWriter = None  # type: ignore

try:  # Optional dependency
    import mlflow  # type: ignore
except Exception:  # pragma: no cover - optional
    mlflow = None  # type: ignore

try:  # Optional dependency
    import wandb  # type: ignore
except Exception:  # pragma: no cover - optional
    wandb = None  # type: ignore


@dataclass
class ExperimentConfig:
    """Configuration for :func:`init_experiment`."""

    name: str
    output_dir: str = "runs"
    tags: Optional[Dict[str, str]] = None
    tensorboard: bool = False
    mlflow: bool = False
    wandb: bool = False


class ExperimentLogger:
    """Lightweight multiplexer over optional logging backends."""

    def __init__(self, cfg: ExperimentConfig):
        self.cfg = cfg
        self.output = Path(cfg.output_dir)
        self.output.mkdir(parents=True, exist_ok=True)
        self._ndjson = self.output / "metrics.ndjson"

        self._tb = None
        if cfg.tensorboard and SummaryWriter is not None:
            try:
                self._tb = SummaryWriter(log_dir=str(self.output / "tensorboard"))
            except Exception:
                self._tb = None

        self._mlflow_run = None
        if cfg.mlflow and mlflow is not None:
            try:
                mlflow.set_experiment(cfg.name)
                self._mlflow_run = mlflow.start_run(run_name=cfg.name)
                if cfg.tags:
                    mlflow.set_tags(cfg.tags)
            except Exception:
                self._mlflow_run = None

        self._wandb_run = None
        if cfg.wandb and wandb is not None:
            try:
                self._wandb_run = wandb.init(
                    project=cfg.name, config=cfg.tags or {}, mode="offline"
                )
            except Exception:
                self._wandb_run = None

    # -- logging --
    def log(self, metrics: Dict[str, float], step: Optional[int] = None) -> None:
        """Record ``metrics`` to all configured backends."""
        rec = dict(metrics)
        if step is not None:
            rec["step"] = int(step)
        try:
            with self._ndjson.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(rec) + "\n")
        except Exception:
            pass

        if self._tb is not None:
            for k, v in metrics.items():
                if isinstance(v, (int, float)):
                    try:
                        self._tb.add_scalar(k, v, step)
                    except Exception:
                        pass
            try:
                self._tb.flush()
            except Exception:
                pass

        if self._mlflow_run is not None:
            try:
                mlflow.log_metrics(metrics, step=step)
            except Exception:
                pass

        if self._wandb_run is not None:
            try:
                wandb.log(metrics, step=step)
            except Exception:
                pass

    def close(self) -> None:
        if self._tb is not None:
            try:
                self._tb.close()
            except Exception:
                pass
        if self._mlflow_run is not None:
            try:
                mlflow.end_run()
            except Exception:
                pass
        if self._wandb_run is not None:
            try:
                self._wandb_run.finish()
            except Exception:
                pass


def init_experiment(cfg: ExperimentConfig) -> ExperimentLogger:
    """Initialise logging backends and return an :class:`ExperimentLogger`."""
    return ExperimentLogger(cfg)


__all__ = ["ExperimentConfig", "ExperimentLogger", "init_experiment"]
