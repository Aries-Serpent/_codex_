"""Minimal training engine façade with optional MLflow logging."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence


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
    def start_run(
        self,
        *,
        params: Mapping[str, Any] | None = None,
        tags: Mapping[str, Any] | None = None,
        datasets: Sequence[str | Path] | None = None,
    ) -> None:
        if not self.enable_mlflow or not self._mlflow_configured:
            return
        mlflow = self._mlflow_module
        if mlflow is None:
            return
        self._active_run = mlflow.start_run(run_name=self.mlflow_run_name)
        self._log_params_internal(params)
        self._set_tags_internal(tags, datasets)

    # ------------------------------------------------------------------
    def log_metrics(self, metrics: Mapping[str, float], step: Optional[int] = None) -> None:
        if not self.enable_mlflow or not self._mlflow_configured:
            return
        mlflow = self._mlflow_module
        if mlflow is None:
            return
        mlflow.log_metrics(dict(metrics), step=step)

    # ------------------------------------------------------------------
    def log_params(self, params: Mapping[str, Any]) -> None:
        if not self.enable_mlflow or not self._mlflow_configured:
            return
        self._log_params_internal(params)

    # ------------------------------------------------------------------
    def set_tags(self, tags: Mapping[str, Any]) -> None:
        if not self.enable_mlflow or not self._mlflow_configured:
            return
        self._set_tags_internal(tags, None)

    # ------------------------------------------------------------------
    def log_artifact(self, path: str | Path, *, artifact_path: str | None = None) -> None:
        if not self.enable_mlflow or not self._mlflow_configured:
            return
        mlflow = self._mlflow_module
        if mlflow is None:
            return
        mlflow.log_artifact(str(Path(path).expanduser()), artifact_path=artifact_path)

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

    # ------------------------------------------------------------------
    def _stringify_mapping(self, payload: Mapping[str, Any] | None) -> dict[str, str]:
        if not payload:
            return {}
        serialised: dict[str, str] = {}
        for key, value in payload.items():
            if value is None:
                continue
            if isinstance(value, (str, int, float, bool)):
                serialised[str(key)] = str(value)
                continue
            try:
                serialised[str(key)] = json.dumps(value, sort_keys=True, default=str)
            except TypeError:
                serialised[str(key)] = str(value)
        return serialised

    # ------------------------------------------------------------------
    def _log_params_internal(self, params: Mapping[str, Any] | None) -> None:
        if not params:
            return
        mlflow = self._mlflow_module
        if mlflow is None:
            return
        serialised = self._stringify_mapping(params)
        if serialised:
            mlflow.log_params(serialised)

    # ------------------------------------------------------------------
    def _set_tags_internal(
        self,
        tags: Mapping[str, Any] | None,
        datasets: Sequence[str | Path] | None,
    ) -> None:
        mlflow = self._mlflow_module
        if mlflow is None:
            return
        combined = self._stringify_mapping(tags)
        if datasets:
            dataset_tag = ";".join(
                sorted(str(Path(dataset).expanduser()) for dataset in datasets if dataset)
            )
            if dataset_tag:
                combined.setdefault("codex.dataset.uris", dataset_tag)
        if combined:
            mlflow.set_tags(combined)


__all__ = ["TrainingEngine"]
