# src/codex_ml/analysis/providers.py
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict


@dataclass
class SearchResult:
    where: str
    snippet: str
    meta: dict


class SearchProvider:
    def search(self, query: str) -> List[dict]:  # pragma: no cover - interface
        raise NotImplementedError


class InternalRepoSearch(SearchProvider):
    def __init__(self, root: Path) -> None:
        self.root = root

    def search(self, query: str) -> List[dict]:
        out: List[dict] = []
        import glob
        import re

        pat = re.compile(re.escape(query), re.I)
        for path in glob.glob(str(self.root / "**/*.py"), recursive=True):
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    for i, line in enumerate(f, 1):
                        if pat.search(line):
                            out.append({"where": path, "line": i, "snippet": line.strip()})
            except Exception:
                pass
        return out


class ExternalWebSearch(SearchProvider):
    def __init__(self) -> None:
        pass

    def search(self, query: str) -> List[dict]:  # pragma: no cover - disabled
        # Disabled by default in offline policy. Placeholder only.
        return [{"disabled": True, "query": query}]
