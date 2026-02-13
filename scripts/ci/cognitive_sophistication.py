#!/usr/bin/env python3
"""Cognitive Sophistication Pillar Assessment (PS-20c).

Measures the 4 sub-dimensions of the Cognitive Sophistication pillar:
1. Self-Awareness — dashboard, trend tracking, healing loop
2. Adaptive Learning — knowledge transfer, sharing, context optimizer
3. Pattern Recognition — knowledge base entries and categories
4. Decision Quality — AAIS history progression and velocity

Usage:
    python scripts/ci/cognitive_sophistication.py           # Human report
    python scripts/ci/cognitive_sophistication.py --json    # JSON output
    python scripts/ci/cognitive_sophistication.py --ci      # GITHUB_STEP_SUMMARY
"""
from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


@dataclass
class DimensionResult:
    name: str
    score: float
    max_score: float
    details: str


@dataclass
class PillarReport:
    pillar: str
    weight: float
    dimensions: list[DimensionResult]

    @property
    def score(self) -> float:
        if not self.dimensions:
            return 0.0
        return sum(d.score for d in self.dimensions) / sum(
            d.max_score for d in self.dimensions
        ) * 100

    def to_dict(self) -> dict:
        return {
            "pillar": self.pillar,
            "weight": self.weight,
            "score": round(self.score, 1),
            "dimensions": [asdict(d) for d in self.dimensions],
        }


def assess_self_awareness() -> DimensionResult:
    """Cognitive self-awareness: dashboard, trend, healing."""
    tools = {
        "dashboard": (ROOT / ".codex/cognitive_brain/dashboard.md").exists(),
        "trend_analysis": (ROOT / "scripts/cognitive/trend_analysis.py").exists(),
        "healing_loop": (ROOT / "scripts/cognitive/healing_loop.py").exists(),
        "introspection": (ROOT / "scripts/monitoring/agent_introspection.py").exists(),
    }
    passed = sum(tools.values())
    score = passed / len(tools) * 25
    detail = ", ".join(f"{k}={'✓' if v else '✗'}" for k, v in tools.items())
    return DimensionResult("Self-Awareness", score, 25.0, detail)


def assess_adaptive_learning() -> DimensionResult:
    """Adaptive learning: knowledge transfer, sharing, context optimizer."""
    tools = {
        "knowledge_transfer": (ROOT / "scripts/cognitive/knowledge_transfer.py").exists(),
        "knowledge_sharing": (ROOT / "scripts/cognitive/knowledge_sharing.py").exists(),
        "context_optimizer": (ROOT / "scripts/cognitive/context_window_optimizer.py").exists(),
    }
    passed = sum(tools.values())
    score = passed / len(tools) * 25
    detail = ", ".join(f"{k}={'✓' if v else '✗'}" for k, v in tools.items())
    return DimensionResult("Adaptive Learning", score, 25.0, detail)


def assess_pattern_recognition() -> DimensionResult:
    """Pattern recognition: knowledge base size and diversity."""
    kb_file = ROOT / "scripts" / "cognitive" / "knowledge_sharing.py"
    entries = 0
    categories = set()
    if kb_file.exists():
        content = kb_file.read_text(errors="ignore")
        # Count KnowledgeEntry instances (excluding the class def line)
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("KnowledgeEntry(") and not stripped.startswith("class "):
                entries += 1
        # Extract categories from VALID_CATEGORIES or inline strings
        for m in re.finditer(r'"(pattern|convention|tool|architecture|ci|testing|security)"', content):
            categories.add(m.group(1))
    # Score based on entries and category diversity
    entry_score = min(12.5, entries / 15 * 12.5)
    cat_score = min(12.5, len(categories) / 7 * 12.5)
    score = entry_score + cat_score
    return DimensionResult(
        "Pattern Recognition", score, 25.0,
        f"{entries} patterns across {len(categories)} categories"
    )


def assess_decision_quality() -> DimensionResult:
    """Decision quality: AAIS progression velocity."""
    trend_file = ROOT / "scripts" / "cognitive" / "trend_analysis.py"
    milestones = 0
    if trend_file.exists():
        content = trend_file.read_text(errors="ignore")
        milestones = content.count('"version"')
        if milestones == 0:
            milestones = content.count("version")
    # Score based on progression milestones (7+ = perfect)
    score = min(25.0, milestones / 7 * 25)
    return DimensionResult(
        "Decision Quality", score, 25.0,
        f"{milestones} AAIS milestones tracked"
    )


def run_assessment() -> PillarReport:
    return PillarReport(
        pillar="Cognitive Sophistication",
        weight=0.30,
        dimensions=[
            assess_self_awareness(),
            assess_adaptive_learning(),
            assess_pattern_recognition(),
            assess_decision_quality(),
        ],
    )


def format_report(report: PillarReport) -> str:
    lines = [
        f"═══ {report.pillar} Pillar Assessment ═══",
        f"Weight: {report.weight * 100:.0f}%",
        f"Score: {report.score:.1f}/100",
        "",
    ]
    for d in report.dimensions:
        pct = d.score / d.max_score if d.max_score > 0 else 0
        bar = "█" * int(pct * 20) + "░" * (20 - int(pct * 20))
        lines.append(f"  {d.name}: {d.score:.1f}/{d.max_score:.1f} {bar}")
        lines.append(f"    {d.details}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Cognitive Sophistication Assessment")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output", type=str)
    parser.add_argument("--ci", action="store_true")
    args = parser.parse_args()

    report = run_assessment()
    out = json.dumps(report.to_dict(), indent=2) if args.json else format_report(report)

    if args.output:
        Path(args.output).write_text(out)
    if args.ci:
        summary = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary:
            with open(summary, "a") as f:
                f.write(f"\n## Cognitive Sophistication: {report.score:.1f}/100\n")
    print(out)


if __name__ == "__main__":
    main()
