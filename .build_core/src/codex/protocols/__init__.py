"""Shared protocols for training/ML decoupling.

This package provides zero-dependency protocol definitions that allow
training and ML components to depend on abstract interfaces rather than
concrete implementations.

Key Exports:
    - DatasetProtocol: Interface for dataset operations
    - ModelProtocol: Interface for model operations  
    - OptimizerProtocol: Interface for optimizer operations
    - SchedulerProtocol: Interface for scheduler operations
    - MetricsProtocol: Interface for metrics operations
    - LossProtocol: Interface for loss operations
    - EvaluatorProtocol: Interface for evaluation operations
    - CheckpointerProtocol: Interface for checkpointing operations
    - TrainerProtocol: Interface for trainer operations
    - LoggerProtocol: Interface for logging operations

Usage:
    from codex.protocols.ml_protocols import (
        DatasetProtocol,
        ModelProtocol,
        TrainerProtocol,
    )
    
    def train(
        trainer: TrainerProtocol,
        model: ModelProtocol,
        data: DatasetProtocol,
    ) -> None:
        # Implementation agnostic of concrete types
        pass
"""

from __future__ import annotations

from .ml_protocols import (
    CheckpointerProtocol,
    DatasetProtocol,
    EvaluatorProtocol,
    LossProtocol,
    LoggerProtocol,
    MetricsProtocol,
    ModelProtocol,
    OptimizerProtocol,
    SchedulerProtocol,
    TrainerProtocol,
    TrainerType,
    DatasetType,
    ModelType,
    MetricsType,
    LoggerType,
)

__all__ = [
    # Protocol definitions
    "DatasetProtocol",
    "ModelProtocol",
    "OptimizerProtocol",
    "SchedulerProtocol",
    "MetricsProtocol",
    "LossProtocol",
    "EvaluatorProtocol",
    "CheckpointerProtocol",
    "TrainerProtocol",
    "LoggerProtocol",
    # Type aliases
    "TrainerType",
    "DatasetType",
    "ModelType",
    "MetricsType",
    "LoggerType",
]
