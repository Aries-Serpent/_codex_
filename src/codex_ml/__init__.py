"""
codex-ml package namespace.
Keeps surface minimal; version is exposed for packaging/diagnostics.
"""

from __future__ import annotations

import logging as _logging

logger = _logging.getLogger(__name__)

from importlib import import_module

__all__ = ["__version__", "api"]
__version__ = "0.3.0"

# Avoid importing heavy deps at import time (Torch/HF) to keep `pip install` fast
# and to prevent side-effects when tools only query metadata.

# Cognitive Brain module - core reasoning and context management
try:  # pragma: no cover - optional module
    from .cognitive_brain import CognitiveBrain, ContextManager, ReasoningEngine
except (ImportError, AttributeError):  # pragma: no cover - degrade gracefully
    CognitiveBrain = None  # type: ignore[assignment,misc]
    ContextManager = None  # type: ignore[assignment,misc]
    ReasoningEngine = None  # type: ignore[assignment,misc]

# Memory module - STM/LTM memory systems
try:  # pragma: no cover - optional module
    from .memory import (
        ConsolidationRecord,
        LTMMemory,
        MemoryConsolidation,
        MemoryEntry,
        STMMemory,
    )
except (ImportError, AttributeError):  # pragma: no cover - degrade gracefully
    ConsolidationRecord = None  # type: ignore[assignment,misc]
    LTMMemory = None  # type: ignore[assignment,misc]
    MemoryConsolidation = None  # type: ignore[assignment,misc]
    MemoryEntry = None  # type: ignore[assignment,misc]
    STMMemory = None  # type: ignore[assignment,misc]

try:  # pragma: no cover - optional dependency (OmegaConf)
    from .config import (
        PretrainingConfig,
        RLHFConfig,
        SFTConfig,
        TrainingWeights,
        ValidationThresholds,
    )
except (
    ImportError,
    AttributeError,
):  # pragma: no cover - degrade gracefully when config deps are missing

    class _MissingConfig:
        def __init__(self, name: str):
            self._name = name

        def __getattr__(self, item: str) -> None:  # pragma: no cover - defensive
            raise AttributeError(
                f"Optional dependency for '{self._name}' is missing; install codex-ml[configs]"
            )

        def __call__(self, *args, **kwargs) -> None:  # pragma: no cover - defensive
            raise RuntimeError(
                f"Optional dependency for '{self._name}' is missing; install codex-ml[configs]"
            )

    PretrainingConfig = _MissingConfig("PretrainingConfig")  # type: ignore[misc,assignment]
    SFTConfig = _MissingConfig("SFTConfig")  # type: ignore[misc,assignment]
    RLHFConfig = _MissingConfig("RLHFConfig")  # type: ignore[misc,assignment]
    TrainingWeights = _MissingConfig("TrainingWeights")  # type: ignore[misc,assignment]
    ValidationThresholds = _MissingConfig("ValidationThresholds")  # type: ignore[misc,assignment]

