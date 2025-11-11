"""Logging registry builder for training and evaluation flows.

This module provides a factory function `build_loggers` that returns a list
of logger objects based on configuration settings. By default, it returns
an NDJSON logger. MLflow logging can be optionally enabled but will not
attempt network connections unless explicitly configured.

Example usage::

    from codex_ml.logging.registry import build_loggers
    
    # Build default loggers (NDJSON only)
    loggers = build_loggers(settings={"output_dir": "runs/exp1"})
    
    # Build with MLflow enabled (offline mode)
    loggers = build_loggers(
        settings={
            "output_dir": "runs/exp2",
            "enable_mlflow": True,
            "mlflow_tracking_uri": "file:///tmp/mlruns",
        }
    )
    
    # Log events
    for logger in loggers:
        logger.log({"step": 1, "loss": 0.5})

The registry avoids importing heavy dependencies at module level and only
imports MLflow when explicitly requested.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any


def build_loggers(
    settings: dict[str, Any],
    cfg: dict[str, Any] | None = None,
) -> list[Any]:
    """Build and return a list of logger instances based on settings.
    
    By default, returns an NDJSON logger that writes to the output directory.
    If `enable_mlflow` is set in settings, also includes an MLflow logger
    configured for offline/file-based tracking.
    
    Args:
        settings: Configuration dictionary with keys:
            - output_dir (str): Directory for log files (required)
            - enable_mlflow (bool): Whether to include MLflow logger (default: False)
            - mlflow_tracking_uri (str): MLflow tracking URI (default: file-based)
            - run_name (str): Optional run name for logging context
        cfg: Optional additional configuration (reserved for future use)
    
    Returns:
        List of logger objects. Each logger implements a `.log(record)` method
        that accepts a dictionary of metrics/metadata.
    
    Raises:
        ValueError: If required settings are missing
        
    Example::
    
        # Minimal NDJSON logging
        loggers = build_loggers({"output_dir": "outputs"})
        
        # With MLflow (offline)
        loggers = build_loggers({
            "output_dir": "outputs",
            "enable_mlflow": True,
            "mlflow_tracking_uri": "file:///tmp/mlruns",
        })
        
        # Log training metrics
        for logger in loggers:
            logger.log({
                "epoch": 1,
                "step": 100,
                "loss": 0.45,
                "accuracy": 0.89,
            })
    """
    if cfg is None:
        cfg = {}
    
    output_dir = settings.get("output_dir")
    if not output_dir:
        raise ValueError("settings['output_dir'] is required for building loggers")
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    loggers: list[Any] = []
    
    # Always include NDJSON logger as the default
    ndjson_logger = _build_ndjson_logger(output_dir, settings)
    loggers.append(ndjson_logger)
    
    # Optionally include MLflow logger
    enable_mlflow = settings.get("enable_mlflow", False)
    if enable_mlflow:
        mlflow_logger = _build_mlflow_logger(output_dir, settings)
        if mlflow_logger is not None:
            loggers.append(mlflow_logger)
    
    return loggers


def _build_ndjson_logger(output_dir: str, settings: dict[str, Any]) -> Any:
    """Build an NDJSON logger instance.
    
    Args:
        output_dir: Directory for log files
        settings: Configuration settings
    
    Returns:
        NDJSONLogger instance
    """
    # Import here to avoid module-level heavy imports
    from codex_ml.logging.ndjson_logger import NDJSONLogger
    
    log_file = Path(output_dir) / "training.ndjson"
    run_name = settings.get("run_name")
    
    return NDJSONLogger(
        path=log_file,
        run_id=run_name,
        max_bytes=64 * 1024 * 1024,  # 64MB rotation
        backup_count=5,
    )


def _build_mlflow_logger(output_dir: str, settings: dict[str, Any]) -> Any | None:
    """Build an MLflow logger instance if mlflow is available.
    
    This function does NOT attempt network connections. It configures MLflow
    for file-based tracking (offline mode) using the tracking_uri setting.
    
    Args:
        output_dir: Directory for log files
        settings: Configuration settings with mlflow_tracking_uri
    
    Returns:
        MLflow logger wrapper or None if mlflow is not available
    """
    try:
        import mlflow
    except ImportError:
        # MLflow not installed - skip silently
        return None
    
    # Configure MLflow for offline/file-based tracking
    tracking_uri = settings.get("mlflow_tracking_uri")
    if not tracking_uri:
        # Default to file-based tracking in the output directory
        tracking_uri = f"file://{Path(output_dir).absolute()}/mlruns"
    
    mlflow.set_tracking_uri(tracking_uri)
    
    # Create a simple wrapper that implements .log() interface
    class MLflowLoggerAdapter:
        """Adapter to provide .log() interface for MLflow."""
        
        def __init__(self, experiment_name: str):
            self.experiment_name = experiment_name
            self._run = None
        
        def log(self, record: dict[str, Any]) -> None:
            """Log a record to MLflow."""
            # Extract metrics from record
            step = record.get("step", record.get("global_step", 0))
            
            # Start run if needed (lazy initialization)
            if self._run is None:
                mlflow.set_experiment(self.experiment_name)
                self._run = mlflow.start_run()
            
            # Log metrics (filter out non-numeric values)
            for key, value in record.items():
                if key in ("step", "global_step", "epoch"):
                    continue
                if isinstance(value, (int, float)):
                    mlflow.log_metric(key, value, step=step)
        
        def close(self) -> None:
            """End the MLflow run."""
            if self._run is not None:
                mlflow.end_run()
                self._run = None
    
    experiment_name = settings.get("run_name", "default")
    return MLflowLoggerAdapter(experiment_name)


__all__ = ["build_loggers"]
