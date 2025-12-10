#!/usr/bin/env python3
"""
Swagger/OpenAPI-style Documentation for Audit CLI v1.5.4

Generates interactive API documentation with:
- Command reference with parameters
- Try-it-out functionality
- Request/response examples
- Schema definitions

Example:
    from scripts.space_traversal.viz_swagger import generate_swagger_docs
    
    generate_swagger_docs(
        output_path=Path("audit_artifacts/api_docs.html"),
        repo_name="my-repo"
    )
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

__all__ = ["generate_swagger_docs", "SWAGGER_TEMPLATE"]


SWAGGER_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Audit CLI API Reference - {repo_name}</title>
    <style>
        :root {{
            --bg-primary: #1a1a1a;
            --bg-secondary: #252525;
            --bg-tertiary: #2d2d2d;
            --bg-code: #1e1e1e;
            --accent-blue: #61affe;
            --accent-green: #49cc90;
            --accent-orange: #fca130;
            --accent-red: #f93e3e;
            --accent-purple: #9012fe;
            --accent-cyan: #50e3c2;
            --text-primary: #fff;
            --text-secondary: #b3b3b3;
            --text-muted: #8a8a8a;
            --border: #404040;
            --shadow: rgba(0,0,0,0.4);
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
        }}
        
        /* Header */
        .swagger-header {{
            background: linear-gradient(135deg, #1a365d 0%, #2d3748 100%);
            padding: 40px 0;
            border-bottom: 4px solid var(--accent-green);
        }}
        .swagger-header .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 24px;
        }}
        .swagger-header h1 {{
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .swagger-header .version {{
            background: var(--accent-green);
            color: #000;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 600;
        }}
        .swagger-header .description {{
            color: var(--text-secondary);
            font-size: 1rem;
            max-width: 600px;
        }}
        .swagger-header .meta {{
            display: flex;
            gap: 24px;
            margin-top: 16px;
            font-size: 0.85rem;
            color: var(--text-muted);
        }}
        .swagger-header .meta a {{
            color: var(--accent-blue);
            text-decoration: none;
        }}
        .swagger-header .meta a:hover {{
            text-decoration: underline;
        }}
        
        /* Main Layout */
        .swagger-main {{
            display: flex;
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        /* Sidebar */
        .swagger-sidebar {{
            width: 280px;
            background: var(--bg-secondary);
            border-right: 1px solid var(--border);
            height: calc(100vh - 180px);
            position: sticky;
            top: 0;
            overflow-y: auto;
        }}
        .sidebar-section {{
            padding: 16px 0;
            border-bottom: 1px solid var(--border);
        }}
        .sidebar-section-title {{
            padding: 0 20px;
            font-size: 0.7rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--text-muted);
            margin-bottom: 8px;
        }}
        .sidebar-item {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 20px;
            cursor: pointer;
            transition: background 0.15s;
            font-size: 0.9rem;
        }}
        .sidebar-item:hover {{
            background: var(--bg-tertiary);
        }}
        .sidebar-item.active {{
            background: var(--bg-tertiary);
            border-left: 3px solid var(--accent-green);
        }}
        .method-badge {{
            font-size: 0.65rem;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 3px;
            text-transform: uppercase;
            min-width: 45px;
            text-align: center;
        }}
        .method-get {{ background: var(--accent-blue); color: #000; }}
        .method-post {{ background: var(--accent-green); color: #000; }}
        .method-put {{ background: var(--accent-orange); color: #000; }}
        .method-delete {{ background: var(--accent-red); color: #fff; }}
        .method-run {{ background: var(--accent-purple); color: #fff; }}
        
        /* Content */
        .swagger-content {{
            flex: 1;
            padding: 32px;
            min-height: calc(100vh - 180px);
        }}
        
        /* Endpoint Card */
        .endpoint-card {{
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 8px;
            margin-bottom: 24px;
            overflow: hidden;
        }}
        .endpoint-header {{
            display: flex;
            align-items: center;
            gap: 16px;
            padding: 16px 20px;
            background: var(--bg-tertiary);
            cursor: pointer;
            transition: background 0.15s;
        }}
        .endpoint-header:hover {{
            background: #363636;
        }}
        .endpoint-header .method-badge {{
            font-size: 0.75rem;
            padding: 6px 12px;
        }}
        .endpoint-path {{
            font-family: 'SF Mono', 'Consolas', monospace;
            font-size: 0.95rem;
            color: var(--text-primary);
            flex: 1;
        }}
        .endpoint-summary {{
            color: var(--text-secondary);
            font-size: 0.85rem;
        }}
        .endpoint-expand {{
            color: var(--text-muted);
            font-size: 1.2rem;
            transition: transform 0.2s;
        }}
        .endpoint-card.expanded .endpoint-expand {{
            transform: rotate(180deg);
        }}
        
        .endpoint-body {{
            display: none;
            padding: 20px;
            border-top: 1px solid var(--border);
        }}
        .endpoint-card.expanded .endpoint-body {{
            display: block;
        }}
        
        /* Description */
        .endpoint-description {{
            color: var(--text-secondary);
            margin-bottom: 24px;
            line-height: 1.7;
        }}
        
        /* Parameters Section */
        .params-section {{
            margin-bottom: 24px;
        }}
        .params-title {{
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .params-table {{
            width: 100%;
            border-collapse: collapse;
        }}
        .params-table th {{
            text-align: left;
            padding: 10px 12px;
            background: var(--bg-tertiary);
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--text-muted);
            border-bottom: 1px solid var(--border);
        }}
        .params-table td {{
            padding: 12px;
            border-bottom: 1px solid var(--border);
            vertical-align: top;
        }}
        .param-name {{
            font-family: 'SF Mono', 'Consolas', monospace;
            font-size: 0.85rem;
            color: var(--accent-cyan);
        }}
        .param-required {{
            color: var(--accent-red);
            font-size: 0.7rem;
            margin-left: 4px;
        }}
        .param-type {{
            font-size: 0.8rem;
            color: var(--text-muted);
            font-family: 'SF Mono', 'Consolas', monospace;
        }}
        .param-desc {{
            font-size: 0.85rem;
            color: var(--text-secondary);
        }}
        .param-default {{
            font-size: 0.8rem;
            color: var(--text-muted);
            margin-top: 4px;
        }}
        .param-default code {{
            background: var(--bg-code);
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'SF Mono', 'Consolas', monospace;
        }}
        
        /* Try It Out Section */
        .try-section {{
            background: var(--bg-tertiary);
            border-radius: 8px;
            padding: 20px;
            margin-top: 20px;
        }}
        .try-title {{
            font-size: 0.9rem;
            font-weight: 600;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .try-form {{
            display: flex;
            flex-direction: column;
            gap: 16px;
        }}
        .try-field {{
            display: flex;
            flex-direction: column;
            gap: 6px;
        }}
        .try-label {{
            font-size: 0.8rem;
            color: var(--text-secondary);
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .try-input {{
            padding: 10px 14px;
            background: var(--bg-code);
            border: 1px solid var(--border);
            border-radius: 6px;
            color: var(--text-primary);
            font-family: 'SF Mono', 'Consolas', monospace;
            font-size: 0.9rem;
        }}
        .try-input:focus {{
            outline: none;
            border-color: var(--accent-blue);
        }}
        .try-input::placeholder {{
            color: var(--text-muted);
        }}
        .try-select {{
            padding: 10px 14px;
            background: var(--bg-code);
            border: 1px solid var(--border);
            border-radius: 6px;
            color: var(--text-primary);
            font-size: 0.9rem;
            cursor: pointer;
        }}
        .try-checkbox-group {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }}
        .try-checkbox {{
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 14px;
            background: var(--bg-code);
            border: 1px solid var(--border);
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.15s;
            font-size: 0.85rem;
        }}
        .try-checkbox:hover {{
            border-color: var(--accent-blue);
        }}
        .try-checkbox.checked {{
            background: rgba(97, 175, 254, 0.15);
            border-color: var(--accent-blue);
        }}
        .try-checkbox input {{
            display: none;
        }}
        .try-slider-container {{
            display: flex;
            align-items: center;
            gap: 16px;
        }}
        .try-slider {{
            flex: 1;
            -webkit-appearance: none;
            height: 6px;
            background: var(--bg-code);
            border-radius: 3px;
        }}
        .try-slider::-webkit-slider-thumb {{
            -webkit-appearance: none;
            width: 18px;
            height: 18px;
            background: var(--accent-blue);
            border-radius: 50%;
            cursor: pointer;
        }}
        .try-slider-value {{
            min-width: 50px;
            text-align: center;
            font-family: 'SF Mono', 'Consolas', monospace;
            color: var(--accent-blue);
        }}
        .try-toggle {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .try-toggle-switch {{
            width: 44px;
            height: 24px;
            background: var(--bg-code);
            border-radius: 12px;
            cursor: pointer;
            position: relative;
            transition: background 0.2s;
        }}
        .try-toggle-switch.active {{
            background: var(--accent-green);
        }}
        .try-toggle-switch::after {{
            content: '';
            position: absolute;
            width: 18px;
            height: 18px;
            background: white;
            border-radius: 50%;
            top: 3px;
            left: 3px;
            transition: transform 0.2s;
        }}
        .try-toggle-switch.active::after {{
            transform: translateX(20px);
        }}
        
        .try-execute {{
            display: flex;
            gap: 12px;
            margin-top: 8px;
        }}
        .try-btn {{
            padding: 12px 24px;
            border: none;
            border-radius: 6px;
            font-size: 0.9rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.15s;
        }}
        .try-btn-execute {{
            background: var(--accent-blue);
            color: #000;
        }}
        .try-btn-execute:hover {{
            filter: brightness(1.1);
        }}
        .try-btn-clear {{
            background: transparent;
            color: var(--text-secondary);
            border: 1px solid var(--border);
        }}
        .try-btn-clear:hover {{
            background: var(--bg-code);
        }}
        .try-btn-copy {{
            background: var(--bg-code);
            color: var(--text-primary);
        }}
        .try-btn-copy:hover {{
            background: var(--border);
        }}
        
        /* Response Section */
        .response-section {{
            margin-top: 20px;
        }}
        .response-title {{
            font-size: 0.85rem;
            font-weight: 600;
            margin-bottom: 12px;
        }}
        .response-tabs {{
            display: flex;
            border-bottom: 1px solid var(--border);
            margin-bottom: 16px;
        }}
        .response-tab {{
            padding: 10px 20px;
            font-size: 0.85rem;
            color: var(--text-muted);
            cursor: pointer;
            border-bottom: 2px solid transparent;
            transition: all 0.15s;
        }}
        .response-tab:hover {{
            color: var(--text-primary);
        }}
        .response-tab.active {{
            color: var(--accent-blue);
            border-bottom-color: var(--accent-blue);
        }}
        .response-code {{
            background: var(--bg-code);
            border-radius: 6px;
            padding: 16px;
            font-family: 'SF Mono', 'Consolas', monospace;
            font-size: 0.85rem;
            overflow-x: auto;
            white-space: pre;
            line-height: 1.5;
        }}
        .response-code .comment {{ color: #6a9955; }}
        .response-code .string {{ color: #ce9178; }}
        .response-code .number {{ color: #b5cea8; }}
        .response-code .keyword {{ color: #569cd6; }}
        .response-code .key {{ color: #9cdcfe; }}
        
        /* Schema Section */
        .schema-section {{
            margin-top: 24px;
            padding-top: 24px;
            border-top: 1px solid var(--border);
        }}
        .schema-title {{
            font-size: 0.85rem;
            font-weight: 600;
            margin-bottom: 16px;
        }}
        .schema-model {{
            background: var(--bg-code);
            border-radius: 6px;
            padding: 16px;
        }}
        .schema-property {{
            display: flex;
            padding: 8px 0;
            border-bottom: 1px solid var(--border);
        }}
        .schema-property:last-child {{
            border-bottom: none;
        }}
        .schema-prop-name {{
            font-family: 'SF Mono', 'Consolas', monospace;
            color: var(--accent-cyan);
            min-width: 150px;
        }}
        .schema-prop-type {{
            font-family: 'SF Mono', 'Consolas', monospace;
            color: var(--text-muted);
            font-size: 0.85rem;
            min-width: 100px;
        }}
        .schema-prop-desc {{
            color: var(--text-secondary);
            font-size: 0.85rem;
        }}
        
        /* Scrollbar */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        ::-webkit-scrollbar-track {{
            background: var(--bg-secondary);
        }}
        ::-webkit-scrollbar-thumb {{
            background: var(--border);
            border-radius: 4px;
        }}
        ::-webkit-scrollbar-thumb:hover {{
            background: var(--text-muted);
        }}
        
        /* Status Badges */
        .status-badge {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
        }}
        .status-success {{
            background: rgba(73, 204, 144, 0.15);
            color: var(--accent-green);
        }}
        .status-error {{
            background: rgba(249, 62, 62, 0.15);
            color: var(--accent-red);
        }}
        
        /* Copy notification */
        .copy-toast {{
            position: fixed;
            bottom: 24px;
            right: 24px;
            background: var(--accent-green);
            color: #000;
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: 600;
            opacity: 0;
            transform: translateY(20px);
            transition: all 0.3s;
            z-index: 1000;
        }}
        .copy-toast.show {{
            opacity: 1;
            transform: translateY(0);
        }}
    </style>
</head>
<body>
    <!-- Header -->
    <div class="swagger-header">
        <div class="container">
            <h1>
                🔍 Audit CLI API
                <span class="version">v{version}</span>
            </h1>
            <p class="description">
                Interactive documentation for the Audit Pipeline CLI. Build, test, and execute 
                audit commands directly from this interface.
            </p>
            <div class="meta">
                <span>📁 {repo_name}</span>
                <span>🕐 Generated: {timestamp}</span>
                <a href="#" onclick="downloadOpenAPI()">📥 Download OpenAPI Spec</a>
            </div>
        </div>
    </div>
    
    <!-- Main -->
    <div class="swagger-main">
        <!-- Sidebar -->
        <div class="swagger-sidebar">
            <div class="sidebar-section">
                <div class="sidebar-section-title">Pipeline Commands</div>
                <div class="sidebar-item active" onclick="scrollToEndpoint('run')">
                    <span class="method-badge method-run">RUN</span>
                    <span>Full Pipeline</span>
                </div>
                <div class="sidebar-item" onclick="scrollToEndpoint('stage')">
                    <span class="method-badge method-run">RUN</span>
                    <span>Single Stage</span>
                </div>
                <div class="sidebar-item" onclick="scrollToEndpoint('validate')">
                    <span class="method-badge method-get">GET</span>
                    <span>Validate</span>
                </div>
            </div>
            
            <div class="sidebar-section">
                <div class="sidebar-section-title">Analysis</div>
                <div class="sidebar-item" onclick="scrollToEndpoint('explain')">
                    <span class="method-badge method-get">GET</span>
                    <span>Explain Score</span>
                </div>
                <div class="sidebar-item" onclick="scrollToEndpoint('diff')">
                    <span class="method-badge method-get">GET</span>
                    <span>Diff Reports</span>
                </div>
                <div class="sidebar-item" onclick="scrollToEndpoint('compare-runs')">
                    <span class="method-badge method-get">GET</span>
                    <span>Compare Runs</span>
                </div>
            </div>
            
            <div class="sidebar-section">
                <div class="sidebar-section-title">Trends</div>
                <div class="sidebar-item" onclick="scrollToEndpoint('store-trend')">
                    <span class="method-badge method-post">POST</span>
                    <span>Store Trend</span>
                </div>
                <div class="sidebar-item" onclick="scrollToEndpoint('show-trend')">
                    <span class="method-badge method-get">GET</span>
                    <span>Show Trend</span>
                </div>
                <div class="sidebar-item" onclick="scrollToEndpoint('check-regressions')">
                    <span class="method-badge method-get">GET</span>
                    <span>Check Regressions</span>
                </div>
            </div>
            
            <div class="sidebar-section">
                <div class="sidebar-section-title">Visualization</div>
                <div class="sidebar-item" onclick="scrollToEndpoint('dashboard')">
                    <span class="method-badge method-post">POST</span>
                    <span>Dashboard</span>
                </div>
                <div class="sidebar-item" onclick="scrollToEndpoint('cli-builder')">
                    <span class="method-badge method-post">POST</span>
                    <span>CLI Builder</span>
                </div>
                <div class="sidebar-item" onclick="scrollToEndpoint('api-collection')">
                    <span class="method-badge method-post">POST</span>
                    <span>API Collection</span>
                </div>
            </div>
        </div>
        
        <!-- Content -->
        <div class="swagger-content" id="endpoints-container">
            <!-- Endpoints will be rendered here -->
        </div>
    </div>
    
    <!-- Copy Toast -->
    <div class="copy-toast" id="copy-toast">✓ Command copied to clipboard</div>
    
    <script>
        // API Endpoints Definition
        const endpoints = [
            {{
                id: 'run',
                method: 'RUN',
                path: 'audit_runner.py run',
                summary: 'Execute Full Pipeline',
                description: 'Runs all 7 stages of the audit pipeline: S1 (Index) → S2 (Facets) → S3 (Capabilities) → S4 (Scoring) → S5 (Gaps) → S6 (Render) → S7 (Manifest). This is the standard command for running a complete self-audit.',
                parameters: [
                    {{ name: '--verbose', type: 'boolean', desc: 'Show detailed progress information', default: 'false' }},
                    {{ name: '--strict', type: 'boolean', desc: 'Fail on any validation error', default: 'false' }},
                    {{ name: '--skip', type: 'array', desc: 'Stages to skip (e.g., S5,S6)', default: '[]' }}
                ],
                example: 'python -m scripts.space_traversal.audit_runner run',
                response: {{
                    success: `{{
  "status": "success",
  "stages_completed": ["S1", "S2", "S3", "S4", "S5", "S6", "S7"],
  "capabilities_scored": 18,
  "average_score": 0.847,
  "duration_seconds": 12.5
}}`
                }}
            }},
            {{
                id: 'stage',
                method: 'RUN',
                path: 'audit_runner.py stage <stage_id>',
                summary: 'Run Single Stage',
                description: 'Execute a specific stage of the audit pipeline. Useful for debugging, re-running failed stages, or running stages independently.',
                parameters: [
                    {{ name: 'stage_id', type: 'string', required: true, desc: 'Stage identifier', enum: ['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'TRENDS'] }}
                ],
                example: 'python -m scripts.space_traversal.audit_runner stage S4',
                response: {{
                    success: `{{
  "status": "success",
  "stage": "S4",
  "stage_name": "Scoring",
  "duration_seconds": 2.3
}}`
                }}
            }},
            {{
                id: 'validate',
                method: 'GET',
                path: 'audit_runner.py validate',
                summary: 'Validate Quality Gates',
                description: 'Checks all capabilities against configured quality gates. Reports low maturity scores, missing detectors, and policy violations.',
                parameters: [
                    {{ name: '--fail-on-warn', type: 'boolean', desc: 'Exit with error code on warnings', default: 'false' }},
                    {{ name: '--severity', type: 'string', desc: 'Minimum severity to report', enum: ['error', 'warning', 'info'], default: 'warning' }}
                ],
                example: 'python -m scripts.space_traversal.audit_runner validate',
                response: {{
                    success: `{{
  "status": "pass",
  "checks_passed": 15,
  "checks_failed": 0,
  "warnings": 2
}}`
                }}
            }},
            {{
                id: 'explain',
                method: 'GET',
                path: 'audit_runner.py explain <capability>',
                summary: 'Explain Capability Score',
                description: 'Provides detailed breakdown of how a capability score was calculated, including component scores (functionality, consistency, tests, safeguards, documentation) and supporting evidence.',
                parameters: [
                    {{ name: 'capability', type: 'string', required: true, desc: 'Capability ID to explain (e.g., checkpointing)' }},
                    {{ name: '--format', type: 'string', desc: 'Output format', enum: ['text', 'json', 'markdown'], default: 'text' }}
                ],
                example: 'python -m scripts.space_traversal.audit_runner explain checkpointing',
                response: {{
                    success: `{{
  "capability_id": "checkpointing",
  "score": 0.85,
  "components": {{
    "functionality": 0.90,
    "consistency": 0.85,
    "tests": 0.80,
    "safeguards": 0.85,
    "documentation": 0.85
  }},
  "evidence": [
    "src/codex_ml/checkpointing.py: Checkpoint class found",
    "tests/test_checkpointing.py: 12 test cases"
  ]
}}`
                }}
            }},
            {{
                id: 'diff',
                method: 'GET',
                path: 'audit_runner.py diff --old <path> --new <path>',
                summary: 'Diff Two Reports',
                description: 'Compares two audit report files and shows score differences. Useful for seeing changes between audit runs.',
                parameters: [
                    {{ name: '--old', type: 'string', required: true, desc: 'Path to old report/JSON file' }},
                    {{ name: '--new', type: 'string', required: true, desc: 'Path to new report/JSON file' }},
                    {{ name: '--color', type: 'boolean', desc: 'Use colored output', default: 'true' }}
                ],
                example: 'python -m scripts.space_traversal.audit_runner diff --old old.json --new new.json'
            }},
            {{
                id: 'store-trend',
                method: 'POST',
                path: 'audit_runner.py store-trend',
                summary: 'Store Audit in Trend DB',
                description: 'Stores the current audit results in the SQLite trend database for historical tracking and analysis. Creates a snapshot with timestamp, git info, and all capability scores.',
                parameters: [
                    {{ name: '--tag', type: 'string', desc: 'Optional tag for this snapshot (e.g., release-v1.0)' }},
                    {{ name: '--force', type: 'boolean', desc: 'Overwrite existing entry with same ID', default: 'false' }}
                ],
                example: 'python -m scripts.space_traversal.audit_runner store-trend --tag release-v1.0',
                response: {{
                    success: `{{
  "status": "stored",
  "run_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "timestamp": "2024-12-10T12:30:00Z",
  "capabilities_stored": 18
}}`
                }}
            }},
            {{
                id: 'show-trend',
                method: 'GET',
                path: 'audit_runner.py show-trend <capability>',
                summary: 'Show Capability Trend',
                description: 'Displays historical trend of scores for a specific capability. Shows score changes over time with timestamps and git info.',
                parameters: [
                    {{ name: 'capability', type: 'string', required: true, desc: 'Capability ID to show trend for' }},
                    {{ name: '--limit', type: 'integer', desc: 'Number of entries to show', default: '30', min: 5, max: 100 }},
                    {{ name: '--branch', type: 'string', desc: 'Filter by git branch' }},
                    {{ name: '--output', type: 'string', desc: 'Output format', enum: ['table', 'sparkline', 'json'], default: 'table' }}
                ],
                example: 'python -m scripts.space_traversal.audit_runner show-trend checkpointing --limit 10'
            }},
            {{
                id: 'check-regressions',
                method: 'GET',
                path: 'audit_runner.py check-regressions',
                summary: 'Detect Score Regressions',
                description: 'Analyzes recent audit history to detect capabilities with declining scores. Compares current scores against recent averages to identify regressions.',
                parameters: [
                    {{ name: '--threshold', type: 'number', desc: 'Score drop threshold (0.02 = 2%)', default: '0.02', min: 0.01, max: 0.10 }},
                    {{ name: '--lookback', type: 'integer', desc: 'Number of previous runs to compare', default: '5', min: 2, max: 20 }},
                    {{ name: '--severity', type: 'string', desc: 'Severity filter', enum: ['all', 'high', 'medium+'], default: 'all' }},
                    {{ name: '--exit-on-regression', type: 'boolean', desc: 'Return non-zero exit code if regressions found', default: 'true' }}
                ],
                example: 'python -m scripts.space_traversal.audit_runner check-regressions --threshold 0.05',
                response: {{
                    success: `{{
  "status": "regressions_detected",
  "regression_count": 2,
  "regressions": [
    {{
      "capability_id": "model_versioning",
      "current_score": 0.75,
      "previous_avg": 0.82,
      "delta": -0.07,
      "severity": "high"
    }}
  ]
}}`
                }}
            }},
            {{
                id: 'compare-runs',
                method: 'GET',
                path: 'audit_runner.py compare-runs --old <path> --new <path>',
                summary: 'Compare Two Audit Runs',
                description: 'Detailed comparison of two audit runs with component-level analysis. Shows regressions, improvements, and unchanged capabilities.',
                parameters: [
                    {{ name: '--old', type: 'string', required: true, desc: 'Path to old capabilities_scored.json' }},
                    {{ name: '--new', type: 'string', required: true, desc: 'Path to new capabilities_scored.json' }},
                    {{ name: '--output', type: 'string', desc: 'Path for comparison report (markdown)' }},
                    {{ name: '--threshold', type: 'number', desc: 'Change threshold', default: '0.02', min: 0.01, max: 0.10 }}
                ],
                example: 'python -m scripts.space_traversal.audit_runner compare-runs --old v1.json --new v2.json --output comparison.md'
            }},
            {{
                id: 'dashboard',
                method: 'POST',
                path: 'audit_runner.py dashboard',
                summary: 'Generate HTML Dashboard',
                description: 'Creates an interactive HTML dashboard with charts, trend visualizations, and capability breakdowns.',
                parameters: [
                    {{ name: '--output', type: 'string', desc: 'Output path for HTML file', default: 'audit_artifacts/dashboard.html' }},
                    {{ name: '--theme', type: 'string', desc: 'Dashboard theme', enum: ['dark', 'light', 'auto'], default: 'dark' }}
                ],
                example: 'python -m scripts.space_traversal.audit_runner dashboard --output report.html'
            }},
            {{
                id: 'cli-builder',
                method: 'POST',
                path: 'audit_runner.py cli-builder',
                summary: 'Generate CLI Builder HTML',
                description: 'Creates an interactive HTML interface for building and previewing CLI commands with visual controls.',
                parameters: [
                    {{ name: '--output', type: 'string', desc: 'Output path for HTML file', default: 'audit_artifacts/cli_builder.html' }}
                ],
                example: 'python -m scripts.space_traversal.audit_runner cli-builder'
            }},
            {{
                id: 'api-collection',
                method: 'POST',
                path: 'audit_runner.py api-collection',
                summary: 'Generate API Collection HTML',
                description: 'Creates an interactive API collection interface with adjustable controls, presets, and command history.',
                parameters: [
                    {{ name: '--output', type: 'string', desc: 'Output path for HTML file', default: 'audit_artifacts/api_collection.html' }}
                ],
                example: 'python -m scripts.space_traversal.audit_runner api-collection'
            }}
        ];
        
        // Render endpoints
        function renderEndpoints() {{
            const container = document.getElementById('endpoints-container');
            container.innerHTML = endpoints.map(ep => renderEndpoint(ep)).join('');
        }}
        
        function renderEndpoint(ep) {{
            const methodClass = ep.method.toLowerCase() === 'run' ? 'method-run' : 
                               ep.method.toLowerCase() === 'post' ? 'method-post' : 
                               ep.method.toLowerCase() === 'get' ? 'method-get' : 'method-get';
            
            return `
                <div class="endpoint-card" id="endpoint-${{ep.id}}">
                    <div class="endpoint-header" onclick="toggleEndpoint('${{ep.id}}')">
                        <span class="method-badge ${{methodClass}}">${{ep.method}}</span>
                        <span class="endpoint-path">${{ep.path}}</span>
                        <span class="endpoint-summary">${{ep.summary}}</span>
                        <span class="endpoint-expand">▼</span>
                    </div>
                    <div class="endpoint-body">
                        <p class="endpoint-description">${{ep.description}}</p>
                        
                        ${{ep.parameters && ep.parameters.length > 0 ? `
                        <div class="params-section">
                            <div class="params-title">📋 Parameters</div>
                            <table class="params-table">
                                <thead>
                                    <tr>
                                        <th>Name</th>
                                        <th>Type</th>
                                        <th>Description</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${{ep.parameters.map(p => `
                                        <tr>
                                            <td>
                                                <span class="param-name">${{p.name}}</span>
                                                ${{p.required ? '<span class="param-required">required</span>' : ''}}
                                            </td>
                                            <td><span class="param-type">${{p.type}}${{p.enum ? ' enum' : ''}}</span></td>
                                            <td>
                                                <div class="param-desc">${{p.desc}}</div>
                                                ${{p.default !== undefined ? `<div class="param-default">Default: <code>${{p.default}}</code></div>` : ''}}
                                                ${{p.enum ? `<div class="param-default">Values: <code>${{p.enum.join(', ')}}</code></div>` : ''}}
                                            </td>
                                        </tr>
                                    `).join('')}}
                                </tbody>
                            </table>
                        </div>
                        ` : ''}}
                        
                        <div class="try-section">
                            <div class="try-title">🧪 Try It Out</div>
                            <div class="try-form" id="try-form-${{ep.id}}">
                                ${{renderTryFields(ep)}}
                            </div>
                            <div class="try-execute">
                                <button class="try-btn try-btn-execute" onclick="executeCommand('${{ep.id}}')">Execute</button>
                                <button class="try-btn try-btn-copy" onclick="copyCommand('${{ep.id}}')">📋 Copy</button>
                                <button class="try-btn try-btn-clear" onclick="clearForm('${{ep.id}}')">Clear</button>
                            </div>
                            
                            <div class="response-section">
                                <div class="response-title">Generated Command</div>
                                <div class="response-code" id="command-output-${{ep.id}}">${{ep.example}}</div>
                            </div>
                            
                            ${{ep.response ? `
                            <div class="response-section">
                                <div class="response-title">Example Response</div>
                                <div class="response-code">${{ep.response.success}}</div>
                            </div>
                            ` : ''}}
                        </div>
                    </div>
                </div>
            `;
        }}
        
        function renderTryFields(ep) {{
            if (!ep.parameters) return '<p style="color:var(--text-muted)">No parameters required</p>';
            
            return ep.parameters.map(p => {{
                const id = `${{ep.id}}-${{p.name.replace(/--/g, '')}}`;
                
                if (p.type === 'boolean') {{
                    return `
                        <div class="try-field">
                            <label class="try-label">${{p.name}}</label>
                            <div class="try-toggle">
                                <div class="try-toggle-switch ${{p.default === 'true' ? 'active' : ''}}" 
                                     id="${{id}}" 
                                     onclick="toggleSwitch(this); updateTryCommand('${{ep.id}}')">
                                </div>
                                <span style="color:var(--text-muted);font-size:0.85rem">${{p.desc}}</span>
                            </div>
                        </div>
                    `;
                }} else if (p.enum) {{
                    return `
                        <div class="try-field">
                            <label class="try-label">${{p.name}} ${{p.required ? '<span style="color:var(--accent-red)">*</span>' : ''}}</label>
                            <select class="try-select" id="${{id}}" onchange="updateTryCommand('${{ep.id}}')">
                                ${{p.enum.map(v => `<option value="${{v}}" ${{v === p.default ? 'selected' : ''}}>${{v}}</option>`).join('')}}
                            </select>
                        </div>
                    `;
                }} else if (p.type === 'integer' || p.type === 'number') {{
                    return `
                        <div class="try-field">
                            <label class="try-label">${{p.name}}</label>
                            <div class="try-slider-container">
                                <input type="range" class="try-slider" id="${{id}}" 
                                       min="${{p.min || 0}}" max="${{p.max || 100}}" 
                                       value="${{p.default || p.min || 0}}"
                                       step="${{p.type === 'number' ? '0.01' : '1'}}"
                                       oninput="document.getElementById('${{id}}-value').textContent = this.value; updateTryCommand('${{ep.id}}')">
                                <span class="try-slider-value" id="${{id}}-value">${{p.default || p.min || 0}}</span>
                            </div>
                        </div>
                    `;
                }} else {{
                    return `
                        <div class="try-field">
                            <label class="try-label">${{p.name}} ${{p.required ? '<span style="color:var(--accent-red)">*</span>' : ''}}</label>
                            <input type="text" class="try-input" id="${{id}}" 
                                   placeholder="${{p.desc}}"
                                   oninput="updateTryCommand('${{ep.id}}')">
                        </div>
                    `;
                }}
            }}).join('');
        }}
        
        function toggleEndpoint(id) {{
            const card = document.getElementById('endpoint-' + id);
            card.classList.toggle('expanded');
        }}
        
        function toggleSwitch(el) {{
            el.classList.toggle('active');
        }}
        
        function updateTryCommand(epId) {{
            const ep = endpoints.find(e => e.id === epId);
            let cmd = 'python -m scripts.space_traversal.audit_runner ' + epId;
            
            if (ep.parameters) {{
                ep.parameters.forEach(p => {{
                    const inputId = `${{epId}}-${{p.name.replace(/--/g, '')}}`;
                    const el = document.getElementById(inputId);
                    
                    if (p.type === 'boolean') {{
                        if (el.classList.contains('active') && p.default !== 'true') {{
                            cmd += ' ' + p.name;
                        }}
                    }} else if (el && el.value) {{
                        if (p.name.startsWith('--')) {{
                            if (el.value !== p.default) {{
                                cmd += ` ${{p.name}} ${{el.value}}`;
                            }}
                        }} else {{
                            cmd += ' ' + el.value;
                        }}
                    }}
                }});
            }}
            
            document.getElementById('command-output-' + epId).textContent = cmd;
        }}
        
        function copyCommand(epId) {{
            const cmd = document.getElementById('command-output-' + epId).textContent;
            navigator.clipboard.writeText(cmd).then(() => {{
                const toast = document.getElementById('copy-toast');
                toast.classList.add('show');
                setTimeout(() => toast.classList.remove('show'), 2000);
            }});
        }}
        
        function executeCommand(epId) {{
            const cmd = document.getElementById('command-output-' + epId).textContent;
            alert('Copy and run in terminal:\\n\\n' + cmd);
            copyCommand(epId);
        }}
        
        function clearForm(epId) {{
            const form = document.getElementById('try-form-' + epId);
            form.querySelectorAll('input[type="text"]').forEach(i => i.value = '');
            form.querySelectorAll('.try-toggle-switch').forEach(t => t.classList.remove('active'));
            form.querySelectorAll('select').forEach(s => s.selectedIndex = 0);
            updateTryCommand(epId);
        }}
        
        function scrollToEndpoint(id) {{
            document.querySelectorAll('.sidebar-item').forEach(i => i.classList.remove('active'));
            event.target.closest('.sidebar-item').classList.add('active');
            
            const card = document.getElementById('endpoint-' + id);
            card.classList.add('expanded');
            card.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
        }}
        
        function downloadOpenAPI() {{
            const spec = {{
                openapi: '3.0.0',
                info: {{
                    title: 'Audit CLI API',
                    version: '{version}',
                    description: 'Audit Pipeline CLI command reference'
                }},
                paths: {{}}
            }};
            
            endpoints.forEach(ep => {{
                spec.paths['/' + ep.id] = {{
                    [ep.method.toLowerCase()]: {{
                        summary: ep.summary,
                        description: ep.description,
                        parameters: ep.parameters?.map(p => ({{
                            name: p.name,
                            in: 'query',
                            required: p.required || false,
                            schema: {{ type: p.type }}
                        }}))
                    }}
                }};
            }});
            
            const blob = new Blob([JSON.stringify(spec, null, 2)], {{ type: 'application/json' }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'audit-cli-openapi.json';
            a.click();
        }}
        
        // Initialize
        renderEndpoints();
    </script>
</body>
</html>
"""


def generate_swagger_docs(
    output_path: Path,
    repo_name: str = "Repository",
    version: str = "1.5.4",
) -> None:
    """
    Generate Swagger/OpenAPI-style documentation HTML.

    Args:
        output_path: Path to write HTML file
        repo_name: Repository name for display
        version: Pipeline version
    """
    html = SWAGGER_TEMPLATE.format(
        repo_name=repo_name,
        version=version,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"),
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
