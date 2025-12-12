"""
Documentation Hub Generator for Audit Pipeline v1.5.x

Generates an interactive HTML documentation hub that sources and displays
all documentation from the repository, with clear navigation and search.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

__all__ = ["generate_docs_hub", "DOCS_HUB_TEMPLATE"]


DOCS_HUB_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Documentation Hub - {repo_name}</title>
    <style>
        :root {{
            --bg-primary: #0d1117;
            --bg-secondary: #161b22;
            --bg-tertiary: #21262d;
            --bg-card: #1c2128;
            --accent: #58a6ff;
            --accent-green: #3fb950;
            --accent-orange: #d29922;
            --accent-purple: #a371f7;
            --text-primary: #c9d1d9;
            --text-secondary: #8b949e;
            --border: #30363d;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
        }}
        
        /* Header */
        .header {{
            background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%);
            padding: 40px 20px;
            text-align: center;
            border-bottom: 1px solid var(--border);
        }}
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
        }}
        .header .subtitle {{
            color: var(--text-secondary);
            font-size: 1.1rem;
        }}
        .header .version {{
            display: inline-block;
            background: var(--accent);
            color: #000;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            margin-top: 15px;
        }}
        
        /* Search */
        .search-container {{
            max-width: 600px;
            margin: -25px auto 30px;
            padding: 0 20px;
        }}
        .search-box {{
            width: 100%;
            padding: 15px 20px;
            font-size: 1rem;
            border: 2px solid var(--border);
            border-radius: 10px;
            background: var(--bg-secondary);
            color: var(--text-primary);
            outline: none;
            transition: border-color 0.2s;
        }}
        .search-box:focus {{
            border-color: var(--accent);
        }}
        
        /* Container */
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        /* Category Grid */
        .category-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 25px;
            margin-bottom: 40px;
        }}
        
        /* Category Card */
        .category-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            overflow: hidden;
        }}
        .category-header {{
            padding: 20px;
            background: var(--bg-tertiary);
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .category-icon {{
            font-size: 1.5rem;
        }}
        .category-title {{
            font-size: 1.2rem;
            font-weight: 600;
        }}
        .category-count {{
            margin-left: auto;
            background: var(--bg-primary);
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 0.8rem;
            color: var(--text-secondary);
        }}
        
        /* Doc Items */
        .doc-list {{
            padding: 10px;
        }}
        .doc-item {{
            display: flex;
            align-items: center;
            padding: 12px 15px;
            border-radius: 8px;
            cursor: pointer;
            transition: background 0.2s;
        }}
        .doc-item:hover {{
            background: var(--bg-tertiary);
        }}
        .doc-item .icon {{
            margin-right: 12px;
            font-size: 1.2rem;
        }}
        .doc-item .info {{
            flex: 1;
        }}
        .doc-item .title {{
            font-weight: 500;
            margin-bottom: 2px;
        }}
        .doc-item .desc {{
            font-size: 0.85rem;
            color: var(--text-secondary);
        }}
        .doc-item .badge {{
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.75rem;
            text-transform: uppercase;
        }}
        .badge-new {{ background: var(--accent-green); color: #000; }}
        .badge-updated {{ background: var(--accent-orange); color: #000; }}
        .badge-api {{ background: var(--accent-purple); color: #fff; }}
        
        /* Quick Links */
        .quick-links {{
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            justify-content: center;
            margin: 30px 0;
            padding: 20px;
            background: var(--bg-secondary);
            border-radius: 12px;
        }}
        .quick-link {{
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 10px 20px;
            background: var(--bg-tertiary);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text-primary);
            text-decoration: none;
            transition: all 0.2s;
        }}
        .quick-link:hover {{
            border-color: var(--accent);
            background: var(--bg-card);
        }}
        
        /* Mermaid Diagram Section */
        .diagram-section {{
            margin: 40px 0;
            padding: 30px;
            background: var(--bg-secondary);
            border-radius: 12px;
            border: 1px solid var(--border);
        }}
        .diagram-section h2 {{
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .mermaid {{
            background: var(--bg-primary);
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
        }}
        
        /* Footer */
        .footer {{
            text-align: center;
            padding: 30px;
            color: var(--text-secondary);
            border-top: 1px solid var(--border);
            margin-top: 40px;
        }}
    </style>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
</head>
<body>
    <div class="header">
        <h1>📚 Documentation Hub</h1>
        <div class="subtitle">{repo_name} - Comprehensive Documentation Portal</div>
        <span class="version">v{version}</span>
    </div>
    
    <div class="search-container">
        <input type="text" class="search-box" placeholder="🔍 Search documentation..." id="searchInput" onkeyup="filterDocs()">
    </div>
    
    <div class="container">
        <!-- Quick Links -->
        <div class="quick-links">
            <a href="#getting-started" class="quick-link">🚀 Getting Started</a>
            <a href="#api-reference" class="quick-link">📖 API Reference</a>
            <a href="#audit-pipeline" class="quick-link">🔍 Audit Pipeline</a>
            <a href="#cli-tools" class="quick-link">⌨️ CLI Tools</a>
            <a href="#architecture" class="quick-link">🏗️ Architecture</a>
            <a href="#wiki" class="quick-link">📝 Wiki</a>
        </div>
        
        <!-- Architecture Diagram -->
        <div class="diagram-section" id="architecture">
            <h2>🏗️ System Architecture</h2>
            <div class="mermaid">
flowchart TB
    subgraph AuditPipeline["🔍 Audit Pipeline v1.5.x"]
        direction TB
        AR[audit_runner.py] --> TD[(TrendDatabase)]
        AR --> TC[trend_compare.py]
        AR --> VIZ[Visualization]
        
        subgraph Storage["💾 Storage Layer"]
            TD --> SQLite[(SQLite DB)]
            TD --> Migrations[Schema Migrations]
        end
        
        subgraph Visualization["📊 Visualization"]
            VIZ --> ASCII[viz_ascii.py]
            VIZ --> HTML[viz_html.py]
            VIZ --> CLI_B[viz_cli_builder.py]
            VIZ --> API_C[viz_api_collection.py]
            VIZ --> SWAGGER[viz_swagger.py]
            VIZ --> DOCS[viz_docs_hub.py]
        end
        
        subgraph Integration["🔗 Integration"]
            WH[webhooks.py] --> Slack
            WH --> Teams
            CI[ci_integration.py] --> GitHub
            CI --> GitLab
            CI --> Jenkins
        end
    end
    
    subgraph Outputs["📤 Generated Outputs"]
        Dashboard[HTML Dashboard]
        Reports[Trend Reports]
        Wiki[Wiki Bundle]
        APIDoc[API Documentation]
    end
    
    VIZ --> Dashboard
    TC --> Reports
    DOCS --> Wiki
    SWAGGER --> APIDoc
            </div>
        </div>
        
        <!-- Documentation Categories -->
        <div class="category-grid" id="docGrid">
            <!-- Getting Started -->
            <div class="category-card" id="getting-started">
                <div class="category-header">
                    <span class="category-icon">🚀</span>
                    <span class="category-title">Getting Started</span>
                    <span class="category-count">5 docs</span>
                </div>
                <div class="doc-list">
                    <div class="doc-item" onclick="openDoc('README.md')">
                        <span class="icon">📄</span>
                        <div class="info">
                            <div class="title">README.md</div>
                            <div class="desc">Main repository overview and quick start</div>
                        </div>
                    </div>
                    <div class="doc-item" onclick="openDoc('AGENTS.md')">
                        <span class="icon">🤖</span>
                        <div class="info">
                            <div class="title">AGENTS.md</div>
                            <div class="desc">Comprehensive guide for AI agents and contributors</div>
                        </div>
                        <span class="badge badge-updated">Updated</span>
                    </div>
                    <div class="doc-item" onclick="openDoc('NEWCOMER_GUIDE.md')">
                        <span class="icon">👋</span>
                        <div class="info">
                            <div class="title">NEWCOMER_GUIDE.md</div>
                            <div class="desc">Onboarding guide for new contributors</div>
                        </div>
                    </div>
                    <div class="doc-item" onclick="openDoc('CONTRIBUTING.md')">
                        <span class="icon">🤝</span>
                        <div class="info">
                            <div class="title">CONTRIBUTING.md</div>
                            <div class="desc">Contribution guidelines and workflow</div>
                        </div>
                    </div>
                    <div class="doc-item" onclick="openDoc('SECURITY.md')">
                        <span class="icon">🔒</span>
                        <div class="info">
                            <div class="title">SECURITY.md</div>
                            <div class="desc">Security policy and vulnerability reporting</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Audit Pipeline -->
            <div class="category-card" id="audit-pipeline">
                <div class="category-header">
                    <span class="category-icon">🔍</span>
                    <span class="category-title">Audit Pipeline v1.5.x</span>
                    <span class="category-count">8 docs</span>
                </div>
                <div class="doc-list">
                    <div class="doc-item" onclick="openDoc('docs/audit/v1.5.x_CHANGELOG.md')">
                        <span class="icon">📋</span>
                        <div class="info">
                            <div class="title">v1.5.x Changelog</div>
                            <div class="desc">Complete changelog for v1.5.0-v1.5.5</div>
                        </div>
                        <span class="badge badge-new">New</span>
                    </div>
                    <div class="doc-item" onclick="openDoc('scripts/space_traversal/trend_db.py')">
                        <span class="icon">💾</span>
                        <div class="info">
                            <div class="title">Trend Database</div>
                            <div class="desc">SQLite-based trend storage system</div>
                        </div>
                        <span class="badge badge-api">API</span>
                    </div>
                    <div class="doc-item" onclick="openDoc('scripts/space_traversal/trend_compare.py')">
                        <span class="icon">📊</span>
                        <div class="info">
                            <div class="title">Trend Comparison</div>
                            <div class="desc">Historical comparison and regression detection</div>
                        </div>
                        <span class="badge badge-api">API</span>
                    </div>
                    <div class="doc-item" onclick="openDoc('scripts/space_traversal/viz_ascii.py')">
                        <span class="icon">📈</span>
                        <div class="info">
                            <div class="title">ASCII Visualization</div>
                            <div class="desc">Terminal charts, sparklines, dashboards</div>
                        </div>
                        <span class="badge badge-api">API</span>
                    </div>
                    <div class="doc-item" onclick="openDoc('scripts/space_traversal/viz_html.py')">
                        <span class="icon">🌐</span>
                        <div class="info">
                            <div class="title">HTML Dashboard</div>
                            <div class="desc">Interactive Chart.js dashboards</div>
                        </div>
                        <span class="badge badge-api">API</span>
                    </div>
                    <div class="doc-item" onclick="openDoc('scripts/space_traversal/webhooks.py')">
                        <span class="icon">🔔</span>
                        <div class="info">
                            <div class="title">Webhook Notifications</div>
                            <div class="desc">Slack, Teams, generic webhook support</div>
                        </div>
                        <span class="badge badge-api">API</span>
                    </div>
                    <div class="doc-item" onclick="openDoc('scripts/space_traversal/ci_integration.py')">
                        <span class="icon">⚙️</span>
                        <div class="info">
                            <div class="title">CI/CD Integration</div>
                            <div class="desc">GitHub, GitLab, Jenkins helpers</div>
                        </div>
                        <span class="badge badge-api">API</span>
                    </div>
                    <div class="doc-item" onclick="openDoc('scripts/space_traversal/performance.py')">
                        <span class="icon">⚡</span>
                        <div class="info">
                            <div class="title">Performance Tools</div>
                            <div class="desc">Caching, profiling, batch operations</div>
                        </div>
                        <span class="badge badge-api">API</span>
                    </div>
                </div>
            </div>
            
            <!-- API Reference -->
            <div class="category-card" id="api-reference">
                <div class="category-header">
                    <span class="category-icon">📖</span>
                    <span class="category-title">API Reference</span>
                    <span class="category-count">4 docs</span>
                </div>
                <div class="doc-list">
                    <div class="doc-item" onclick="openDoc('api-docs.html')">
                        <span class="icon">📚</span>
                        <div class="info">
                            <div class="title">Swagger / OpenAPI</div>
                            <div class="desc">Interactive API documentation with try-it-out</div>
                        </div>
                        <span class="badge badge-new">New</span>
                    </div>
                    <div class="doc-item" onclick="openDoc('api-collection.html')">
                        <span class="icon">📦</span>
                        <div class="info">
                            <div class="title">API Collection</div>
                            <div class="desc">Postman-style API request builder</div>
                        </div>
                        <span class="badge badge-new">New</span>
                    </div>
                    <div class="doc-item" onclick="openDoc('cli-builder.html')">
                        <span class="icon">⌨️</span>
                        <div class="info">
                            <div class="title">CLI Builder</div>
                            <div class="desc">Interactive CLI command generator</div>
                        </div>
                        <span class="badge badge-new">New</span>
                    </div>
                    <div class="doc-item" onclick="openDoc('docs/api/README.md')">
                        <span class="icon">📄</span>
                        <div class="info">
                            <div class="title">API README</div>
                            <div class="desc">API documentation overview</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- CLI Tools -->
            <div class="category-card" id="cli-tools">
                <div class="category-header">
                    <span class="category-icon">⌨️</span>
                    <span class="category-title">CLI Tools</span>
                    <span class="category-count">6 docs</span>
                </div>
                <div class="doc-list">
                    <div class="doc-item" onclick="openDoc('docs/cli/status_audit.md')">
                        <span class="icon">🔍</span>
                        <div class="info">
                            <div class="title">codex-status-audit</div>
                            <div class="desc">Repository status audit command</div>
                        </div>
                    </div>
                    <div class="doc-item" onclick="openDoc('docs/CLI.md')">
                        <span class="icon">📋</span>
                        <div class="info">
                            <div class="title">CLI Overview</div>
                            <div class="desc">All CLI commands and options</div>
                        </div>
                    </div>
                    <div class="doc-item" onclick="openDoc('tools/README_status_update.md')">
                        <span class="icon">📊</span>
                        <div class="info">
                            <div class="title">Status Update Generator</div>
                            <div class="desc">JSON status report generator</div>
                        </div>
                    </div>
                    <div class="doc-item" onclick="openDoc('docs/DUPLICATE_DETECTION.md')">
                        <span class="icon">🔎</span>
                        <div class="info">
                            <div class="title">Duplicate Detection</div>
                            <div class="desc">Code duplication analysis tool</div>
                        </div>
                    </div>
                    <div class="doc-item" onclick="openDoc('docs/INFERENCE_SERVING_GUIDE.md')">
                        <span class="icon">🚀</span>
                        <div class="info">
                            <div class="title">Inference Serving</div>
                            <div class="desc">FastAPI inference server guide</div>
                        </div>
                    </div>
                    <div class="doc-item" onclick="openDoc('docs/QUALITY_GATES.md')">
                        <span class="icon">✅</span>
                        <div class="info">
                            <div class="title">Quality Gates</div>
                            <div class="desc">Quality gate configuration and thresholds</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Configuration -->
            <div class="category-card">
                <div class="category-header">
                    <span class="category-icon">⚙️</span>
                    <span class="category-title">Configuration</span>
                    <span class="category-count">4 docs</span>
                </div>
                <div class="doc-list">
                    <div class="doc-item" onclick="openDoc('.copilot-space/workflow.yaml')">
                        <span class="icon">📝</span>
                        <div class="info">
                            <div class="title">Workflow Configuration</div>
                            <div class="desc">Audit pipeline workflow settings</div>
                        </div>
                    </div>
                    <div class="doc-item" onclick="openDoc('pyproject.toml')">
                        <span class="icon">📦</span>
                        <div class="info">
                            <div class="title">Project Configuration</div>
                            <div class="desc">Python project metadata and dependencies</div>
                        </div>
                    </div>
                    <div class="doc-item" onclick="openDoc('configs/')">
                        <span class="icon">📂</span>
                        <div class="info">
                            <div class="title">Hydra Configs</div>
                            <div class="desc">Training and experiment configurations</div>
                        </div>
                    </div>
                    <div class="doc-item" onclick="openDoc('schemas/')">
                        <span class="icon">📋</span>
                        <div class="info">
                            <div class="title">JSON Schemas</div>
                            <div class="desc">Data validation schemas</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Wiki -->
            <div class="category-card" id="wiki">
                <div class="category-header">
                    <span class="category-icon">📝</span>
                    <span class="category-title">Wiki Pages</span>
                    <span class="category-count">8 pages</span>
                </div>
                <div class="doc-list">
                    <div class="doc-item" onclick="openDoc('wiki/Home.md')">
                        <span class="icon">🏠</span>
                        <div class="info">
                            <div class="title">Home</div>
                            <div class="desc">Wiki home page</div>
                        </div>
                    </div>
                    <div class="doc-item" onclick="openDoc('wiki/Getting-Started.md')">
                        <span class="icon">🚀</span>
                        <div class="info">
                            <div class="title">Getting Started</div>
                            <div class="desc">Quick start guide</div>
                        </div>
                    </div>
                    <div class="doc-item" onclick="openDoc('wiki/Audit-Pipeline.md')">
                        <span class="icon">🔍</span>
                        <div class="info">
                            <div class="title">Audit Pipeline</div>
                            <div class="desc">Audit pipeline documentation</div>
                        </div>
                    </div>
                    <div class="doc-item" onclick="openDoc('wiki/API-Reference.md')">
                        <span class="icon">📖</span>
                        <div class="info">
                            <div class="title">API Reference</div>
                            <div class="desc">Complete API documentation</div>
                        </div>
                    </div>
                    <div class="doc-item" onclick="openDoc('wiki/CLI-Commands.md')">
                        <span class="icon">⌨️</span>
                        <div class="info">
                            <div class="title">CLI Commands</div>
                            <div class="desc">All CLI commands reference</div>
                        </div>
                    </div>
                    <div class="doc-item" onclick="openDoc('wiki/Architecture.md')">
                        <span class="icon">🏗️</span>
                        <div class="info">
                            <div class="title">Architecture</div>
                            <div class="desc">System architecture overview</div>
                        </div>
                    </div>
                    <div class="doc-item" onclick="openDoc('wiki/FAQ.md')">
                        <span class="icon">❓</span>
                        <div class="info">
                            <div class="title">FAQ</div>
                            <div class="desc">Frequently asked questions</div>
                        </div>
                    </div>
                    <div class="doc-item" onclick="openDoc('wiki/Troubleshooting.md')">
                        <span class="icon">🔧</span>
                        <div class="info">
                            <div class="title">Troubleshooting</div>
                            <div class="desc">Common issues and solutions</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Data Flow Diagram -->
        <div class="diagram-section">
            <h2>📊 Audit Pipeline Data Flow</h2>
            <div class="mermaid">
sequenceDiagram
    participant User
    participant CLI as audit_runner.py
    participant DB as TrendDatabase
    participant Compare as trend_compare
    participant Viz as Visualization
    participant CI as CI Integration
    participant Webhook as Webhooks
    
    User->>CLI: audit run
    CLI->>CLI: Execute audit checks
    CLI->>DB: store_snapshot()
    DB-->>CLI: run_id
    
    User->>CLI: check-regressions
    CLI->>DB: get_trend()
    CLI->>Compare: compare_runs()
    Compare-->>CLI: ComparisonResult[]
    
    alt Regressions Detected
        CLI->>Webhook: send_slack_notification()
        Webhook-->>CLI: delivery status
    end
    
    User->>CLI: dashboard
    CLI->>DB: get_latest_scores()
    CLI->>Viz: generate_dashboard()
    Viz-->>User: HTML Dashboard
    
    User->>CLI: show-trend &lt;cap&gt;
    CLI->>DB: get_trend(capability)
    CLI->>Viz: sparkline(), bar_chart()
    Viz-->>User: ASCII visualization
    
    Note over CI: CI/CD Integration
    CI->>CLI: trigger audit
    CLI->>CI: write_github_step_summary()
    CLI->>CI: set_github_output()
            </div>
        </div>
        
        <!-- Module Dependency Diagram -->
        <div class="diagram-section">
            <h2>📦 Module Dependencies</h2>
            <div class="mermaid">
graph LR
    subgraph Core["Core Modules"]
        TD[trend_db.py]
        TC[trend_compare.py]
        AR[audit_runner.py]
    end
    
    subgraph Viz["Visualization"]
        VA[viz_ascii.py]
        VH[viz_html.py]
        VCB[viz_cli_builder.py]
        VAC[viz_api_collection.py]
        VS[viz_swagger.py]
        VDH[viz_docs_hub.py]
    end
    
    subgraph Integration["Integration"]
        WH[webhooks.py]
        CI[ci_integration.py]
        PF[performance.py]
    end
    
    subgraph Storage["Storage"]
        MG[migrations/]
        DB[(SQLite)]
    end
    
    AR --> TD
    AR --> TC
    AR --> VA
    AR --> VH
    AR --> WH
    AR --> CI
    AR --> PF
    
    TD --> MG
    TD --> DB
    
    TC --> TD
    
    VH --> VA
    VCB --> VA
    VAC --> VA
    VS --> VA
    VDH --> VA
    
    WH --> CI
    
    style TD fill:#58a6ff
    style AR fill:#3fb950
    style VH fill:#a371f7
            </div>
        </div>
    </div>
    
    <div class="footer">
        <p>Generated by Audit Pipeline v{version} • {timestamp}</p>
        <p>📚 <a href="https://github.com/{repo_name}" style="color: var(--accent);">View on GitHub</a></p>
    </div>
    
    <script>
        // Initialize Mermaid
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'dark',
            themeVariables: {{
                primaryColor: '#58a6ff',
                primaryTextColor: '#c9d1d9',
                primaryBorderColor: '#30363d',
                lineColor: '#8b949e',
                secondaryColor: '#21262d',
                tertiaryColor: '#161b22'
            }}
        }});
        
        // Search functionality
        function filterDocs() {{
            const query = document.getElementById('searchInput').value.toLowerCase();
            const items = document.querySelectorAll('.doc-item');
            
            items.forEach(item => {{
                const title = item.querySelector('.title').textContent.toLowerCase();
                const desc = item.querySelector('.desc').textContent.toLowerCase();
                const match = title.includes(query) || desc.includes(query);
                item.style.display = match ? 'flex' : 'none';
            }});
        }}
        
        // Open document
        function openDoc(path) {{
            // In production, this would open the actual document
            // For now, show an alert with the path
            alert('Opening: ' + path + '\\n\\nIn production, this will navigate to the actual document.');
        }}
    </script>
</body>
</html>
"""


def generate_docs_hub(
    output_path: Path,
    repo_name: str = "Repository",
    version: str = "1.5.5",
) -> None:
    """
    Generate an interactive documentation hub HTML page.

    Args:
        output_path: Path to write the HTML file
        repo_name: Repository name for display
        version: Pipeline version
    """
    html = DOCS_HUB_TEMPLATE.format(
        repo_name=repo_name,
        version=version,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    import sys

    output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("docs_hub.html")
    repo = sys.argv[2] if len(sys.argv) > 2 else "Aries-Serpent/_codex_"
    generate_docs_hub(output, repo)
    print(f"Generated documentation hub: {output}")
