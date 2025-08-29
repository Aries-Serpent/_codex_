# BEGIN: CODEX_MLFLOW_UTILS
from __future__ import annotations

import contextlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

# Lazy import of mlflow
try:  # pragma: no cover
    import mlflow as _mlf  # type: ignore

    _HAS_MLFLOW = True
except Exception:  # pragma: no cover
    _HAS_MLFLOW = False
    _mlf = None  # type: ignore


@dataclass
class MlflowConfig:
    enable: bool = False
    tracking_uri: str = "./mlruns"
    experiment: str = "codex-experiments"


def start_run(cfg: MlflowConfig):
    """Context manager that yields the active run or False when disabled.

    Raises:
        RuntimeError: if MLflow was requested but is unavailable.
    """
    if not cfg.enable:

        @contextlib.contextmanager
        def _noop():
            yield False

        return _noop()
    if not _HAS_MLFLOW:
        raise RuntimeError("MLflow requested but not installed")
    os.environ.setdefault("MLFLOW_ENABLE_SYSTEM_METRICS", "false")
    _mlf.set_tracking_uri(cfg.tracking_uri)
    _mlf.set_experiment(cfg.experiment)
    return _mlf.start_run()


def log_params(d: Mapping[str, Any], *, enabled: bool = False) -> None:
    if enabled and _HAS_MLFLOW:
        _mlf.log_params(dict(d))  # type: ignore


def log_metrics(
    d: Mapping[str, float], step: Optional[int] = None, *, enabled: bool = False
) -> None:
    if enabled and _HAS_MLFLOW:
        _mlf.log_metrics(dict(d), step=step)  # type: ignore


def log_artifacts(path: str | Path, *, enabled: bool = False) -> None:
    if enabled and _HAS_MLFLOW:
        _mlf.log_artifacts(str(path))  # type: ignore


def seed_snapshot(
    seeds: Mapping[str, Any], out_dir: Path, *, enabled: bool = False
) -> Path:
    """Write `seeds.json` under ``out_dir`` and log to MLflow when enabled."""
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "seeds.json"
    path.write_text(json.dumps(dict(seeds), indent=2), encoding="utf-8")
    log_artifacts(path, enabled=enabled)
    return path


def ensure_local_artifacts(
    run_dir: Path, summary: Dict[str, Any], seeds: Dict[str, Any]
) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    seed_snapshot(seeds, run_dir)


# END: CODEX_MLFLOW_UTILS
