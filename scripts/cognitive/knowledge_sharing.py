#!/usr/bin/env python3
"""Cross-team knowledge sharing — structured knowledge base for AI agents.

Manages a repository of learnings, patterns, and conventions that can be
shared across teams and sessions.

Usage:
    python scripts/cognitive/knowledge_sharing.py              # List entries
    python scripts/cognitive/knowledge_sharing.py --json       # JSON output
    python scripts/cognitive/knowledge_sharing.py --export kb.json
    python scripts/cognitive/knowledge_sharing.py --category pattern
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

CATEGORIES = [
    "pattern",
    "convention",
    "tool",
    "architecture",
    "ci",
    "testing",
    "security",
]


VALID_SEVERITIES = ["critical", "high", "medium", "low"]


@dataclass
class KnowledgeEntry:
    """A single knowledge item."""

    id: str
    title: str
    category: str
    severity: str  # critical, high, medium, low
    description: str
    evidence: str = ""
    session: str = ""

    def __post_init__(self) -> None:
        if self.severity not in VALID_SEVERITIES:
            msg = f"Invalid severity {self.severity!r}, must be one of {VALID_SEVERITIES}"
            raise ValueError(msg)


@dataclass
class KnowledgeBase:
    """Collection of knowledge entries."""

    entries: list[KnowledgeEntry] = field(default_factory=list)
    version: str = "1.0.0"

    def add(self, entry: KnowledgeEntry) -> None:
        self.entries.append(entry)

    def by_category(self, cat: str) -> list[KnowledgeEntry]:
        return [e for e in self.entries if e.category == cat]

    def by_severity(self, sev: str) -> list[KnowledgeEntry]:
        return [e for e in self.entries if e.severity == sev]

    def export_json(self) -> str:
        return json.dumps(
            {"version": self.version, "entries": [asdict(e) for e in self.entries]},
            indent=2,
        )

    @classmethod
    def from_json(cls, data: str) -> KnowledgeBase:
        d = json.loads(data)
        kb = cls(version=d.get("version", "1.0.0"))
        for e in d.get("entries", []):
            kb.add(KnowledgeEntry(**e))
        return kb


def build_default_kb() -> KnowledgeBase:
    """Build the default knowledge base from codex conventions."""
    kb = KnowledgeBase()
    entries = [
        KnowledgeEntry(
            "KS-001", "Import guard ordering", "pattern", "critical",
            "pytest.importorskip() must appear AFTER import pytest",
            ".codex/scripts/add_import_guards.py", "Session 21",
        ),
        KnowledgeEntry(
            "KS-002", "Torch stub safety", "pattern", "critical",
            "Use getattr(torch, attr, default) — never direct attribute access",
            "src/codex_ml/checkpoint.py, seed_manager.py", "Session 29",
        ),
        KnowledgeEntry(
            "KS-003", "RAG model loading", "pattern", "high",
            "Use safe_load_sentence_transformer() from _model_utils.py",
            "src/codex/rag/_model_utils.py", "Session 25",
        ),
        KnowledgeEntry(
            "KS-004", "CodeQL empty except", "convention", "high",
            "Comment must be on the except line, not the pass line",
            "conftest.py:1029,1185,1211", "Session 24",
        ),
        KnowledgeEntry(
            "KS-005", "CodeQL mixed import", "convention", "high",
            "Don't mix import X and from X import Y — use attribute access",
            "test_tiny_overfit.py", "Session 24",
        ),
        KnowledgeEntry(
            "KS-006", "CacheManager integration", "ci", "medium",
            "Every workflow needs generate_cache_keys.py --health step",
            ".github/workflows/*.yml", "Session 28",
        ),
        KnowledgeEntry(
            "KS-007", "Future import ordering", "pattern", "critical",
            "Guards must appear AFTER from __future__ import annotations",
            ".codex/scripts/add_import_guards.py", "Session 17",
        ),
        KnowledgeEntry(
            "KS-008", "JSON serialization safety", "pattern", "high",
            "Use json.dumps(data, default=str) for provenance data",
            "src/codex_ml/utils/provenance.py", "Session 29",
        ),
        KnowledgeEntry(
            "KS-009", "Import shadowing prevention", "convention", "high",
            "Use sys.path.append() not insert(0) to avoid shadowing",
            "src/cli.py", "Session 29",
        ),
        KnowledgeEntry(
            "KS-010", "No torch.set_default_device", "pattern", "critical",
            "Never use torch.set_default_device() — causes meta tensor errors",
            "tests/conftest.py", "Session 12",
        ),
        KnowledgeEntry(
            "KS-011", "Nox test session", "tool", "medium",
            "Must pip install -e . --no-deps before running pytest",
            "noxfile.py", "Session 13",
        ),
        KnowledgeEntry(
            "KS-012", "Healing loop convergence", "ci", "medium",
            "healing_loop.py supports --max-iterations 3 for multi-cycle",
            "scripts/cognitive/healing_loop.py", "Session 20",
        ),
        KnowledgeEntry(
            "KS-013", "Conftest torch version", "pattern", "high",
            "Use getattr(torch, '__version__', 'unknown') with except (ImportError, AttributeError)",
            "tests/conftest.py:76-78", "Session 12",
        ),
        KnowledgeEntry(
            "KS-014", "E731 lambda fix", "convention", "high",
            "Never convert lambda inside SimpleNamespace() or function args — use noqa",
            "Multiple test files", "Session 4",
        ),
        KnowledgeEntry(
            "KS-015", "Windows filenames", "convention", "medium",
            "Use windows_safe_timestamp() — no colons in filenames",
            "codex.utils.path_utils", ".codex/archive/deprecated/AGENTS.md",
        ),
    ]
    for e in entries:
        kb.add(e)
    return kb


def main() -> None:
    parser = argparse.ArgumentParser(description="Knowledge Sharing Manager")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--export", help="Export to file")
    parser.add_argument("--category", help="Filter by category")
    parser.add_argument("--severity", help="Filter by severity")
    args = parser.parse_args()

    kb = build_default_kb()

    entries = kb.entries
    if args.category:
        entries = kb.by_category(args.category)
    if args.severity:
        entries = [e for e in entries if e.severity == args.severity]

    if args.json or args.export:
        filtered_kb = KnowledgeBase(entries=entries)
        output = filtered_kb.export_json()
        if args.export:
            Path(args.export).write_text(output)
            print(f"Exported {len(entries)} entries to {args.export}")
        else:
            print(output)
    else:
        print(f"Knowledge Base v{kb.version} — {len(entries)} entries\n")
        for e in entries:
            sev_icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
            print(f"  {sev_icon.get(e.severity, '⚪')} [{e.id}] {e.title} ({e.category})")
            print(f"    {e.description}")
        print(f"\nCategories: {', '.join(CATEGORIES)}")

    sys.exit(0)


if __name__ == "__main__":
    main()
