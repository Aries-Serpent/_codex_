"""Interfaces for future RLHF integration.

These minimal stubs document the expected APIs for reward modelling and
reinforcement learning trainers.  Concrete implementations will be added in a
future iteration.
"""

from __future__ import annotations

from typing import Any


class RewardModel:
    """Abstract reward model used during RLHF training."""

    def score(self, *args: Any, **kwargs: Any) -> float:  # pragma: no cover - stub
        """Return a scalar reward for the provided inputs."""
        raise NotImplementedError


class RLTrainer:
    """Placeholder RL trainer for future integration."""

    def train(self, *args: Any, **kwargs: Any) -> None:  # pragma: no cover - stub
        """Run the RLHF training loop."""
        raise NotImplementedError
