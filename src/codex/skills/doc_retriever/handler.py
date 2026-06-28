"""Handler for the doc.retriever.core built-in skill.

Retrieves embedded documentation chunks matching a query.  In production this
should be wired to the RAG retriever (``codex.rag``).  The built-in
implementation performs a lightweight full-text grep over markdown files in the
repository and returns the top-k matching excerpts.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).parents[4]
_DOCS_GLOB = "docs/**/*.md"
_DEFAULT_TOP_K = 5
_EXCERPT_CHARS = 400


def run(payload: dict[str, Any]) -> dict[str, Any]:
    """Retrieve document chunks matching the query in *payload*.

    Parameters
    ----------
    payload : dict
        Expected keys:
        - ``query`` (str, required): search term(s).
        - ``top_k`` (int, optional): max results (default 5).
        - ``doc_root`` (str, optional): override docs root path.

    Returns
    -------
    dict
        ``{"results": [{"path": ..., "excerpt": ..., "score": ...}]}``.
    """
    query: str = str(payload.get("query", "")).strip()
    if not query:
        return {"results": [], "error": "query is required"}

    top_k: int = int(payload.get("top_k", _DEFAULT_TOP_K))
    doc_root = Path(payload.get("doc_root", _REPO_ROOT))

    terms = [re.escape(t) for t in query.split() if t]
    pattern = re.compile("|".join(terms), re.IGNORECASE) if terms else None

    results: list[dict[str, Any]] = []
    for md_file in sorted(doc_root.glob(_DOCS_GLOB)):
        try:
            text = md_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        if pattern is None or not pattern.search(text):
            continue

        # Score: number of query term hits
        score = len(pattern.findall(text))
        # Build excerpt around first hit
        match = pattern.search(text)
        if match:
            start = max(0, match.start() - 100)
            end = min(len(text), match.end() + _EXCERPT_CHARS)
            excerpt = text[start:end].replace("\n", " ").strip()
        else:
            excerpt = text[:_EXCERPT_CHARS].replace("\n", " ").strip()

        results.append(
            {
                "path": _safe_relative(md_file, doc_root),
                "excerpt": excerpt,
                "score": score,
            }
        )

    results.sort(key=lambda r: r["score"], reverse=True)
    return {"results": results[:top_k], "total_found": len(results)}


def _safe_relative(path: Path, base: Path) -> str:
    """Return *path* relative to *base* (or *_REPO_ROOT*), falling back to str."""
    for anchor in (base, _REPO_ROOT):
        try:
            return str(path.relative_to(anchor))
        except ValueError:
            continue
    return str(path)
