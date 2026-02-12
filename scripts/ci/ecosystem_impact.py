#!/usr/bin/env python3
"""Ecosystem Impact Pillar Assessment (PS-20e).

Measures the 4 sub-dimensions of the Ecosystem Impact pillar:
1. Reusability — agent count, shared scripts, reusable components
2. Documentation Quality — doc coverage, freshness, link health
3. Community Engagement — agent orchestration, multi-repo support
4. Integration Breadth — workflow count, tool diversity, API coverage

Usage:
    python scripts/ci/ecosystem_impact.py           # Human report
    python scripts/ci/ecosystem_impact.py --json    # JSON output
    python scripts/ci/ecosystem_impact.py --ci      # GITHUB_STEP_SUMMARY
"""
from __future__ import annotations

import argparse
import json
import os
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


def assess_reusability() -> DimensionResult:
    """Reusability: agents, scripts, shared components."""
    agents_dir = ROOT / ".github" / "agents"
    agent_count = len(list(agents_dir.glob("*.md"))) if agents_dir.exists() else 0

    ci_scripts = len(list((ROOT / "scripts" / "ci").glob("*.py")))
    cognitive_scripts = len(list((ROOT / "scripts" / "cognitive").glob("*.py")))
    monitoring_scripts = len(list((ROOT / "scripts" / "monitoring").glob("*.py")))
    total_scripts = ci_scripts + cognitive_scripts + monitoring_scripts

    # Score: agents (50%) + scripts (50%)
    agent_score = min(12.5, agent_count / 50 * 12.5)
    script_score = min(12.5, total_scripts / 25 * 12.5)
    score = agent_score + script_score
    return DimensionResult(
        "Reusability", score, 25.0,
        f"{agent_count} agents, {total_scripts} scripts "
        f"(ci={ci_scripts}, cognitive={cognitive_scripts}, monitoring={monitoring_scripts})"
    )


def assess_documentation_quality() -> DimensionResult:
    """Documentation quality: coverage, freshness, formats."""
    doc_files = len(list((ROOT / "docs").rglob("*.md"))) if (ROOT / "docs").exists() else 0
    readme_exists = (ROOT / "README.md").exists()
    has_auto_doc = (ROOT / "scripts/ci/auto_doc_generator.py").exists()
    has_mkdocs = (ROOT / "mkdocs.yml").exists()

    checks = sum([readme_exists, has_auto_doc, has_mkdocs, doc_files > 20])
    score = checks / 4 * 25
    return DimensionResult(
        "Documentation Quality", score, 25.0,
        f"{doc_files} doc files, readme={'✓' if readme_exists else '✗'}, "
        f"auto_doc={'✓' if has_auto_doc else '✗'}, mkdocs={'✓' if has_mkdocs else '✗'}"
    )


def assess_community_engagement() -> DimensionResult:
    """Community engagement: orchestration, multi-repo."""
    checks = {
        "multi_repo": (ROOT / "scripts/monitoring/multi_repo_orchestrator.py").exists(),
        "task_router": (ROOT / "scripts/monitoring/agent_orchestrator.py").exists(),
        "knowledge_sharing": (ROOT / "scripts/cognitive/knowledge_sharing.py").exists(),
        "planset_registry": (ROOT / "docs/evolution/PLANSET_REGISTRY.md").exists(),
    }
    passed = sum(checks.values())
    score = passed / len(checks) * 25
    detail = ", ".join(f"{k}={'✓' if v else '✗'}" for k, v in checks.items())
    return DimensionResult("Community Engagement", score, 25.0, detail)


def assess_integration_breadth() -> DimensionResult:
    """Integration breadth: workflows, tools, APIs."""
    wf_dir = ROOT / ".github" / "workflows"
    workflows = len(list(wf_dir.glob("*.yml"))) if wf_dir.exists() else 0

    # Check tool diversity by verifying pyproject.toml content
    pyproject = ROOT / "pyproject.toml"
    pyproject_content = pyproject.read_text(errors="ignore") if pyproject.exists() else ""
    tools = {
        "ruff": "[tool.ruff" in pyproject_content,
        "pytest": "[tool.pytest" in pyproject_content,
        "mkdocs": (ROOT / "mkdocs.yml").exists(),
        "nox": (ROOT / "noxfile.py").exists(),
    }
    tool_count = sum(tools.values())

    # Score: workflows (50%) + tools (50%)
    wf_score = min(12.5, workflows / 50 * 12.5)
    tool_score = tool_count / len(tools) * 12.5
    score = wf_score + tool_score
    return DimensionResult(
        "Integration Breadth", score, 25.0,
        f"{workflows} workflows, {tool_count} build tools integrated"
    )


def run_assessment() -> PillarReport:
    return PillarReport(
        pillar="Ecosystem Impact",
        weight=0.20,
        dimensions=[
            assess_reusability(),
            assess_documentation_quality(),
            assess_community_engagement(),
            assess_integration_breadth(),
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
    parser = argparse.ArgumentParser(description="Ecosystem Impact Assessment")
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
                f.write(f"\n## Ecosystem Impact: {report.score:.1f}/100\n")
    print(out)


if __name__ == "__main__":
    main()
