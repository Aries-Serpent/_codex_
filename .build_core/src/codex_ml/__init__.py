"""
codex-ml package namespace.
Keeps surface minimal; version is exposed for packaging/diagnostics.
"""

from __future__ import annotations

import logging as _logging

logger = _logging.getLogger(__name__)

from importlib import import_module

__all__ = ["__version__"]
__version__ = "0.1.0"

# Avoid importing heavy deps at import time (Torch/HF) to keep `pip install` fast
# and to prevent side-effects when tools only query metadata.

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

try:  # pragma: no cover - optional dependency tree
    from .pipeline import run_codex_pipeline
except (ImportError, AttributeError):  # pragma: no cover - degrade gracefully when configs missing

    def run_codex_pipeline(*_args, **_kwargs) -> None:  # type: ignore[misc]
        raise RuntimeError("Optional dependencies for run_codex_pipeline are missing")


try:  # pragma: no cover - optional metrics dependency
    from .metrics.api import (
        get_metric,
        list_metrics,
        register_metric,
        summarize_ndjson_logs,
    )
    from .metrics.metric_implementations import (
        BLEUScore,
        F1Score,
        MetricRegistry,
        RecallScore,
        TokenAccuracy,
    )
except (
    ImportError,
    AttributeError,
):  # pragma: no cover - degrade gracefully when metrics extras missing

    class _MissingMetric:
        def __init__(self, name: str):
            self._name = name

        def __call__(self, *_args, **_kwargs) -> None:  # pragma: no cover - defensive
            raise RuntimeError(f"Metrics module unavailable; {self._name} requires optional extras")

        def __getattr__(self, _item: str) -> None:  # pragma: no cover - defensive
            msg = f"Metrics module unavailable; {self._name} requires optional extras"
            raise AttributeError(msg)

    MetricRegistry = _MissingMetric("MetricRegistry")  # type: ignore[misc,assignment]
    F1Score = _MissingMetric("F1Score")  # type: ignore[misc,assignment]
    RecallScore = _MissingMetric("RecallScore")  # type: ignore[misc,assignment]
    BLEUScore = _MissingMetric("BLEUScore")  # type: ignore[misc,assignment]
    TokenAccuracy = _MissingMetric("TokenAccuracy")  # type: ignore[misc,assignment]
    get_metric = _MissingMetric("get_metric")  # type: ignore[assignment]
    register_metric = _MissingMetric("register_metric")  # type: ignore[assignment]
    list_metrics = _MissingMetric("list_metrics")  # type: ignore[assignment]
    summarize_ndjson_logs = _MissingMetric("summarize_ndjson_logs")  # type: ignore[assignment]

if MetricRegistry.__class__.__name__ != "_MissingMetric":
    __all__ += [
        "BLEUScore",
        "F1Score",
        "MetricRegistry",
        "RecallScore",
        "TokenAccuracy",
        "get_metric",
        "list_metrics",
        "register_metric",
        "summarize_ndjson_logs",
    ]


# Optional imports: symbolic pipeline requires tokenizer/transformers; guard for environments
# without heavy ML deps.
try:  # pragma: no cover - optional path
    from .symbolic_pipeline import (
        ModelHandle,
        PretrainCfg,
        RewardModelCfg,
        RewardModelHandle,
        RLHFCfg,
        SFTCfg,
        Weights,
        run_codex_symbolic_pipeline,
    )
except (
    ImportError,
    AttributeError,
):  # pragma: no cover - degrade gracefully when symbolic deps missing

    class _MissingSymbolic:
        def __init__(self, name: str):
            self._name = name

        def __getattr__(self, item: str) -> None:  # pragma: no cover - defensive
            raise AttributeError(
                f"Optional dependency for '{self._name}' is missing; install codex-ml[symbolic]"
            )

        def __call__(self, *_args, **_kwargs) -> None:  # pragma: no cover - defensive
            raise RuntimeError(
                f"Optional dependency for '{self._name}' is missing; install codex-ml[symbolic]"
            )

    run_codex_symbolic_pipeline = _MissingSymbolic("run_codex_symbolic_pipeline")  # type: ignore[assignment]
    Weights = _MissingSymbolic("Weights")  # type: ignore[misc,assignment]
    PretrainCfg = _MissingSymbolic("PretrainCfg")  # type: ignore[misc,assignment]
    SFTCfg = _MissingSymbolic("SFTCfg")  # type: ignore[misc,assignment]
    RewardModelCfg = _MissingSymbolic("RewardModelCfg")  # type: ignore[misc,assignment]
    RLHFCfg = _MissingSymbolic("RLHFCfg")  # type: ignore[misc,assignment]
    ModelHandle = _MissingSymbolic("ModelHandle")  # type: ignore[misc,assignment]
    RewardModelHandle = _MissingSymbolic("RewardModelHandle")  # type: ignore[misc,assignment]


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
    except (IOError, OSError) as exc:  # pragma: no cover - optional dependency path
        message = (
            f"{attr_name} is unavailable because importing {module_name!r} failed."
            " Install optional Codex ML dependencies to enable this feature."
        )
        raise AttributeError(message) from exc
    return getattr(module, attr_name)


__all__ = sorted(set(__all__ + list(_EXPORT_MAP)))
