"""
Engine Module

This module provides functionality for engine.

Usage:
    from training.engine import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

# Sentinel: distinguishes "explicitly passed None (no mlflow)" from "not provided (auto-detect)"
_MLFLOW_UNSET: object = object()


def _normalize_params(params: Mapping[str, Any]) -> dict[str, str | float | int]:
    normalized: dict[str, str | float | int] = {}
    for key, value in params.items():
        if value is None:
            continue
        key_str = str(key)
        if isinstance(value, bool):
            normalized[key_str] = int(value)
        elif isinstance(value, (str, int, float)):
            normalized[key_str] = value
        else:
            normalized[key_str] = str(value)
    return normalized


@dataclass
class TrainingEngine:
    """Track high-level training state and optional MLflow logging."""

    enable_mlflow: bool = False
    mlflow_dir: str = ".mlruns"
    mlflow_experiment: str = "codex_experiment"
    mlflow_run_name: str | None = None
    mlflow_tags: Mapping[str, Any] | None = None
    auto_log_datasets: bool = True
    _mlflow_module: Any | None = field(default=_MLFLOW_UNSET, repr=False)
    _active_run: Any | None = field(default=None, init=False, repr=False)
    _mlflow_configured: bool = field(default=False, init=False, repr=False)
    _mlflow_error: str | None = field(default=None, init=False, repr=False)
    _pending_params: dict[str, str | float | int] = field(
        default_factory=dict, init=False, repr=False
    )
    _pending_tags: dict[str, str] = field(default_factory=dict, init=False, repr=False)
    _registered_datasets: list[dict[str, str]] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self) -> None:
        if self._mlflow_module is _MLFLOW_UNSET:
            # Auto-detect mlflow only when caller did not explicitly pass a module
            try:  # pragma: no cover - optional dependency path
                import mlflow as _mlflow
            except (IOError, OSError):  # pragma: no cover - mlflow missing
                _mlflow = None
            self._mlflow_module = _mlflow
        # If caller explicitly passed None, treat as "no mlflow available"
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
        if params:
            self.log_params(params)
        if tags:
            self.set_tags(tags)
        if datasets:
            for index, dataset in enumerate(datasets):
                dataset_name = f"dataset_{index}"
                self.register_dataset(dataset_name, uri=dataset)
        if self.mlflow_tags:
            self.set_tags(self.mlflow_tags)
        self._flush_tags()
        self._flush_params()

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
        normalized = _normalize_params(params)
        if not normalized:
            return
        self._pending_params.update(normalized)
        self._flush_params()

    # ------------------------------------------------------------------
    def set_tags(self, tags: Mapping[str, Any]) -> None:
        normalized = {str(key): str(value) for key, value in tags.items() if value is not None}
        if not normalized:
            return
        self._pending_tags.update(normalized)
        self._flush_tags()

    # ------------------------------------------------------------------
    def register_dataset(
        self,
        name: str,
        *,
        version: str | None = None,
        uri: str | Path | None = None,
    ) -> None:
        payload: dict[str, str] = {"name": str(name)}
        if version:
            payload["version"] = str(version)
        if uri:
            payload["uri"] = str(Path(uri).expanduser())
        self._registered_datasets.append(payload)
        if not self.auto_log_datasets:
            return
        dataset_tags = {
            f"dataset.{index}.{key}": value
            for index, meta in enumerate(self._registered_datasets)
            for key, value in meta.items()
        }
        self.set_tags(dataset_tags)

    # ------------------------------------------------------------------
    def log_artifact(self, path: str | Path, *, artifact_path: str | None = None) -> None:
        if not self.enable_mlflow or not self._mlflow_configured:
            return
        mlflow = self._mlflow_module
        if mlflow is None:
            return
        target = Path(path).expanduser()
        try:
            mlflow.log_artifact(str(target), artifact_path=artifact_path)
        except TypeError:  # pragma: no cover - legacy mlflow signatures
            mlflow.log_artifact(str(target), artifact_path)

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
    def _flush_params(self) -> None:
        if not self._pending_params:
            return
        mlflow = self._mlflow_module
        if not (
            self.enable_mlflow
            and self._mlflow_configured
            and mlflow is not None
            and self._active_run is not None
        ):
            return
        if hasattr(mlflow, "log_params"):
            mlflow.log_params(dict(self._pending_params))
        self._pending_params.clear()

    # ------------------------------------------------------------------
    def _flush_tags(self) -> None:
        if not self._pending_tags:
            return
        mlflow = self._mlflow_module
        if not (
            self.enable_mlflow
            and self._mlflow_configured
            and mlflow is not None
            and self._active_run is not None
        ):
            return
        if hasattr(mlflow, "set_tags"):
            mlflow.set_tags(dict(self._pending_tags))
        elif hasattr(mlflow, "set_tag"):
            for key, value in self._pending_tags.items():
                mlflow.set_tag(key, value)
        self._pending_tags.clear()


__all__ = ["TrainingEngine"]
