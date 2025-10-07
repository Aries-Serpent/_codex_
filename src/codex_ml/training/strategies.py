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

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Protocol, Optional, Callable

CallbackFn = Callable[..., None]


class TrainingCallback(Protocol):
    def on_epoch_start(self, epoch: int, state: Dict[str, Any]) -> None: ...

    def on_epoch_end(
        self, epoch: int, metrics: Dict[str, float], state: Dict[str, Any]
    ) -> None: ...

    def on_step(
        self,
        batch_index: int,
        global_step: int,
        loss: float,
        state: Dict[str, Any],
    ) -> None: ...

    def on_checkpoint(
        self,
        epoch: int,
        path: str,
        metrics: Dict[str, float],
        state: Dict[str, Any],
    ) -> None: ...


class NoOpCallback:
    def on_epoch_start(self, epoch: int, state: Dict[str, Any]) -> None: ...

    def on_epoch_end(
        self, epoch: int, metrics: Dict[str, float], state: Dict[str, Any]
    ) -> None: ...

    def on_step(
        self,
        batch_index: int,
        global_step: int,
        loss: float,
        state: Dict[str, Any],
    ) -> None: ...

    def on_checkpoint(
        self,
        epoch: int,
        path: str,
        metrics: Dict[str, float],
        state: Dict[str, Any],
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
        from codex_ml.training.functional_training import (
            run_functional_training as _fn,
        )  # type: ignore

        # Minimal shim; functional loop currently handles internal logging.
        for cb in callbacks:
            try:
                cb.on_epoch_start(0, {"resume_from": resume_from})
            except Exception:
                pass

        try:
            _fn(
                model_name=config.model_name,
                epochs=config.epochs,
                batch_size=config.batch_size,
                grad_accum=config.grad_accum,
                seed=config.seed,
                output_dir=config.output_dir,
                mlflow_enable=config.mlflow_enable,
            )
            status = "ok"
        except Exception as exc:  # pragma: no cover - defensive
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
