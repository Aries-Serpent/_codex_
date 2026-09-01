#!/usr/bin/env python3
"""
Viz Ascii

Purpose:
    [To be documented - Viz Ascii]

Usage:
    python scripts/space_traversal/viz_ascii.py [options]

    Examples:
    $ python scripts/space_traversal/viz_ascii.py --help

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

from typing import Optional

__all__ = [
    "sparkline",
    "bar_chart",
    "trend_indicator",
    "score_badge",
    "capability_dashboard",
    "mini_bar",
    "progress_bar",
]


def sparkline(values: list[float], width: int = 20) -> str:
    """
    Generate sparkline for trend visualization.

    Args:
        values: List of numeric values
        width: Maximum width of sparkline

    Returns:
        String of unicode block characters representing the trend
    """
    if not values:
        return "—"

    blocks = " ▁▂▃▄▅▆▇█"
    min_val, max_val = min(values), max(values)

    if max_val == min_val:
        return blocks[4] * min(len(values), width)

    # Sample if too many values
    if len(values) > width:
        step = len(values) / width
        values = [values[int(i * step)] for i in range(width)]

    result = []
    for v in values:
        normalized = (v - min_val) / (max_val - min_val)
        idx = int(normalized * (len(blocks) - 1))
        result.append(blocks[idx])

    return "".join(result)


def bar_chart(
    data: dict[str, float],
    width: int = 40,
    show_values: bool = True,
    sort_by_value: bool = True,
) -> str:
    """
    Generate horizontal bar chart.

    Args:
        data: Dictionary mapping labels to values
        width: Width of the bar section
        show_values: Whether to show numeric values
        sort_by_value: Whether to sort bars by value (descending)

    Returns:
        Multi-line string representing the bar chart
    """
    if not data:
        return ""

    max_label = max(len(k) for k in data)
    max_val = max(data.values()) if data.values() else 1

    items: list[tuple[str, float]] = list(data.items())
    if sort_by_value:
        items = sorted(items, key=lambda x: -x[1])

    lines = []
    for label, value in items:
        bar_width = int((value / max_val) * width) if max_val > 0 else 0
        bar = "█" * bar_width + "░" * (width - bar_width)
        value_str = f" {value:.3f}" if show_values else ""
        lines.append(f"{label:<{max_label}} │{bar}│{value_str}")

    return "\n".join(lines)


def trend_indicator(current: float, previous: float, threshold: float = 0.02) -> str:
    """
    Get trend indicator emoji.

    Args:
        current: Current score
        previous: Previous score
        threshold: Minimum change to show trend

    Returns:
        Emoji indicating trend direction
    """
    delta = current - previous
    if delta > threshold:
        return "📈"  # Improving
    if delta < -threshold:
        return "📉"  # Declining
    return "➡️"  # Stable


def score_badge(score: float) -> str:
    """
    Get score badge with color indicator.

    Args:
        score: Score value between 0 and 1

    Returns:
        Emoji-prefixed score string
    """
    if score >= 0.95:
        return f"🟢 {score:.3f}"
    if score >= 0.85:
        return f"🟡 {score:.3f}"
    if score >= 0.70:
        return f"🟠 {score:.3f}"
    return f"🔴 {score:.3f}"


def mini_bar(value: float, width: int = 10) -> str:
    """
    Generate a mini progress bar.

    Args:
        value: Value between 0 and 1
        width: Width of the bar

    Returns:
        String representation of progress bar
    """
    filled = int(value * width)
    empty = width - filled
    return "█" * filled + "░" * empty


def progress_bar(
    value: float,
    width: int = 30,
    show_percent: bool = True,
    filled_char: str = "█",
    empty_char: str = "░",
) -> str:
    """
    Generate a progress bar with percentage.

    Args:
        value: Value between 0 and 1
        width: Width of the bar
        show_percent: Whether to show percentage
        filled_char: Character for filled portion
        empty_char: Character for empty portion

    Returns:
        String representation with optional percentage
    """
    filled = int(value * width)
    empty = width - filled
    bar = filled_char * filled + empty_char * empty

    if show_percent:
        return f"[{bar}] {value*100:.1f}%"
    return f"[{bar}]"


def capability_dashboard(
    capability_id: str,
    current_score: float,
    trend_data: list[dict],
    components: dict[str, float],
) -> str:
    """
    Generate full capability dashboard.

    Args:
        capability_id: ID of the capability
        current_score: Current score
        trend_data: List of trend entries (must have 'score' key)
        components: Dictionary of component scores

    Returns:
        Multi-line string with formatted dashboard
    """
    lines = []

    # Header
    lines.append(f"╔{'═' * 60}╗")
    lines.append(f"║ {capability_id:<58} ║")
    lines.append(f"╠{'═' * 60}╣")

    # Current score
    badge = score_badge(current_score)
    if len(trend_data) > 1:
        prev_score = trend_data[1]["score"]
        indicator = trend_indicator(current_score, prev_score)
    else:
        indicator = "—"
    score_line = f"Score: {badge} {indicator}"
    lines.append(f"║ {score_line:<58} ║")

    # Trend sparkline
    if trend_data:
        scores = [t["score"] for t in reversed(trend_data[-20:])]
        spark = sparkline(scores, width=40)
    else:
        spark = "No trend data"
    lines.append(f"║ Trend: {spark:<51} ║")

    # Components
    lines.append(f"╠{'═' * 60}╣")
    lines.append(f"║ {'Components:':<58} ║")

    for comp, val in sorted(components.items()):
        if val is None:
            val = 0
        bar_width = int(val * 30)
        bar = "█" * bar_width + "░" * (30 - bar_width)
        comp_line = f"  {comp:<15} │{bar}│ {val:.3f}"
        lines.append(f"║ {comp_line:<57} ║")

    lines.append(f"╚{'═' * 60}╝")

    return "\n".join(lines)


def summary_table(
    capabilities: list[dict],
    show_trend: bool = True,
    trend_data: Optional[dict[str, list[dict]]] = None,
) -> str:
    """
    Generate summary table for all capabilities.

    Args:
        capabilities: List of capability dictionaries
        show_trend: Whether to include trend column
        trend_data: Optional trend data keyed by capability_id

    Returns:
        Formatted table string
    """
    lines = []

    # Header
    if show_trend:
        lines.append(f"{'Capability':<25} │ {'Score':>8} │ {'Trend':>5} │ {'Sparkline':<20}")
        lines.append("─" * 25 + "─┼─" + "─" * 8 + "─┼─" + "─" * 5 + "─┼─" + "─" * 20)
    else:
        lines.append(f"{'Capability':<25} │ {'Score':>8}")
        lines.append("─" * 25 + "─┼─" + "─" * 8)

    # Sort by score descending
    sorted_caps = sorted(capabilities, key=lambda c: c.get("score", 0), reverse=True)

    for cap in sorted_caps:
        cap_id = cap.get("id", "unknown")[:25]
        score = cap.get("score", 0)

        if show_trend and trend_data and cap_id in trend_data:
            cap_trend = trend_data[cap_id]
            if len(cap_trend) > 1:
                indicator = trend_indicator(cap_trend[0]["score"], cap_trend[1]["score"])
            else:
                indicator = "—"
            scores = [t["score"] for t in reversed(cap_trend[-10:])]
            spark = sparkline(scores, width=20)
            lines.append(f"{cap_id:<25} │ {score:>8.3f} │ {indicator:>5} │ {spark:<20}")
        else:
            lines.append(f"{cap_id:<25} │ {score:>8.3f}")

    return "\n".join(lines)


def regression_alert(regressions: list[dict]) -> str:
    """
    Generate regression alert box.

    Args:
        regressions: List of regression dictionaries

    Returns:
        Formatted alert string
    """
    if not regressions:
        return "✅ No regressions detected"

    lines = [
        "┌" + "─" * 58 + "┐",
        f"│ {'⚠️  REGRESSIONS DETECTED':^56} │",
        "├" + "─" * 58 + "┤",
    ]

    for reg in regressions[:5]:  # Show top 5
        severity_icon = "🔴" if reg.get("severity") == "high" else "🟡"
        cap_id = reg.get("capability_id", "unknown")[:30]
        delta = reg.get("delta", 0)
        line = f"{severity_icon} {cap_id}: {delta:+.3f}"
        lines.append(f"│ {line:<56} │")

    if len(regressions) > 5:
        more = f"... and {len(regressions) - 5} more"
        lines.append(f"│ {more:<56} │")

    lines.append("└" + "─" * 58 + "┘")

    return "\n".join(lines)
