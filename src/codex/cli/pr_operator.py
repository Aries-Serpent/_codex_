"""Compatibility wrapper for the legacy ``codex.cli.pr_operator`` module."""

from aries_serpent_core.cli.pr_operator import (  # noqa: F401
    DEFAULT_LABELS,
    PRConfig,
    PRContent,
    PROperator,
    PRResult,
    _generate_pr_body,
    _sanitize_branch_name,
)

__all__ = [
    "DEFAULT_LABELS",
    "PRConfig",
    "PRContent",
    "PROperator",
    "PRResult",
    "_generate_pr_body",
    "_sanitize_branch_name",
]
