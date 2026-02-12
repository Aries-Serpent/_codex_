#!/usr/bin/env python3
"""Agent capability introspection.

Scans .github/agents/ directory for agent specification files and extracts
capability metadata. Provides a unified view of all agent capabilities,
tools, and responsibilities for the task router and orchestrator.

Usage::

    python scripts/monitoring/agent_introspection.py
    python scripts/monitoring/agent_introspection.py --json
    python scripts/monitoring/agent_introspection.py --capabilities security
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
AGENTS_DIR = REPO_ROOT / ".github" / "agents"

CATEGORY_KEYWORDS = {
    "ci_cd": ["ci", "workflow", "build", "pipeline", "deploy", "artifact"],
    "testing": ["test", "coverage", "qa", "mutation", "assertion"],
    "security": ["security", "vulnerability", "pii", "secret", "scanning"],
    "documentation": ["doc", "link", "freshness", "consolidat", "pages"],
    "configuration": ["config", "migration", "hydra", "validator"],
    "rag_ml": ["rag", "tensor", "model", "meta", "peft"],
    "repository": ["repository", "hygiene", "organiz", "reference", "cleanup"],
    "monitoring": ["monitor", "performance", "regression", "alert"],
}


def categorize_agent(name: str, content: str) -> str:
    """Categorize an agent based on its name and content."""
    text = (name + " " + content[:500]).lower()
    scores: dict[str, int] = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        scores[category] = sum(1 for kw in keywords if kw in text)
    best = max(scores, key=lambda k: scores[k])
    return best if scores[best] > 0 else "other"


def scan_agents() -> list[dict]:
    """Scan .github/agents/ for agent specifications."""
    agents: list[dict] = []

    if not AGENTS_DIR.exists():
        return agents

    for agent_file in sorted(AGENTS_DIR.iterdir()):
        if not agent_file.is_file():
            continue
        if agent_file.suffix not in (".md", ".yml", ".yaml"):
            continue
        if agent_file.name == "README.md":
            continue

        try:
            content = agent_file.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        name = agent_file.stem.replace("-", " ").replace("_", " ").replace(".agent", "")
        category = categorize_agent(name, content)

        # Extract purpose from first paragraph
        purpose = ""
        for line in content.split("\n"):
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and not stripped.startswith("---"):
                purpose = stripped[:200]
                break

        agents.append(
            {
                "name": name,
                "file": str(agent_file.relative_to(REPO_ROOT)),
                "category": category,
                "purpose": purpose,
                "size_bytes": len(content),
            }
        )

    return agents


def print_summary(agents: list[dict], filter_category: str | None = None) -> None:
    """Print agent summary table."""
    if filter_category:
        agents = [a for a in agents if a["category"] == filter_category]

    categories: dict[str, list[dict]] = {}
    for agent in agents:
        cat = agent["category"]
        categories.setdefault(cat, []).append(agent)

    print(f"Agent Introspection Report ({len(agents)} agents)")
    print("=" * 60)

    for cat in sorted(categories):
        print(f"\n## {cat.upper()} ({len(categories[cat])} agents)")
        for agent in categories[cat]:
            print(f"  - {agent['name']}")
            if agent["purpose"]:
                print(f"    Purpose: {agent['purpose'][:80]}")

    print(f"\nTotal: {len(agents)} agents across {len(categories)} categories")


def main() -> int:
    parser = argparse.ArgumentParser(description="Agent capability introspection")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--capabilities", type=str, help="Filter by category")
    args = parser.parse_args()

    agents = scan_agents()

    if args.json:
        output = {
            "total_agents": len(agents),
            "agents": agents,
            "categories": {},
        }
        for agent in agents:
            cat = agent["category"]
            output["categories"].setdefault(cat, 0)
            output["categories"][cat] += 1
        print(json.dumps(output, indent=2))
    else:
        print_summary(agents, args.capabilities)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
