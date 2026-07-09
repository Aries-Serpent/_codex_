"""
Real-time analytics dashboard for RAG metrics.

Generates HTML dashboard with charts and statistics.
"""

from datetime import datetime, timezone
from pathlib import Path

from .metrics_db import MetricsDatabase


class AnalyticsDashboard:
    """Generate and serve RAG analytics dashboard."""

    def __init__(self, metrics_db: MetricsDatabase):
        """
        Initialize dashboard generator.

        Args:
            metrics_db: Metrics database instance
        """
        self.metrics_db = metrics_db

    def generate_html(self, hours: int = 24) -> str:
        """
        Generate HTML dashboard.

        Args:
            hours: Time window for metrics

        Returns:
            HTML string
        """
        stats = self.metrics_db.get_stats(hours=hours)
        percentiles = self.metrics_db.get_percentiles(hours=hours)

        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RAG Analytics Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1 {{
            color: #333;
            margin-bottom: 30px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .stat-label {{
            color: #666;
            font-size: 14px;
            margin-bottom: 8px;
        }}
        .stat-value {{
            color: #333;
            font-size: 28px;
            font-weight: bold;
        }}
        .stat-unit {{
            color: #999;
            font-size: 16px;
        }}
        .chart-container {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .timestamp {{
            text-align: center;
            color: #999;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>RAG Analytics Dashboard</h1>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total Queries</div>
                <div class="stat-value">{stats["total_queries"]}</div>
            </div>

            <div class="stat-card">
                <div class="stat-label">Avg Latency</div>
                <div class="stat-value">
                    {stats["avg_latency_ms"]}
                    <span class="stat-unit">ms</span>
                </div>
            </div>

            <div class="stat-card">
                <div class="stat-label">Cache Hit Rate</div>
                <div class="stat-value">
                    {stats["cache_hit_rate"]}
                    <span class="stat-unit">%</span>
                </div>
            </div>

            <div class="stat-card">
                <div class="stat-label">Avg Results</div>
                <div class="stat-value">{stats["avg_results"]:.1f}</div>
            </div>
        </div>

        <div class="chart-container">
            <h2>Latency Percentiles</h2>
            <canvas id="percentiles-chart"></canvas>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">P50 Latency</div>
                <div class="stat-value">
                    {percentiles["p50"]:.1f}
                    <span class="stat-unit">ms</span>
                </div>
            </div>

            <div class="stat-card">
                <div class="stat-label">P95 Latency</div>
                <div class="stat-value">
                    {percentiles["p95"]:.1f}
                    <span class="stat-unit">ms</span>
                </div>
            </div>

            <div class="stat-card">
                <div class="stat-label">P99 Latency</div>
                <div class="stat-value">
                    {percentiles["p99"]:.1f}
                    <span class="stat-unit">ms</span>
                </div>
            </div>
        </div>

        <div class="timestamp">
            Last updated: {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")}
        </div>
    </div>

    <script>
        // Percentiles chart
        const ctx = document.getElementById('percentiles-chart').getContext('2d');
        new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: ['P50', 'P95', 'P99'],
                datasets: [{{
                    label: 'Latency (ms)',
                    data: [{percentiles["p50"]:.1f}, {percentiles["p95"]:.1f}, {percentiles["p99"]:.1f}],
                    backgroundColor: [
                        'rgba(75, 192, 192, 0.8)',
                        'rgba(255, 206, 86, 0.8)',
                        'rgba(255, 99, 132, 0.8)'
                    ],
                    borderColor: [
                        'rgba(75, 192, 192, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(255, 99, 132, 1)'
                    ],
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{
                            display: true,
                            text: 'Latency (ms)'
                        }}
                    }}
                }}
            }}
        }});

        // Auto-refresh every 30 seconds
        setTimeout(() => location.reload(), 30000);
    </script>
</body>
</html>
"""  # noqa: E501

    def save_to_file(self, output_path: Path, hours: int = 24) -> None:
        """
        Save dashboard HTML to file.

        Args:
            output_path: Path to output HTML file
            hours: Time window for metrics
        """
        html = self.generate_html(hours=hours)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            f.write(html)
