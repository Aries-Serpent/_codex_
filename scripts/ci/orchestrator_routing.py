"""
scripts/ci/orchestrator_routing.py
Phase 4 — Dynamic orchestrator→specialist routing via FAISS capability search.

Uses Phase 3 FAISS corpus to match task descriptions to agent capability_tags
in AGENT_REGISTRY.yaml.  Returns the best-matching specialist agent ID.

Usage (import):
  from scripts.ci.orchestrator_routing import select_specialist
  agent_id = select_specialist("fix failing CI tests and diagnose import errors")

Usage (CLI):
  python scripts/ci/orchestrator_routing.py "fix failing CI tests"
  python scripts/ci/orchestrator_routing.py --top-k 3 "generate documentation"
"""

from __future__ import annotations

import logging
import pathlib
from typing import Any

import yaml

logger = logging.getLogger(__name__)

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
REGISTRY_PATH = REPO_ROOT / ".github" / "agents" / "AGENT_REGISTRY.yaml"

# Safe default when no match found
_DEFAULT_AGENT = "cognitive-brain-cli-agent"


def _load_registry() -> list[dict[str, Any]]:
    """Load active agents from AGENT_REGISTRY.yaml."""
    if not REGISTRY_PATH.exists():
        return []
    data = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    return [a for a in data.get("agents", []) if a.get("status") == "active"]


def select_specialist(task_description: str, top_k: int = 1) -> str:
    """
    Dynamically route a task description to the best-matching specialist agent.

    Strategy (in priority order):
    1. FAISS semantic search over corpus (Phase 3 index required)
    2. Capability-tag keyword match against AGENT_REGISTRY.yaml
    3. Safe default: cognitive-brain-cli-agent

    Returns the agent ID string (e.g. "ci-testing-agent").
    """
    # Strategy 1: FAISS semantic search (requires Phase 3 index)
    try:
        from scripts.ci.query_corpus import query as corpus_query  # type: ignore[import]

        results = corpus_query(
            f"agent capable of: {task_description}",
            top_k=top_k * 3,  # over-fetch, then filter to agent sources
        )
        agent_results = [
            r
            for r in results
            if ".github/agents/" in r.get("source", "") or "AGENT_REGISTRY" in r.get("source", "")
        ]
        if agent_results:
            raw = agent_results[0]["source"].split("/")[-1]
            agent_id = raw.replace(".md", "").replace(".yaml", "").replace(".yml", "")
            if top_k == 1:
                return agent_id
            return "\n".join(
                r["source"].split("/")[-1].replace(".md", "") for r in agent_results[:top_k]
            )
    except Exception:  # noqa: BLE001
        logger.debug("Suppressed exception in handler", exc_info=True)
    # Strategy 2: Keyword match against capability_tags in registry
    agents = _load_registry()
    query_words = set(task_description.lower().split())
    scored: list[tuple[int, str]] = []

    for agent in agents:
        tags = [t.lower() for t in agent.get("capability_tags", [])]
        capabilities = [c.lower() for c in agent.get("capabilities", [])]
        all_terms = tags + capabilities + [agent.get("id", "").lower()]
        score = sum(1 for word in query_words if any(word in term for term in all_terms))
        if score > 0:
            scored.append((score, agent["id"]))

    if scored:
        scored.sort(key=lambda x: -x[0])
        if top_k == 1:
            return scored[0][1]
        return "\n".join(s[1] for s in scored[:top_k])

    # Strategy 3: Safe default
    return _DEFAULT_AGENT


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(
        description="Route a task description to the best-matching specialist agent"
    )
    ap.add_argument("task", nargs="+", help="Task description")
    ap.add_argument("--top-k", type=int, default=1, help="Return top-k agent IDs (default: 1)")
    args = ap.parse_args()

    task_text = " ".join(args.task)
    result = select_specialist(task_text, top_k=args.top_k)
    print(f"Task: {task_text!r}")
    print(f"Best match(es):\n{result}")
