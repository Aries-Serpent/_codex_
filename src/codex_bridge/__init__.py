"""
Codex Bridge Module - Adapters connecting Codex to external runtimes and services.

This module provides backward compatibility imports for GitHub client operations.
The actual implementations have been moved to src/codex/clients/ for P19 shadow
import resolution.

Usage:
    from codex_bridge.github_client import list_branches, get_text

    # Or via the main codex namespace:
    from codex.clients import list_branches, get_text
"""

from __future__ import annotations

# Backward compatibility imports (P19 shadow import fix)
# These modules have been moved to src/codex/clients/
from codex.clients.github_client import (
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
