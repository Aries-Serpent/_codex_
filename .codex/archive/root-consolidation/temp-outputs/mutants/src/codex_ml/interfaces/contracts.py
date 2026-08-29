"""Formal capability contracts for tokenization and training.

These contracts are intentionally lightweight so they can be validated in
offline environments. They document the required inputs/outputs, error modes,
and configuration expectations for key capabilities used across the
specialization track.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

from collections.abc import Mapping, Sequence  # noqa: E402
from dataclasses import dataclass  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Any, Protocol, runtime_checkable  # noqa: E402


class TokenizationContractError(TypeError):
    """Raised when a tokenizer violates the formal contract."""


class TrainingContractError(TypeError):
    """Raised when a training component violates the formal contract."""


@runtime_checkable
class TokenizerContract(Protocol):
    """Minimal tokenizer surface used by training and evaluation."""

    def encode(self, text: str) -> list[int]:
        pass

    def decode(self, ids: Sequence[int]) -> str:
        pass

    def add_special_tokens(self, tokens: Sequence[str]) -> Mapping[str, int]:
        pass

    def save(self, path: Path) -> None:
        pass

    @property
    def vocab_size(self) -> int:
        pass

    @property
    def name_or_path(self) -> str:
        pass


@dataclass(slots=True)
class TrainingBatchResult:
    """Structured result expected from a training step."""

    loss: float
    metrics: Mapping[str, float]


@dataclass(slots=True)
class TrainingConfigContract:
    """Configuration fields that every training loop must expose."""

    batch_size: int
    learning_rate: float
    num_epochs: int
    seed: int | None = None


def validate_tokenizer_contract(adapter: Any) -> None:
    """Validate that a tokenizer adapter honours the contract.

    The adapter must:
    * Accept only strings for ``encode`` and raise ``TypeError`` otherwise.
    * Accept sequences of integers for ``decode`` and raise ``ValueError`` on
      bad input.
    * Expose ``vocab_size`` and ``name_or_path`` attributes.
    """

    missing = [
        name for name in ("encode", "decode", "add_special_tokens") if not hasattr(adapter, name)
    ]
    if missing:
        raise TokenizationContractError(f"Tokenizer missing required methods: {missing}")

    if not hasattr(adapter, "vocab_size") or not hasattr(adapter, "name_or_path"):
        raise TokenizationContractError(
            "Tokenizer must expose vocab_size and name_or_path properties"
        )

    try:
        tokens = adapter.encode("contract smoke test")
    except (ValueError, TypeError) as e:
        type(e).__name__
        logger.debug("TypeError/ValueError: <ERROR_TYPE>")
        logger.warning("TypeError/ValueError: <ERROR_TYPE>", exc_info=True)
        raise TokenizationContractError(f"encode failed: {e}") from e

    if not isinstance(tokens, list) or not all(isinstance(t, int) for t in tokens):
        raise TokenizationContractError("encode must return a list[int]")

    try:
        adapter.encode(None)
    except (TypeError, ValueError):
        # HuggingFace fast tokenizers raise ValueError for non-string input;
        # slow/custom tokenizers may raise TypeError.  Both are acceptable.
        logger.debug("TypeError/ValueError on encode(None): <ERROR_TYPE>")
    else:  # pragma: no cover - enforce strict error mode
        raise TokenizationContractError(
            "encode must reject non-string input with TypeError or ValueError"
        )

    try:
        adapter.decode([0, 1])
    except (ValueError, TypeError) as exc:  # pragma: no cover - adapter-specific
        raise TokenizationContractError(f"decode failed for numeric ids: {exc}") from exc

    try:
        adapter.decode(["bad"])
    except (ValueError, TypeError):
        # HuggingFace fast tokenizers may raise TypeError for non-integer ids;
        # slow tokenizers may raise ValueError.  Both are acceptable.
        logger.debug("ValueError/TypeError on decode(['bad']): <ERROR_TYPE>")
    else:  # pragma: no cover - enforce strict error mode
        raise TokenizationContractError(
            "decode must raise ValueError or TypeError for non-integer ids"
        )


def validate_training_model(
    model: Any, sample_batch: Any, state: Mapping[str, Any] | None = None
) -> None:
    """Validate that a model exposes a compliant ``step`` method using a real batch."""

    if not hasattr(model, "step"):
        raise TrainingContractError("Model must implement a step(batch, state) method")

    step_fn = model.step
    if not callable(step_fn):
        raise TrainingContractError("Model.step must be callable")

    state_copy: dict[str, Any] = dict(state) if state is not None else {}
    try:
        result = step_fn(sample_batch, state_copy)
    except Exception as exc:  # pragma: no cover - model specific
        raise TrainingContractError(f"Model.step failed contract smoke test: {exc}") from exc

    if not isinstance(result, Mapping):
        raise TrainingContractError("Model.step must return a mapping of metrics")
    for key, value in result.items():
        if not isinstance(key, str):
            raise TrainingContractError("Metric keys must be strings")
        if not isinstance(value, (int, float)) and not hasattr(value, "item"):
            raise TrainingContractError("Metric values must be numeric")


def validate_training_config(config: Mapping[str, Any]) -> TrainingConfigContract:
    """Validate and coerce the required training configuration fields."""

    required = ("batch_size", "learning_rate", "num_epochs")
    missing = [field for field in required if field not in config]
    if missing:
        raise TrainingContractError(f"Training config missing required fields: {missing}")

    try:
        batch_size = int(config["batch_size"])
        learning_rate = float(config["learning_rate"])
        num_epochs = int(config["num_epochs"])
    except Exception as exc:  # pragma: no cover - type coercion errors
        raise TrainingContractError(f"Training config fields have invalid types: {exc}") from exc

    seed = config.get("seed")
    seed_value = int(seed) if seed is not None else None

    if batch_size <= 0 or learning_rate <= 0 or num_epochs <= 0:
        raise TrainingContractError("batch_size, learning_rate, and num_epochs must be positive")

    return TrainingConfigContract(
        batch_size=batch_size,
        learning_rate=learning_rate,
        num_epochs=num_epochs,
        seed=seed_value,
    )


__all__ = [
    "TokenizationContractError",
    "TokenizerContract",
    "TrainingBatchResult",
    "TrainingConfigContract",
    "TrainingContractError",
    "validate_tokenizer_contract",
    "validate_training_config",
    "validate_training_model",
]
