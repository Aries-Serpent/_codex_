"""
Unified Logging System v1.0.0
Centralized multi-backend logging with plugin architecture

Author: mbaetiong
Generated: 2025-11-19 04:02:05
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Optional

logger = logging.getLogger(__name__)


class LoggerBackend(ABC):
    """Base class for logger backends"""

    @abstractmethod
    def log_metrics(self, metrics: dict[str, Any], step: Optional[int] = None) -> None:
        pass

    @abstractmethod
    def log_params(self, params: dict[str, Any]) -> None:
        pass

    @abstractmethod
    def start_run(self, run_name: Optional[str] = None) -> None:
        pass

    @abstractmethod
    def end_run(self) -> None:
        pass


class MLflowBackend(LoggerBackend):
    """MLflow backend implementation"""

    def __init__(self, tracking_uri: Optional[str] = None):
        try:
            import mlflow

            self.mlflow = mlflow
            if tracking_uri:
                mlflow.set_tracking_uri(tracking_uri)
        except ImportError as e:
            type(e).__name__
            logger.debug("ImportError: <ERROR_TYPE>")
            logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
            raise ImportError("MLflow not installed. Install: pip install mlflow") from e

    def start_run(self, run_name=None) -> None:
        self.mlflow.start_run(run_name=run_name)

    def end_run(self) -> None:
        self.mlflow.end_run()

    def log_metrics(self, metrics, step=None) -> None:
        for k, v in metrics.items():
            self.mlflow.log_metric(k, v, step=step)

    def log_params(self, params) -> None:
        self.mlflow.log_params(params)


class TensorBoardBackend(LoggerBackend):
    """TensorBoard backend"""

    def __init__(self, log_dir: str):
        try:
            from torch.utils.tensorboard import SummaryWriter

            self.writer = SummaryWriter(log_dir)
        except ImportError as e:
            type(e).__name__
            logger.debug("ImportError: <ERROR_TYPE>")
            logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
            raise ImportError("TensorBoard not installed. Install: pip install tensorboard") from e

    def start_run(self, run_name=None) -> None:
        pass

    def end_run(self) -> None:
        self.writer.close()

    def log_metrics(self, metrics, step=None) -> None:
        for k, v in metrics.items():
            self.writer.add_scalar(k, v, step)

    def log_params(self, params) -> None:
        text = "\n".join(f"{k}: {v}" for k, v in params.items())
        self.writer.add_text("params", text)


class WandBBackend(LoggerBackend):
    """Weights & Biases backend"""

    def __init__(self, project: str, entity: Optional[str] = None):
        try:
            import wandb

            self.wandb = wandb
            self.project = project
            self.entity = entity
        except ImportError as e:
            type(e).__name__
            logger.debug("ImportError: <ERROR_TYPE>")
            logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
            raise ImportError("Weights & Biases not installed. Install: pip install wandb") from e

    def start_run(self, run_name=None) -> None:
        self.wandb.init(project=self.project, entity=self.entity, name=run_name)

    def end_run(self) -> None:
        self.wandb.finish()

    def log_metrics(self, metrics, step=None) -> None:
        self.wandb.log(metrics, step=step)

    def log_params(self, params) -> None:
        self.wandb.config.update(params)


class LoggerRegistry:
    """Central logger registry"""

    def __init__(self) -> None:
        self.backends: dict[str, LoggerBackend] = {}

    def register(self, name: str, backend: LoggerBackend) -> None:
        self.backends[name] = backend
        logger.info(f"Registered: {name}")

    def start_run(self, run_name: Optional[str] = None) -> None:
        for name, backend in self.backends.items():
            try:
                backend.start_run(run_name)
            except (ValueError, TypeError, RuntimeError) as e:
                type(e).__name__
                logger.debug("Exception: <ERROR_TYPE>")
                logger.error(f"Failed start on {name}: <ERROR_TYPE>")

    def end_run(self) -> None:
        for backend in self.backends.values():
            try:
                backend.end_run()
            except (ValueError, TypeError, RuntimeError) as e:
                type(e).__name__
                logger.debug("Exception: <ERROR_TYPE>")
                logger.error("Failed end: <ERROR_TYPE>")

    def log_metrics(self, metrics: dict[str, Any], step: Optional[int] = None) -> None:
        for backend in self.backends.values():
            try:
                backend.log_metrics(metrics, step)
            except (ValueError, TypeError, RuntimeError) as e:
                type(e).__name__
                logger.debug("Exception: <ERROR_TYPE>")
                logger.error("Failed log: <ERROR_TYPE>")

    def log_params(self, params: dict[str, Any]) -> None:
        for backend in self.backends.values():
            try:
                backend.log_params(params)
            except (ValueError, TypeError, RuntimeError) as e:
                type(e).__name__
                logger.debug("Exception: <ERROR_TYPE>")
                logger.error("Failed params: <ERROR_TYPE>")


# Global instance
_registry = LoggerRegistry()


def get_logger_registry() -> LoggerRegistry:
    return _registry
