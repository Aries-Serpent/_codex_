"""
Plugin registry discovery via Python entry points (PEP 621).

Entry point group used by default:  "codex_ml.plugins"

Public API:
    discover(group: str = "codex_ml.plugins") -> dict[str, object]
    get(name: str, group: str = "codex_ml.plugins") -> object
"""

from __future__ import annotations

from importlib import metadata
from typing import Dict

DEFAULT_GROUP = "codex_ml.plugins"


def discover(group: str = DEFAULT_GROUP) -> Dict[str, object]:
    """
    Return a mapping of {ep_name: loaded_object} for the given entry point group.
    Never raises: returns {} if the group is missing or any single load fails.
    """

    results: Dict[str, object] = {}
    try:
        eps = metadata.entry_points()
        # Newer Python exposes .select, but keep compatibility
        items = (
            eps.select(group=group)
            if hasattr(eps, "select")
            else [ep for ep in eps if ep.group == group]
        )
        for ep in items:
            try:
                results[ep.name] = ep.load()
            except Exception:
                # Best-effort: skip broken entry points
                continue
    except Exception:
        return {}
    return results


def get(name: str, group: str = DEFAULT_GROUP) -> object:
    """
    Load a single entry point object by name. Returns None if not found.
    """

    return discover(group).get(name)
