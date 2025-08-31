"""Minimal MLflow tracking helpers with safe fallbacks."""

from __future__ import annotations

import json
import os
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Generator

try:  # pragma: no cover - import guarded
    import mlflow  # type: ignore
except Exception:  # pragma: no cover - optional dep
    mlflow = None  # type: ignore


@dataclass
class MlflowConfig:
    tracking_uri: str | None = None
    experiment: str | None = None
    run_tags: Dict[str, str] | None = None
    enable_system_metrics: bool | None = None


def _coerce_config(cfg: MlflowConfig | str | None) -> MlflowConfig:
    if isinstance(cfg, MlflowConfig):
        return cfg
    if isinstance(cfg, str):
        return MlflowConfig(experiment=cfg)
    return MlflowConfig()


@contextmanager
def start_run(config: MlflowConfig | str | None = None) -> Generator[Any | None, None, None]:
    """Start an MLflow run if the library is available.

    When MLflow is not installed the context manager yields ``None`` and
    performs no operations.
    """

    cfg = _coerce_config(config)
    if mlflow is None:  # pragma: no cover - simple branch
        yield None
        return

    if cfg.enable_system_metrics is not None:
        os.environ["MLFLOW_ENABLE_SYSTEM_METRICS"] = "1" if cfg.enable_system_metrics else "0"
    if cfg.tracking_uri:
        mlflow.set_tracking_uri(cfg.tracking_uri)
    if cfg.experiment:
        mlflow.set_experiment(cfg.experiment)
    with mlflow.start_run(tags=cfg.run_tags or {}):
        yield mlflow


def log_params(params: Dict[str, Any], *, enabled: bool | None = None) -> None:
    if mlflow is None or enabled is False:
        return
    mlflow.log_params(params)


def log_metrics(metrics: Dict[str, float], *, enabled: bool | None = None) -> None:
    if mlflow is None or enabled is False:
        return
    mlflow.log_metrics(metrics)


def log_artifacts(path: Path, *, enabled: bool | None = None) -> None:
    if mlflow is None or enabled is False:
        return
    mlflow.log_artifacts(str(path))


def seed_snapshot(seeds: Dict[str, int], out_dir: Path, *, enabled: bool | None = None) -> Path:
    out = out_dir / "seeds.json"
    out.write_text(json.dumps(seeds))
    if enabled:
        log_artifacts(out)
    return out


def ensure_local_artifacts(out_dir: Path, summary: Dict[str, Any], seeds: Dict[str, int]) -> None:
    (out_dir / "summary.json").write_text(json.dumps(summary))
    (out_dir / "seeds.json").write_text(json.dumps(seeds))


__all__ = [
    "MlflowConfig",
    "start_run",
    "log_params",
    "log_metrics",
    "log_artifacts",
    "seed_snapshot",
    "ensure_local_artifacts",
]
