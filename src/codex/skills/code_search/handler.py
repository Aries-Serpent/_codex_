"""Handler for the code.search.extract built-in skill.

Searches the repository codebase for patterns matching the query and returns
matched snippets with file paths and line numbers.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).parents[5]
_DEFAULT_TOP_K = 10
_CONTEXT_LINES = 3
_PYTHON_GLOB = "**/*.py"


def run(payload: dict) -> dict:
    """Search codebase for *query* and return matched snippets.

    Parameters
    ----------
    payload : dict
        Expected keys:
        - ``query`` (str, required): search term or pattern.
        - ``top_k`` (int, optional): max results (default 10).
        - ``glob`` (str, optional): file glob (default ``**/*.py``).
        - ``root`` (str, optional): search root (default repo root).
        - ``case_sensitive`` (bool, optional): default False.

    Returns
    -------
    dict
        ``{"matches": [{"path": ..., "line": int, "snippet": str}]}``.
    """
    query: str = str(payload.get("query", "")).strip()
    if not query:
        return {"matches": [], "error": "query is required"}

    top_k: int = int(payload.get("top_k", _DEFAULT_TOP_K))
    glob_pattern: str = str(payload.get("glob", _PYTHON_GLOB))
    root = Path(payload.get("root", _REPO_ROOT))
    case_sensitive: bool = bool(payload.get("case_sensitive", False))

    flags = 0 if case_sensitive else re.IGNORECASE
    try:
        pattern = re.compile(query, flags)
    except re.error as exc:
        return {"matches": [], "error": f"Invalid regex pattern: {exc}"}

    matches: list[dict] = []
    for py_file in sorted(root.glob(glob_pattern)):
        if "__pycache__" in str(py_file):
            continue
        try:
            lines = py_file.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue

        for lineno, line in enumerate(lines, start=1):
            if not pattern.search(line):
                continue
            start = max(0, lineno - 1 - _CONTEXT_LINES)
            end = min(len(lines), lineno + _CONTEXT_LINES)
            snippet = "\n".join(
                f"{start + i + 1:4}: {lines[start + i]}" for i in range(end - start)
            )
            matches.append({
                "path": str(py_file.relative_to(_REPO_ROOT)),
                "line": lineno,
                "snippet": snippet,
            })
            if len(matches) >= top_k:
                return {"matches": matches, "total_found": len(matches)}

    return {"matches": matches, "total_found": len(matches)}
