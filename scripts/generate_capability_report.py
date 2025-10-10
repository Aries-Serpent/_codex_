#!/usr/bin/env python3
"""Generate capability summary report.

Reads capabilities_scored.json and produces a concise markdown summary
with actionable recommendations per AGENTS.md guidelines.

Usage:
    python scripts/generate_capability_report.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = REPO_ROOT / "audit_artifacts"
OUTPUT_FILE = REPO_ROOT / "reports" / "capability_summary.md"


def load_capabilities() -> Dict:
    """Load scored capabilities from audit artifacts."""
    scored_file = ARTIFACTS_DIR / "capabilities_scored.json"
    if not scored_file.exists():
        print("Error: capabilities_scored.json not found. Run audit first.", file=sys.stderr)
        sys.exit(1)
    return json.loads(scored_file.read_text(encoding="utf-8"))


def categorize_capabilities(capabilities: List[Dict]) -> Dict[str, List[Dict]]:
    """Categorize capabilities by maturity level."""
    categories = {"high": [], "medium": [], "low": []}

    for cap in capabilities:
        score = cap["score"]
        if score >= 0.85:
            categories["high"].append(cap)
        elif score >= 0.70:
            categories["medium"].append(cap)
        else:
            categories["low"].append(cap)

    return categories


def generate_recommendations(cap: Dict) -> List[str]:
    """Generate actionable recommendations for a capability."""
    recommendations = []
    components = cap["components"]

    # Find weakest components
    sorted_components = sorted(components.items(), key=lambda x: x[1])

    for comp_name, comp_value in sorted_components[:2]:  # Top 2 deficits
        if comp_value < 0.70:
            if comp_name == "functionality":
                recommendations.append(
                    f"Implement missing core patterns (currently {comp_value:.2f})"
                )
            elif comp_name == "consistency":
                recommendations.append(
                    f"Reduce duplication - consolidate implementation (currently {comp_value:.2f})"
                )
            elif comp_name == "tests":
                recommendations.append(
                    f"Add {int((0.80 - comp_value) * len(cap['evidence_files']))} more test files"
                )
            elif comp_name == "safeguards":
                recommendations.append("Add integrity checks (SHA256, seeds, offline guards)")
            elif comp_name == "documentation":
                recommendations.append(f"Document usage in docs/ (currently {comp_value:.2f})")

    return recommendations


def generate_report(data: Dict) -> str:
    """Generate markdown report."""
    capabilities = data["capabilities"]
    categories = categorize_capabilities(capabilities)

    lines = [
        "# [Report]: Capability Summary",
        f"> Generated: {data.get('generated', 'N/A')} | Author: mbaetiong",
        " Roles: [Primary: Audit Orchestrator], [Secondary: Capability Cartographer]  Energy: 5",
        "",
        "## Executive Summary",
        "",
        f"- **Total Capabilities**: {len(capabilities)}",
        f"- **High Maturity (≥0.85)**: {len(categories['high'])}",
        f"- **Medium Maturity (0.70-0.84)**: {len(categories['medium'])}",
        f"- **Low Maturity (<0.70)**: {len(categories['low'])}",
        "",
        "## Maturity Distribution",
        "",
        "| Level | Count | Capabilities |",
        "|-------|------:|--------------|",
    ]

    for level, caps in categories.items():
        cap_names = ", ".join(c["id"] for c in caps[:5])
        if len(caps) > 5:
            cap_names += f" (+{len(caps) - 5} more)"
        lines.append(f"| {level.title()} | {len(caps)} | {cap_names} |")

    # Low maturity focus
    if categories["low"]:
        lines.extend(
            [
                "",
                "## ⚠️ Low Maturity Capabilities (Action Required)",
                "",
                "| ID | Score | Top Deficit | Recommendation |",
                "|----|----- :|-------------|----------------|",
            ]
        )

        for cap in sorted(categories["low"], key=lambda x: x["score"]):
            components = cap["components"]
            weakest = min(components.items(), key=lambda x: x[1])
            recommendations = generate_recommendations(cap)
            rec_text = recommendations[0] if recommendations else "Review implementation"

            lines.append(
                f"| {cap['id']} | {cap['score']:.2f} | "
                f"{weakest[0]} ({weakest[1]:.2f}) | {rec_text} |"
            )

    # High performers
    if categories["high"]:
        lines.extend(
            [
                "",
                "## ✅ High Maturity Capabilities (Maintain)",
                "",
                "| ID | Score | Strengths |",
                "|----|------:|-----------|",
            ]
        )

        for cap in sorted(categories["high"], key=lambda x: -x["score"]):
            components = cap["components"]
            strengths = [k for k, v in components.items() if v >= 0.90]
            strength_text = ", ".join(strengths) if strengths else "All components"

            lines.append(f"| {cap['id']} | {cap['score']:.2f} | {strength_text} |")

    lines.extend(
        [
            "",
            "## Next Steps",
            "",
            "1. **Address Low Maturity**: Focus on capabilities below 0.70 threshold",
            "2. **Strengthen Medium**: Bring 0.70-0.84 capabilities above 0.85",
            "3. **Maintain High**: Ensure no regression in high-performing capabilities",
            "",
            "---",
            "",
            "*Generated by Space Traversal Audit System v1.1.0*",
        ]
    )

    return "\n".join(lines)


def main():
    """Main entry point."""
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    data = load_capabilities()
    report = generate_report(data)

    OUTPUT_FILE.write_text(report, encoding="utf-8")
    print(f"Report generated: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
