"""In-memory snippets used to satisfy the knowledge search endpoint."""

from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Iterable, List

from .models import KnowledgeSearchRequest, KnowledgeSearchResult


@dataclass(frozen=True)
class KnowledgeBaseEntry:
    snippet: str
    source: str
    keywords: tuple[str, ...]

    def score(self, query: str) -> float:
        tokens = " ".join(self.keywords)
        baseline = SequenceMatcher(a=query.lower(), b=self.snippet.lower()).ratio()
        keyword_boost = SequenceMatcher(a=query.lower(), b=tokens).ratio()
        return round((baseline + keyword_boost) / 2, 4)


_DEFAULT_ENTRIES: List[KnowledgeBaseEntry] = [
    KnowledgeBaseEntry(
        snippet="Use the Internal Tools API to consolidate Codex and Copilot automation via a single audited backend.",
        source="docs/bridge/overview.md",
        keywords=("codex", "copilot", "bridge", "internal tools api"),
    ),
    KnowledgeBaseEntry(
        snippet="Always forward GitHub requests through the ITA to enforce confirm=true and dry_run defaults.",
        source="docs/bridge/governance.md",
        keywords=("confirm", "dry_run", "github", "ita"),
    ),
    KnowledgeBaseEntry(
        snippet="Follow the Ubuntu CLI guide to wire Codex and Copilot tooling into the shared bridge scripts.",
        source="docs/bridge/ubuntu_cli.md",
        keywords=("ubuntu", "cli", "setup", "codex", "copilot"),
    ),
    KnowledgeBaseEntry(
        snippet="Register the GitHub App with read contents and write pull_requests scopes before enabling mutation flows.",
        source="copilot/app/README.md",
        keywords=("github app", "permissions", "pull requests"),
    ),
]


def search_knowledge(
    request: KnowledgeSearchRequest, *, entries: Iterable[KnowledgeBaseEntry] | None = None
) -> List[KnowledgeSearchResult]:
    dataset = list(entries or _DEFAULT_ENTRIES)
    scored = [(entry.score(request.query), entry) for entry in dataset]
    scored.sort(key=lambda item: item[0], reverse=True)
    top = [result for result in scored[: request.top_k] if result[0] > 0]
    return [
        KnowledgeSearchResult(snippet=entry.snippet, source=entry.source, score=score)
        for score, entry in top
    ]


__all__ = ["KnowledgeBaseEntry", "search_knowledge"]
