#!/usr/bin/env python3
"""
Viz Html

Purpose:
    [To be documented - Viz Html]

Usage:
    python scripts/space_traversal/viz_html.py [options]

    Examples:
    $ python scripts/space_traversal/viz_html.py --help

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
from datetime import datetime
from pathlib import Path

__all__ = ["generate_dashboard", "generate_capability_detail", "HTML_TEMPLATE"]


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Audit Dashboard - {repo_name}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js" integrity="sha384-Wu6WSKW9XlJFLlS7yDnULhvzDn1Fn0kDuAdXXq0bXrOJKGJG6s8k9qEXVjZkQTZD" crossorigin="anonymous"></script>
    <style>
        :root {{
            --bg-primary: #1a1a2e;
            --bg-secondary: #16213e;
            --accent: #0f3460;
            --text-primary: #eee;
            --text-secondary: #aaa;
            --success: #4ade80;
            --warning: #fbbf24;
            --danger: #f87171;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            padding: 20px;
            line-height: 1.6;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            padding: 20px;
            background: var(--bg-secondary);
            border-radius: 10px;
        }}
        .header h1 {{ font-size: 1.5rem; }}
        .header .meta {{ color: var(--text-secondary); font-size: 0.9rem; }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}
        .card {{
            background: var(--bg-secondary);
            border-radius: 10px;
            padding: 20px;
        }}
        .card h3 {{
            margin-bottom: 15px;
            color: var(--text-secondary);
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .score {{
            font-size: 2.5rem;
            font-weight: bold;
        }}
        .score.high {{ color: var(--success); }}
        .score.medium {{ color: var(--warning); }}
        .score.low {{ color: var(--danger); }}
        .trend {{ font-size: 1.2rem; margin-left: 10px; }}
        .chart-container {{ height: 300px; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }}
        th, td {{
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid var(--accent);
        }}
        th {{ color: var(--text-secondary); font-weight: normal; }}
        .badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
        }}
        .badge.success {{ background: var(--success); color: #000; }}
        .badge.warning {{ background: var(--warning); color: #000; }}
        .badge.danger {{ background: var(--danger); color: #000; }}
        .stat-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }}
        .stat-card {{
            background: var(--accent);
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-card .value {{
            font-size: 1.8rem;
            font-weight: bold;
            color: var(--text-primary);
        }}
        .stat-card .label {{
            font-size: 0.8rem;
            color: var(--text-secondary);
            text-transform: uppercase;
        }}
        .progress-bar {{
            width: 100%;
            height: 8px;
            background: var(--accent);
            border-radius: 4px;
            overflow: hidden;
        }}
        .progress-bar .fill {{
            height: 100%;
            border-radius: 4px;
            transition: width 0.3s ease;
        }}
        .progress-bar .fill.high {{ background: var(--success); }}
        .progress-bar .fill.medium {{ background: var(--warning); }}
        .progress-bar .fill.low {{ background: var(--danger); }}
        @media (max-width: 768px) {{
            .stat-grid {{ grid-template-columns: repeat(2, 1fr); }}
            .header {{ flex-direction: column; text-align: center; gap: 10px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>🔍 Audit Dashboard</h1>
                <div class="meta">{repo_name} • v{version} • {timestamp}</div>
            </div>
            <div>
                <span class="score {avg_class}">{avg_score:.1%}</span>
                <span class="trend">{trend_indicator}</span>
            </div>
        </div>

        <div class="stat-grid">
            <div class="stat-card">
                <div class="value">{capability_count}</div>
                <div class="label">Capabilities</div>
            </div>
            <div class="stat-card">
                <div class="value">{high_count}</div>
                <div class="label">High (≥85%)</div>
            </div>
            <div class="stat-card">
                <div class="value">{regression_count}</div>
                <div class="label">Regressions</div>
            </div>
            <div class="stat-card">
                <div class="value">{run_count}</div>
                <div class="label">Trend Runs</div>
            </div>
        </div>

        <div class="grid">
            <div class="card">
                <h3>Score Distribution</h3>
                <div class="chart-container">
                    <canvas id="distributionChart"></canvas>
                </div>
            </div>

            <div class="card">
                <h3>Trend (Last 30 Runs)</h3>
                <div class="chart-container">
                    <canvas id="trendChart"></canvas>
                </div>
            </div>

            <div class="card" style="grid-column: span 2;">
                <h3>Capabilities</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Capability</th>
                            <th>Score</th>
                            <th>Trend</th>
                            <th>F</th>
                            <th>C</th>
                            <th>T</th>
                            <th>S</th>
                            <th>D</th>
                        </tr>
                    </thead>
                    <tbody>
                        {capability_rows}
                    </tbody>
                </table>
            </div>
        </div>

        <div class="card" style="margin-top: 20px;">
            <h3>Component Legend</h3>
            <p style="color: var(--text-secondary);">
                <strong>F</strong>: Functionality |
                <strong>C</strong>: Consistency |
                <strong>T</strong>: Tests |
                <strong>S</strong>: Safeguards |
                <strong>D</strong>: Documentation
            </p>
        </div>
    </div>

    <script>
        const distributionData = {distribution_json};
        const trendData = {trend_json};

        new Chart(document.getElementById('distributionChart'), {{
            type: 'doughnut',
            data: {{
                labels: ['High (≥0.85)', 'Medium (0.70-0.85)', 'Low (<0.70)'],
                datasets: [{{
                    data: distributionData,
                    backgroundColor: ['#4ade80', '#fbbf24', '#f87171']
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'bottom',
                        labels: {{ color: '#eee' }}
                    }}
                }}
            }}
        }});

        new Chart(document.getElementById('trendChart'), {{
            type: 'line',
            data: {{
                labels: trendData.labels,
                datasets: [{{
                    label: 'Average Score',
                    data: trendData.values,
                    borderColor: '#4ade80',
                    backgroundColor: 'rgba(74, 222, 128, 0.1)',
                    tension: 0.3,
                    fill: true
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{
                        min: 0,
                        max: 1,
                        ticks: {{ color: '#aaa' }},
                        grid: {{ color: '#333' }}
                    }},
                    x: {{
                        ticks: {{ color: '#aaa', maxRotation: 45 }},
                        grid: {{ color: '#333' }}
                    }}
                }},
                plugins: {{
                    legend: {{ display: false }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""


def generate_dashboard(
    capabilities: list[dict],
    trend_data: list[dict],
    output_path: Path,
    repo_name: str = "Repository",
    version: str = "1.5.2",
    regressions: list[dict] | None = None,
) -> None:
    """
    Generate HTML dashboard.

    Args:
        capabilities: List of capability dictionaries with id, score, components
        trend_data: List of trend entries with avg_score and date/timestamp
        output_path: Path to write HTML file
        repo_name: Repository name for display
        version: Pipeline version
        regressions: Optional list of detected regressions
    """
    # Calculate metrics
    scores = [c.get("score", 0) for c in capabilities]
    avg_score = sum(scores) / len(scores) if scores else 0

    high_count = sum(1 for s in scores if s >= 0.85)
    medium_count = sum(1 for s in scores if 0.70 <= s < 0.85)
    low_count = sum(1 for s in scores if s < 0.70)

    # Determine trend indicator
    if len(trend_data) >= 2:
        recent_scores = [t.get("avg_score", 0) for t in trend_data[: min(6, len(trend_data))]]
        if len(recent_scores) >= 2:
            prev_avg = sum(recent_scores[1:]) / len(recent_scores[1:])
            if avg_score > prev_avg + 0.02:
                trend_indicator = "📈"
            elif avg_score < prev_avg - 0.02:
                trend_indicator = "📉"
            else:
                trend_indicator = "➡️"
        else:
            trend_indicator = "—"
    else:
        trend_indicator = "—"

    # Score class
    avg_class = "high" if avg_score >= 0.85 else "medium" if avg_score >= 0.70 else "low"

    # Capability rows
    rows = []
    for cap in sorted(capabilities, key=lambda x: -x.get("score", 0)):
        score = cap.get("score", 0)
        badge_class = "success" if score >= 0.85 else "warning" if score >= 0.70 else "danger"
        comp = cap.get("components", {})

        # Get trend indicator for this capability
        cap_trend = cap.get("trend_indicator", "—")

        rows.append(
            f"""
            <tr>
                <td>{cap.get('id', 'unknown')}</td>
                <td><span class="badge {badge_class}">{score:.3f}</span></td>
                <td>{cap_trend}</td>
                <td>{comp.get('functionality', 0):.2f}</td>
                <td>{comp.get('consistency', 0):.2f}</td>
                <td>{comp.get('tests', 0):.2f}</td>
                <td>{comp.get('safeguards', 0):.2f}</td>
                <td>{comp.get('documentation', 0):.2f}</td>
            </tr>
        """
        )

    # Trend chart data
    trend_labels = []
    trend_values = []
    for i, t in enumerate(reversed(trend_data[-30:])):
        label = t.get("date") or t.get("timestamp") or f"Run {i + 1}"
        if isinstance(label, (int, float)):
            label = datetime.fromtimestamp(label).strftime("%m/%d")
        trend_labels.append(str(label)[:10])
        trend_values.append(t.get("avg_score", 0))

    regression_count = len(regressions) if regressions else 0

    html = HTML_TEMPLATE.format(
        repo_name=repo_name,
        version=version,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"),
        avg_score=avg_score,
        avg_class=avg_class,
        trend_indicator=trend_indicator,
        capability_count=len(capabilities),
        high_count=high_count,
        regression_count=regression_count,
        run_count=len(trend_data),
        distribution_json=json.dumps([high_count, medium_count, low_count]),
        trend_json=json.dumps({"labels": trend_labels, "values": trend_values}),
        capability_rows="\n".join(rows),
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")


def generate_capability_detail(
    capability: dict,
    trend_history: list[dict],
    output_path: Path,
) -> None:
    """
    Generate detailed HTML page for a single capability.

    Args:
        capability: Capability dictionary
        trend_history: Historical trend data for this capability
        output_path: Path to write HTML file
    """
    cap_id = capability.get("id", "unknown")
    score = capability.get("score", 0)
    components = capability.get("components", {})

    # Build trend data for chart
    trend_labels = []
    trend_values = []
    for i, t in enumerate(reversed(trend_history[-50:])):
        ts = t.get("timestamp")
        if ts:
            label = datetime.fromtimestamp(ts).strftime("%m/%d %H:%M")
        else:
            label = f"Run {i + 1}"
        trend_labels.append(label)
        trend_values.append(t.get("score", 0))

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{cap_id} - Capability Detail</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg-primary: #1a1a2e;
            --bg-secondary: #16213e;
            --text-primary: #eee;
            --text-secondary: #aaa;
            --success: #4ade80;
        }}
        body {{
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            padding: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }}
        .card {{
            background: var(--bg-secondary);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        h1 {{ margin-bottom: 10px; }}
        .score {{ font-size: 3rem; color: var(--success); }}
        .chart-container {{ height: 400px; }}
        .component-bar {{
            margin: 10px 0;
        }}
        .component-bar label {{
            display: inline-block;
            width: 120px;
            color: var(--text-secondary);
        }}
        .bar {{
            display: inline-block;
            height: 20px;
            background: var(--success);
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <div class="card">
        <h1>{cap_id}</h1>
        <div class="score">{score:.3f}</div>
    </div>

    <div class="card">
        <h2>Components</h2>
        {"".join(f'''
        <div class="component-bar">
            <label>{comp}:</label>
            <div class="bar" style="width: {val * 300}px;"></div>
            <span>{val:.3f}</span>
        </div>
        ''' for comp, val in sorted(components.items()))}
    </div>

    <div class="card">
        <h2>Score History</h2>
        <div class="chart-container">
            <canvas id="historyChart"></canvas>
        </div>
    </div>

    <script>
        new Chart(document.getElementById('historyChart'), {{
            type: 'line',
            data: {{
                labels: {json.dumps(trend_labels)},
                datasets: [{{
                    label: 'Score',
                    data: {json.dumps(trend_values)},
                    borderColor: '#4ade80',
                    tension: 0.3,
                    fill: false
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{ min: 0, max: 1, ticks: {{ color: '#aaa' }} }},
                    x: {{ ticks: {{ color: '#aaa', maxRotation: 45 }} }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
