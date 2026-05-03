"""FastAPI dashboard for real-time CI/CD and security metrics."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

app = FastAPI(
    title="Codex Monitoring Dashboard",
    description="Real-time monitoring for CI/CD workflows and security metrics",
    version="1.0.0",
)

# CORS configuration - restrict in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint with dashboard info."""
    return {
        "name": "Codex Monitoring Dashboard API",
        "version": "1.0.0",
        "endpoints": {
            "ci_metrics": "/api/metrics/ci",
            "security_metrics": "/api/metrics/security",
            "agent_metrics": "/api/metrics/agents",
            "alerts": "/api/alerts",
            "health": "/health",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/api/metrics/ci")
async def get_ci_metrics() -> dict[str, Any]:
    """Get current CI/CD metrics."""
    # In production, would query from InfluxDB or Prometheus
    metrics_dir = Path("metrics_data")

    # Load latest CI metrics file
    ci_files = sorted(metrics_dir.glob("ci_*.json"), reverse=True)
    if ci_files:
        with open(ci_files[0], encoding="utf-8") as f:
            return json.load(f)

    # Fallback mock data
    return {
        "timestamp": datetime.now().isoformat(),
        "workflow_runs_total": 1250,
        "workflow_success_rate": 0.95,
        "average_duration_seconds": 240,
        "builds_per_day": 50,
        "cache_hit_rate": 0.90,
        "failed_workflows": [],
    }


@app.get("/api/metrics/security")
async def get_security_metrics() -> dict[str, Any]:
    """Get current security metrics."""
    metrics_dir = Path("metrics_data")

    # Load latest security metrics file
    sec_files = sorted(metrics_dir.glob("security_*.json"), reverse=True)
    if sec_files:
        with open(sec_files[0], encoding="utf-8") as f:
            return json.load(f)

    # Fallback mock data
    return {
        "timestamp": datetime.now().isoformat(),
        "security_score": 98,
        "vulnerabilities_total": 0,
        "vulnerabilities_by_severity": {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
        },
        "dependabot_alerts": 0,
        "codeql_alerts": 0,
        "last_security_scan": datetime.now().isoformat(),
    }


@app.get("/api/metrics/agents")
async def get_agent_metrics() -> dict[str, Any]:
    """Get custom agent performance metrics."""
    metrics_dir = Path("metrics_data")

    # Load latest agent metrics file
    agent_files = sorted(metrics_dir.glob("agents_*.json"), reverse=True)
    if agent_files:
        with open(agent_files[0], encoding="utf-8") as f:
            return json.load(f)

    # Fallback mock data
    return {
        "timestamp": datetime.now().isoformat(),
        "ml_threat_detections": 23,
        "ci_diagnostic_runs": 47,
        "auto_fixes_applied": 12,
        "pattern_recognition_accuracy": 0.87,
    }


@app.get("/api/alerts")
async def get_alerts() -> dict[str, Any]:
    """Get active and recent alerts."""
    return {
        "active_alerts": [],
        "resolved_today": 5,
        "critical_count": 0,
        "warning_count": 2,
    }


@app.get("/api/metrics/history/ci")
async def get_ci_history(hours: int = 24) -> list[dict[str, Any]]:
    """Get historical CI metrics."""
    # Would query time-series database
    # For now, return empty or load from files
    return []


@app.get("/api/metrics/history/security")
async def get_security_history(hours: int = 24) -> list[dict[str, Any]]:
    """Get historical security metrics."""
    # Would query time-series database
    return []


@app.get("/ui", response_class=HTMLResponse)
async def dashboard_ui():
    """Serve dashboard HTML UI."""
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Codex Monitoring Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .header h1 { font-size: 32px; margin-bottom: 10px; }
        .header p { opacity: 0.9; }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .metric-card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        .metric-value {
            font-size: 42px;
            font-weight: bold;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .metric-label {
            font-size: 14px;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .metric-subtitle {
            font-size: 12px;
            color: #999;
            margin-top: 5px;
        }
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .status-healthy { background: #10b981; }
        .status-warning { background: #f59e0b; }
        .status-critical { background: #ef4444; }
        .last-updated {
            text-align: center;
            color: #999;
            font-size: 12px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Codex Monitoring Dashboard</h1>
        <p>Real-time CI/CD & Security Metrics</p>
    </div>

    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-value" id="security-score">--</div>
            <div class="metric-label">Security Score</div>
            <div class="metric-subtitle">
                <span class="status-indicator status-healthy"></span>
                <span id="vuln-count">0 vulnerabilities</span>
            </div>
        </div>

        <div class="metric-card">
            <div class="metric-value" id="success-rate">--</div>
            <div class="metric-label">CI Success Rate</div>
            <div class="metric-subtitle" id="total-runs">-- total runs</div>
        </div>

        <div class="metric-card">
            <div class="metric-value" id="avg-duration">--</div>
            <div class="metric-label">Avg Build Time</div>
            <div class="metric-subtitle">Last 100 builds</div>
        </div>

        <div class="metric-card">
            <div class="metric-value" id="cache-hit">--</div>
            <div class="metric-label">Cache Hit Rate</div>
            <div class="metric-subtitle">Optimization metric</div>
        </div>

        <div class="metric-card">
            <div class="metric-value" id="ml-detections">--</div>
            <div class="metric-label">ML Threat Detections</div>
            <div class="metric-subtitle">AI-powered security</div>
        </div>

        <div class="metric-card">
            <div class="metric-value" id="auto-fixes">--</div>
            <div class="metric-label">Auto-Fixes Applied</div>
            <div class="metric-subtitle">Self-healing system</div>
        </div>
    </div>

    <div class="last-updated">
        Last updated: <span id="last-update">--</span> |
        Auto-refresh: 30s
    </div>

    <script>
        async function fetchMetrics() {
            try {
                // Fetch CI metrics
                const ciResponse = await fetch('/api/metrics/ci');
                const ciData = await ciResponse.json();

                // Fetch security metrics
                const secResponse = await fetch('/api/metrics/security');
                const secData = await secResponse.json();

                // Fetch agent metrics
                const agentResponse = await fetch('/api/metrics/agents');
                const agentData = await agentResponse.json();

                // Update UI
                document.getElementById('security-score').textContent = secData.security_score;
                document.getElementById('vuln-count').textContent =
                    `${secData.vulnerabilities_total} vulnerabilities`;

                document.getElementById('success-rate').textContent =
                    `${(ciData.workflow_success_rate * 100).toFixed(1)}%`;
                document.getElementById('total-runs').textContent =
                    `${ciData.workflow_runs_total} total runs`;

                document.getElementById('avg-duration').textContent =
                    `${Math.round(ciData.average_duration_seconds)}s`;

                document.getElementById('cache-hit').textContent =
                    `${(ciData.cache_hit_rate * 100).toFixed(1)}%`;

                document.getElementById('ml-detections').textContent = agentData.ml_threat_detections;
                document.getElementById('auto-fixes').textContent = agentData.auto_fixes_applied;

                document.getElementById('last-update').textContent =
                    new Date().toLocaleTimeString();

            } catch (error) {
                console.error('Error fetching metrics:', error);
            }
        }

        // Initial fetch
        fetchMetrics();

        // Auto-refresh every 30 seconds
        setInterval(fetchMetrics, 30000);
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
