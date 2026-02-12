#!/usr/bin/env python3
"""Operational Maturity Pillar Assessment (PS-20d).

Measures the 4 sub-dimensions of the Operational Maturity pillar:
1. Automation Level — CacheManager coverage, healing loop, CI integration
2. Reliability — workflow health monitoring, error handling patterns
3. Observability — dashboard, metrics scripts, artifact tracking
4. Incident Response — healing loop iterations, self-healing workflow

Usage:
    python scripts/ci/operational_maturity.py           # Human report
    python scripts/ci/operational_maturity.py --json    # JSON output
    python scripts/ci/operational_maturity.py --ci      # GITHUB_STEP_SUMMARY
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


def assess_automation_level() -> DimensionResult:
    """Automation: CacheManager coverage, healing, CI scripts."""
    wf_dir = ROOT / ".github" / "workflows"
    workflows = len(list(wf_dir.glob("*.yml"))) if wf_dir.exists() else 0
    cache_count = 0
    if wf_dir.exists():
        for wf in wf_dir.glob("*.yml"):
            if "generate_cache_keys.py" in wf.read_text(errors="ignore"):
                cache_count += 1
    cache_pct = (cache_count / max(workflows, 1)) * 100

    ci_scripts = len(list((ROOT / "scripts" / "ci").glob("*.py")))
    has_healing = (ROOT / "scripts/cognitive/healing_loop.py").exists()

    # Score: cache coverage (40%) + ci scripts (30%) + healing (30%)
    cache_score = cache_pct / 100 * 10.0
    script_score = min(7.5, ci_scripts / 15 * 7.5)
    healing_score = 7.5 if has_healing else 0.0
    score = min(25.0, cache_score + script_score + healing_score)
    return DimensionResult(
        "Automation Level", min(score, 25.0), 25.0,
        f"CacheManager {cache_count}/{workflows} ({cache_pct:.0f}%), "
        f"{ci_scripts} CI scripts, healing={'✓' if has_healing else '✗'}"
    )


def assess_reliability() -> DimensionResult:
    """Reliability: error handling, health monitoring, guards."""
    checks = {
        "health_monitoring": (ROOT / ".github/workflows/repository-health-monitoring.yml").exists(),
        "ci_health": (ROOT / ".github/workflows/ci-health-monitor.yml").exists(),
        "self_healing": (ROOT / ".github/workflows/self-healing.yml").exists(),
        "status_gate": (ROOT / ".github/workflows/status_gate.yml").exists(),
    }
    passed = sum(checks.values())
    score = passed / len(checks) * 25
    detail = ", ".join(f"{k}={'✓' if v else '✗'}" for k, v in checks.items())
    return DimensionResult("Reliability", score, 25.0, detail)


def assess_observability() -> DimensionResult:
    """Observability: dashboard, metrics, artifact tracking."""
    checks = {
        "dashboard": (ROOT / ".codex/cognitive_brain/dashboard.md").exists(),
        "trend_analysis": (ROOT / "scripts/cognitive/trend_analysis.py").exists(),
        "introspection": (ROOT / "scripts/monitoring/agent_introspection.py").exists(),
        "benchmarking": (ROOT / "scripts/ci/performance_benchmark.py").exists(),
    }
    passed = sum(checks.values())
    score = passed / len(checks) * 25
    detail = ", ".join(f"{k}={'✓' if v else '✗'}" for k, v in checks.items())
    return DimensionResult("Observability", score, 25.0, detail)


def assess_incident_response() -> DimensionResult:
    """Incident response: healing loop, auto-fix, fragile scan."""
    checks = {
        "healing_loop": (ROOT / "scripts/cognitive/healing_loop.py").exists(),
        "auto_fix": (ROOT / "scripts/ci/auto_fix_common_issues.py").exists(),
        "fragile_scan": (ROOT / ".codex/scripts/fragile_tests_scan.py").exists(),
        "genesis_protocol": (ROOT / "docs/admin/GENESIS_10_1_GUARD_REMOVAL.md").exists(),
    }
    passed = sum(checks.values())
    score = passed / len(checks) * 25
    detail = ", ".join(f"{k}={'✓' if v else '✗'}" for k, v in checks.items())
    return DimensionResult("Incident Response", score, 25.0, detail)


def run_assessment() -> PillarReport:
    return PillarReport(
        pillar="Operational Maturity",
        weight=0.25,
        dimensions=[
            assess_automation_level(),
            assess_reliability(),
            assess_observability(),
            assess_incident_response(),
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
    parser = argparse.ArgumentParser(description="Operational Maturity Assessment")
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
                f.write(f"\n## Operational Maturity: {report.score:.1f}/100\n")
    print(out)


if __name__ == "__main__":
    main()
