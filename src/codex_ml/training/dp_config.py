"""
Dp Config Module

This module provides functionality for dp config.

Usage:
    from training.dp_config import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class DifferentialPrivacyConfig:
    """Encapsulates Opacus differential privacy settings."""

    enabled: bool = False
    epsilon: float = 1.0
    delta: float = 1e-5
    max_grad_norm: float = 1.0
    noise_multiplier: float = 1.0
    secure_rng: bool = False
    _dependency_checked: bool = field(init=False, default=False, repr=False)

    def __post_init__(self) -> None:
        if self.enabled:
            # Reject invalid privacy parameters before probing for Opacus so
            # misconfiguration surfaces as a clear ValueError.
            self._validate_parameters()
            self._ensure_dependency()

    def _validate_parameters(self) -> None:
        if not self.epsilon > 0:
            raise ValueError(f"epsilon must be positive, got {self.epsilon!r}")
        if not 0 < self.delta < 1:
            raise ValueError(f"delta must be in (0, 1), got {self.delta!r}")
        if not self.max_grad_norm > 0:
            raise ValueError(f"max_grad_norm must be positive, got {self.max_grad_norm!r}")
        if not self.noise_multiplier >= 0:
            raise ValueError(
                f"noise_multiplier must be non-negative, got {self.noise_multiplier!r}"
            )

    def _ensure_dependency(self) -> None:
        if self._dependency_checked:
            return
        try:
            __import__("opacus")
        except ImportError as exc:  # pragma: no cover - optional dependency path
            raise ImportError(
                "Opacus is required for differential privacy; install with 'pip install opacus'."
            ) from exc
        self._dependency_checked = True

    def as_dict(self) -> dict[str, Any]:
        return {
            "enabled": self.enabled,
            "epsilon": float(self.epsilon),
            "delta": float(self.delta),
            "max_grad_norm": float(self.max_grad_norm),
            "noise_multiplier": float(self.noise_multiplier),
            "secure_rng": bool(self.secure_rng),
        }


def make_private_model(
    model: Any,
    optimizer: Any,
    data_loader: Any,
    dp_config: DifferentialPrivacyConfig,
) -> tuple[Any, Any, Any, Any]:
    """Wrap the training components with Opacus privacy engine when enabled."""

    if not dp_config.enabled:
        return model, optimizer, data_loader, None

    dp_config._ensure_dependency()
    from opacus import PrivacyEngine

    privacy_engine = PrivacyEngine(secure_rng=bool(dp_config.secure_rng))
    model, optimizer, data_loader = privacy_engine.make_private(
        module=model,
        optimizer=optimizer,
        data_loader=data_loader,
        noise_multiplier=float(dp_config.noise_multiplier),
        max_grad_norm=float(dp_config.max_grad_norm),
    )
    return model, optimizer, data_loader, privacy_engine


__all__ = ["DifferentialPrivacyConfig", "make_private_model"]
