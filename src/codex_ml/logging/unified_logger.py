"""
Unified Logging System v1.0.0
Centralized multi-backend logging with plugin architecture

Author: mbaetiong
Generated: 2025-11-19 04:02:05
"""
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class LoggerBackend(ABC):
    """Base class for logger backends"""
    
    @abstractmethod
    def log_metrics(self, metrics: Dict[str, Any], step: Optional[int] = None):
        pass
    
    @abstractmethod
    def log_params(self, params: Dict[str, Any]):
        pass
    
    @abstractmethod
    def start_run(self, run_name: Optional[str] = None):
        pass
    
    @abstractmethod
    def end_run(self):
        pass


class MLflowBackend(LoggerBackend):
    """MLflow backend implementation"""
    def __init__(self, tracking_uri: Optional[str] = None):
        try:
            import mlflow
            self.mlflow = mlflow
            if tracking_uri:
                mlflow.set_tracking_uri(tracking_uri)
        except ImportError:
            raise ImportError("MLflow not installed. Install: pip install mlflow")
    
    def start_run(self, run_name=None):
        self.mlflow.start_run(run_name=run_name)
    
    def end_run(self):
        self.mlflow.end_run()
    
    def log_metrics(self, metrics, step=None):
        for k, v in metrics.items():
            self.mlflow.log_metric(k, v, step=step)
    
    def log_params(self, params):
        self.mlflow.log_params(params)


class TensorBoardBackend(LoggerBackend):
    """TensorBoard backend"""
    def __init__(self, log_dir: str):
        try:
            from torch.utils.tensorboard import SummaryWriter
            self.writer = SummaryWriter(log_dir)
        except ImportError:
            raise ImportError("TensorBoard not installed. Install: pip install tensorboard")
    
    def start_run(self, run_name=None):
        pass
    
    def end_run(self):
        self.writer.close()
    
    def log_metrics(self, metrics, step=None):
        for k, v in metrics.items():
            self.writer.add_scalar(k, v, step)
    
    def log_params(self, params):
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
        except ImportError:
            raise ImportError("Weights & Biases not installed. Install: pip install wandb")
    
    def start_run(self, run_name=None):
        self.wandb.init(project=self.project, entity=self.entity, name=run_name)
    
    def end_run(self):
        self.wandb.finish()
    
    def log_metrics(self, metrics, step=None):
        self.wandb.log(metrics, step=step)
    
    def log_params(self, params):
        self.wandb.config.update(params)


class LoggerRegistry:
    """Central logger registry"""
    def __init__(self):
        self.backends: Dict[str, LoggerBackend] = {}
    
    def register(self, name: str, backend: LoggerBackend):
        self.backends[name] = backend
        logger.info(f"Registered: {name}")
    
    def start_run(self, run_name: Optional[str] = None):
        for name, backend in self.backends.items():
            try:
                backend.start_run(run_name)
            except Exception as e:
                logger.error(f"Failed start on {name}: {e}")
    
    def end_run(self):
        for backend in self.backends.values():
            try:
                backend.end_run()
            except Exception as e:
                logger.error(f"Failed end: {e}")
    
    def log_metrics(self, metrics: Dict, step: Optional[int] = None):
        for backend in self.backends.values():
            try:
                backend.log_metrics(metrics, step)
            except Exception as e:
                logger.error(f"Failed log: {e}")
    
    def log_params(self, params: Dict):
        for backend in self.backends.values():
            try:
                backend.log_params(params)
            except Exception as e:
                logger.error(f"Failed params: {e}")


# Global instance
_registry = LoggerRegistry()


def get_logger_registry() -> LoggerRegistry:
    return _registry
