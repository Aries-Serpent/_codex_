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

import logging
import warnings
from collections.abc import Iterable
from contextlib import suppress
from copy import deepcopy
from dataclasses import asdict, dataclass, is_dataclass, replace
from importlib import import_module
from pathlib import Path
from typing import Any, Optional, Protocol, runtime_checkable

from codex_ml.data.jsonl_loader import load_jsonl

logger = logging.getLogger(__name__)


@runtime_checkable
class TrainingCallback(Protocol):
    def on_epoch_start(self, epoch: int, state: dict[str, Any]) -> None:
        pass

    def on_epoch_end(self, epoch: int, metrics: dict[str, float], state: dict[str, Any]) -> None:
        pass

    def on_step(
        self, batch_index: int, global_step: int, loss: float, state: dict[str, Any]
    ) -> None:
        pass

    def on_checkpoint(
        self, epoch: int, path: str, metrics: dict[str, float], state: dict[str, Any]
    ) -> None:
        pass


class NoOpCallback:
    def on_epoch_start(self, epoch: int, state: dict[str, Any]) -> None:
        pass

    def on_epoch_end(self, epoch: int, metrics: dict[str, float], state: dict[str, Any]) -> None:
        pass

    def on_step(
        self, batch_index: int, global_step: int, loss: float, state: dict[str, Any]
    ) -> None:
        pass

    def on_checkpoint(
        self, epoch: int, path: str, metrics: dict[str, float], state: dict[str, Any]
    ) -> None:
        pass


@dataclass
class TrainingResult:
    status: str
    backend: str
    final_epoch: int
    output_dir: str
    extra: dict[str, Any]


@runtime_checkable
class BackendStrategy(Protocol):
    backend_name: str

    def run(
        self,
        config: Any,
        callbacks: Iterable[TrainingCallback],
        resume_from: Optional[str] = None,
    ) -> TrainingResult:
        pass


def _safe_callbacks(callbacks: Iterable[TrainingCallback]) -> list[TrainingCallback]:
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
        TrainConfig = ft_module.TrainConfig
        train_fn = ft_module.train

        extra_payload: dict[str, Any] = {}

        # Minimal shim; functional loop currently handles internal logging.
        for cb in callbacks:
            try:
                cb.on_epoch_start(0, {"resume_from": resume_from})
            except (ValueError, TypeError, RuntimeError) as e:
                type(e).__name__
                logger.warning("Exception: <ERROR_TYPE>", exc_info=True)

        functional_overrides: dict[str, Any] = {}
        if isinstance(getattr(config, "extra", None), dict):
            functional_overrides.update(config.extra)
            nested = config.extra.get("functional")
            if isinstance(nested, dict):
                functional_overrides.update(nested)
            nested = config.extra.get("functional_training")
            if isinstance(nested, dict):
                functional_overrides.update(nested)

        train_texts = functional_overrides.pop("train_texts", None)
        if train_texts is None:
            train_texts = functional_overrides.pop("texts", [])
        if isinstance(train_texts, str):
            train_texts = [train_texts]
        elif isinstance(train_texts, Iterable) and not isinstance(train_texts, str):
            train_texts = list(train_texts)
        elif train_texts and not isinstance(train_texts, bool):
            train_texts = [train_texts]
        else:
            train_texts = []
        val_texts = functional_overrides.pop(
            "val_texts", functional_overrides.pop("eval_texts", None)
        )
        model_override = functional_overrides.pop("model", None)

        cfg_payload: dict[str, Any] = {
            "model_name": config.model_name,
            "epochs": config.epochs,
            "batch_size": config.batch_size,
            "gradient_accumulation_steps": config.grad_accum,
            "seed": config.seed,
            "checkpoint_dir": config.output_dir,
            "mlflow_enable": config.mlflow_enable,
        }
        learning_rate = getattr(config, "learning_rate", None)
        if learning_rate is not None:
            cfg_payload["lr"] = learning_rate
        for key in list(functional_overrides):
            if key in getattr(TrainConfig, "__annotations__", {}):
                cfg_payload[key] = functional_overrides.pop(key)

        train_config = TrainConfig(**cfg_payload)

        status = "ok"
        metrics: dict[str, Any] = {}

        try:
            val_arg: Any
            val_is_boolish = val_texts is None or isinstance(val_texts, bool)
            if val_is_boolish:  # guard against truthy flags
                val_arg = None if val_texts is None else val_texts
            elif isinstance(val_texts, str):
                val_arg = [val_texts]
            elif isinstance(val_texts, Iterable):
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
        except (ValueError, TypeError, RuntimeError) as exc:  # pragma: no cover - defensive
            status = "error"
            extra_payload["exception"] = repr(exc)
            for cb in callbacks:
                try:
                    cb.on_epoch_end(0, {"error": 1.0}, {"exception": repr(exc)})
                except (ValueError, TypeError, RuntimeError) as e:
                    type(e).__name__
                    logger.warning("Exception: <ERROR_TYPE>", exc_info=True)
        else:
            for cb in callbacks:
                try:
                    cb.on_epoch_end(
                        0,
                        {"status": 1.0},
                        {"metrics": metrics or {}, "trained": bool(train_texts)},
                    )
                except (ValueError, TypeError, RuntimeError) as e:
                    type(e).__name__
                    logger.warning("Exception: <ERROR_TYPE>", exc_info=True)

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
        from codex_ml.train_loop import run_training as _legacy

        warnings.warn(
            "Legacy training loop usage is deprecated – unified orchestrator proxy.",
            DeprecationWarning,
            stacklevel=2,
        )
        for cb in callbacks:
            try:
                cb.on_epoch_start(0, {"resume_from": resume_from})
            except (ValueError, TypeError, RuntimeError) as e:
                type(e).__name__
                logger.warning("Exception: <ERROR_TYPE>", exc_info=True)
        try:
            _legacy(
                epochs=config.epochs,
                grad_accum=config.grad_accum,
                seed=config.seed,
                art_dir=None,
                model_name=config.model_name,
            )
            status = "ok"
        except (ValueError, TypeError, RuntimeError) as exc:  # pragma: no cover
            status = "error"
            for cb in callbacks:
                try:
                    cb.on_epoch_end(0, {"error": 1.0}, {"exception": repr(exc)})
                except (ValueError, TypeError, RuntimeError) as e:
                    type(e).__name__
                    logger.warning("Exception: <ERROR_TYPE>", exc_info=True)
        return TrainingResult(
            status=status,
            backend=self.backend_name,
            final_epoch=config.epochs,
            output_dir=config.output_dir,
            extra={"resume_from": resume_from},
        )


