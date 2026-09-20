from __future__ import annotations

import argparse
import json
from pathlib import Path

from .query import query_search, query_table
from .utils import parse_common_args


def classify_objective(objective: str) -> str:
    low = objective.lower()
    if any(k in low for k in ["test", "validate", "check"]):
        return "validation"
    if any(k in low for k in ["migrate", "convert", "ingest"]):
        return "migration"
    if any(k in low for k in ["docs", "documentation", "readme"]):
        return "documentation"
    return "implementation"


def run_task_brief(repo_root: Path, objective: str) -> dict:
    intent = classify_objective(objective)
    hits = query_search(repo_root, objective, 20)
    actions = query_table(repo_root, "actions", 200)["rows"]
    open_actions = [a for a in actions if a.get("status") == "open"]
    blocked_actions = [a for a in actions if a.get("status") == "blocked"]
    docs = [h for h in hits.get("results", []) if h.get("entity_type") == "document"]
    return {
        "objective": objective,
        "classified_intent": intent,
        "relevant_records": hits.get("results", []),
        "related_documents": docs,
        "related_files": sorted({d.get("id") for d in docs}),
        "open_actions": open_actions,
        "blocked_actions": blocked_actions,
        "known_decisions": query_table(repo_root, "decisions", 100)["rows"],
        "known_requirements": query_table(repo_root, "requirements", 200)["rows"],
        "constraints": ["Use machine-readable policy", "Validate before/after rebuild"],
        "recommended_execution_sequence": [
            "get_agent_context",
            "search_docs",
            "get_related_context",
            "impact_analysis",
            "apply changes",
            "rebuild_indexes",
            "validate_docs",
        ],
        "done_definition": [
            "validation passes",
            "indexes rebuilt",
            "no unmanaged candidates for new files",
        ],
        "validation_commands": [
            "python -m tools.docs_agent.validate --json",
            "python -m tools.docs_agent.build_index --json",
            "python -m tools.docs_agent.query health --json",
            "python -m tools.docs_agent.no_unmanaged_candidates --json",
        ],
    }


def main() -> int:
    parser = parse_common_args(
        argparse.ArgumentParser(description="Generate structured task brief")
    )
    parser.add_argument("objective")
    args = parser.parse_args()
    print(json.dumps(run_task_brief(Path(args.repo_root), args.objective), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
