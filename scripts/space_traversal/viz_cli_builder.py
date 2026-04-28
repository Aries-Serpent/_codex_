#!/usr/bin/env python3
"""
Viz Cli Builder

Purpose:
    Builds viz_cli_builder

Usage:
    python scripts/space_traversal/viz_cli_builder.py [options]

    Examples:
    $ python scripts/space_traversal/viz_cli_builder.py --help

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

from pathlib import Path

__all__ = ["generate_cli_builder", "CLI_BUILDER_TEMPLATE"]


CLI_BUILDER_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Audit CLI Builder - {repo_name}</title>
    <style>
        :root {{
            --bg-primary: #1a1a2e;
            --bg-secondary: #16213e;
            --bg-tertiary: #0f3460;
            --accent: #e94560;
            --accent-hover: #ff6b6b;
            --text-primary: #eee;
            --text-secondary: #aaa;
            --success: #4ade80;
            --warning: #fbbf24;
            --danger: #f87171;
            --border: #333;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 20px;
            line-height: 1.6;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}

        /* Header */
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px;
            background: var(--bg-secondary);
            border-radius: 12px;
            margin-bottom: 24px;
            border: 1px solid var(--border);
        }}
        .header h1 {{
            font-size: 1.5rem;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .header .meta {{
            color: var(--text-secondary);
            font-size: 0.9rem;
        }}

        /* Main Layout */
        .main-grid {{
            display: grid;
            grid-template-columns: 350px 1fr;
            gap: 24px;
        }}
        @media (max-width: 900px) {{
            .main-grid {{ grid-template-columns: 1fr; }}
        }}

        /* Sidebar - Command Selection */
        .sidebar {{
            background: var(--bg-secondary);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid var(--border);
        }}
        .sidebar h2 {{
            font-size: 1rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 16px;
        }}

        /* Command Buttons */
        .command-list {{
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        .command-btn {{
            background: var(--bg-tertiary);
            border: 2px solid transparent;
            color: var(--text-primary);
            padding: 12px 16px;
            border-radius: 8px;
            cursor: pointer;
            text-align: left;
            transition: all 0.2s;
            font-size: 0.95rem;
        }}
        .command-btn:hover {{
            background: var(--accent);
            transform: translateX(4px);
        }}
        .command-btn.active {{
            border-color: var(--accent);
            background: var(--accent);
        }}
        .command-btn .cmd-name {{
            font-weight: 600;
            display: block;
        }}
        .command-btn .cmd-desc {{
            font-size: 0.8rem;
            color: var(--text-secondary);
            margin-top: 4px;
        }}
        .command-btn.active .cmd-desc {{
            color: var(--text-primary);
        }}

        /* Main Content */
        .content {{
            display: flex;
            flex-direction: column;
            gap: 24px;
        }}

        /* Cards */
        .card {{
            background: var(--bg-secondary);
            border-radius: 12px;
            padding: 24px;
            border: 1px solid var(--border);
        }}
        .card h3 {{
            font-size: 1rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        /* Form Controls */
        .form-group {{
            margin-bottom: 20px;
        }}
        .form-group:last-child {{
            margin-bottom: 0;
        }}
        .form-label {{
            display: block;
            font-size: 0.9rem;
            color: var(--text-secondary);
            margin-bottom: 8px;
        }}
        .form-label .required {{
            color: var(--accent);
        }}

        /* Text Input */
        .form-input {{
            width: 100%;
            padding: 12px 16px;
            background: var(--bg-tertiary);
            border: 2px solid var(--border);
            border-radius: 8px;
            color: var(--text-primary);
            font-size: 0.95rem;
            transition: border-color 0.2s;
        }}
        .form-input:focus {{
            outline: none;
            border-color: var(--accent);
        }}
        .form-input::placeholder {{
            color: var(--text-secondary);
        }}

        /* Select */
        .form-select {{
            width: 100%;
            padding: 12px 16px;
            background: var(--bg-tertiary);
            border: 2px solid var(--border);
            border-radius: 8px;
            color: var(--text-primary);
            font-size: 0.95rem;
            cursor: pointer;
        }}
        .form-select:focus {{
            outline: none;
            border-color: var(--accent);
        }}

        /* Range Slider (Knob) */
        .knob-container {{
            display: flex;
            align-items: center;
            gap: 16px;
        }}
        .knob-slider {{
            flex: 1;
            -webkit-appearance: none;
            height: 8px;
            background: var(--bg-tertiary);
            border-radius: 4px;
            outline: none;
        }}
        .knob-slider::-webkit-slider-thumb {{
            -webkit-appearance: none;
            width: 24px;
            height: 24px;
            background: var(--accent);
            border-radius: 50%;
            cursor: pointer;
            transition: transform 0.2s;
        }}
        .knob-slider::-webkit-slider-thumb:hover {{
            transform: scale(1.2);
        }}
        .knob-slider::-moz-range-thumb {{
            width: 24px;
            height: 24px;
            background: var(--accent);
            border-radius: 50%;
            cursor: pointer;
            border: none;
        }}
        .knob-value {{
            min-width: 60px;
            padding: 8px 12px;
            background: var(--bg-tertiary);
            border-radius: 6px;
            text-align: center;
            font-family: 'Consolas', monospace;
            font-weight: 600;
        }}

        /* Rotary Knob Style */
        .rotary-knob-container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 12px;
        }}
        .rotary-knob {{
            position: relative;
            width: 80px;
            height: 80px;
            border-radius: 50%;
            background: conic-gradient(
                from 135deg,
                var(--bg-tertiary) 0deg,
                var(--accent) calc(var(--knob-percent, 0) * 2.7deg),
                var(--bg-tertiary) calc(var(--knob-percent, 0) * 2.7deg)
            );
            cursor: grab;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3), inset 0 2px 4px rgba(255,255,255,0.1);
        }}
        .rotary-knob::before {{
            content: '';
            position: absolute;
            top: 8px;
            left: 8px;
            right: 8px;
            bottom: 8px;
            background: var(--bg-secondary);
            border-radius: 50%;
            box-shadow: inset 0 2px 8px rgba(0,0,0,0.4);
        }}
        .rotary-knob::after {{
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 4px;
            height: 20px;
            background: var(--accent);
            border-radius: 2px;
            transform-origin: bottom center;
            transform: translate(-50%, -100%) rotate(calc((var(--knob-percent, 0) * 2.7deg) - 135deg));
            box-shadow: 0 0 8px var(--accent);
        }}
        .rotary-knob:active {{
            cursor: grabbing;
        }}
        .rotary-value {{
            font-size: 1.2rem;
            font-weight: 700;
            font-family: 'Consolas', monospace;
            color: var(--accent);
        }}
        .rotary-label {{
            font-size: 0.8rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        /* Number Stepper */
        .stepper-container {{
            display: flex;
            align-items: center;
            gap: 0;
            background: var(--bg-tertiary);
            border-radius: 8px;
            overflow: hidden;
            border: 2px solid var(--border);
        }}
        .stepper-btn {{
            width: 44px;
            height: 44px;
            background: var(--bg-tertiary);
            border: none;
            color: var(--text-primary);
            font-size: 1.2rem;
            cursor: pointer;
            transition: background 0.2s;
        }}
        .stepper-btn:hover {{
            background: var(--accent);
        }}
        .stepper-btn:active {{
            transform: scale(0.95);
        }}
        .stepper-value {{
            min-width: 80px;
            padding: 0 16px;
            text-align: center;
            font-family: 'Consolas', monospace;
            font-size: 1.1rem;
            font-weight: 600;
            background: var(--bg-primary);
        }}

        /* Toggle Switch */
        .toggle-container {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .toggle {{
            position: relative;
            width: 56px;
            height: 28px;
            background: var(--bg-tertiary);
            border-radius: 14px;
            cursor: pointer;
            transition: background 0.3s;
        }}
        .toggle.active {{
            background: var(--success);
        }}
        .toggle::after {{
            content: '';
            position: absolute;
            top: 4px;
            left: 4px;
            width: 20px;
            height: 20px;
            background: var(--text-primary);
            border-radius: 50%;
            transition: transform 0.3s;
        }}
        .toggle.active::after {{
            transform: translateX(28px);
        }}
        .toggle-label {{
            color: var(--text-secondary);
        }}

        /* Checkbox Group */
        .checkbox-group {{
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
        }}
        .checkbox-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            background: var(--bg-tertiary);
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .checkbox-item:hover {{
            background: var(--accent);
        }}
        .checkbox-item.checked {{
            background: var(--accent);
        }}
        .checkbox-item input {{
            display: none;
        }}
        .checkbox-mark {{
            width: 18px;
            height: 18px;
            border: 2px solid var(--text-secondary);
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .checkbox-item.checked .checkbox-mark {{
            background: var(--text-primary);
            border-color: var(--text-primary);
        }}
        .checkbox-item.checked .checkbox-mark::after {{
            content: '✓';
            color: var(--accent);
            font-weight: bold;
            font-size: 12px;
        }}

        /* Command Preview */
        .preview-box {{
            background: #0d1117;
            border-radius: 8px;
            padding: 20px;
            font-family: 'Consolas', 'Monaco', monospace;
            position: relative;
            overflow-x: auto;
        }}
        .preview-prompt {{
            color: var(--success);
            user-select: none;
        }}
        .preview-command {{
            color: var(--text-primary);
            word-break: break-all;
        }}
        .preview-arg {{
            color: var(--warning);
        }}
        .preview-flag {{
            color: #58a6ff;
        }}
        .preview-value {{
            color: #a5d6ff;
        }}

        /* Copy Button */
        .copy-btn {{
            position: absolute;
            top: 12px;
            right: 12px;
            background: var(--bg-tertiary);
            border: none;
            color: var(--text-secondary);
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.85rem;
            transition: all 0.2s;
        }}
        .copy-btn:hover {{
            background: var(--accent);
            color: var(--text-primary);
        }}
        .copy-btn.copied {{
            background: var(--success);
            color: #000;
        }}

        /* Action Buttons */
        .action-buttons {{
            display: flex;
            gap: 12px;
            margin-top: 20px;
        }}
        .btn {{
            padding: 14px 28px;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .btn-primary {{
            background: var(--accent);
            color: var(--text-primary);
        }}
        .btn-primary:hover {{
            background: var(--accent-hover);
            transform: translateY(-2px);
        }}
        .btn-secondary {{
            background: var(--bg-tertiary);
            color: var(--text-primary);
        }}
        .btn-secondary:hover {{
            background: var(--border);
        }}

        /* Help Text */
        .help-text {{
            font-size: 0.8rem;
            color: var(--text-secondary);
            margin-top: 6px;
        }}

        /* Info Box */
        .info-box {{
            background: rgba(88, 166, 255, 0.1);
            border: 1px solid rgba(88, 166, 255, 0.3);
            border-radius: 8px;
            padding: 16px;
            margin-top: 16px;
        }}
        .info-box h4 {{
            color: #58a6ff;
            font-size: 0.9rem;
            margin-bottom: 8px;
        }}
        .info-box p {{
            color: var(--text-secondary);
            font-size: 0.85rem;
        }}

        /* Hidden */
        .hidden {{
            display: none !important;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>🔧 Audit CLI Builder</h1>
                <div class="meta">{repo_name} • v{version} • {timestamp}</div>
            </div>
        </div>

        <div class="main-grid">
            <!-- Sidebar: Command Selection -->
            <div class="sidebar">
                <h2>Select Command</h2>
                <div class="command-list">
                    <button class="command-btn active" data-command="run" onclick="selectCommand('run')">
                        <span class="cmd-name">▶️ run</span>
                        <span class="cmd-desc">Execute full audit pipeline (S1→S7)</span>
                    </button>
                    <button class="command-btn" data-command="validate" onclick="selectCommand('validate')">
                        <span class="cmd-name">✅ validate</span>
                        <span class="cmd-desc">Check quality gates</span>
                    </button>
                    <button class="command-btn" data-command="store-trend" onclick="selectCommand('store-trend')">
                        <span class="cmd-name">💾 store-trend</span>
                        <span class="cmd-desc">Store audit in trend database</span>
                    </button>
                    <button class="command-btn" data-command="show-trend" onclick="selectCommand('show-trend')">
                        <span class="cmd-name">📈 show-trend</span>
                        <span class="cmd-desc">Show capability trend history</span>
                    </button>
                    <button class="command-btn" data-command="check-regressions" onclick="selectCommand('check-regressions')">
                        <span class="cmd-name">⚠️ check-regressions</span>
                        <span class="cmd-desc">Detect score regressions</span>
                    </button>
                    <button class="command-btn" data-command="compare-runs" onclick="selectCommand('compare-runs')">
                        <span class="cmd-name">🔄 compare-runs</span>
                        <span class="cmd-desc">Compare two audit runs</span>
                    </button>
                    <button class="command-btn" data-command="dashboard" onclick="selectCommand('dashboard')">
                        <span class="cmd-name">📊 dashboard</span>
                        <span class="cmd-desc">Generate HTML dashboard</span>
                    </button>
                    <button class="command-btn" data-command="explain" onclick="selectCommand('explain')">
                        <span class="cmd-name">🔍 explain</span>
                        <span class="cmd-desc">Explain a capability's score</span>
                    </button>
                    <button class="command-btn" data-command="diff" onclick="selectCommand('diff')">
                        <span class="cmd-name">📋 diff</span>
                        <span class="cmd-desc">Diff two report files</span>
                    </button>
                    <button class="command-btn" data-command="stage" onclick="selectCommand('stage')">
                        <span class="cmd-name">🎯 stage</span>
                        <span class="cmd-desc">Run a single pipeline stage</span>
                    </button>
                </div>
            </div>

            <!-- Main Content -->
            <div class="content">
                <!-- Parameters Card -->
                <div class="card">
                    <h3>⚙️ Parameters</h3>

                    <!-- run command options -->
                    <div id="params-run" class="params-section">
                        <div class="info-box">
                            <h4>ℹ️ Full Pipeline Execution</h4>
                            <p>Runs all stages S1→S7: Index → Facets → Capabilities → Scoring → Gaps → Render → Manifest</p>
                        </div>
                    </div>

                    <!-- validate command options -->
                    <div id="params-validate" class="params-section hidden">
                        <div class="info-box">
                            <h4>ℹ️ Policy Validation</h4>
                            <p>Checks quality gates including low maturity thresholds and missing detectors.</p>
                        </div>
                    </div>

                    <!-- store-trend command options -->
                    <div id="params-store-trend" class="params-section hidden">
                        <div class="info-box">
                            <h4>ℹ️ Store Current Audit</h4>
                            <p>Stores the current audit results in the SQLite trend database for historical tracking.</p>
                        </div>
                    </div>

                    <!-- show-trend command options -->
                    <div id="params-show-trend" class="params-section hidden">
                        <div class="form-group">
                            <label class="form-label">Capability ID <span class="required">*</span></label>
                            <input type="text" class="form-input" id="show-trend-capability" placeholder="e.g., checkpointing" oninput="updatePreview()">
                            <div class="help-text">The capability ID to show trend for</div>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Limit (entries)</label>
                            <div class="knob-container">
                                <input type="range" class="knob-slider" id="show-trend-limit" min="5" max="100" value="30" oninput="updateKnobValue(this, 'show-trend-limit-value'); updatePreview()">
                                <span class="knob-value" id="show-trend-limit-value">30</span>
                            </div>
                            <div class="help-text">Number of historical entries to display</div>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Branch Filter (optional)</label>
                            <input type="text" class="form-input" id="show-trend-branch" placeholder="e.g., main" oninput="updatePreview()">
                            <div class="help-text">Filter results by git branch</div>
                        </div>
                    </div>

                    <!-- check-regressions command options -->
                    <div id="params-check-regressions" class="params-section hidden">
                        <div class="form-group">
                            <label class="form-label">Regression Threshold</label>
                            <div class="knob-container">
                                <input type="range" class="knob-slider" id="regression-threshold" min="0.01" max="0.10" step="0.01" value="0.02" oninput="updateKnobValue(this, 'regression-threshold-value', true); updatePreview()">
                                <span class="knob-value" id="regression-threshold-value">0.02</span>
                            </div>
                            <div class="help-text">Score drop threshold to flag as regression (0.02 = 2%)</div>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Lookback Runs</label>
                            <div class="knob-container">
                                <input type="range" class="knob-slider" id="regression-lookback" min="2" max="20" value="5" oninput="updateKnobValue(this, 'regression-lookback-value'); updatePreview()">
                                <span class="knob-value" id="regression-lookback-value">5</span>
                            </div>
                            <div class="help-text">Number of previous runs to compare against</div>
                        </div>
                    </div>

                    <!-- compare-runs command options -->
                    <div id="params-compare-runs" class="params-section hidden">
                        <div class="form-group">
                            <label class="form-label">Old File Path <span class="required">*</span></label>
                            <input type="text" class="form-input" id="compare-old" placeholder="path/to/old/capabilities_scored.json" oninput="updatePreview()">
                        </div>
                        <div class="form-group">
                            <label class="form-label">New File Path <span class="required">*</span></label>
                            <input type="text" class="form-input" id="compare-new" placeholder="path/to/new/capabilities_scored.json" oninput="updatePreview()">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Output Report Path (optional)</label>
                            <input type="text" class="form-input" id="compare-output" placeholder="path/to/comparison_report.md" oninput="updatePreview()">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Comparison Threshold</label>
                            <div class="knob-container">
                                <input type="range" class="knob-slider" id="compare-threshold" min="0.01" max="0.10" step="0.01" value="0.02" oninput="updateKnobValue(this, 'compare-threshold-value', true); updatePreview()">
                                <span class="knob-value" id="compare-threshold-value">0.02</span>
                            </div>
                        </div>
                    </div>

                    <!-- dashboard command options -->
                    <div id="params-dashboard" class="params-section hidden">
                        <div class="form-group">
                            <label class="form-label">Output Path (optional)</label>
                            <input type="text" class="form-input" id="dashboard-output" placeholder="audit_artifacts/dashboard.html" oninput="updatePreview()">
                            <div class="help-text">Leave empty for default location</div>
                        </div>
                    </div>

                    <!-- explain command options -->
                    <div id="params-explain" class="params-section hidden">
                        <div class="form-group">
                            <label class="form-label">Capability ID <span class="required">*</span></label>
                            <input type="text" class="form-input" id="explain-capability" placeholder="e.g., checkpointing" oninput="updatePreview()">
                            <div class="help-text">The capability ID to explain</div>
                        </div>
                    </div>

                    <!-- diff command options -->
                    <div id="params-diff" class="params-section hidden">
                        <div class="form-group">
                            <label class="form-label">Old File Path <span class="required">*</span></label>
                            <input type="text" class="form-input" id="diff-old" placeholder="path/to/old_report.json" oninput="updatePreview()">
                        </div>
                        <div class="form-group">
                            <label class="form-label">New File Path <span class="required">*</span></label>
                            <input type="text" class="form-input" id="diff-new" placeholder="path/to/new_report.json" oninput="updatePreview()">
                        </div>
                    </div>

                    <!-- stage command options -->
                    <div id="params-stage" class="params-section hidden">
                        <div class="form-group">
                            <label class="form-label">Stage ID <span class="required">*</span></label>
                            <select class="form-select" id="stage-id" onchange="updatePreview()">
                                <option value="S1">S1 - Index (scan repository)</option>
                                <option value="S2">S2 - Facets (extract features)</option>
                                <option value="S3">S3 - Capabilities (detect capabilities)</option>
                                <option value="S4">S4 - Scoring (calculate scores)</option>
                                <option value="S5">S5 - Gaps (identify gaps)</option>
                                <option value="S6">S6 - Render (generate reports)</option>
                                <option value="S7">S7 - Manifest (create manifest)</option>
                                <option value="TRENDS">TRENDS - Trend aggregation</option>
                            </select>
                        </div>
                    </div>
                </div>

                <!-- Command Preview Card -->
                <div class="card">
                    <h3>📝 Command Preview</h3>
                    <div class="preview-box">
                        <button class="copy-btn" onclick="copyCommand()">📋 Copy</button>
                        <span class="preview-prompt">$ </span>
                        <span id="command-preview" class="preview-command">python -m scripts.space_traversal.audit_runner run</span>
                    </div>

                    <div class="action-buttons">
                        <button class="btn btn-primary" onclick="copyCommand()">
                            📋 Copy to Clipboard
                        </button>
                        <button class="btn btn-secondary" onclick="resetForm()">
                            🔄 Reset
                        </button>
                    </div>
                </div>

                <!-- Quick Actions Card -->
                <div class="card">
                    <h3>⚡ Quick Actions</h3>
                    <div class="checkbox-group">
                        <label class="checkbox-item" onclick="quickAction('self-audit')">
                            <span class="checkbox-mark"></span>
                            <span>🔍 Self-Audit</span>
                        </label>
                        <label class="checkbox-item" onclick="quickAction('full-report')">
                            <span class="checkbox-mark"></span>
                            <span>📊 Full Report</span>
                        </label>
                        <label class="checkbox-item" onclick="quickAction('regression-check')">
                            <span class="checkbox-mark"></span>
                            <span>⚠️ Check Regressions</span>
                        </label>
                        <label class="checkbox-item" onclick="quickAction('generate-dashboard')">
                            <span class="checkbox-mark"></span>
                            <span>🖥️ Generate Dashboard</span>
                        </label>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentCommand = 'run';

        function selectCommand(cmd) {{
            currentCommand = cmd;

            // Update button states
            document.querySelectorAll('.command-btn').forEach(btn => {{
                btn.classList.remove('active');
                if (btn.dataset.command === cmd) {{
                    btn.classList.add('active');
                }}
            }});

            // Show/hide parameter sections
            document.querySelectorAll('.params-section').forEach(section => {{
                section.classList.add('hidden');
            }});
            const params = document.getElementById('params-' + cmd);
            if (params) {{
                params.classList.remove('hidden');
            }}

            updatePreview();
        }}

        function updateKnobValue(slider, valueId, isFloat = false) {{
            const valueEl = document.getElementById(valueId);
            valueEl.textContent = isFloat ? parseFloat(slider.value).toFixed(2) : slider.value;
        }}

        function updatePreview() {{
            let cmd = 'python -m scripts.space_traversal.audit_runner ' + currentCommand;

            switch(currentCommand) {{
                case 'show-trend':
                    const cap = document.getElementById('show-trend-capability').value;
                    if (cap) cmd += ' ' + cap;
                    const limit = document.getElementById('show-trend-limit').value;
                    if (limit !== '30') cmd += ' --limit ' + limit;
                    const branch = document.getElementById('show-trend-branch').value;
                    if (branch) cmd += ' --branch ' + branch;
                    break;

                case 'check-regressions':
                    const threshold = document.getElementById('regression-threshold').value;
                    if (threshold !== '0.02') cmd += ' --threshold ' + threshold;
                    const lookback = document.getElementById('regression-lookback').value;
                    if (lookback !== '5') cmd += ' --lookback ' + lookback;
                    break;

                case 'compare-runs':
                    const oldPath = document.getElementById('compare-old').value;
                    const newPath = document.getElementById('compare-new').value;
                    if (oldPath) cmd += ' --old ' + oldPath;
                    if (newPath) cmd += ' --new ' + newPath;
                    const output = document.getElementById('compare-output').value;
                    if (output) cmd += ' --output ' + output;
                    const cmpThreshold = document.getElementById('compare-threshold').value;
                    if (cmpThreshold !== '0.02') cmd += ' --threshold ' + cmpThreshold;
                    break;

                case 'dashboard':
                    const dashOutput = document.getElementById('dashboard-output').value;
                    if (dashOutput) cmd += ' --output ' + dashOutput;
                    break;

                case 'explain':
                    const explainCap = document.getElementById('explain-capability').value;
                    if (explainCap) cmd += ' ' + explainCap;
                    break;

                case 'diff':
                    const diffOld = document.getElementById('diff-old').value;
                    const diffNew = document.getElementById('diff-new').value;
                    if (diffOld) cmd += ' --old ' + diffOld;
                    if (diffNew) cmd += ' --new ' + diffNew;
                    break;

                case 'stage':
                    const stageId = document.getElementById('stage-id').value;
                    cmd += ' ' + stageId;
                    break;
            }}

            // Syntax highlight the command
            const preview = document.getElementById('command-preview');
            preview.innerHTML = highlightCommand(cmd);
        }}

        function highlightCommand(cmd) {{
            // Simple syntax highlighting
            return cmd
                .replace(/(python -m scripts\\.space_traversal\\.audit_runner)/g, '<span class="preview-command">$1</span>')
                .replace(/(--\\w+)/g, '<span class="preview-flag">$1</span>')
                .replace(/( [A-Z]\\d)/g, '<span class="preview-arg">$1</span>');
        }}

        function copyCommand() {{
            const preview = document.getElementById('command-preview');
            const text = preview.textContent || preview.innerText;
            navigator.clipboard.writeText(text).then(() => {{
                const btn = document.querySelector('.copy-btn');
                btn.textContent = '✅ Copied!';
                btn.classList.add('copied');
                setTimeout(() => {{
                    btn.textContent = '📋 Copy';
                    btn.classList.remove('copied');
                }}, 2000);
            }});
        }}

        function resetForm() {{
            // Reset all form inputs
            document.querySelectorAll('.form-input').forEach(input => {{
                input.value = '';
            }});
            document.querySelectorAll('.knob-slider').forEach(slider => {{
                slider.value = slider.defaultValue;
                const valueId = slider.id + '-value';
                const valueEl = document.getElementById(valueId);
                if (valueEl) {{
                    valueEl.textContent = slider.defaultValue;
                }}
            }});
            document.getElementById('stage-id').selectedIndex = 0;
            updatePreview();
        }}

        function quickAction(action) {{
            switch(action) {{
                case 'self-audit':
                    selectCommand('run');
                    break;
                case 'full-report':
                    selectCommand('run');
                    setTimeout(() => {{
                        selectCommand('dashboard');
                    }}, 100);
                    break;
                case 'regression-check':
                    selectCommand('check-regressions');
                    break;
                case 'generate-dashboard':
                    selectCommand('dashboard');
                    break;
            }}
        }}

        // Initialize
        updatePreview();
    </script>
</body>
</html>
"""


def generate_cli_builder(
    output_path: Path,
    repo_name: str = "Repository",
    version: str = "1.5.3",
) -> None:
    """
    Generate CLI builder HTML page.

    Args:
        output_path: Path to write HTML file
        repo_name: Repository name for display
        version: Pipeline version
    """
    from datetime import datetime, timezone

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    html = CLI_BUILDER_TEMPLATE.format(
        repo_name=repo_name,
        version=version,
        timestamp=timestamp,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
