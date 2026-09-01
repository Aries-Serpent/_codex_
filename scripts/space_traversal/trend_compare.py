#!/usr/bin/env python3
"""
Trend Compare

Purpose:
    [To be documented - Trend Compare]

Usage:
    python scripts/space_traversal/trend_compare.py [options]

    Examples:
    $ python scripts/space_traversal/trend_compare.py --help

Arguments:
    [To be documented]

Environment Variables:
    [To be documented]

Dependencies:
    [To be documented]

Exit Codes:
    0: Success
    1: Error

Author: Codex Team
Last Updated: 2026-01-16
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

__all__ = ["ComparisonResult", "compare_runs", "generate_comparison_report"]


@dataclass
class ComparisonResult:
    """Result of comparing two audit runs for a single capability."""

    capability_id: str
    old_score: float
    new_score: float
    delta: float
    old_components: dict[str, float]
    new_components: dict[str, float]
    component_deltas: dict[str, float]
    is_regression: bool
    regression_severity: Optional[str]


def compare_runs(
    old_path: Path,
    new_path: Path,
    threshold: float = 0.02,
) -> list[ComparisonResult]:
    """
    Compare two audit runs with detailed component analysis.

    Args:
        old_path: Path to old capabilities_scored.json
        new_path: Path to new capabilities_scored.json
        threshold: Minimum delta to consider as significant change

    Returns:
        List of ComparisonResult objects for each capability
    """
    with open(old_path, encoding="utf-8") as f:
        old_data = json.load(f)
    with open(new_path, encoding="utf-8") as f:
        new_data = json.load(f)

    old_caps = {c["id"]: c for c in old_data.get("capabilities", [])}
    new_caps = {c["id"]: c for c in new_data.get("capabilities", [])}

    all_ids = set(old_caps.keys()) | set(new_caps.keys())
    results = []

    for cap_id in sorted(all_ids):
        old_cap = old_caps.get(cap_id, {"score": 0, "components": {}})
        new_cap = new_caps.get(cap_id, {"score": 0, "components": {}})

        old_score = old_cap.get("score", 0)
        new_score = new_cap.get("score", 0)
        delta = new_score - old_score

        old_components = old_cap.get("components", {})
        new_components = new_cap.get("components", {})

        component_deltas = {}
        for comp in [
            "functionality",
            "consistency",
            "tests",
            "safeguards",
            "documentation",
        ]:
            old_val = old_components.get(comp, 0) or 0
            new_val = new_components.get(comp, 0) or 0
            component_deltas[comp] = new_val - old_val

        is_regression = delta < -threshold
        severity = None
        if is_regression:
            if delta < -0.05:
                severity = "high"
            elif delta < -0.02:
                severity = "medium"
            else:
                severity = "low"

        results.append(
            ComparisonResult(
                capability_id=cap_id,
                old_score=old_score,
                new_score=new_score,
                delta=delta,
                old_components=old_components,
                new_components=new_components,
                component_deltas=component_deltas,
                is_regression=is_regression,
                regression_severity=severity,
            )
        )

    return results


def generate_comparison_report(
    results: list[ComparisonResult],
    output_path: Path,
    old_name: str = "Previous",
    new_name: str = "Current",
) -> None:
    """
    Generate detailed comparison markdown report.

    Args:
        results: List of ComparisonResult objects
        output_path: Path to write markdown report
        old_name: Label for old run
        new_name: Label for new run
    """
    regressions = [r for r in results if r.is_regression]
    improvements = [r for r in results if r.delta > 0.02]
    unchanged = [r for r in results if -0.02 <= r.delta <= 0.02]

    # Calculate aggregate stats
    old_avg = sum(r.old_score for r in results) / len(results) if results else 0
    new_avg = sum(r.new_score for r in results) / len(results) if results else 0
    avg_delta = new_avg - old_avg

    lines = [
        "# Audit Comparison Report",
        "",
        f"**Generated:** {datetime.now().isoformat()}",
        f"**Comparing:** {old_name} → {new_name}",
        "",
        "## Summary",
        "",
        f"- **Total capabilities:** {len(results)}",
        f"- **Regressions:** {len(regressions)}",
        f"- **Improvements:** {len(improvements)}",
        f"- **Unchanged:** {len(unchanged)}",
        "",
        f"- **Average score ({old_name}):** {old_avg:.4f}",
        f"- **Average score ({new_name}):** {new_avg:.4f}",
        f"- **Average delta:** {avg_delta:+.4f}",
        "",
    ]

    # Regressions section
    if regressions:
        lines.extend(
            [
                "## ⚠️ Regressions",
                "",
                "| Capability | Old | New | Δ | Severity | Weakest Component |",
                "|------------|-----|-----|---|----------|-------------------|",
            ]
        )
        for r in sorted(regressions, key=lambda x: x.delta):
            # Find weakest component (most negative delta)
            if r.component_deltas:
                weakest = min(r.component_deltas.items(), key=lambda x: x[1])
                weakest_str = f"{weakest[0]} ({weakest[1]:+.3f})"
            else:
                weakest_str = "—"
            lines.append(
                f"| {r.capability_id} | {r.old_score:.3f} | {r.new_score:.3f} | "
                f"{r.delta:+.3f} | {r.regression_severity} | {weakest_str} |"
            )
        lines.append("")

    # Improvements section
    if improvements:
        lines.extend(
            [
                "## ✅ Improvements",
                "",
                "| Capability | Old | New | Δ | Best Component |",
                "|------------|-----|-----|---|----------------|",
            ]
        )
        for r in sorted(improvements, key=lambda x: -x.delta):
            # Find best component (most positive delta)
            if r.component_deltas:
                best = max(r.component_deltas.items(), key=lambda x: x[1])
                best_str = f"{best[0]} ({best[1]:+.3f})"
            else:
                best_str = "—"
            lines.append(
                f"| {r.capability_id} | {r.old_score:.3f} | {r.new_score:.3f} | "
                f"{r.delta:+.3f} | {best_str} |"
            )
        lines.append("")

    # Full comparison table
    lines.extend(
        [
            "## Full Comparison",
            "",
            "| Capability | Old | New | Δ | F | C | T | S | D |",
            "|------------|-----|-----|---|---|---|---|---|---|",
        ]
    )
    for r in sorted(results, key=lambda x: x.capability_id):
        cd = r.component_deltas
        lines.append(
            f"| {r.capability_id} | {r.old_score:.3f} | {r.new_score:.3f} | "
            f"{r.delta:+.3f} | {cd.get('functionality', 0):+.2f} | "
            f"{cd.get('consistency', 0):+.2f} | {cd.get('tests', 0):+.2f} | "
            f"{cd.get('safeguards', 0):+.2f} | {cd.get('documentation', 0):+.2f} |"
        )
    lines.append("")

    # Component legend
    lines.extend(
        [
            "### Component Legend",
            "",
            "- **F**: Functionality",
            "- **C**: Consistency",
            "- **T**: Tests",
            "- **S**: Safeguards",
            "- **D**: Documentation",
            "",
            "---",
            "",
            "*Report generated by Audit Pipeline v1.5.1*",
        ]
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")


def compare_with_baseline(
    current_path: Path,
    baseline_dir: Path,
    threshold: float = 0.02,
) -> list[ComparisonResult]:
    """
    Compare current audit with baseline.

    Args:
        current_path: Path to current capabilities_scored.json
        baseline_dir: Directory containing baseline capabilities_scored.json
        threshold: Regression threshold

    Returns:
        List of ComparisonResult objects
    """
    baseline_path = baseline_dir / "capabilities_scored.json"
    if not baseline_path.exists():
        # Try alternate locations
        for alt in [
            baseline_dir / "baselines" / "capabilities_scored.json",
            baseline_dir.parent / "baselines" / "capabilities_scored.json",
        ]:
            if alt.exists():
                baseline_path = alt
                break

    if not baseline_path.exists():
        raise FileNotFoundError(f"No baseline found in {baseline_dir}")

    return compare_runs(baseline_path, current_path, threshold)


def get_regression_summary(results: list[ComparisonResult]) -> dict[str, Any]:
    """
    Get summary statistics about regressions.

    Args:
        results: List of comparison results

    Returns:
        Dictionary with regression summary
    """
    regressions = [r for r in results if r.is_regression]
    high_severity = [r for r in regressions if r.regression_severity == "high"]
    medium_severity = [r for r in regressions if r.regression_severity == "medium"]
    low_severity = [r for r in regressions if r.regression_severity == "low"]

    # Find most affected components
    component_impacts: dict[str, list[float]] = {
        "functionality": [],
        "consistency": [],
        "tests": [],
        "safeguards": [],
        "documentation": [],
    }

    for r in regressions:
        for comp, delta in r.component_deltas.items():
            if delta < 0:
                component_impacts[comp].append(delta)

    most_affected = None
    max_impact = 0.0
    for comp, deltas in component_impacts.items():
        if deltas:
            avg_impact = abs(sum(deltas) / len(deltas))
            if avg_impact > max_impact:
                max_impact = avg_impact
                most_affected = comp

    return {
        "total_regressions": len(regressions),
        "high_severity_count": len(high_severity),
        "medium_severity_count": len(medium_severity),
        "low_severity_count": len(low_severity),
        "high_severity_ids": [r.capability_id for r in high_severity],
        "most_affected_component": most_affected,
        "worst_regression": (
            min(regressions, key=lambda r: r.delta).capability_id if regressions else None
        ),
    }