_EXPORT_MAP = {
    # Existing exports
    "run_codex_pipeline": ("codex_ml.pipeline", "run_codex_pipeline"),
    "TrainingWeights": ("codex_ml.config", "TrainingWeights"),
    "PretrainingConfig": ("codex_ml.config", "PretrainingConfig"),
    "SFTConfig": ("codex_ml.config", "SFTConfig"),
    "RLHFConfig": ("codex_ml.config", "RLHFConfig"),
    "ValidationThresholds": ("codex_ml.config", "ValidationThresholds"),
    "run_codex_symbolic_pipeline": (
        "codex_ml.symbolic_pipeline",
        "run_codex_symbolic_pipeline",
    ),
    "Weights": ("codex_ml.symbolic_pipeline", "Weights"),
    "PretrainCfg": ("codex_ml.symbolic_pipeline", "PretrainCfg"),
    "SFTCfg": ("codex_ml.symbolic_pipeline", "SFTCfg"),
    "RewardModelCfg": ("codex_ml.symbolic_pipeline", "RewardModelCfg"),
    "RLHFCfg": ("codex_ml.symbolic_pipeline", "RLHFCfg"),
    "ModelHandle": ("codex_ml.symbolic_pipeline", "ModelHandle"),
    "RewardModelHandle": ("codex_ml.symbolic_pipeline", "RewardModelHandle"),
    "get_metric": ("codex_ml.metrics.api", "get_metric"),
    "list_metrics": ("codex_ml.metrics.api", "list_metrics"),
    "register_metric": ("codex_ml.metrics.api", "register_metric"),
    "summarize_ndjson_logs": ("codex_ml.metrics.api", "summarize_ndjson_logs"),
    "BLEUScore": ("codex_ml.metrics.metric_implementations", "BLEUScore"),
    "F1Score": ("codex_ml.metrics.metric_implementations", "F1Score"),
    "MetricRegistry": ("codex_ml.metrics.metric_implementations", "MetricRegistry"),
    "RecallScore": ("codex_ml.metrics.metric_implementations", "RecallScore"),
    "TokenAccuracy": ("codex_ml.metrics.metric_implementations", "TokenAccuracy"),
    # P1 - CLI-Critical Exports (BLOCKING) - Successfully implemented
    "set_reproducible": ("codex_ml.utils.repro", "set_reproducible"),
    "load_tokenizer": ("codex_ml.tokenization", "load_tokenizer"),
    "set_seed": ("codex_ml.utils.repro", "set_seed"),
    # P2 - Core ML Functionality (High Priority) - Successfully implemented
    "CheckpointManager": ("codex_ml.utils.checkpointing", "CheckpointManager"),
    "load_checkpoint": ("codex_ml.utils.checkpointing", "load_checkpoint"),
    "save_checkpoint": ("codex_ml.utils.checkpointing", "save_checkpoint"),
    "load_training_checkpoint": ("codex_ml.utils.checkpointing", "load_training_checkpoint"),
    "verify_ckpt_integrity": ("codex_ml.utils.checkpointing", "verify_ckpt_integrity"),
    # P3 - Observability/Utilities (Medium Priority) - Successfully implemented
    "init_logger": ("codex_ml.monitoring.codex_logging", "init_logger"),
    "init_telemetry": ("codex_ml.monitoring.codex_logging", "init_telemetry"),
    "DatasetManifest": ("codex_ml.utils.repro", "DatasetManifest"),
    # API module exports
    "RagAPI": ("codex_ml.api", "RagAPI"),
    "BaseRagAPI": ("codex_ml.api", "BaseRagAPI"),
    "RagAPIRegistry": ("codex_ml.api", "RagAPIRegistry"),
}


def __getattr__(name: str):
    """Lazily import heavy optional modules on first access."""

    if name not in _EXPORT_MAP:
        # Fall back to subpackage import (e.g. codex_ml.interfaces, codex_ml.training).
        # Python normally sets these automatically when the subpackage is imported, but
        # pytest monkeypatch resolves dotted paths via attribute access on the parent package
        # before the subpackage has been loaded in the current process.
        try:
            return import_module(f"codex_ml.{name}")
        except ImportError:
            logger.debug("Suppressed exception in handler", exc_info=True)
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from None

    module_name, attr_name = _EXPORT_MAP[name]
    try:
        module = import_module(module_name)
    except (
        IOError,
        OSError,
        ModuleNotFoundError,
        ImportError,
    ) as exc:  # pragma: no cover - optional dependency path
        message = (
            f"{attr_name} is unavailable because importing {module_name!r} failed."
            " Install optional Codex ML dependencies to enable this feature."
        )
        raise AttributeError(message) from exc
    return getattr(module, attr_name)


__all__ = sorted(set(__all__ + list(_EXPORT_MAP)))
