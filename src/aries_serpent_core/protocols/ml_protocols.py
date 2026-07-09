"""
Shared protocols for training/ML decoupling.

This module defines zero-dependency protocols that allow training and ML
components to depend on abstract interfaces rather than concrete implementations.
This breaks circular dependencies between codex.training and codex_ml.

Zero import dependencies: Only uses typing and abc modules.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Protocol, Sequence, TypeVar

if TYPE_CHECKING:
    from pathlib import Path

T = TypeVar("T")


class DatasetProtocol(Protocol):
    """Interface for dataset operations.
    
    Implemented by: codex_ml.data.dataset.Dataset and similar classes.
    """

    @abstractmethod
    def __len__(self) -> int:
        """Return the total number of samples."""
        ...

    @abstractmethod
    def __getitem__(self, idx: int) -> Any:
        """Get a sample by index."""
        ...

    @abstractmethod
    def split(self, ratio: float) -> tuple[DatasetProtocol, DatasetProtocol]:
        """Split dataset into train/val or similar."""
        ...


class ModelProtocol(Protocol):
    """Interface for model operations.
    
    Implemented by: codex_ml.models.model_base.ModelBase and similar classes.
    """

    @abstractmethod
    def forward(self, x: Any) -> Any:
        """Forward pass."""
        ...

    @abstractmethod
    def save(self, path: str | Path) -> None:
        """Save model to disk."""
        ...

    @abstractmethod
    def load(self, path: str | Path) -> None:
        """Load model from disk."""
        ...

    @abstractmethod
    def to(self, device: str) -> ModelProtocol:
        """Move model to device (e.g., 'cuda', 'cpu')."""
        ...

    @abstractmethod
    def train(self) -> None:
        """Set model to training mode."""
        ...

    @abstractmethod
    def eval(self) -> None:
        """Set model to eval mode."""
        ...


class OptimizerProtocol(Protocol):
    """Interface for optimizer operations.
    
    Implemented by: torch.optim.Optimizer subclasses.
    """

    @abstractmethod
    def zero_grad(self) -> None:
        """Clear accumulated gradients."""
        ...

    @abstractmethod
    def step(self) -> None:
        """Perform optimization step."""
        ...


class SchedulerProtocol(Protocol):
    """Interface for learning rate scheduler operations.
    
    Implemented by: torch.optim.lr_scheduler subclasses.
    """

    @abstractmethod
    def step(self) -> None:
        """Perform scheduler step."""
        ...

    @abstractmethod
    def get_last_lr(self) -> list[float]:
        """Get current learning rates."""
        ...


class MetricsProtocol(Protocol):
    """Interface for metrics operations.
    
    Implemented by: codex_ml.metrics.Metrics and similar classes.
    """

    @abstractmethod
    def update(self, predictions: Any, targets: Any) -> None:
        """Update metrics with new predictions/targets."""
        ...

    @abstractmethod
    def compute(self) -> dict[str, float]:
        """Compute and return metric values."""
        ...

    @abstractmethod
    def reset(self) -> None:
        """Reset metrics state."""
        ...


class LossProtocol(Protocol):
    """Interface for loss operations.
    
    Implemented by: torch.nn.Module subclasses and custom loss functions.
    """

    @abstractmethod
    def __call__(self, predictions: Any, targets: Any) -> Any:
        """Compute loss."""
        ...


class EvaluatorProtocol(Protocol):
    """Interface for evaluation operations.
    
    Implemented by: codex_ml.evaluation.Evaluator and similar classes.
    """

    @abstractmethod
    def evaluate(
        self,
        model: ModelProtocol,
        dataset: DatasetProtocol,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Run evaluation on model with dataset."""
        ...


class CheckpointerProtocol(Protocol):
    """Interface for checkpointing operations.
    
    Implemented by: training.checkpoint_manager.CheckpointManager and similar.
    """

    @abstractmethod
    def save(
        self,
        model: ModelProtocol,
        optimizer: OptimizerProtocol,
        step: int,
        metrics: dict[str, Any] | None = None,
    ) -> None:
        """Save checkpoint."""
        ...

    @abstractmethod
    def load(
        self,
        path: str | Path,
        model: ModelProtocol,
        optimizer: OptimizerProtocol | None = None,
    ) -> int:
        """Load checkpoint and return step number."""
        ...


class TrainerProtocol(Protocol):
    """Interface for trainer operations.
    
    Implemented by: training.trainer.Trainer and codex_ml.training classes.
    """

    @abstractmethod
    def train(
        self,
        train_dataset: DatasetProtocol,
        val_dataset: DatasetProtocol | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Run training loop."""
        ...

    @abstractmethod
    def validate(self, dataset: DatasetProtocol) -> dict[str, float]:
        """Run validation on dataset."""
        ...

    @abstractmethod
    def save_checkpoint(self, path: str | Path) -> None:
        """Save training checkpoint."""
        ...

    @abstractmethod
    def load_checkpoint(self, path: str | Path) -> None:
        """Load training checkpoint."""
        ...


class LoggerProtocol(Protocol):
    """Interface for logging operations.
    
    Implemented by: codex_ml.logging and similar.
    """

    @abstractmethod
    def log_metrics(self, metrics: dict[str, Any], step: int | None = None) -> None:
        """Log metrics."""
        ...

    @abstractmethod
    def log_params(self, params: dict[str, Any]) -> None:
        """Log hyperparameters."""
        ...

    @abstractmethod
    def log_artifact(self, path: str | Path, artifact_type: str | None = None) -> None:
        """Log artifact."""
        ...


# Type aliases for common patterns
TrainerType = TrainerProtocol
DatasetType = DatasetProtocol
ModelType = ModelProtocol
MetricsType = MetricsProtocol
LoggerType = LoggerProtocol
