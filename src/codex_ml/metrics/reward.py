"""Reward-based evaluation metrics for RLHF and preference learning.

Provides metrics for computing mean and median rewards from model predictions,
supporting both scalar rewards and dictionary payloads with reward fields.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

from collections.abc import Callable, Mapping, Sequence  # noqa: E402


def register_metric(
    name: str,
    fn: Callable[..., object] | None = None,
    *,
    override: bool = False,
) -> Callable[[Callable[..., object]], Callable[..., object]] | Callable[..., object]:
    from .registry import register_metric as _register_metric

    return _register_metric(name, fn, override=override)


def _coerce_reward(value: object) -> float:
    if isinstance(value, Mapping) and "reward" in value:
        value = value.get("reward")
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        logger.debug("Exception caught, returning", exc_info=True)
        return 0.0


@register_metric("reward/mean", override=True)  # type: ignore[arg-type]
@register_metric("reward:mean", override=True)
def reward_mean(predictions: Sequence[object], targets: Sequence[object] | None = None) -> float:
    """Return the mean reward from predictions or mapping payloads."""

    if not predictions:
        return 0.0
    values = [_coerce_reward(p) for p in predictions]
    return float(sum(values) / len(values))


@register_metric("reward/success_rate", override=True)  # type: ignore[arg-type]
@register_metric("reward:success_rate", override=True)
def reward_success_rate(
    predictions: Sequence[object],
    targets: Sequence[object] | None = None,
    *,
    threshold: float = 0.0,
) -> float:
    """Proportion of rewards meeting or exceeding ``threshold``."""

    if not predictions:
        return 0.0
    values = [_coerce_reward(p) for p in predictions]
    hits = sum(1 for value in values if value >= threshold)
    return float(hits / len(values))


__all__ = ["reward_mean", "reward_success_rate"]
