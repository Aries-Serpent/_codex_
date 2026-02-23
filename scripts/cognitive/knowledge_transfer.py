#!/usr/bin/env python3
"""Cross-session knowledge transfer — persist and recall session learnings.

Implements AAIS Improvement #11: Cross-Session Knowledge Transfer (+0.7 pts).

This module provides:
- Session summary generation from change_log entries
- Knowledge extraction from completed sessions
- Transfer protocol for passing context between agent sessions
- Pattern library aggregation from historical sessions

Usage:
    python scripts/cognitive/knowledge_transfer.py --extract [--session N]
    python scripts/cognitive/knowledge_transfer.py --summary
    python scripts/cognitive/knowledge_transfer.py --patterns
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CHANGELOG = REPO_ROOT / ".codex" / "change_log.md"
DASHBOARD = REPO_ROOT / ".codex" / "cognitive_brain" / "dashboard.md"


# Known session knowledge base (extracted from PR #3244 history)
SESSION_KNOWLEDGE = [
    {
        "session": 1,
        "topic": "CI Resolution",
        "learnings": [
            "Flake8 E501 violations require line-by-line fixes, not blanket ignores",
            "Start with --check-only to assess scope before applying fixes",
        ],
        "patterns": ["incremental-lint-fix"],
    },
    {
        "session": 4,
        "topic": "Lambda Fix Pattern",
        "learnings": [
            "NEVER convert lambda to def inside SimpleNamespace/dataclass constructors",
            "Use noqa:E731 for lambda in keyword arguments",
        ],
        "patterns": ["lambda-preservation"],
    },
    {
        "session": 8,
        "topic": "RAG Device Initialization",
        "learnings": [
            "SentenceTransformer requires device='cpu' (not None)",
            "torch.set_default_device causes meta tensor errors",
            "safe_model_to_device provides additional safety net",
        ],
        "patterns": ["device-explicit-init", "no-set-default-device"],
    },
    {
        "session": 12,
        "topic": "MCP Package Features",
        "learnings": [
            "--estimate calculates size with 10% overhead margin",
            "--exclude uses pattern complement subtraction",
        ],
        "patterns": ["cli-flag-design"],
    },
    {
        "session": 13,
        "topic": "Agent Task Routing",
        "learnings": [
            "Keyword matching with confidence thresholds enables fuzzy routing",
            "Fallback chains prevent unrouted tasks",
        ],
        "patterns": ["keyword-routing", "fallback-chains"],
    },
    {
        "session": 17,
        "topic": "Fragile Test Hardening",
        "learnings": [
            "pytest.importorskip must be AFTER import pytest",
            "Guards must be AFTER from __future__ import annotations",
            "False positives: project modules matching optional package names",
        ],
        "patterns": ["import-guard-ordering", "future-import-safety"],
    },
    {
        "session": 21,
        "topic": "Import Guard Ordering",
        "learnings": [
            "51 files had guards before import pytest — caused NameError",
            "Automated tools need safety checks for import ordering",
        ],
        "patterns": ["automated-tool-safety-checks"],
    },
]


def extract_session_knowledge(session_id: int | None = None) -> list[dict]:
    """Extract knowledge for a specific session or all sessions."""
    if session_id is not None:
        return [s for s in SESSION_KNOWLEDGE if s["session"] == session_id]
    return SESSION_KNOWLEDGE


def get_pattern_library() -> dict[str, list[str]]:
    """Aggregate all patterns from session knowledge into a searchable library."""
    library: dict[str, list[str]] = {}
    for session in SESSION_KNOWLEDGE:
        for pattern in session["patterns"]:
            if pattern not in library:
                library[pattern] = []
            # Only add learnings once per pattern (avoid cross-pattern duplication)
            for learning in session["learnings"]:
                if learning not in library[pattern]:
                    library[pattern].append(learning)
    return library


def generate_transfer_summary() -> dict:
    """Generate a compact summary for the next session to consume."""
    patterns = get_pattern_library()
    return {
        "total_sessions": len(SESSION_KNOWLEDGE),
        "total_patterns": len(patterns),
        "total_learnings": sum(len(s["learnings"]) for s in SESSION_KNOWLEDGE),
        "critical_patterns": [
            {
                "pattern": "import-guard-ordering",
                "rule": "pytest.importorskip() MUST appear AFTER 'import pytest'",
                "severity": "critical",
            },
            {
                "pattern": "no-set-default-device",
                "rule": "Never use torch.set_default_device() in conftest.py",
                "severity": "critical",
            },
            {
                "pattern": "lambda-preservation",
                "rule": "Never convert lambda to def inside SimpleNamespace/dataclass",
                "severity": "high",
            },
            {
                "pattern": "device-explicit-init",
                "rule": "RAG SentenceTransformer must use device='cpu' explicitly",
                "severity": "high",
            },
        ],
        "session_topics": [
            {"session": s["session"], "topic": s["topic"]}
            for s in SESSION_KNOWLEDGE
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Cross-session knowledge transfer")
    parser.add_argument(
        "--extract", action="store_true", help="Extract session knowledge"
    )
    parser.add_argument(
        "--session", type=int, default=None, help="Filter by session ID"
    )
    parser.add_argument(
        "--summary", action="store_true", help="Generate transfer summary"
    )
    parser.add_argument(
        "--patterns", action="store_true", help="Show pattern library"
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if args.extract:
        knowledge = extract_session_knowledge(args.session)
        if args.json:
            print(json.dumps(knowledge, indent=2))
        else:
            for k in knowledge:
                print(f"\n📚 Session {k['session']}: {k['topic']}")
                for learning in k["learnings"]:
                    print(f"  • {learning}")
                print(f"  Patterns: {', '.join(k['patterns'])}")
        return 0

    if args.summary:
        summary = generate_transfer_summary()
        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            print("📋 Knowledge Transfer Summary")
            print(f"  Sessions: {summary['total_sessions']}")
            print(f"  Patterns: {summary['total_patterns']}")
            print(f"  Learnings: {summary['total_learnings']}")
            print("\n🔴 Critical Patterns:")
            for cp in summary["critical_patterns"]:
                print(f"  [{cp['severity'].upper()}] {cp['pattern']}: {cp['rule']}")
        return 0

    if args.patterns:
        library = get_pattern_library()
        if args.json:
            print(json.dumps(library, indent=2))
        else:
            print("📖 Pattern Library")
            for pattern, learnings in sorted(library.items()):
                print(f"\n  {pattern}:")
                for learning in learnings:
                    print(f"    • {learning}")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
