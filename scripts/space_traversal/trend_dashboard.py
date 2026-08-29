"""
from __future__ import annotations

Capability Audit Trending Dashboard Generator (v1.0.0)

Generates visual trending analysis across multiple audit runs:
- Score progression over time
- Component-level trend analysis
- Regression detection
- Improvement tracking
- HTML dashboard with sparklines

Usage:
    python scripts/space_traversal/trend_dashboard.py \
        --history audit_artifacts/history/ \
        --output .codex/reports/trend_dashboard.html

Dependencies:
    pip install jinja2

Author: mbaetiong
Generated: 2025-11-19 00:49:03 UTC
Roles: [Audit Orchestrator], [Data Visualization Engineer] ⚡ Energy: 5
"""


import argparse
import json
import logging
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)



def calculate_trend(scores: list[float]) -> tuple[str, str, str]:
    """
    Calculate trend direction and classification

    Returns:
        (trend_text, trend_class, trend_symbol)
    """
    if len(scores) < 2:
        return ("N/A", "trend-stable", "—")

    first_half = scores[: len(scores) // 2]
    second_half = scores[len(scores) // 2 :]

    avg_first = sum(first_half) / len(first_half)
    avg_second = sum(second_half) / len(second_half)

    delta = avg_second - avg_first

    if abs(delta) < 0.01:
        return ("Stable", "trend-stable", "→")
    if delta > 0:
        pct = (delta / avg_first) * 100 if avg_first > 0 else 0
        return (f"+{pct:.1f}%", "trend-up", "↑")
    pct = (abs(delta) / avg_first) * 100 if avg_first > 0 else 0
    return (f"-{pct:.1f}%", "trend-down", "↓")


def load_audit_runs(history_dir: Path) -> list[dict]:
    """Load all audit run JSON files from history directory"""
    runs = []

    for json_file in sorted(history_dir.glob("capabilities_scored_*.json")):
        try:
            with open(json_file) as f:
                data = json.load(f)
                data["_filename"] = json_file.name
                runs.append(data)
        except Exception as e:
            logger.debug(f"Exception: {e}")
            print(f"Error loading {json_file}: {e}", file=sys.stderr)

    return runs


def extract_trends(runs: list[dict]) -> dict:
    """Extract capability trends across runs"""
    capability_scores = defaultdict(list)
    timestamps = []

    for run in runs:
        timestamp = run.get("generated", 0)
        timestamps.append(timestamp)

        for cap in run.get("capabilities", []):
            cap_id = cap["id"]
            score = cap["score"]
            capability_scores[cap_id].append(score)

    return {
        "capability_scores": dict(capability_scores),
        "timestamps": timestamps,
        "run_count": len(runs),
    }


def generate_capability_row(cap_id: str, scores: list[float]) -> str:
    """Generate HTML table row for capability"""
    current_score = scores[-1]

    # Calculate change from first to last
    if len(scores) >= 2:
        change = scores[-1] - scores[0]
        change_str = f"{change:+.4f}"
        change_class = "trend-up" if change > 0 else "trend-down" if change < 0 else "trend-stable"
    else:
        change_str = "N/A"
        change_class = "trend-stable"

    # Determine status badge
    if current_score >= 0.85:
        status = '<span class="badge badge-high">High</span>'
    elif current_score >= 0.70:
        status = '<span class="badge badge-medium">Medium</span>'
    else:
        status = '<span class="badge badge-low">Low</span>'

    # Generate sparkline canvas
    scores_json = json.dumps([round(s, 4) for s in scores])
    sparkline = (
        f'<canvas class="sparkline" width="100" height="30" data-scores=\'{scores_json}\'></canvas>'
    )

    return f"""
        <tr>
            <td>{cap_id}</td>
            <td>{current_score:.2f}</td>
            <td>{sparkline}</td>
            <td class="{change_class}">{change_str}</td>
            <td>{status}</td>
        </tr>
    """


def generate_component_card(component: str, scores_by_cap: dict[str, list[float]]) -> str:
    """Generate component analysis card"""
    # Calculate average across all capabilities for this component
    all_values = []
    for cap_scores in scores_by_cap.values():
        all_values.extend(cap_scores)

    if not all_values:
        avg = 0.0
        trend_text = "N/A"
        trend_class = "trend-stable"
    else:
        avg = sum(all_values) / len(all_values)
        trend_text, trend_class, _ = calculate_trend(all_values)

    return f"""
        <div class="card">
            <div class="card-title">{component.title()}</div>
            <div class="card-value">{avg:.2f}</div>
            <div class="card-trend {trend_class}">{trend_text}</div>
        </div>
    """


def generate_regression_section(runs: list[dict], threshold: float = 0.02) -> str:
    """Generate regression alerts section"""
    if len(runs) < 2:
        return "<p>Need at least 2 runs to detect regressions.</p>"

    old_run = runs[-2]
    new_run = runs[-1]

    old_caps = {c["id"]: c["score"] for c in old_run.get("capabilities", [])}
    new_caps = {c["id"]: c["score"] for c in new_run.get("capabilities", [])}

    regressions = []
    for cap_id in sorted(set(old_caps.keys()) & set(new_caps.keys())):
        delta = new_caps[cap_id] - old_caps[cap_id]
        if delta < -threshold:
            regressions.append((cap_id, old_caps[cap_id], new_caps[cap_id], delta))

    if not regressions:
        return '<p style="color: #3fb950;">✓ No significant regressions detected.</p>'

    rows = []
    for cap_id, old_score, new_score, delta in regressions:
        rows.append(
            f"""
            <tr>
                <td>{cap_id}</td>
                <td>{old_score:.4f}</td>
                <td>{new_score:.4f}</td>
                <td class="trend-down">{delta:.4f}</td>
            </tr>
        """
        )

    return f"""
        <table>
            <thead>
                <tr>
                    <th>Capability</th>
                    <th>Previous</th>
                    <th>Current</th>
                    <th>Change</th>
                </tr>
            </thead>
            <tbody>
                {"".join(rows)}
            </tbody>
        </table>
    """


def generate_dashboard(runs: list[dict], output_path: Path):
    """Generate complete HTML dashboard"""
    if not runs:
        print("No audit runs found.", file=sys.stderr)
        sys.exit(1)

    trends = extract_trends(runs)
    capability_scores = trends["capability_scores"]

    # Calculate summary stats
    latest_run = runs[-1]
    latest_caps = latest_run.get("capabilities", [])

    avg_score = sum(c["score"] for c in latest_caps) / len(latest_caps) if latest_caps else 0
    high_maturity = sum(1 for c in latest_caps if c["score"] >= 0.85)
    low_maturity = sum(1 for c in latest_caps if c["score"] < 0.70)

    # Calculate trends for summary
    if len(runs) >= 2:
        prev_caps = runs[-2].get("capabilities", [])
        prev_avg = sum(c["score"] for c in prev_caps) / len(prev_caps) if prev_caps else 0
        prev_high = sum(1 for c in prev_caps if c["score"] >= 0.85)
        prev_low = sum(1 for c in prev_caps if c["score"] < 0.70)

        avg_trend_text, avg_trend_class, _ = calculate_trend([prev_avg, avg_score])
        high_trend_text, high_trend_class, _ = calculate_trend(
            [float(prev_high), float(high_maturity)]
        )
        low_trend_text, low_trend_class, _ = calculate_trend([float(prev_low), float(low_maturity)])
    else:
        avg_trend_text = "N/A"
        avg_trend_class = "trend-stable"
        high_trend_text = "N/A"
        high_trend_class = "trend-stable"
        low_trend_text = "N/A"
        low_trend_class = "trend-stable"

    # Generate capability rows
    capability_rows = []
    for cap_id in sorted(capability_scores.keys()):
        scores = capability_scores[cap_id]
        capability_rows.append(generate_capability_row(cap_id, scores))

    # Generate component cards (if available)
    component_cards = ""
    if latest_caps and latest_caps[0].get("components"):
        components = ["functionality", "consistency", "tests", "safeguards", "documentation"]
        for comp in components:
            comp_scores = defaultdict(list)
            for run in runs:
                for cap in run.get("capabilities", []):
                    if comp in cap.get("components", {}):
                        comp_scores[cap["id"]].append(cap["components"][comp])
            component_cards += generate_component_card(comp, comp_scores)

    # Date range
    if trends["timestamps"]:
        date_range = f"{datetime.fromtimestamp(min(trends['timestamps'])).strftime('%Y-%m-%d')} to {datetime.fromtimestamp(max(trends['timestamps'])).strftime('%Y-%m-%d')}"
    else:
        date_range = "N/A"

    # Generate HTML
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Capability Audit Trend Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0d1117;
            color: #c9d1d9;
            padding: 2rem;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        header {{
            margin-bottom: 3rem;
            border-bottom: 2px solid #30363d;
            padding-bottom: 1.5rem;
        }}
        h1 {{
            font-size: 2.5rem;
            color: #58a6ff;
            margin-bottom: 0.5rem;
        }}
        .meta {{
            color: #8b949e;
            font-size: 0.9rem;
        }}
        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 3rem;
        }}
        .card {{
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 1.5rem;
        }}
        .card-title {{
            font-size: 0.875rem;
            color: #8b949e;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
        }}
        .card-value {{
            font-size: 2rem;
            font-weight: bold;
            color: #58a6ff;
        }}
        .card-trend {{
            font-size: 0.875rem;
            margin-top: 0.5rem;
        }}
        .trend-up {{ color: #3fb950; }}
        .trend-down {{ color: #f85149; }}
        .trend-stable {{ color: #8b949e; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            overflow: hidden;
        }}
        th, td {{
            padding: 1rem;
            text-align: left;
            border-bottom: 1px solid #30363d;
        }}
        th {{
            background: #0d1117;
            color: #8b949e;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.75rem;
            letter-spacing: 0.05em;
        }}
        tr:last-child td {{
            border-bottom: none;
        }}
        .sparkline {{
            display: inline-block;
            width: 100px;
            height: 30px;
            vertical-align: middle;
        }}
        .badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
        }}
        .badge-high {{ background: #2ea04326; color: #3fb950; }}
        .badge-medium {{ background: #bb800926; color: #d29922; }}
        .badge-low {{ background: #da364626; color: #f85149; }}
        .section {{
            margin-bottom: 3rem;
        }}
        .section-title {{
            font-size: 1.5rem;
            color: #c9d1d9;
            margin-bottom: 1.5rem;
        }}
        .component-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔍 Capability Audit Trend Dashboard</h1>
            <div class="meta">
                Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')} |
                Runs Analyzed: {len(runs)} |
                Period: {date_range}
            </div>
        </header>

        <div class="summary-cards">
            <div class="card">
                <div class="card-title">Average Score</div>
                <div class="card-value">{avg_score:.2f}</div>
                <div class="card-trend {avg_trend_class}">{avg_trend_text}</div>
            </div>
            <div class="card">
                <div class="card-title">Capabilities Tracked</div>
                <div class="card-value">{len(latest_caps)}</div>
            </div>
            <div class="card">
                <div class="card-title">High Maturity</div>
                <div class="card-value">{high_maturity}</div>
                <div class="card-trend {high_trend_class}">{high_trend_text}</div>
            </div>
            <div class="card">
                <div class="card-title">Low Maturity</div>
                <div class="card-value">{low_maturity}</div>
                <div class="card-trend {low_trend_class}">{low_trend_text}</div>
            </div>
        </div>

        <section class="section">
            <h2 class="section-title">Capability Score Trends</h2>
            <table>
                <thead>
                    <tr>
                        <th>Capability</th>
                        <th>Current Score</th>
                        <th>Trend</th>
                        <th>Change</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(capability_rows)}
                </tbody>
            </table>
        </section>

        <section class="section">
            <h2 class="section-title">Component Analysis</h2>
            <div class="component-grid">
                {component_cards}
            </div>
        </section>

        <section class="section">
            <h2 class="section-title">Regression Alerts</h2>
            {generate_regression_section(runs)}
        </section>
    </div>

    <script>
        // Sparkline drawing function
        function drawSparkline(canvas, data) {{
            const ctx = canvas.getContext('2d');
            const width = canvas.width;
            const height = canvas.height;
            const max = Math.max(...data);
            const min = Math.min(...data);
            const range = max - min || 1;

            ctx.clearRect(0, 0, width, height);
            ctx.strokeStyle = '#58a6ff';
            ctx.lineWidth = 2;
            ctx.beginPath();

            data.forEach((value, index) => {{
                const x = (index / (data.length - 1)) * width;
                const y = height - ((value - min) / range) * height;
                if (index === 0) {{
                    ctx.moveTo(x, y);
                }} else {{
                    ctx.lineTo(x, y);
                }}
            }});

            ctx.stroke();

            // Draw points
            data.forEach((value, index) => {{
                const x = (index / (data.length - 1)) * width;
                const y = height - ((value - min) / range) * height;
                ctx.fillStyle = index === data.length - 1 ? '#3fb950' : '#58a6ff';
                ctx.beginPath();
                ctx.arc(x, y, 3, 0, 2 * Math.PI);
                ctx.fill();
            }});
        }}

        // Draw all sparklines
        document.querySelectorAll('.sparkline').forEach(canvas => {{
            const data = JSON.parse(canvas.dataset.scores);
            drawSparkline(canvas, data);
        }});
    </script>
</body>
</html>
"""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_content, encoding="utf-8")
    print(f"✓ Dashboard generated: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate capability audit trending dashboard")
    parser.add_argument(
        "--history",
        type=Path,
        required=True,
        help="Directory containing historical audit JSON files",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(".codex/reports/trend_dashboard.html"),
        help="Output HTML file path",
    )

    args = parser.parse_args()

    if not args.history.exists():
        print(f"History directory not found: {args.history}", file=sys.stderr)
        sys.exit(1)

    runs = load_audit_runs(args.history)
    generate_dashboard(runs, args.output)


if __name__ == "__main__":
    main()