class ContinualReplayStrategy:
    """Phase-by-phase continual-learning wrapper around the functional strategy."""

    backend_name = "continual_replay"

    def __init__(self, base_strategy: BackendStrategy | None = None) -> None:
        self._base = base_strategy or FunctionalStrategy()

    def _coerce_text_list(self, value: Any) -> list[str]:
        if value is None or value is False:
            return []
        if isinstance(value, str):
            return [value]
        if isinstance(value, Iterable):
            return [str(item) for item in value if item]
        return [str(value)]

    def _materialize_dataset_texts(
        self, dataset: Any, *, seed: int
    ) -> tuple[list[str], list[str]] | None:
        if not isinstance(dataset, dict):
            return None

        if "texts" in dataset:
            train_items = self._coerce_text_list(dataset.get("texts"))
            val_items = self._coerce_text_list(dataset.get("val_texts"))
            return train_items, val_items

        path = dataset.get("path")
        if not path:
            return None

        format_hint = str(dataset.get("format", "jsonl") or "").lower()
        dataset_seed_raw = dataset.get("seed")
        try:
            dataset_seed = int(dataset_seed_raw if dataset_seed_raw is not None else seed)
        except (TypeError, ValueError):
            dataset_seed = seed

        val_fraction_raw = dataset.get("val_fraction")
        try:
            val_fraction = float(val_fraction_raw) if val_fraction_raw is not None else 0.0
        except (TypeError, ValueError):
            val_fraction = 0.0

        target_path = Path(str(path))

        if format_hint in {"jsonl", "ndjson"}:
            train_texts, val_texts = load_jsonl(
                target_path,
                seed=dataset_seed,
                val_fraction=val_fraction,
            )
            return train_texts, val_texts

        if format_hint in {"text", "txt"}:
            try:
                payload = target_path.read_text(encoding="utf-8")
            except OSError as e:
                type(e).__name__
                logger.debug("OSError: <ERROR_TYPE>")
                logger.warning("OSError: <ERROR_TYPE>", exc_info=True)
                return [], []
            texts = [line.strip() for line in payload.splitlines() if line.strip()]
            return texts, []

        # Fallback: treat the provided path (or object) as direct training text.
        return self._coerce_text_list(path), []

    def _resolve_schedule(self, config: Any) -> list[dict[str, Any]]:
        extra = getattr(config, "extra", {}) or {}
        continual = extra.get("continual", {}) if isinstance(extra, dict) else {}
        phases = continual.get("phases") if isinstance(continual, dict) else None
        if not phases:
            continual_cfg = getattr(config, "continual", None)
            if continual_cfg:
                if isinstance(continual_cfg, dict):
                    phases = continual_cfg.get("phases")
                else:
                    phases = getattr(continual_cfg, "phases", None)
        if not phases:
            phases = getattr(config, "continual_schedule", None)
        if not phases:
            message = "missing config.extra['continual']['phases'] schedule for continual replay"
            raise ValueError(message)

        resolved: list[dict[str, Any]] = []
        for phase in phases:
            if isinstance(phase, dict):
                resolved.append(dict(phase))
            elif is_dataclass(phase):
                resolved.append(asdict(phase))  # type: ignore[arg-type]
            else:
                try:
                    resolved.append(dict(phase))
                except TypeError as e:
                    type(e).__name__
                    logger.debug("TypeError: <ERROR_TYPE>")
                    logger.warning("TypeError: <ERROR_TYPE>", exc_info=True)
                    resolved.append(dict(vars(phase)))
        return resolved

    def run(
        self,
        config: Any,
        callbacks: Iterable[TrainingCallback],
        resume_from: Optional[str] = None,
    ) -> TrainingResult:
        schedule = self._resolve_schedule(config)
        phase_results: list[dict[str, Any]] = []
        output_root = Path(getattr(config, "output_dir", "runs/continual"))
        carry_resume = resume_from
        status = "ok"

        for index, phase in enumerate(schedule):
            phase_name = phase.get("name") or f"phase-{index}"
            epochs = int(phase.get("epochs", getattr(config, "epochs", 1)))
            base_extra = getattr(config, "extra", {}) or {}
            overrides = deepcopy(base_extra) if isinstance(base_extra, dict) else {}
            phase_overrides_src = phase.get("overrides", {})
            if isinstance(phase_overrides_src, dict):
                phase_overrides = dict(phase_overrides_src)
            else:
                phase_overrides = {}
            for key, value in phase_overrides.items():
                if isinstance(value, dict) and isinstance(overrides.get(key), dict):
                    merged = dict(overrides[key])
                    merged.update(value)
                    overrides[key] = merged
                else:
                    overrides[key] = value

            dataset_spec = phase.get("dataset")
            if dataset_spec and isinstance(overrides, dict):
                functional = overrides.setdefault("functional", {})
                if not isinstance(functional, dict):
                    functional = {}
                    overrides["functional"] = functional

                base_seed_raw = getattr(config, "seed", 0)
                try:
                    dataset_seed = int(base_seed_raw or 0)
                except (TypeError, ValueError):
                    dataset_seed = 0
                dataset_texts = self._materialize_dataset_texts(
                    dataset_spec,
                    seed=dataset_seed,
                )
                if dataset_texts:
                    train_split, val_split = dataset_texts
                    role = str(dataset_spec.get("role", "train") or "").lower()
                    eval_roles = {"eval", "validation", "val", "test"}

                    if "train_texts" not in phase and role not in eval_roles and train_split:
                        functional.setdefault("train_texts", list(train_split))

                    if "val_texts" not in phase and val_split:
                        functional.setdefault("val_texts", list(val_split))

                    if "val_texts" not in phase and role in eval_roles:
                        candidate = val_split or train_split
                        if candidate:
                            functional.setdefault("val_texts", list(candidate))

            if "train_texts" in phase:
                functional = overrides.setdefault("functional", {})
                if isinstance(functional, dict):
                    functional["train_texts"] = phase["train_texts"]
            if "val_texts" in phase:
                functional = overrides.setdefault("functional", {})
                if isinstance(functional, dict):
                    functional["val_texts"] = phase["val_texts"]

            phase_config = replace(
                config,
                epochs=epochs,
                output_dir=str(output_root / phase_name),
                extra=overrides,
            )

            for cb in callbacks:
                with suppress(Exception):
                    callback_state = {"phase": phase_name, "resume_from": carry_resume}
                    cb.on_epoch_start(index, callback_state)

            result = self._base.run(
                phase_config,
                callbacks,
                resume_from=carry_resume,
            )
            phase_results.append(
                {
                    "name": phase_name,
                    "status": result.status,
                    "output_dir": result.output_dir,
                    "epochs": epochs,
                }
            )
            carry_resume = result.output_dir
            if result.status != "ok":
                status = "error"
                if not getattr(config, "continue_after_failure", False):
                    break

        total_epochs = sum(int(phase.get("epochs", 0)) for phase in phase_results)

        return TrainingResult(
            status=status,
            backend=self.backend_name,
            final_epoch=total_epochs if total_epochs else getattr(config, "epochs", 0),
            output_dir=str(output_root),
            extra={
                "phases": phase_results,
                "resume_from": resume_from,
            },
        )


STRATEGY_REGISTRY = {
    "functional": FunctionalStrategy(),
    "legacy": LegacyStrategy(),
    "continual_replay": ContinualReplayStrategy(),
}


def resolve_strategy(name: str | None) -> BackendStrategy:
    """Return the BackendStrategy for *name*.

    Accepts ``None`` (defaults to ``"functional"``), case-insensitive strings,
    and any key registered in :data:`STRATEGY_REGISTRY`.
    """
    if name is None:
        name = "functional"
    normalised = str(name).lower().strip()
    try:
        return STRATEGY_REGISTRY[normalised]  # type: ignore[return-value]
    except KeyError as err:
        raise ValueError(
            f"Unknown backend strategy: {name!r}. Choices={list(STRATEGY_REGISTRY)}"
        ) from err
