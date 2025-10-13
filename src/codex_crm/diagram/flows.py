"""Helpers for constructing CRM flow diagrams."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

Edge = tuple[str, str]
StepLike = Any


def _step_to_label(step: StepLike) -> str:
    """Return a human-readable label for *step*.

    The CRM pipeline represents steps using lightweight containers (strings,
    dictionaries, or small objects).  When the object exposes a ``label`` or
    ``name`` attribute/key we prefer that over the raw ``repr`` to keep the
    diagram readable.
    """

    if isinstance(step, str):
        return step

    if isinstance(step, Mapping):
        for key in ("label", "name", "title", "id"):
            value = step.get(key)
            if value:
                return str(value)
        return str(dict(step))

    for attr in ("label", "name", "title", "id"):
        if hasattr(step, attr):
            value = getattr(step, attr)
            if value is not None:
                return str(value)

    return str(step)


def build_flow_edges(
    steps: Sequence[StepLike],
    *,
    start_label: str = "Start",
    close_label: str = "Close",
) -> tuple[list[Edge], str]:
    """Create ordered edges representing the CRM flow.

    Parameters
    ----------
    steps:
        Ordered collection describing each step in the CRM workflow.
    start_label, close_label:
        Labels used for the implicit ``Start`` and ``Close`` sentinel nodes.

    Returns
    -------
    tuple[list[Edge], str]
        A tuple containing the list of edges (represented as ``(source, target)``
        tuples) and the label of the last node that was connected.  The latter is
        useful for callers that wish to append additional terminal edges.
    """

    edges: list[Edge] = []
    prev = start_label

    if not steps:
        edges.append((start_label, close_label))
        prev = close_label
        return edges, prev

    for step in steps:
        current = _step_to_label(step)
        edges.append((prev, current))
        prev = current

    edges.append((prev, close_label))
    prev = close_label

    return edges, prev
