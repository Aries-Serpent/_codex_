"""Backend strategy interfaces for the unified training orchestrator.

Each strategy MUST implement:
    - run(config, callbacks) -> TrainingResult
    - name (property / attribute)

Callbacks receive:
    on_epoch_start(epoch, state)
    on_epoch_end(epoch, metrics, state)
    on_step(batch_index, global_step, loss, state)
    on_checkpoint(epoch, path, metrics, state)

Minimal surface keeps legacy + functional backends pluggable.
"""

from __future__ import annotations

from collections.abc import Iterable as IterableABC
from dataclasses import dataclass
from importlib import import_module
from typing import Any, Dict, Iterable, List, Protocol, Optional


class TrainingCallback(Protocol):
    def on_epoch_start(self, epoch: int, state: Dict[str, Any]) -> None: ...
    def on_epoch_end(
        self, epoch: int, metrics: Dict[str, float], state: Dict[str, Any]
    ) -> None: ...
    def on_step(
        self, batch_index: int, global_step: int, loss: float, state: Dict[str, Any]
    ) -> None: ...
    def on_checkpoint(
        self, epoch: int, path: str, metrics: Dict[str, float], state: Dict[str, Any]
    ) -> None: ...


class NoOpCallback:
    def on_epoch_start(self, epoch: int, state: Dict[str, Any]) -> None: ...
    def on_epoch_end(
        self, epoch: int, metrics: Dict[str, float], state: Dict[str, Any]
    ) -> None: ...
    def on_step(
        self, batch_index: int, global_step: int, loss: float, state: Dict[str, Any]
    ) -> None: ...
    def on_checkpoint(
        self, epoch: int, path: str, metrics: Dict[str, float], state: Dict[str, Any]
    ) -> None: ...


@dataclass
class TrainingResult:
    status: str
    backend: str
    final_epoch: int
    output_dir: str
    extra: Dict[str, Any]


class BackendStrategy(Protocol):
    backend_name: str

    def run(
        self,
        config: Any,
        callbacks: Iterable[TrainingCallback],
        resume_from: Optional[str] = None,
    ) -> TrainingResult: ...


def _safe_callbacks(callbacks: Iterable[TrainingCallback]) -> List[TrainingCallback]:
    return list(callbacks) if callbacks else [NoOpCallback()]


# ---- Strategy Implementations ------------------------------------------------


class FunctionalStrategy:
    """Adapter around existing functional_training module."""

    backend_name = "functional"

    def run(
        self,
        config: Any,
        callbacks: Iterable[TrainingCallback],
        resume_from: Optional[str] = None,
    ) -> TrainingResult:
        ft_module = import_module("codex_ml.training.functional_training")
        TrainConfig = getattr(ft_module, "TrainConfig")
        train_fn = getattr(ft_module, "train")

        extra_payload: Dict[str, Any] = {}

        # Minimal shim; functional loop currently handles internal logging.
        for cb in callbacks:
            try:
                cb.on_epoch_start(0, {"resume_from": resume_from})
            except Exception:
                pass

        functional_overrides: Dict[str, Any] = {}
        if isinstance(getattr(config, "extra", None), dict):
            functional_overrides.update(config.extra)
            nested = config.extra.get("functional")
            if isinstance(nested, dict):
                functional_overrides.update(nested)
            nested = config.extra.get("functional_training")
            if isinstance(nested, dict):
                functional_overrides.update(nested)

        train_texts = functional_overrides.pop("train_texts", functional_overrides.pop("texts", []))
        if isinstance(train_texts, str):
            train_texts = [train_texts]
        elif isinstance(train_texts, IterableABC):
            train_texts = list(train_texts)
        elif train_texts and not isinstance(train_texts, bool):
            train_texts = [train_texts]
        else:
            train_texts = []
        val_texts = functional_overrides.pop(
            "val_texts", functional_overrides.pop("eval_texts", None)
        )
        model_override = functional_overrides.pop("model", None)

        cfg_payload: Dict[str, Any] = {
            "model_name": config.model_name,
            "epochs": config.epochs,
            "batch_size": config.batch_size,
            "gradient_accumulation_steps": config.grad_accum,
            "seed": config.seed,
            "checkpoint_dir": config.output_dir,
            "mlflow_enable": config.mlflow_enable,
        }
        for key in list(functional_overrides):
            if key in getattr(TrainConfig, "__annotations__", {}):
                cfg_payload[key] = functional_overrides.pop(key)

        train_config = TrainConfig(**cfg_payload)

        status = "ok"
        metrics: Dict[str, Any] = {}

        try:
            val_arg: Any
            if val_texts is None or isinstance(val_texts, bool):  # guard against truthy flags
                val_arg = None if val_texts is None else val_texts
            elif isinstance(val_texts, str):
                val_arg = [val_texts]
            elif isinstance(val_texts, IterableABC):
                val_arg = list(val_texts)
            else:
                val_arg = val_texts

            if train_texts:
                metrics = train_fn(
                    list(train_texts),
                    config=train_config,
                    val_texts=val_arg,
                    model=model_override,
                )
                extra_payload["trained"] = True
            else:
                extra_payload["trained"] = False
        except Exception as exc:  # pragma: no cover - defensive
            status = "error"
            extra_payload["exception"] = repr(exc)
            for cb in callbacks:
                try:
                    cb.on_epoch_end(0, {"error": 1.0}, {"exception": repr(exc)})
                except Exception:
                    pass
        else:
            for cb in callbacks:
                try:
                    cb.on_epoch_end(
                        0, {"status": 1.0}, {"metrics": metrics or {}, "trained": bool(train_texts)}
                    )
                except Exception:
                    pass

        if functional_overrides:
            extra_payload["unused_overrides"] = functional_overrides

        return TrainingResult(
            status=status,
            backend=self.backend_name,
            final_epoch=config.epochs,
            output_dir=config.output_dir,
            extra={"resume_from": resume_from, **extra_payload},
        )


class LegacyStrategy:
    """Adapter wrapping legacy train_loop entry point."""

    backend_name = "legacy"

    def run(
        self,
        config: Any,
        callbacks: Iterable[TrainingCallback],
        resume_from: Optional[str] = None,
    ) -> TrainingResult:
        import warnings
        from codex_ml.train_loop import run_training as _legacy  # type: ignore

        warnings.warn(
            "Legacy training loop usage is deprecated – unified orchestrator proxy.",
            DeprecationWarning,
            stacklevel=2,
        )
        for cb in callbacks:
            try:
                cb.on_epoch_start(0, {"resume_from": resume_from})
            except Exception:
                pass
        try:
            _legacy(
                epochs=config.epochs,
                grad_accum=config.grad_accum,
                seed=config.seed,
                art_dir=None,
                model_name=config.model_name,
            )
            status = "ok"
        except Exception as exc:  # pragma: no cover
            status = "error"
            for cb in callbacks:
                try:
                    cb.on_epoch_end(0, {"error": 1.0}, {"exception": repr(exc)})
                except Exception:
                    pass
        return TrainingResult(
            status=status,
            backend=self.backend_name,
            final_epoch=config.epochs,
            output_dir=config.output_dir,
            extra={"resume_from": resume_from},
        )


STRATEGY_REGISTRY = {
    "functional": FunctionalStrategy(),
    "legacy": LegacyStrategy(),
}


def resolve_strategy(name: str) -> BackendStrategy:
    try:
        return STRATEGY_REGISTRY[name]
    except KeyError:
        raise ValueError(f"Unknown backend strategy: {name!r}. Choices={list(STRATEGY_REGISTRY)}")
