#!/usr/bin/env python3
"""
Generate Audit Dashboard

Purpose:
    Generates audit_dashboard

Usage:
    python scripts/generate_audit_dashboard.py [options]

    Examples:
    $ python scripts/generate_audit_dashboard.py --help

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



import html
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Import planning components
try:
    from planning_components import (
        generate_planning_html,
        generate_planning_javascript,
    )

    PLANNING_AVAILABLE = True
except ImportError as e:
    error_type = type(e).__name__
    logger.debug("ImportError: <ERROR_TYPE>")
    PLANNING_AVAILABLE = False

# Supported file extensions for badge styling
SUPPORTED_EXTENSIONS = {"json", "md", "txt", "html"}


def format_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def format_timestamp(timestamp: float) -> str:
    """Format Unix timestamp to human-readable date."""
    try:
        # Reject clearly invalid timestamps (negative or unreasonably large)
        if timestamp < 0 or timestamp > 32503680000:  # Max: year 3000
            return "Unknown"
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, OSError):
        logger.debug("Exception caught, returning", exc_info=True)
        return "Unknown"


def scan_directory(base_path: Path) -> list[dict[str, Any]]:
    """Scan directory for files and return metadata."""
    files = []
    if not base_path.exists():
        return files

    for item in sorted(base_path.rglob("*")):
        if item.is_file():
            rel_path = item.relative_to(base_path.parent)
            try:
                stat = item.stat()
                files.append(
                    {
                        "path": str(rel_path),
                        "name": item.name,
                        "size": stat.st_size,
                        "modified": stat.st_mtime,
                        "type": item.suffix or "file",
                    }
                )
            except OSError as e:
                error_type = type(e).__name__
                logger.debug("OSError: <ERROR_TYPE>")
                logger.warning("OSError: <ERROR_TYPE>", exc_info=True)
                # Skip files that can't be accessed

    return files


def load_manifest(manifest_path: Path) -> dict[str, Any]:
    """Load audit run manifest if it exists."""
    if not manifest_path.exists():
        return {}

    try:
        with open(manifest_path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {}


def load_gaps_and_plans(base_path: Path) -> dict[str, Any]:
    """Load gaps and improvement plans from audit artifacts."""
    gaps_data = {}
    plans_data = {}

    # Load gaps.json
    gaps_file = base_path / "audit_artifacts" / "gaps.json"
    if gaps_file.exists():
        try:
            with open(gaps_file, encoding="utf-8") as f:
                gaps_data = json.load(f)
        except json.JSONDecodeError:
            # gaps.json is optional; if corrupt, log warning and continue with empty gaps data.
            logger.warning("Could not parse gaps.json (corrupt JSON): <ERROR_TYPE>")
        except OSError as e:
            error_type = type(e).__name__
            logger.debug("OSError: <ERROR_TYPE>")
            # gaps.json is optional; if unreadable, log warning and continue with empty gaps data.
            logger.warning("Could not read gaps.json (I/O error): <ERROR_TYPE>")

    # Load improvement plan MD file
    plan_file = base_path / "audit_artifacts" / "HIGH_MATURITY_ACHIEVEMENT_PLAN.md"
    if plan_file.exists():
        try:
            plans_data["plan_content"] = plan_file.read_text(encoding="utf-8")
            # Extract phases from the plan
            phases = []
            lines = plans_data["plan_content"].split("\n")
            for line in lines:
                if line.startswith("## Phase "):
                    phases.append(line.strip("# ").strip())
            plans_data["phases"] = phases
        except OSError as e:
            error_type = type(e).__name__
            logger.debug("OSError: <ERROR_TYPE>")
            logger.warning("OSError: <ERROR_TYPE>", exc_info=True)
            # The plan file is optional; skip if it cannot be read.

    return {"gaps": gaps_data, "plans": plans_data}


def generate_html_dashboard(
    audit_artifacts: list[dict[str, Any]],
    reports: list[dict[str, Any]],
    manifest: dict[str, Any],
    output_path: Path,
    gaps_and_plans: dict[str, Any] | None = None,
) -> None:
    """Generate HTML dashboard for audit artifacts."""

    # Extract manifest data
    manifest_artifacts = manifest.get("artifacts", [])
    manifest_version = manifest.get("version", "Unknown")
    manifest_timestamp = manifest.get("timestamp", 0)
    manifest_weights = manifest.get("weights", {})

    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Audit Dashboard - Determinism & Validation</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: #24292e;
            background: #f6f8fa;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12);
            padding: 30px;
        }

        header {
            border-bottom: 2px solid #e1e4e8;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }

        h1 {
            font-size: 32px;
            font-weight: 600;
            color: #0366d6;
            margin-bottom: 10px;
        }

        .metadata {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            background: #f6f8fa;
            padding: 20px;
            border-radius: 6px;
            margin-bottom: 30px;
        }

        .metadata-item {
            display: flex;
            flex-direction: column;
        }

        .metadata-label {
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            color: #586069;
            margin-bottom: 5px;
        }

        .metadata-value {
            font-size: 14px;
            color: #24292e;
            font-weight: 500;
        }

        h2 {
            font-size: 24px;
            font-weight: 600;
            margin: 30px 0 15px 0;
            color: #24292e;
            border-bottom: 1px solid #e1e4e8;
            padding-bottom: 10px;
        }

        .section {
            margin-bottom: 40px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            font-size: 14px;
        }

        thead {
            background: #f6f8fa;
        }

        th {
            text-align: left;
            padding: 12px;
            font-weight: 600;
            color: #24292e;
            border-bottom: 2px solid #e1e4e8;
        }

        td {
            padding: 12px;
            border-bottom: 1px solid #e1e4e8;
        }

        tbody tr:hover {
            background: #f6f8fa;
        }

        a {
            color: #0366d6;
            text-decoration: none;
        }

        a:hover {
            text-decoration: underline;
        }

        .badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
            background: #0366d6;
            color: white;
        }

        .badge.json { background: #28a745; }
        .badge.md { background: #6f42c1; }
        .badge.txt { background: #586069; }
        .badge.html { background: #d73a49; }

        .weights {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 10px;
        }

        .weight-item {
            background: #f1f8ff;
            border: 1px solid #0366d6;
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 13px;
        }

        .weight-label {
            font-weight: 600;
            color: #0366d6;
        }

        .empty-state {
            text-align: center;
            padding: 40px;
            color: #586069;
            font-style: italic;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }

        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }

        .stat-value {
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 5px;
        }

        .stat-label {
            font-size: 12px;
            text-transform: uppercase;
            opacity: 0.9;
        }

        .search-box {
            width: 100%;
            padding: 12px;
            border: 2px solid #e1e4e8;
            border-radius: 6px;
            font-size: 14px;
            margin-bottom: 20px;
        }

        .search-box:focus {
            outline: none;
            border-color: #0366d6;
        }

        footer {
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #e1e4e8;
            text-align: center;
            color: #586069;
            font-size: 12px;
        }
"""

    # Add planning CSS if available
    if PLANNING_AVAILABLE and gaps_and_plans:
        try:
            from planning_components import generate_planning_css

            html_content += generate_planning_css()
        except ImportError as e:
            error_type = type(e).__name__
            logger.debug("ImportError: <ERROR_TYPE>")

    html_content += """
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔍 Audit Dashboard</h1>
            <p>Determinism & Validation Artifacts</p>
        </header>

        <div class="metadata">
            <div class="metadata-item">
                <span class="metadata-label">Audit Version</span>
                <span class="metadata-value">{html.escape(manifest_version)}</span>
            </div>
            <div class="metadata-item">
                <span class="metadata-label">Generated At</span>
                <span class="metadata-value">{format_timestamp(manifest_timestamp)}</span>
            </div>
            <div class="metadata-item">
                <span class="metadata-label">Total Artifacts</span>
                <span class="metadata-value">{len(audit_artifacts) + len(reports)}</span>
            </div>
            <div class="metadata-item">
                <span class="metadata-label">Manifest Entries</span>
                <span class="metadata-value">{len(manifest_artifacts)}</span>
            </div>
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{len(audit_artifacts)}</div>
                <div class="stat-label">Audit Artifacts</div>
            </div>
            <div class="stat-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                <div class="stat-value">{len(reports)}</div>
                <div class="stat-label">Reports</div>
            </div>
            <div class="stat-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                <div class="stat-value">{len(manifest_artifacts)}</div>
                <div class="stat-label">Registered</div>
            </div>
        </div>
"""

    # Add interactive planning section if available
    if PLANNING_AVAILABLE and gaps_and_plans:
        html_content += generate_planning_html(gaps_and_plans)

    # Scoring weights section
    if manifest_weights:
        html_content += """
        <div class="section">
            <h2>📊 Scoring Weights</h2>
            <div class="weights">
"""
        for key, value in manifest_weights.items():
            escaped_key = html.escape(str(key))
            escaped_value = html.escape(str(value))
            html_content += f"""                <div class="weight-item">
                    <span class="weight-label">{escaped_key.title()}:</span> {escaped_value}
                </div>
"""
        html_content += """            </div>
        </div>
"""

    # Audit Artifacts section
    html_content += """
        <div class="section">
            <h2>📦 Audit Artifacts</h2>
            <input type="text" class="search-box" id="artifactsSearch" placeholder="Search audit artifacts..." onkeyup="filterTable('artifactsTable', 'artifactsSearch')">
"""

    if audit_artifacts:
        html_content += """            <table id="artifactsTable">
                <thead>
                    <tr>
                        <th>File Name</th>
                        <th>Type</th>
                        <th>Size</th>
                        <th>Modified</th>
                        <th>Path</th>
                    </tr>
                </thead>
                <tbody>
"""
        for artifact in audit_artifacts:
            ext = artifact["type"].lstrip(".")
            badge_class = ext if ext in SUPPORTED_EXTENSIONS else "badge"
            # Escape all user-controlled data to prevent XSS
            escaped_path = html.escape(artifact["path"])
            escaped_name = html.escape(artifact["name"])
            escaped_badge_class = html.escape(badge_class)
            escaped_ext = html.escape(ext.upper())

            html_content += f"""                    <tr>
                        <td><a href="{escaped_path}">{escaped_name}</a></td>
                        <td><span class="badge {escaped_badge_class}">{escaped_ext}</span></td>
                        <td>{format_size(artifact['size'])}</td>
                        <td>{format_timestamp(artifact['modified'])}</td>
                        <td><code>{escaped_path}</code></td>
                    </tr>
"""
        html_content += """                </tbody>
            </table>
"""
    else:
        html_content += """            <div class="empty-state">No audit artifacts found</div>
"""

    html_content += """        </div>
"""

    # Reports section
    html_content += """
        <div class="section">
            <h2>📄 Reports</h2>
            <input type="text" class="search-box" id="reportsSearch" placeholder="Search reports..." onkeyup="filterTable('reportsTable', 'reportsSearch')">
"""

    if reports:
        html_content += """            <table id="reportsTable">
                <thead>
                    <tr>
                        <th>File Name</th>
                        <th>Type</th>
                        <th>Size</th>
                        <th>Modified</th>
                        <th>Path</th>
                    </tr>
                </thead>
                <tbody>
"""
        for report in reports:
            ext = report["type"].lstrip(".")
            badge_class = ext if ext in SUPPORTED_EXTENSIONS else "badge"
            # Escape all user-controlled data to prevent XSS
            escaped_path = html.escape(report["path"])
            escaped_name = html.escape(report["name"])
            escaped_badge_class = html.escape(badge_class)
            escaped_ext = html.escape(ext.upper())

            html_content += f"""                    <tr>
                        <td><a href="{escaped_path}">{escaped_name}</a></td>
                        <td><span class="badge {escaped_badge_class}">{escaped_ext}</span></td>
                        <td>{format_size(report['size'])}</td>
                        <td>{format_timestamp(report['modified'])}</td>
                        <td><code>{escaped_path}</code></td>
                    </tr>
"""
        html_content += """                </tbody>
            </table>
"""
    else:
        html_content += """            <div class="empty-state">No reports found</div>
"""

    html_content += """        </div>
"""

    # Manifest Artifacts section
    if manifest_artifacts:
        html_content += """
        <div class="section">
            <h2>📋 Manifest Registry</h2>
            <p style="margin-bottom: 15px; color: #586069;">Artifacts registered in audit_run_manifest.json</p>
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Format</th>
                        <th>Size</th>
                        <th>SHA-256</th>
                        <th>Generated At</th>
                    </tr>
                </thead>
                <tbody>
"""
        for artifact in manifest_artifacts:
            artifact_format = artifact.get("format", "file")
            artifact_name = artifact.get("name", "Unknown")
            artifact_size = artifact.get("size", 0)
            artifact_sha = artifact.get("sha", "N/A")
            # Safe SHA truncation - only truncate if we have a valid SHA
            sha_display = f"{artifact_sha[:16]}..." if len(artifact_sha) > 16 else artifact_sha
            artifact_timestamp = artifact.get("generated_at", 0)

            # Escape all manifest data to prevent XSS from malicious JSON
            escaped_name = html.escape(artifact_name)
            escaped_format = html.escape(artifact_format)
            escaped_format_upper = html.escape(artifact_format.upper())
            escaped_sha = html.escape(sha_display)

            html_content += f"""                    <tr>
                        <td>{escaped_name}</td>
                        <td><span class="badge {escaped_format}">{escaped_format_upper}</span></td>
                        <td>{format_size(artifact_size)}</td>
                        <td><code style="font-size: 11px;">{escaped_sha}</code></td>
                        <td>{format_timestamp(artifact_timestamp)}</td>
                    </tr>
"""
        html_content += """                </tbody>
            </table>
        </div>
"""

    # Footer with JavaScript
    html_content += f"""
        <footer>
            <p>Generated by Audit Dashboard Generator • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </footer>
    </div>

    <script>
        function filterTable(tableId, searchId) {{
            const input = document.getElementById(searchId);
            const filter = input.value.toUpperCase();
            const table = document.getElementById(tableId);
            const tr = table ? table.getElementsByTagName('tr') : [];

            for (let i = 1; i < tr.length; i++) {{
                let txtValue = tr[i].textContent || tr[i].innerText;
                if (txtValue.toUpperCase().indexOf(filter) > -1) {{
                    tr[i].style.display = '';
                }} else {{
                    tr[i].style.display = 'none';
                }}
            }}
        }}

        // Add tooltips on hover for long paths
        document.querySelectorAll('code').forEach(el => {{
            el.title = el.textContent;
        }});
    </script>
"""

    # Add planning JavaScript if available
    if PLANNING_AVAILABLE and gaps_and_plans:
        html_content += generate_planning_javascript()

    html_content += """
</body>
</html>
"""

    # Substitute manifest metadata placeholders (template strings are not f-strings)
    html_content = (
        html_content
        .replace("{html.escape(manifest_version)}", html.escape(str(manifest_version)))
        .replace("{format_timestamp(manifest_timestamp)}", format_timestamp(manifest_timestamp))
    )

    # Write HTML to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_content, encoding="utf-8")


