"""
Example: Using Chronicle Analytics Programmatically

This script demonstrates how to use the ChronicleAnalytics API
to analyze session history and generate personalized tips.
"""

import sys
from pathlib import Path

# Add src to path for local development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from codex.logging.chronicle_analytics import ChronicleAnalytics
from aries_serpent_core.logging.chronicle_cost import (
    ChronicleStore,
    analyze_costs,
    build_standup_report,
    format_cost_tips,
    format_standup,
)
from codex.logging.session_database import SessionDatabase


def example_basic_usage():
    """Basic usage: Get tips and print them."""
    print("=" * 70)
    print("EXAMPLE 1: Basic Tips Generation")
    print("=" * 70)
    
    db = SessionDatabase(".codex/codex.sqlite")
    analytics = ChronicleAnalytics(db)
    
    # Generate tips
    tips = analytics.generate_tips()
    
    print(f"\nGenerated {len(tips)} tips:\n")
    for i, tip in enumerate(tips, 1):
        print(f"{i}. {tip['title']}")
        print(f"   Category: {tip['category']}")
        print(f"   {tip['description']}\n")


def example_pattern_analysis():
    """Analyze patterns in detail."""
    print("=" * 70)
    print("EXAMPLE 2: Detailed Pattern Analysis")
    print("=" * 70)
    
    db = SessionDatabase(".codex/codex.sqlite")
    analytics = ChronicleAnalytics(db)
    
    patterns = analytics.analyze_patterns()
    
    # Show frequency patterns
    print("\nFrequency Patterns:")
    freq = patterns.get("frequency", {})
    print(f"  Total Sessions: {freq.get('total_sessions', 0)}")
    print(f"  Avg Sessions/Day: {freq.get('avg_sessions_per_day', 0)}")
    
    # Show performance
    print("\nPerformance Metrics:")
    perf = patterns.get("performance", {})
    print(f"  Success Rate: {perf.get('success_rate', 0)}%")
    print(f"  Successful: {perf.get('successful', 0)}")
    print(f"  Failed: {perf.get('failed', 0)}")
    
    # Show top tools
    print("\nTop Tools Used:")
    tools = patterns.get("tools", {})
    for tool, count in list(tools.get("top_tools", {}).items())[:3]:
        print(f"  - {tool}: {count} uses")


def example_summary_generation():
    """Generate a formatted summary."""
    print("=" * 70)
    print("EXAMPLE 3: Formatted Summary")
    print("=" * 70)
    
    db = SessionDatabase(".codex/codex.sqlite")
    analytics = ChronicleAnalytics(db)
    
    # Generate and print summary
    summary = analytics.generate_summary()
    print("\n" + summary)


def example_json_export():
    """Export analysis as JSON."""
    print("=" * 70)
    print("EXAMPLE 4: JSON Export")
    print("=" * 70)
    
    db = SessionDatabase(".codex/codex.sqlite")
    analytics = ChronicleAnalytics(db)
    
    # Export to JSON
    json_str = analytics.export_json()
    
    # Save to file
    output_file = Path(".codex/chronicle_analysis.json")
    output_file.write_text(json_str, encoding="utf-8")
    
    print(f"\nAnalysis exported to: {output_file}")
    print(f"File size: {len(json_str)} bytes")
    print("\nFirst 500 characters:")
    print(json_str[:500])


def example_filter_by_category():
    """Filter tips by category."""
    print("=" * 70)
    print("EXAMPLE 5: Filter Tips by Category")
    print("=" * 70)
    
    db = SessionDatabase(".codex/codex.sqlite")
    analytics = ChronicleAnalytics(db)
    
    tips = analytics.generate_tips()
    
    # Group by category
    by_category = {}
    for tip in tips:
        category = tip["category"]
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(tip)
    
    print("\nTips by category:\n")
    for category, category_tips in sorted(by_category.items()):
        print(f"  {category.upper()} ({len(category_tips)})")
        for tip in category_tips:
            print(f"    - {tip['title']}")


def example_trend_analysis():
    """Analyze usage trends."""
    print("=" * 70)
    print("EXAMPLE 6: Usage Trend Analysis")
    print("=" * 70)
    
    db = SessionDatabase(".codex/codex.sqlite")
    analytics = ChronicleAnalytics(db)
    
    patterns = analytics.analyze_patterns()
    trends = patterns.get("trends", {})
    
    print(f"\nTrend Direction: {trends.get('trend', 'unknown')}")
    print(f"Recent Activity: {trends.get('recent_sessions_per_day', 0)} sessions/day")
    print(f"Previous Activity: {trends.get('older_sessions_per_day', 0)} sessions/day")
    
    # Interpretation
    trend = trends.get("trend", "unknown")
    if trend == "increasing":
        print("\n✅ Your session activity is increasing - keep up the momentum!")
    elif trend == "decreasing":
        print("\n⚠️  Your session activity is decreasing - try to establish a routine")
    else:
        print("\n➡️  Your session activity is stable")


def example_cost_and_standup():
    """Generate cost tips and a completion report without inventing metrics."""
    print("=" * 70)
    print("EXAMPLE 7: Cost Tips and Standup")
    print("=" * 70)

    store = ChronicleStore(".codex/codex.sqlite")
    records = store.load_sessions()
    cost_report = analyze_costs(records, store.diagnostics)
    print("\n" + format_cost_tips(cost_report))

    standup_report = build_standup_report(records, store.diagnostics)
    print("\n" + format_standup(standup_report))


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("CHRONICLE ANALYTICS - USAGE EXAMPLES")
    print("=" * 70 + "\n")
    
    try:
        example_basic_usage()
        print("\n")
        
        example_pattern_analysis()
        print("\n")
        
        example_summary_generation()
        print("\n")
        
        example_json_export()
        print("\n")
        
        example_filter_by_category()
        print("\n")
        
        example_trend_analysis()
        print("\n")

        example_cost_and_standup()
        
        print("\n" + "=" * 70)
        print("✅ All examples completed successfully!")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
