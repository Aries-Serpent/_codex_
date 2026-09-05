"""Codex bridge compatibility exports.

This module intentionally re-exports the repo-local GitHub client rather than
reaching into the legacy ``codex.*`` namespace. The repository uses a namespace
bridge for some migrated modules, but bridge-facing imports should stay pinned to
this package so they are not accidentally shadowed by an installed third-party
``codex`` package.
"""

from __future__ import annotations

# Prefer the in-repo implementation. Keep a compatibility fallback for the
# migrated ``aries_serpent_core.clients`` package if this module is imported from
# an environment where that package is installed without the bridge package.
try:
    from .github_client import (
        CACHE_DIR,
        OWNER,
        REPO,
        TOKEN,
        cache_get,
        cache_set,
        code_search,
        get_text,
        gh_get,
        list_branches,
        most_recent_branch,
    )
except ImportError:  # pragma: no cover - compatibility fallback only
    from aries_serpent_core.clients.github_client import (
        CACHE_DIR,
        OWNER,
        REPO,
        TOKEN,
        cache_get,
        cache_set,
        code_search,
        get_text,
        gh_get,
        list_branches,
        most_recent_branch,
    )

__all__: list[str] = [
    "CACHE_DIR",
    "OWNER",
    "REPO",
    "TOKEN",
    "cache_get",
    "cache_set",
    "code_search",
    "gh_get",
    "get_text",
    "list_branches",
    "most_recent_branch",
]