def main() -> int:
    """Main entry point."""
    repo_root = Path(__file__).parent.parent

    # Scan directories
    audit_artifacts_path = repo_root / "audit_artifacts"
    reports_path = repo_root / ".codex" / "reports"
    manifest_path = repo_root / "audit_run_manifest.json"
    output_path = repo_root / ".codex" / "reports" / "audit_dashboard.html"

    print("🔍 Scanning audit artifacts...")
    audit_artifacts = scan_directory(audit_artifacts_path)
    print(f"   Found {len(audit_artifacts)} audit artifacts")

    print("📄 Scanning reports...")
    reports = scan_directory(reports_path)
    print(f"   Found {len(reports)} reports")

    print("📋 Loading manifest...")
    manifest = load_manifest(manifest_path)
    manifest_count = len(manifest.get("artifacts", []))
    print(f"   Found {manifest_count} manifest entries")

    print("🎯 Loading gaps and plans...")
    gaps_and_plans = load_gaps_and_plans(repo_root)
    gap_count = len(gaps_and_plans.get("gaps", {}).get("low_maturity", []))
    plan_count = len(gaps_and_plans.get("plans", {}).get("phases", []))
    print(f"   Found {gap_count} low maturity capabilities, {plan_count} phases")

    print("🎨 Generating HTML dashboard...")
    generate_html_dashboard(audit_artifacts, reports, manifest, output_path, gaps_and_plans)
    print(f"✅ Dashboard generated: {output_path}")
    print(f"   Total artifacts indexed: {len(audit_artifacts) + len(reports)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
