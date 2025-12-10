#!/usr/bin/env python3
"""
Generate an index.html dashboard for audit artifacts.

This script scans audit_artifacts/, reports/, and audit_run_manifest.json
to create an interactive web-based dashboard for reviewing audit results.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


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
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, OSError):
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
                files.append({
                    "path": str(rel_path),
                    "name": item.name,
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                    "type": item.suffix or "file"
                })
            except OSError:
                # Skip files that can't be accessed
                pass
    
    return files


def load_manifest(manifest_path: Path) -> dict[str, Any]:
    """Load audit run manifest if it exists."""
    if not manifest_path.exists():
        return {}
    
    try:
        with open(manifest_path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def generate_html_dashboard(
    audit_artifacts: list[dict[str, Any]],
    reports: list[dict[str, Any]],
    manifest: dict[str, Any],
    output_path: Path
) -> None:
    """Generate HTML dashboard for audit artifacts."""
    
    # Extract manifest data
    manifest_artifacts = manifest.get("artifacts", [])
    manifest_version = manifest.get("version", "Unknown")
    manifest_timestamp = manifest.get("timestamp", 0)
    manifest_weights = manifest.get("weights", {})
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Audit Dashboard - Determinism & Validation</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: #24292e;
            background: #f6f8fa;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12);
            padding: 30px;
        }}
        
        header {{
            border-bottom: 2px solid #e1e4e8;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        
        h1 {{
            font-size: 32px;
            font-weight: 600;
            color: #0366d6;
            margin-bottom: 10px;
        }}
        
        .metadata {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            background: #f6f8fa;
            padding: 20px;
            border-radius: 6px;
            margin-bottom: 30px;
        }}
        
        .metadata-item {{
            display: flex;
            flex-direction: column;
        }}
        
        .metadata-label {{
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            color: #586069;
            margin-bottom: 5px;
        }}
        
        .metadata-value {{
            font-size: 14px;
            color: #24292e;
            font-weight: 500;
        }}
        
        h2 {{
            font-size: 24px;
            font-weight: 600;
            margin: 30px 0 15px 0;
            color: #24292e;
            border-bottom: 1px solid #e1e4e8;
            padding-bottom: 10px;
        }}
        
        .section {{
            margin-bottom: 40px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            font-size: 14px;
        }}
        
        thead {{
            background: #f6f8fa;
        }}
        
        th {{
            text-align: left;
            padding: 12px;
            font-weight: 600;
            color: #24292e;
            border-bottom: 2px solid #e1e4e8;
        }}
        
        td {{
            padding: 12px;
            border-bottom: 1px solid #e1e4e8;
        }}
        
        tbody tr:hover {{
            background: #f6f8fa;
        }}
        
        a {{
            color: #0366d6;
            text-decoration: none;
        }}
        
        a:hover {{
            text-decoration: underline;
        }}
        
        .badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
            background: #0366d6;
            color: white;
        }}
        
        .badge.json {{ background: #28a745; }}
        .badge.md {{ background: #6f42c1; }}
        .badge.txt {{ background: #586069; }}
        .badge.html {{ background: #d73a49; }}
        
        .weights {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 10px;
        }}
        
        .weight-item {{
            background: #f1f8ff;
            border: 1px solid #0366d6;
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 13px;
        }}
        
        .weight-label {{
            font-weight: 600;
            color: #0366d6;
        }}
        
        .empty-state {{
            text-align: center;
            padding: 40px;
            color: #586069;
            font-style: italic;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            font-size: 12px;
            text-transform: uppercase;
            opacity: 0.9;
        }}
        
        .search-box {{
            width: 100%;
            padding: 12px;
            border: 2px solid #e1e4e8;
            border-radius: 6px;
            font-size: 14px;
            margin-bottom: 20px;
        }}
        
        .search-box:focus {{
            outline: none;
            border-color: #0366d6;
        }}
        
        footer {{
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #e1e4e8;
            text-align: center;
            color: #586069;
            font-size: 12px;
        }}
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
                <span class="metadata-value">{manifest_version}</span>
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

    # Scoring weights section
    if manifest_weights:
        html_content += """
        <div class="section">
            <h2>📊 Scoring Weights</h2>
            <div class="weights">
"""
        for key, value in manifest_weights.items():
            html_content += f"""                <div class="weight-item">
                    <span class="weight-label">{key.title()}:</span> {value}
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
            badge_class = ext if ext in ["json", "md", "txt", "html"] else "badge"
            html_content += f"""                    <tr>
                        <td><a href="{artifact['path']}">{artifact['name']}</a></td>
                        <td><span class="badge {badge_class}">{ext.upper()}</span></td>
                        <td>{format_size(artifact['size'])}</td>
                        <td>{format_timestamp(artifact['modified'])}</td>
                        <td><code>{artifact['path']}</code></td>
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
            badge_class = ext if ext in ["json", "md", "txt", "html"] else "badge"
            html_content += f"""                    <tr>
                        <td><a href="{report['path']}">{report['name']}</a></td>
                        <td><span class="badge {badge_class}">{ext.upper()}</span></td>
                        <td>{format_size(report['size'])}</td>
                        <td>{format_timestamp(report['modified'])}</td>
                        <td><code>{report['path']}</code></td>
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
            html_content += f"""                    <tr>
                        <td>{artifact.get('name', 'Unknown')}</td>
                        <td><span class="badge {artifact.get('format', 'file')}">{artifact.get('format', 'N/A').upper()}</span></td>
                        <td>{format_size(artifact.get('size', 0))}</td>
                        <td><code style="font-size: 11px;">{artifact.get('sha', 'N/A')[:16]}...</code></td>
                        <td>{format_timestamp(artifact.get('generated_at', 0))}</td>
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
</body>
</html>
"""
    
    # Write HTML to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_content, encoding="utf-8")


def main() -> int:
    """Main entry point."""
    repo_root = Path(__file__).parent.parent
    
    # Scan directories
    audit_artifacts_path = repo_root / "audit_artifacts"
    reports_path = repo_root / "reports"
    manifest_path = repo_root / "audit_run_manifest.json"
    output_path = repo_root / "index.html"
    
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
    
    print("🎨 Generating HTML dashboard...")
    generate_html_dashboard(audit_artifacts, reports, manifest, output_path)
    print(f"✅ Dashboard generated: {output_path}")
    print(f"   Total artifacts indexed: {len(audit_artifacts) + len(reports)}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
