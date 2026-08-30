from __future__ import annotations

from services.ita.app.knowledge_base import KnowledgeBaseEntry, search_knowledge
from services.ita.app.models import KnowledgeSearchRequest


def test_knowledge_entry_score_is_normalized() -> None:
    entry = KnowledgeBaseEntry("Copilot bridge", "docs/a.md", ("copilot", "bridge"))
    score = entry.score("copilot")
    assert 0 <= score <= 1, "0 is not valid"


def test_search_knowledge_orders_and_limits_results() -> None:
    entries = [
        KnowledgeBaseEntry("alpha copilot", "a.md", ("copilot", "alpha")),
        KnowledgeBaseEntry("beta governance", "b.md", ("confirm", "dry_run")),
        KnowledgeBaseEntry("gamma setup", "c.md", ("ubuntu", "cli")),
    ]
    results = search_knowledge(KnowledgeSearchRequest(query="copilot", top_k=2), entries=entries)
    assert len(results) == 2, "Results must not be empty"
    assert results[0].score >= results[1].score, "score must be greater than zero"
    assert results[0].source == "a.md", "Result must not be empty"
