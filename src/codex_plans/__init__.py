"""Codex planning package.

This module provides a namespace for repository planning artifacts used in
continuous improvement tasks. It intentionally remains lightweight to allow
packaging tools to include the plan documents alongside source code.
"""

from __future__ import annotations

from pathlib import Path

__all__ = ["list_plan_documents"]


def list_plan_documents(base_dir: Path | None = None) -> list[Path]:
    """Return available plan documents within the ``codex_plans`` package.

    Parameters
    ----------
    base_dir:
        Optional override for the root search directory. Defaults to the
        directory containing this module.

    Returns
    -------
    list[pathlib.Path]
        Sorted list of Markdown files representing execution plans.
    """

    root = base_dir or Path(__file__).resolve().parent
    return sorted(root.glob("*.md"))
