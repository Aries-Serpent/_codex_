"""Minimal training engine façade with optional MLflow logging."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Optional


@dataclass
class TrainingEngine:
    """Track high-level training state and optional MLflow logging."""

    enable_mlflow: bool = False
    mlflow_dir: str = ".mlruns"
    mlflow_experiment: str = "codex_experiment"
    mlflow_run_name: str | None = None
    _mlflow_module: Any | None = field(default=None, repr=False)
    _active_run: Any | None = field(default=None, init=False, repr=False)
    _mlflow_configured: bool = field(default=False, init=False, repr=False)
    _mlflow_error: str | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        if self._mlflow_module is None:
            try:  # pragma: no cover - optional dependency path
                import mlflow as _mlflow
            except Exception:  # pragma: no cover - mlflow missing
                _mlflow = None
            self._mlflow_module = _mlflow
        if self.enable_mlflow:
            self._configure_mlflow()

    # ------------------------------------------------------------------
    def _configure_mlflow(self) -> None:
        mlflow = self._mlflow_module
        if mlflow is None:
            self._mlflow_error = "mlflow package unavailable; disabling tracking"
            self.enable_mlflow = False
            return
        tracking_dir = Path(self.mlflow_dir).expanduser().resolve()
        tracking_dir.mkdir(parents=True, exist_ok=True)
        mlflow.set_tracking_uri(tracking_dir.as_uri())
        mlflow.set_experiment(self.mlflow_experiment)
        self._mlflow_configured = True

    # ------------------------------------------------------------------
    def start_run(self) -> None:
        if not self.enable_mlflow or not self._mlflow_configured:
            return
        mlflow = self._mlflow_module
        if mlflow is None:
            return
        self._active_run = mlflow.start_run(run_name=self.mlflow_run_name)

    # ------------------------------------------------------------------
    def log_metrics(self, metrics: Mapping[str, float], step: Optional[int] = None) -> None:
        if not self.enable_mlflow or not self._mlflow_configured:
            return
        mlflow = self._mlflow_module
        if mlflow is None:
            return
        mlflow.log_metrics(dict(metrics), step=step)

    # ------------------------------------------------------------------
    def end_run(self) -> None:
        if not self.enable_mlflow or not self._mlflow_configured:
            return
        mlflow = self._mlflow_module
        if mlflow is None:
            return
        try:
            mlflow.end_run()
        finally:
            self._active_run = None

    # ------------------------------------------------------------------
    @property
    def mlflow_error(self) -> str | None:
        return self._mlflow_error


__all__ = ["TrainingEngine"]
