#!/usr/bin/env python3
"""
Track Progress

Purpose:
    Main execution script

Usage:
    python scripts/track_progress.py [options]
    
    Examples:
    $ python scripts/track_progress.py --help

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


"""
Progress tracking script for High Maturity Achievement Plan.

Monitors capability scores and provides actionable next steps.
"""
import json
from pathlib import Path


def load_capabilities() -> list[dict]:
    """Load capability scores from audit artifacts."""
    # Check multiple possible locations for capabilities_scored.json
    possible_paths = [
        Path(__file__).parent / "capabilities_scored.json",
        Path(__file__).parent.parent / "audit_artifacts" / "capabilities_scored.json",
        Path(__file__).parent.parent / "capabilities_scored.json",
    ]

    artifacts_path = None
    for path in possible_paths:
        if path.exists():
            artifacts_path = path
            break

    if artifacts_path is None:
        print("❌ Run audit first: python scripts/space_traversal/audit_runner.py run")
        return []

    with open(artifacts_path) as f:
        data = json.load(f)
    return data.get("capabilities", [])


def categorize_capabilities(caps: list[dict]) -> dict:
    """Categorize capabilities by maturity level."""
    return {
        "critical": [c for c in caps if c["score"] < 0.40],
        "low": [c for c in caps if 0.40 <= c["score"] < 0.70],
        "medium": [c for c in caps if 0.70 <= c["score"] < 0.85],
        "high": [c for c in caps if c["score"] >= 0.85],
    }


def print_progress_report(caps: list[dict]):
    """Print comprehensive progress report."""
    if not caps:
        return

    categories = categorize_capabilities(caps)
    avg_score = sum(c["score"] for c in caps) / len(caps)

    print("=" * 70)
    print("📊 HIGH MATURITY ACHIEVEMENT PLAN - PROGRESS REPORT")
    print("=" * 70)

    print(f"\n🎯 Overall Progress")
    print(f"  Total Capabilities: {len(caps)}")
    print(f"  Average Score: {avg_score:.4f}")
    print()

    print(
        f"  Critical (<0.40):  {len(categories['critical']):2d} ({len(categories['critical'])/len(caps)*100:5.1f}%)"
    )
    print(
        f"  Low (0.40-0.69):   {len(categories['low']):2d} ({len(categories['low'])/len(caps)*100:5.1f}%)"
    )
    print(
        f"  Medium (0.70-0.84): {len(categories['medium']):2d} ({len(categories['medium'])/len(caps)*100:5.1f}%)"
    )
    print(
        f"  High (≥0.85):      {len(categories['high']):2d} ({len(categories['high'])/len(caps)*100:5.1f}%)"
    )

    # Phase targets
    print(f"\n📈 Phase Targets")
    phase1_complete = len(categories["critical"]) == 0 and len(categories["low"]) == 0
    phase2_complete = len(categories["medium"]) == 0
    phase3_complete = len(categories["high"]) == len(caps)

    print(
        f"  Phase 1 (ALL ≥0.70):  {'✅' if phase1_complete else '❌'} {len(categories['critical']) + len(categories['low'])} remaining"
    )
    print(
        f"  Phase 2 (ALL ≥0.85):  {'✅' if phase2_complete else '❌'} {len(categories['medium'])} remaining"
    )
    print(
        f"  Phase 3 (AVG ≥0.93):  {'✅' if avg_score >= 0.93 else '❌'} {0.93 - avg_score:+.4f} to target"
    )

    # Next priorities
    low_maturity = categories["critical"] + categories["low"]
    if low_maturity:
        print(f"\n⏳ Next Priorities (Phase 1 - Low Maturity)")
        low_sorted = sorted(low_maturity, key=lambda x: x["score"])
        for i, cap in enumerate(low_sorted[:8], 1):
            components = cap.get("components", {})
            weakest = (
                min(components.items(), key=lambda x: x[1]) if components else ("unknown", 0.0)
            )
            print(
                f"  {i}. {cap['id']:30s}  Score: {cap['score']:.4f}  Weakest: {weakest[0]} ({weakest[1]:.2f})"
            )

    medium_maturity = categories["medium"]
    if medium_maturity and not low_maturity:
        print(f"\n⏳ Next Priorities (Phase 2 - Medium to High)")
        medium_sorted = sorted(medium_maturity, key=lambda x: x["score"])
        for i, cap in enumerate(medium_sorted[:5], 1):
            print(f"  {i}. {cap['id']:30s}  Score: {cap['score']:.4f}")

    # Component analysis
    print(f"\n📊 Component Analysis (Weakest Areas)")
    component_scores = {
        "tests": [],
        "documentation": [],
        "functionality": [],
        "safeguards": [],
        "consistency": [],
    }
    for cap in caps:
        components = cap.get("components", {})
        for comp_name in component_scores:
            if comp_name in components:
                component_scores[comp_name].append(components[comp_name])

    for comp_name, scores in component_scores.items():
        if scores:
            avg = sum(scores) / len(scores)
            below_80 = sum(1 for s in scores if s < 0.80)
            print(f"  {comp_name.capitalize():15s}  Avg: {avg:.4f}  Below 0.80: {below_80}")

    print("\n" + "=" * 70)


def generate_next_command(caps: list[dict]):
    """Generate next command to execute."""
    categories = categorize_capabilities(caps)
    low_maturity = categories["critical"] + categories["low"]

    if low_maturity:
        next_cap = sorted(low_maturity, key=lambda x: x["score"])[0]
        print(f"\n🚀 Next Command:")
        print(f"   python scripts/space_traversal/audit_runner.py explain {next_cap['id']}")
        print(f"\n📝 Then improve weakest component for {next_cap['id']}")
    elif categories["medium"]:
        next_cap = sorted(categories["medium"], key=lambda x: x["score"])[0]
        print(f"\n🚀 Next Command (Phase 2):")
        print(f"   python scripts/space_traversal/audit_runner.py explain {next_cap['id']}")
    else:
        print(f"\n🎉 All capabilities at high maturity!")
        print(f"   Consider running excellence phase optimizations")


def main():
    """Main entry point."""
    caps = load_capabilities()
    if not caps:
        return

    print_progress_report(caps)
    generate_next_command(caps)


if __name__ == "__main__":
    main()
