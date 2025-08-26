"""Pluggable search providers used by codex.

This module supplies a minimal plugin architecture with a registry that can
combine multiple search backends. It is intentionally lightweight so that new
providers can be added without altering existing code. The implementation
follows the repurpose/enhance/fallback strategy: each provider gracefully
handles errors and returns an empty list on failure.
"""

from __future__ import annotations

import abc
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


class SearchProvider(abc.ABC):
    """Abstract base class for search providers."""

    @abc.abstractmethod
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search for *query* and return a list of results."""


@dataclass
class InternalRepoSearch(SearchProvider):
    """Ripgrep-backed search inside the repository.

    Parameters
    ----------
    root:
        Directory to search. Defaults to the current working directory.
    """

    root: Path = Path.cwd()

    def search(self, query: str) -> List[Dict[str, Any]]:
        try:
            completed = subprocess.run(
                ["rg", "--json", query, str(self.root)],
                check=True,
                capture_output=True,
                text=True,
            )
        except Exception:
            return []

        results: List[Dict[str, Any]] = []
        for line in completed.stdout.splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("type") == "match":
                data = event.get("data", {})
                path = data.get("path", {}).get("text")
                line_text = data.get("lines", {}).get("text", "").rstrip("\n")
                if path:
                    results.append({"path": path, "line": line_text})
        return results


@dataclass
class ExternalWebSearch(SearchProvider):
    """Best-effort web search provider using DuckDuckGo.

    Network failures are caught and surfaced as an empty result set, allowing
    the rest of the system to continue operating.
    """

    def search(self, query: str) -> List[Dict[str, Any]]:
        import urllib.error
        import urllib.parse
        import urllib.request

        url = (
            "https://duckduckgo.com/?q="
            + urllib.parse.quote(query)
            + "&format=json&no_redirect=1&no_html=1"
        )
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.load(response)
        except (urllib.error.URLError, ValueError):
            return []

        results: List[Dict[str, Any]] = []
        for topic in data.get("RelatedTopics", []):
            if isinstance(topic, dict) and "Text" in topic and "FirstURL" in topic:
                results.append({"text": topic["Text"], "url": topic["FirstURL"]})
        return results


class SearchRegistry:
    """Registry aggregating search providers."""

    def __init__(self, enable_external: bool = False, root: Optional[Path] = None):
        self.providers: List[SearchProvider] = [
            InternalRepoSearch(root=root or Path.cwd())
        ]
        if enable_external:
            self.providers.append(ExternalWebSearch())

    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search all providers and concatenate their results."""

        results: List[Dict[str, Any]] = []
        for provider in self.providers:
            try:
                results.extend(provider.search(query))
            except Exception:
                # Each provider is responsible for handling its own errors. If
                # an unexpected exception bubbles up we swallow it here so that
                # other providers still run.
                continue
        return results
