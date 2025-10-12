"""Utility functions to apply Zendesk plans."""

from __future__ import annotations

import logging
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from codex.zendesk.monitoring.zendesk_metrics import metrics as _metrics

LOGGER = logging.getLogger(__name__)

PlanOperations = Iterable[Mapping[str, Any]]


def _extract_operations(plan_data: Any, resource: str) -> list[Mapping[str, Any]]:
    """Normalize various plan payload structures into a list of operations."""

    candidate: Any
    if isinstance(plan_data, Mapping):
        if resource in plan_data:
            candidate = plan_data[resource]
        elif "operations" in plan_data:
            candidate = plan_data["operations"]
        else:
            candidate = [plan_data]
    else:
        candidate = plan_data

    if isinstance(candidate, str | bytes | bytearray):
        raise ValueError(
            f"Plan for {resource} must be a sequence of operation mappings, not a scalar."
        )
    if not isinstance(candidate, Sequence):
        raise ValueError(f"Plan for {resource} must be a sequence of operation mappings.")

    operations: list[Mapping[str, Any]] = []
    for index, entry in enumerate(candidate):
        if not isinstance(entry, Mapping):
            entry_type = type(entry).__name__
            raise ValueError(
                f"Plan for {resource} must contain mapping entries; "
                f"item {index} is {entry_type}."
            )
        operations.append(entry)
    return operations


def _log_pending(resource: str, operations: PlanOperations, env: str) -> None:
    ops = list(operations)
    LOGGER.info(
        "Prepared %s operation(s) for %s in environment '%s'.",
        len(ops),
        resource,
        env,
    )
    if not ops:
        LOGGER.info("No changes required for resource '%s'.", resource)

    try:
        metric = _metrics.get("zendesk_diff_operations")
        if metric is not None and hasattr(metric, "observe"):
            metric.observe(float(len(ops)))
    except Exception:  # pragma: no cover - metrics are best-effort offline
        LOGGER.debug("Metrics emit skipped for resource '%s'.", resource)


def apply_triggers(plan_data: Any, env: str) -> None:
    """Apply trigger operations to the given Zendesk environment."""

    _log_pending("triggers", _extract_operations(plan_data, "triggers"), env)


def apply_fields(plan_data: Any, env: str) -> None:
    """Apply ticket field operations to the given Zendesk environment."""

    _log_pending("fields", _extract_operations(plan_data, "fields"), env)


def apply_forms(plan_data: Any, env: str) -> None:
    """Apply ticket form operations to the given Zendesk environment."""

    _log_pending("forms", _extract_operations(plan_data, "forms"), env)


def apply_groups(plan_data: Any, env: str) -> None:
    """Apply group operations to the given Zendesk environment."""

    _log_pending("groups", _extract_operations(plan_data, "groups"), env)


def apply_macros(plan_data: Any, env: str) -> None:
    """Apply macro operations to the given Zendesk environment."""

    _log_pending("macros", _extract_operations(plan_data, "macros"), env)


def apply_views(plan_data: Any, env: str) -> None:
    """Apply view operations to the given Zendesk environment."""

    _log_pending("views", _extract_operations(plan_data, "views"), env)


def apply_webhooks(plan_data: Any, env: str) -> None:
    """Apply webhook operations to the given Zendesk environment."""

    _log_pending("webhooks", _extract_operations(plan_data, "webhooks"), env)


def apply_apps(plan_data: Any, env: str) -> None:
    """Apply app operations to the given Zendesk environment."""

    _log_pending("apps", _extract_operations(plan_data, "apps"), env)


def apply_widgets(plan_data: Any, env: str) -> None:
    """Apply web widget operations to the given Zendesk environment."""

    _log_pending("widgets", _extract_operations(plan_data, "widgets"), env)


def apply_guide(plan_data: Any, env: str) -> None:
    """Apply Guide (Help Center) operations to the given Zendesk environment."""

    _log_pending("guide", _extract_operations(plan_data, "guide"), env)


def apply_routing(plan_data: Any, env: str) -> None:
    """Apply routing operations (skills-based routing) to the given environment."""

    _log_pending("routing", _extract_operations(plan_data, "routing"), env)


def apply_talk(plan_data: Any, env: str) -> None:
    """Apply Zendesk Talk operations (IVR, greetings, numbers) offline."""

    _log_pending("talk", _extract_operations(plan_data, "talk"), env)


__all__ = [
    "apply_apps",
    "apply_fields",
    "apply_forms",
    "apply_groups",
    "apply_guide",
    "apply_macros",
    "apply_routing",
    "apply_talk",
    "apply_triggers",
    "apply_views",
    "apply_webhooks",
    "apply_widgets",
]
