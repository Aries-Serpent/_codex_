"""Backward-compatible helpers for CRM flow diagrams."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from codex.diagram.flows import *  # noqa: F403

__all__ = [*globals().get("__all__", []), "build_flow_edges"]


def build_flow_edges(steps: Iterable[Any]) -> tuple[list[tuple[str, str]], str]:
    """Convert sequential steps into start-to-close edge tuples.

    The helper accepts strings, mappings with ``label``/``name`` keys, or objects
    exposing a ``label`` attribute. It mirrors the legacy CRM pipeline visualiser
    that the tests exercise.
    """

    resolved_steps: list[str] = []
    for step in steps:
        label = _extract_label(step)
        if label:
            resolved_steps.append(label)

    edges: list[tuple[str, str]] = []
    previous = "Start"
    for label in resolved_steps:
        edges.append((previous, label))
        previous = label
    edges.append((previous, "Close"))
    return edges, "Close"


def _extract_label(step: Any) -> str:
    if isinstance(step, str):
        return step
    if isinstance(step, dict):
        for key in ("label", "name"):
            if key in step:
                return str(step[key])
        return ""
    for attr in ("label", "name"):
        value = getattr(step, attr, None)
        if value is not None:
            return str(value)
    return ""
