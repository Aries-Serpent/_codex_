"""
Agent Control Interface for Audit Pipeline v1.5.x

Generates an HTML interface specifically designed for AI agents (ChatGPT 5.1 Agent mode)
to navigate, understand, and trigger actions on the audit pipeline.

Features:
- Semantic HTML structure with clear action affordances
- Machine-readable data attributes
- Explicit action buttons with predictable outcomes
- Structured capability selection
- Report generation triggers
- Full repo-wide validation controls
"""

from __future__ import annotations

from pathlib import Path

__all__ = ["generate_agent_interface", "AGENT_INTERFACE_TEMPLATE"]


AGENT_INTERFACE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="AI Agent Control Interface for Audit Pipeline - Designed for ChatGPT 5.1 Agent Mode">
    <meta name="agent-compatible" content="true">
    <meta name="agent-version" content="chatgpt-5.1">
    <meta name="pipeline-version" content="{version}">
    <title>🤖 Agent Control Interface - {repo_name}</title>
    
    <!-- Agent-readable metadata -->
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": "Audit Pipeline Agent Interface",
        "version": "{version}",
        "description": "AI Agent control interface for repository audit and validation",
        "applicationCategory": "DeveloperApplication",
        "operatingSystem": "Web",
        "offers": {{
            "@type": "Offer",
            "price": "0"
        }},
        "featureList": [
            "Full repository validation",
            "Per-capability audit triggers",
            "Trend analysis and comparison",
            "Report generation",
            "Regression detection",
            "Dashboard generation"
        ]
    }}
    </script>
    
    <style>
        :root {{
            --bg-primary: #0f1419;
            --bg-secondary: #192734;
            --bg-card: #22303c;
            --bg-input: #253341;
            --accent: #1d9bf0;
            --accent-green: #00ba7c;
            --accent-orange: #ff7a00;
            --accent-red: #f4212e;
            --accent-purple: #7856ff;
            --text-primary: #e7e9ea;
            --text-secondary: #71767b;
            --border: #38444d;
            --hover: #2c3640;
        }}
        
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.5;
            min-height: 100vh;
        }}
        
        /* Agent Instructions Banner */
        .agent-banner {{
            background: linear-gradient(135deg, var(--accent-purple) 0%, var(--accent) 100%);
            padding: 20px;
            text-align: center;
            border-bottom: 2px solid var(--border);
        }}
        .agent-banner h1 {{
            font-size: 1.5rem;
            margin-bottom: 8px;
        }}
        .agent-banner p {{
            opacity: 0.9;
            font-size: 0.95rem;
        }}
        
        /* Main Container */
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        /* Agent Instructions Section */
        .agent-instructions {{
            background: var(--bg-card);
            border: 2px solid var(--accent);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 24px;
        }}
        .agent-instructions h2 {{
            color: var(--accent);
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .agent-instructions pre {{
            background: var(--bg-input);
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            font-size: 0.9rem;
            line-height: 1.6;
        }}
        
        /* Action Grid */
        .action-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 24px;
        }}
        
        /* Action Card */
        .action-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            overflow: hidden;
        }}
        .action-card[data-priority="high"] {{
            border-color: var(--accent-green);
        }}
        .action-card[data-priority="medium"] {{
            border-color: var(--accent-orange);
        }}
        
        .card-header {{
            padding: 16px 20px;
            background: var(--bg-secondary);
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .card-header .icon {{
            font-size: 1.5rem;
        }}
        .card-header .title {{
            font-weight: 600;
            font-size: 1.1rem;
        }}
        .card-header .badge {{
            margin-left: auto;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.75rem;
            text-transform: uppercase;
        }}
        .badge-primary {{ background: var(--accent); }}
        .badge-success {{ background: var(--accent-green); }}
        .badge-warning {{ background: var(--accent-orange); }}
        
        .card-body {{
            padding: 20px;
        }}
        .card-body p {{
            color: var(--text-secondary);
            margin-bottom: 16px;
        }}
        
        /* Form Controls */
        .form-group {{
            margin-bottom: 16px;
        }}
        .form-group label {{
            display: block;
            margin-bottom: 6px;
            font-weight: 500;
            font-size: 0.9rem;
        }}
        .form-group input,
        .form-group select,
        .form-group textarea {{
            width: 100%;
            padding: 10px 14px;
            background: var(--bg-input);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text-primary);
            font-size: 0.95rem;
        }}
        .form-group input:focus,
        .form-group select:focus {{
            outline: none;
            border-color: var(--accent);
        }}
        
        /* Checkbox Group */
        .checkbox-group {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 8px;
        }}
        .checkbox-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 12px;
            background: var(--bg-input);
            border-radius: 6px;
            cursor: pointer;
            transition: background 0.2s;
        }}
        .checkbox-item:hover {{
            background: var(--hover);
        }}
        .checkbox-item input[type="checkbox"] {{
            width: 18px;
            height: 18px;
            accent-color: var(--accent);
        }}
        
        /* Action Buttons */
        .action-btn {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            width: 100%;
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .action-btn-primary {{
            background: var(--accent);
            color: white;
        }}
        .action-btn-primary:hover {{
            background: #1a8cd8;
        }}
        .action-btn-success {{
            background: var(--accent-green);
            color: white;
        }}
        .action-btn-success:hover {{
            background: #00a36c;
        }}
        .action-btn-warning {{
            background: var(--accent-orange);
            color: white;
        }}
        .action-btn-warning:hover {{
            background: #e66d00;
        }}
        .action-btn-secondary {{
            background: var(--bg-input);
            color: var(--text-primary);
            border: 1px solid var(--border);
        }}
        .action-btn-secondary:hover {{
            background: var(--hover);
        }}
        
        /* Command Output */
        .command-output {{
            background: var(--bg-input);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 12px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 0.85rem;
            margin-top: 12px;
            white-space: pre-wrap;
            word-break: break-all;
        }}
        
        /* Capability List */
        .capability-list {{
            max-height: 300px;
            overflow-y: auto;
            border: 1px solid var(--border);
            border-radius: 8px;
        }}
        .capability-item {{
            display: flex;
            align-items: center;
            padding: 12px 16px;
            border-bottom: 1px solid var(--border);
            cursor: pointer;
            transition: background 0.2s;
        }}
        .capability-item:last-child {{
            border-bottom: none;
        }}
        .capability-item:hover {{
            background: var(--hover);
        }}
        .capability-item.selected {{
            background: rgba(29, 155, 240, 0.1);
            border-left: 3px solid var(--accent);
        }}
        .capability-item input {{
            margin-right: 12px;
        }}
        .capability-item .name {{
            flex: 1;
            font-weight: 500;
        }}
        .capability-item .score {{
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }}
        .score-high {{ background: var(--accent-green); color: #000; }}
        .score-medium {{ background: var(--accent-orange); color: #000; }}
        .score-low {{ background: var(--accent-red); color: #fff; }}
        
        /* Quick Actions Bar */
        .quick-actions {{
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin-bottom: 24px;
        }}
        .quick-action {{
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 10px 16px;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text-primary);
            text-decoration: none;
            font-weight: 500;
            transition: all 0.2s;
            cursor: pointer;
        }}
        .quick-action:hover {{
            background: var(--hover);
            border-color: var(--accent);
        }}
        
        /* Status Indicator */
        .status-bar {{
            display: flex;
            align-items: center;
            gap: 20px;
            padding: 16px 20px;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            margin-bottom: 24px;
        }}
        .status-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .status-dot {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
        }}
        .status-dot.active {{ background: var(--accent-green); }}
        .status-dot.warning {{ background: var(--accent-orange); }}
        .status-dot.error {{ background: var(--accent-red); }}
        
        /* Results Panel */
        .results-panel {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            margin-top: 24px;
            overflow: hidden;
        }}
        .results-header {{
            padding: 16px 20px;
            background: var(--bg-secondary);
            border-bottom: 1px solid var(--border);
            font-weight: 600;
        }}
        .results-body {{
            padding: 20px;
            max-height: 400px;
            overflow-y: auto;
        }}
        .results-body pre {{
            background: var(--bg-input);
            padding: 15px;
            border-radius: 8px;
            font-family: 'Consolas', monospace;
            font-size: 0.85rem;
            white-space: pre-wrap;
        }}
        
        /* Agent Data Section */
        .agent-data {{
            display: none;
        }}
        
        /* Responsive */
        @media (max-width: 768px) {{
            .action-grid {{
                grid-template-columns: 1fr;
            }}
            .checkbox-group {{
                grid-template-columns: 1fr;
            }}
            .quick-actions {{
                flex-direction: column;
            }}
        }}
    </style>
</head>
<body>
    <!-- Agent Banner -->
    <div class="agent-banner">
        <h1>🤖 AI Agent Control Interface</h1>
        <p>Audit Pipeline v{version} • Designed for ChatGPT 5.1 Agent Mode</p>
    </div>
    
    <div class="container">
        <!-- Agent Instructions -->
        <section class="agent-instructions" data-section="instructions" aria-label="Instructions for AI Agents">
            <h2>📋 Agent Instructions</h2>
            <pre>
AGENT NAVIGATION GUIDE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. FULL REPOSITORY VALIDATION:
   → Click "🔍 Run Full Audit" button in Quick Actions
   → Or use Action Card: "Repository-Wide Validation"
   
2. PER-CAPABILITY AUDIT:
   → Go to "Capability Selection" card
   → Check desired capabilities from the list
   → Click "Run Selected Capability Audit"
   
3. GENERATE REPORTS:
   → Use "Report Generation" card
   → Select report type (Dashboard, Trend, Comparison)
   → Configure options and click generate
   
4. CHECK REGRESSIONS:
   → Click "⚠️ Check Regressions" in Quick Actions
   → Or configure threshold in "Regression Detection" card
   
5. VIEW TRENDS:
   → Select capability in "Trend Analysis" card
   → Choose time range and visualization type

AVAILABLE COMMANDS (for programmatic access):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
python -m scripts.space_traversal.audit_runner run
python -m scripts.space_traversal.audit_runner check-regressions
python -m scripts.space_traversal.audit_runner show-trend [CAPABILITY]
python -m scripts.space_traversal.audit_runner dashboard
python -m scripts.space_traversal.audit_runner store-trend
            </pre>
        </section>
        
        <!-- Status Bar -->
        <div class="status-bar" data-section="status" aria-label="System Status">
            <div class="status-item">
                <span class="status-dot active"></span>
                <span>Pipeline: Active</span>
            </div>
            <div class="status-item">
                <span class="status-dot active"></span>
                <span>Database: Connected</span>
            </div>
            <div class="status-item">
                <span class="status-dot active"></span>
                <span>Version: v{version}</span>
            </div>
            <div class="status-item">
                <span class="status-dot active"></span>
                <span>Capabilities: 18 tracked</span>
            </div>
        </div>
        
        <!-- Quick Actions -->
        <nav class="quick-actions" data-section="quick-actions" aria-label="Quick Actions">
            <button class="quick-action" data-action="full-audit" onclick="runFullAudit()">
                🔍 Run Full Audit
            </button>
            <button class="quick-action" data-action="check-regressions" onclick="checkRegressions()">
                ⚠️ Check Regressions
            </button>
            <button class="quick-action" data-action="generate-dashboard" onclick="generateDashboard()">
                📊 Generate Dashboard
            </button>
            <button class="quick-action" data-action="store-trend" onclick="storeTrend()">
                💾 Store Trend Data
            </button>
            <button class="quick-action" data-action="export-csv" onclick="exportCSV()">
                📥 Export CSV
            </button>
            <button class="quick-action" data-action="view-docs" onclick="openDocs()">
                📚 View Documentation
            </button>
        </nav>
        
        <!-- Action Grid -->
        <div class="action-grid">
            <!-- Repository-Wide Validation -->
            <article class="action-card" data-priority="high" data-action-type="validation">
                <div class="card-header">
                    <span class="icon">🔍</span>
                    <span class="title">Repository-Wide Validation</span>
                    <span class="badge badge-success">Primary</span>
                </div>
                <div class="card-body">
                    <p>Execute comprehensive repository audit across all capabilities with configurable options.</p>
                    
                    <div class="form-group">
                        <label for="validation-scope">Validation Scope</label>
                        <select id="validation-scope" data-param="scope">
                            <option value="full">Full Repository Scan</option>
                            <option value="changed">Changed Files Only</option>
                            <option value="critical">Critical Capabilities Only</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label>Validation Options</label>
                        <div class="checkbox-group">
                            <label class="checkbox-item">
                                <input type="checkbox" data-option="store-results" checked>
                                <span>Store Results</span>
                            </label>
                            <label class="checkbox-item">
                                <input type="checkbox" data-option="check-regressions" checked>
                                <span>Check Regressions</span>
                            </label>
                            <label class="checkbox-item">
                                <input type="checkbox" data-option="generate-report">
                                <span>Generate Report</span>
                            </label>
                            <label class="checkbox-item">
                                <input type="checkbox" data-option="notify-webhook">
                                <span>Send Notifications</span>
                            </label>
                        </div>
                    </div>
                    
                    <button class="action-btn action-btn-success" data-action="run-validation" onclick="runValidation()">
                        ▶️ Execute Full Validation
                    </button>
                    
                    <div class="command-output" id="validation-output">
Command: python -m scripts.space_traversal.audit_runner run --store-trend
Status: Ready
                    </div>
                </div>
            </article>
            
            <!-- Capability Selection -->
            <article class="action-card" data-priority="high" data-action-type="capability-audit">
                <div class="card-header">
                    <span class="icon">📋</span>
                    <span class="title">Capability Selection</span>
                    <span class="badge badge-primary">Per-Capability</span>
                </div>
                <div class="card-body">
                    <p>Select specific capabilities to audit. Click to select, then run audit on selection.</p>
                    
                    <div class="form-group">
                        <div style="display: flex; gap: 8px; margin-bottom: 12px;">
                            <button class="action-btn action-btn-secondary" style="flex:1" onclick="selectAll()">Select All</button>
                            <button class="action-btn action-btn-secondary" style="flex:1" onclick="selectNone()">Clear All</button>
                            <button class="action-btn action-btn-secondary" style="flex:1" onclick="selectFailing()">Select Failing</button>
                        </div>
                    </div>
                    
                    <div class="capability-list" data-component="capability-selector" aria-label="Capability Selection List">
                        <label class="capability-item" data-capability="checkpointing" data-score="0.95">
                            <input type="checkbox" name="capability" value="checkpointing">
                            <span class="name">checkpointing</span>
                            <span class="score score-high">0.95</span>
                        </label>
                        <label class="capability-item" data-capability="experiment_tracking" data-score="0.92">
                            <input type="checkbox" name="capability" value="experiment_tracking">
                            <span class="name">experiment_tracking</span>
                            <span class="score score-high">0.92</span>
                        </label>
                        <label class="capability-item" data-capability="model_registry" data-score="0.88">
                            <input type="checkbox" name="capability" value="model_registry">
                            <span class="name">model_registry</span>
                            <span class="score score-high">0.88</span>
                        </label>
                        <label class="capability-item" data-capability="data_versioning" data-score="0.85">
                            <input type="checkbox" name="capability" value="data_versioning">
                            <span class="name">data_versioning</span>
                            <span class="score score-high">0.85</span>
                        </label>
                        <label class="capability-item" data-capability="pipeline_orchestration" data-score="0.82">
                            <input type="checkbox" name="capability" value="pipeline_orchestration">
                            <span class="name">pipeline_orchestration</span>
                            <span class="score score-medium">0.82</span>
                        </label>
                        <label class="capability-item" data-capability="feature_store" data-score="0.78">
                            <input type="checkbox" name="capability" value="feature_store">
                            <span class="name">feature_store</span>
                            <span class="score score-medium">0.78</span>
                        </label>
                        <label class="capability-item" data-capability="model_serving" data-score="0.75">
                            <input type="checkbox" name="capability" value="model_serving">
                            <span class="name">model_serving</span>
                            <span class="score score-medium">0.75</span>
                        </label>
                        <label class="capability-item" data-capability="monitoring" data-score="0.90">
                            <input type="checkbox" name="capability" value="monitoring">
                            <span class="name">monitoring</span>
                            <span class="score score-high">0.90</span>
                        </label>
                        <label class="capability-item" data-capability="drift_detection" data-score="0.87">
                            <input type="checkbox" name="capability" value="drift_detection">
                            <span class="name">drift_detection</span>
                            <span class="score score-high">0.87</span>
                        </label>
                        <label class="capability-item" data-capability="auto_retraining" data-score="0.85">
                            <input type="checkbox" name="capability" value="auto_retraining">
                            <span class="name">auto_retraining</span>
                            <span class="score score-high">0.85</span>
                        </label>
                        <label class="capability-item" data-capability="ci_cd_integration" data-score="0.93">
                            <input type="checkbox" name="capability" value="ci_cd_integration">
                            <span class="name">ci_cd_integration</span>
                            <span class="score score-high">0.93</span>
                        </label>
                        <label class="capability-item" data-capability="testing_framework" data-score="0.91">
                            <input type="checkbox" name="capability" value="testing_framework">
                            <span class="name">testing_framework</span>
                            <span class="score score-high">0.91</span>
                        </label>
                        <label class="capability-item" data-capability="documentation" data-score="0.89">
                            <input type="checkbox" name="capability" value="documentation">
                            <span class="name">documentation</span>
                            <span class="score score-high">0.89</span>
                        </label>
                        <label class="capability-item" data-capability="security_scanning" data-score="0.94">
                            <input type="checkbox" name="capability" value="security_scanning">
                            <span class="name">security_scanning</span>
                            <span class="score score-high">0.94</span>
                        </label>
                        <label class="capability-item" data-capability="compliance" data-score="0.86">
                            <input type="checkbox" name="capability" value="compliance">
                            <span class="name">compliance</span>
                            <span class="score score-high">0.86</span>
                        </label>
                        <label class="capability-item" data-capability="cost_management" data-score="0.72">
                            <input type="checkbox" name="capability" value="cost_management">
                            <span class="name">cost_management</span>
                            <span class="score score-medium">0.72</span>
                        </label>
                        <label class="capability-item" data-capability="reproducibility" data-score="0.88">
                            <input type="checkbox" name="capability" value="reproducibility">
                            <span class="name">reproducibility</span>
                            <span class="score score-high">0.88</span>
                        </label>
                        <label class="capability-item" data-capability="governance" data-score="0.84">
                            <input type="checkbox" name="capability" value="governance">
                            <span class="name">governance</span>
                            <span class="score score-medium">0.84</span>
                        </label>
                    </div>
                    
                    <button class="action-btn action-btn-primary" style="margin-top: 16px" data-action="run-selected" onclick="runSelectedCapabilities()">
                        ▶️ Run Selected Capability Audit
                    </button>
                </div>
            </article>
            
            <!-- Report Generation -->
            <article class="action-card" data-priority="medium" data-action-type="report">
                <div class="card-header">
                    <span class="icon">📊</span>
                    <span class="title">Report Generation</span>
                    <span class="badge badge-warning">Reports</span>
                </div>
                <div class="card-body">
                    <p>Generate various reports and visualizations from audit data.</p>
                    
                    <div class="form-group">
                        <label for="report-type">Report Type</label>
                        <select id="report-type" data-param="report-type" onchange="updateReportOptions()">
                            <option value="dashboard">HTML Dashboard</option>
                            <option value="trend">Trend Report (Markdown)</option>
                            <option value="comparison">Comparison Report</option>
                            <option value="regression">Regression Report</option>
                            <option value="csv">CSV Export</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="report-output">Output Path</label>
                        <input type="text" id="report-output" data-param="output" value="audit_artifacts/dashboard.html">
                    </div>
                    
                    <div class="form-group" id="trend-options" style="display:none">
                        <label for="trend-limit">Trend History Limit</label>
                        <input type="number" id="trend-limit" data-param="limit" value="30" min="5" max="100">
                    </div>
                    
                    <div class="form-group" id="comparison-options" style="display:none">
                        <label for="baseline-path">Baseline Path</label>
                        <input type="text" id="baseline-path" data-param="baseline" value="audit_artifacts/baseline.json">
                    </div>
                    
                    <button class="action-btn action-btn-primary" data-action="generate-report" onclick="generateReport()">
                        📝 Generate Report
                    </button>
                    
                    <div class="command-output" id="report-output-display">
Command: python -m scripts.space_traversal.audit_runner dashboard --output audit_artifacts/dashboard.html
Status: Ready
                    </div>
                </div>
            </article>
            
            <!-- Regression Detection -->
            <article class="action-card" data-priority="medium" data-action-type="regression">
                <div class="card-header">
                    <span class="icon">⚠️</span>
                    <span class="title">Regression Detection</span>
                    <span class="badge badge-warning">Monitoring</span>
                </div>
                <div class="card-body">
                    <p>Detect and analyze score regressions compared to historical data.</p>
                    
                    <div class="form-group">
                        <label for="regression-threshold">Regression Threshold</label>
                        <input type="range" id="regression-threshold" data-param="threshold" min="0.01" max="0.10" step="0.01" value="0.02" oninput="updateThresholdDisplay()">
                        <div style="display:flex; justify-content:space-between; font-size:0.85rem; color:var(--text-secondary)">
                            <span>1%</span>
                            <span id="threshold-value">2%</span>
                            <span>10%</span>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label for="lookback-runs">Lookback Runs</label>
                        <select id="lookback-runs" data-param="lookback">
                            <option value="3">Last 3 runs</option>
                            <option value="5" selected>Last 5 runs</option>
                            <option value="10">Last 10 runs</option>
                            <option value="20">Last 20 runs</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label>Options</label>
                        <div class="checkbox-group">
                            <label class="checkbox-item">
                                <input type="checkbox" data-option="fail-on-high" checked>
                                <span>Fail on High Severity</span>
                            </label>
                            <label class="checkbox-item">
                                <input type="checkbox" data-option="notify" checked>
                                <span>Send Notifications</span>
                            </label>
                        </div>
                    </div>
                    
                    <button class="action-btn action-btn-warning" data-action="check-regressions" onclick="runRegressionCheck()">
                        🔎 Run Regression Check
                    </button>
                </div>
            </article>
            
            <!-- Trend Analysis -->
            <article class="action-card" data-priority="medium" data-action-type="trend">
                <div class="card-header">
                    <span class="icon">📈</span>
                    <span class="title">Trend Analysis</span>
                    <span class="badge badge-primary">Analytics</span>
                </div>
                <div class="card-body">
                    <p>Analyze historical trends for specific capabilities.</p>
                    
                    <div class="form-group">
                        <label for="trend-capability">Capability</label>
                        <select id="trend-capability" data-param="capability">
                            <option value="">-- Select Capability --</option>
                            <option value="checkpointing">checkpointing</option>
                            <option value="experiment_tracking">experiment_tracking</option>
                            <option value="model_registry">model_registry</option>
                            <option value="data_versioning">data_versioning</option>
                            <option value="pipeline_orchestration">pipeline_orchestration</option>
                            <option value="feature_store">feature_store</option>
                            <option value="model_serving">model_serving</option>
                            <option value="monitoring">monitoring</option>
                            <option value="drift_detection">drift_detection</option>
                            <option value="auto_retraining">auto_retraining</option>
                            <option value="ci_cd_integration">ci_cd_integration</option>
                            <option value="testing_framework">testing_framework</option>
                            <option value="documentation">documentation</option>
                            <option value="security_scanning">security_scanning</option>
                            <option value="compliance">compliance</option>
                            <option value="cost_management">cost_management</option>
                            <option value="reproducibility">reproducibility</option>
                            <option value="governance">governance</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="trend-range">Time Range</label>
                        <select id="trend-range" data-param="range">
                            <option value="10">Last 10 runs</option>
                            <option value="20" selected>Last 20 runs</option>
                            <option value="30">Last 30 runs</option>
                            <option value="50">Last 50 runs</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="trend-format">Output Format</label>
                        <select id="trend-format" data-param="format">
                            <option value="table">Table</option>
                            <option value="sparkline">Sparkline (ASCII)</option>
                            <option value="json">JSON</option>
                            <option value="csv">CSV</option>
                        </select>
                    </div>
                    
                    <button class="action-btn action-btn-primary" data-action="show-trend" onclick="showTrend()">
                        📊 Show Trend
                    </button>
                </div>
            </article>
            
            <!-- Webhook Configuration -->
            <article class="action-card" data-priority="low" data-action-type="webhook">
                <div class="card-header">
                    <span class="icon">🔔</span>
                    <span class="title">Notifications</span>
                    <span class="badge badge-primary">Webhooks</span>
                </div>
                <div class="card-body">
                    <p>Configure and test webhook notifications.</p>
                    
                    <div class="form-group">
                        <label for="webhook-type">Notification Type</label>
                        <select id="webhook-type" data-param="type">
                            <option value="slack">Slack</option>
                            <option value="teams">Microsoft Teams</option>
                            <option value="generic">Generic Webhook</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="webhook-url">Webhook URL</label>
                        <input type="text" id="webhook-url" data-param="url" placeholder="https://hooks.slack.com/...">
                    </div>
                    
                    <div class="form-group">
                        <label>Trigger Events</label>
                        <div class="checkbox-group">
                            <label class="checkbox-item">
                                <input type="checkbox" data-event="audit_complete" checked>
                                <span>Audit Complete</span>
                            </label>
                            <label class="checkbox-item">
                                <input type="checkbox" data-event="regression_detected" checked>
                                <span>Regression Detected</span>
                            </label>
                            <label class="checkbox-item">
                                <input type="checkbox" data-event="threshold_crossed">
                                <span>Threshold Crossed</span>
                            </label>
                            <label class="checkbox-item">
                                <input type="checkbox" data-event="improvement">
                                <span>Improvement</span>
                            </label>
                        </div>
                    </div>
                    
                    <button class="action-btn action-btn-secondary" data-action="test-webhook" onclick="testWebhook()">
                        🧪 Test Webhook
                    </button>
                </div>
            </article>
        </div>
        
        <!-- Results Panel -->
        <section class="results-panel" data-section="results" aria-label="Action Results">
            <div class="results-header">📋 Action Results</div>
            <div class="results-body">
                <pre id="results-content">
╔════════════════════════════════════════════════════════════════════════════════╗
║  AUDIT PIPELINE v{version} - Agent Control Interface                            ║
╠════════════════════════════════════════════════════════════════════════════════╣
║                                                                                ║
║  Ready to execute actions. Select an action above to begin.                    ║
║                                                                                ║
║  QUICK START FOR AGENTS:                                                       ║
║  1. Click "🔍 Run Full Audit" for complete repository validation               ║
║  2. Use "Capability Selection" to audit specific capabilities                  ║
║  3. Click "📊 Generate Dashboard" for visual reports                           ║
║                                                                                ║
║  All actions will display their output here with copy-ready commands.          ║
║                                                                                ║
╚════════════════════════════════════════════════════════════════════════════════╝
                </pre>
            </div>
        </section>
    </div>
    
    <!-- Agent-readable data (hidden) -->
    <div class="agent-data" aria-hidden="true">
        <script type="application/json" id="agent-commands">
        {{
            "commands": {{
                "full_audit": "python -m scripts.space_traversal.audit_runner run",
                "store_trend": "python -m scripts.space_traversal.audit_runner store-trend",
                "check_regressions": "python -m scripts.space_traversal.audit_runner check-regressions --threshold {{threshold}} --lookback {{lookback}}",
                "show_trend": "python -m scripts.space_traversal.audit_runner show-trend {{capability}} --limit {{limit}}",
                "dashboard": "python -m scripts.space_traversal.audit_runner dashboard --output {{output}}",
                "compare_runs": "python -m scripts.space_traversal.audit_runner compare-runs --old {{old}} --new {{new}}",
                "cli_builder": "python -m scripts.space_traversal.audit_runner cli-builder --output {{output}}",
                "api_collection": "python -m scripts.space_traversal.audit_runner api-collection --output {{output}}",
                "api_docs": "python -m scripts.space_traversal.audit_runner api-docs --output {{output}}"
            }},
            "capabilities": [
                "checkpointing", "experiment_tracking", "model_registry", "data_versioning",
                "pipeline_orchestration", "feature_store", "model_serving", "monitoring",
                "drift_detection", "auto_retraining", "ci_cd_integration", "testing_framework",
                "documentation", "security_scanning", "compliance", "cost_management",
                "reproducibility", "governance"
            ],
            "version": "{version}",
            "repo": "{repo_name}"
        }}
        </script>
    </div>
    
    <script>
        // Agent-friendly JavaScript functions
        
        function updateResults(content) {{
            document.getElementById('results-content').textContent = content;
        }}
        
        function runFullAudit() {{
            const scope = document.getElementById('validation-scope').value;
            const options = [];
            document.querySelectorAll('[data-option]:checked').forEach(cb => {{
                options.push(cb.dataset.option);
            }});
            
            const cmd = `python -m scripts.space_traversal.audit_runner run --scope ${{scope}}`;
            updateResults(`
╔════════════════════════════════════════════════════════════════════════════════╗
║  EXECUTING: Full Repository Audit                                              ║
╠════════════════════════════════════════════════════════════════════════════════╣

COMMAND:
${{cmd}}

OPTIONS:
- Scope: ${{scope}}
- Store Results: ${{options.includes('store-results')}}
- Check Regressions: ${{options.includes('check-regressions')}}
- Generate Report: ${{options.includes('generate-report')}}

STATUS: Command ready for execution
COPY THIS COMMAND AND RUN IN TERMINAL

╚════════════════════════════════════════════════════════════════════════════════╝
            `);
        }}
        
        function runValidation() {{
            runFullAudit();
        }}
        
        function checkRegressions() {{
            const threshold = document.getElementById('regression-threshold').value;
            const lookback = document.getElementById('lookback-runs').value;
            
            const cmd = `python -m scripts.space_traversal.audit_runner check-regressions --threshold ${{threshold}} --lookback ${{lookback}}`;
            updateResults(`
╔════════════════════════════════════════════════════════════════════════════════╗
║  EXECUTING: Regression Check                                                   ║
╠════════════════════════════════════════════════════════════════════════════════╣

COMMAND:
${{cmd}}

PARAMETERS:
- Threshold: ${{(threshold * 100).toFixed(0)}}%
- Lookback: ${{lookback}} runs

STATUS: Command ready for execution
COPY THIS COMMAND AND RUN IN TERMINAL

╚════════════════════════════════════════════════════════════════════════════════╝
            `);
        }}
        
        function runRegressionCheck() {{
            checkRegressions();
        }}
        
        function generateDashboard() {{
            const cmd = 'python -m scripts.space_traversal.audit_runner dashboard --output audit_artifacts/dashboard.html';
            updateResults(`
╔════════════════════════════════════════════════════════════════════════════════╗
║  EXECUTING: Dashboard Generation                                               ║
╠════════════════════════════════════════════════════════════════════════════════╣

COMMAND:
${{cmd}}

OUTPUT: audit_artifacts/dashboard.html

STATUS: Command ready for execution
COPY THIS COMMAND AND RUN IN TERMINAL

╚════════════════════════════════════════════════════════════════════════════════╝
            `);
        }}
        
        function storeTrend() {{
            const cmd = 'python -m scripts.space_traversal.audit_runner store-trend';
            updateResults(`
╔════════════════════════════════════════════════════════════════════════════════╗
║  EXECUTING: Store Trend Data                                                   ║
╠════════════════════════════════════════════════════════════════════════════════╣

COMMAND:
${{cmd}}

ACTION: Stores current audit results in trend database for historical analysis

STATUS: Command ready for execution
COPY THIS COMMAND AND RUN IN TERMINAL

╚════════════════════════════════════════════════════════════════════════════════╝
            `);
        }}
        
        function exportCSV() {{
            const cmd = 'python -c "from scripts.space_traversal.trend_db import TrendDatabase; db = TrendDatabase(); db.export_csv(Path(\\'audit_artifacts/trends.csv\\'))"';
            updateResults(`
╔════════════════════════════════════════════════════════════════════════════════╗
║  EXECUTING: CSV Export                                                         ║
╠════════════════════════════════════════════════════════════════════════════════╣

COMMAND:
${{cmd}}

OUTPUT: audit_artifacts/trends.csv

STATUS: Command ready for execution
COPY THIS COMMAND AND RUN IN TERMINAL

╚════════════════════════════════════════════════════════════════════════════════╝
            `);
        }}
        
        function openDocs() {{
            updateResults(`
╔════════════════════════════════════════════════════════════════════════════════╗
║  DOCUMENTATION LINKS                                                           ║
╠════════════════════════════════════════════════════════════════════════════════╣

LOCAL FILES:
- README.md                         - Repository overview
- AGENTS.md                         - Agent instructions
- docs/audit/v1.5.x_CHANGELOG.md    - v1.5.x changelog

GENERATED DOCS (run commands to generate):
- CLI Builder:     python -m scripts.space_traversal.audit_runner cli-builder
- API Collection:  python -m scripts.space_traversal.audit_runner api-collection  
- API Docs:        python -m scripts.space_traversal.audit_runner api-docs
- Wiki:            python -m scripts.space_traversal.wiki_generator

╚════════════════════════════════════════════════════════════════════════════════╝
            `);
        }}
        
        function selectAll() {{
            document.querySelectorAll('.capability-list input[type="checkbox"]').forEach(cb => cb.checked = true);
        }}
        
        function selectNone() {{
            document.querySelectorAll('.capability-list input[type="checkbox"]').forEach(cb => cb.checked = false);
        }}
        
        function selectFailing() {{
            document.querySelectorAll('.capability-item').forEach(item => {{
                const score = parseFloat(item.dataset.score);
                const checkbox = item.querySelector('input[type="checkbox"]');
                checkbox.checked = score < 0.85;
            }});
        }}
        
        function runSelectedCapabilities() {{
            const selected = [];
            document.querySelectorAll('.capability-list input[type="checkbox"]:checked').forEach(cb => {{
                selected.push(cb.value);
            }});
            
            if (selected.length === 0) {{
                updateResults('⚠️ No capabilities selected. Please select at least one capability.');
                return;
            }}
            
            const cmds = selected.map(cap => `python -m scripts.space_traversal.audit_runner show-trend ${{cap}}`);
            updateResults(`
╔════════════════════════════════════════════════════════════════════════════════╗
║  EXECUTING: Selected Capability Audit                                          ║
╠════════════════════════════════════════════════════════════════════════════════╣

SELECTED CAPABILITIES (${{selected.length}}):
${{selected.map(c => '  - ' + c).join('\\n')}}

COMMANDS TO RUN:
${{cmds.join('\\n')}}

STATUS: Commands ready for execution
COPY THESE COMMANDS AND RUN IN TERMINAL

╚════════════════════════════════════════════════════════════════════════════════╝
            `);
        }}
        
        function updateReportOptions() {{
            const type = document.getElementById('report-type').value;
            document.getElementById('trend-options').style.display = type === 'trend' ? 'block' : 'none';
            document.getElementById('comparison-options').style.display = type === 'comparison' ? 'block' : 'none';
            
            const outputMap = {{
                'dashboard': 'audit_artifacts/dashboard.html',
                'trend': 'audit_artifacts/trend_report.md',
                'comparison': 'audit_artifacts/comparison_report.md',
                'regression': 'audit_artifacts/regression_report.md',
                'csv': 'audit_artifacts/trends.csv'
            }};
            document.getElementById('report-output').value = outputMap[type] || 'audit_artifacts/report.html';
        }}
        
        function generateReport() {{
            const type = document.getElementById('report-type').value;
            const output = document.getElementById('report-output').value;
            
            const cmdMap = {{
                'dashboard': `python -m scripts.space_traversal.audit_runner dashboard --output ${{output}}`,
                'trend': `python -m scripts.space_traversal.audit_runner trend-report --output ${{output}}`,
                'comparison': `python -m scripts.space_traversal.audit_runner compare-runs --output ${{output}}`,
                'regression': `python -m scripts.space_traversal.audit_runner check-regressions --output ${{output}}`,
                'csv': `python -c "from scripts.space_traversal.trend_db import TrendDatabase; from pathlib import Path; db = TrendDatabase(); db.export_csv(Path('${{output}}'))"`
            }};
            
            updateResults(`
╔════════════════════════════════════════════════════════════════════════════════╗
║  EXECUTING: Report Generation                                                  ║
╠════════════════════════════════════════════════════════════════════════════════╣

REPORT TYPE: ${{type}}
OUTPUT: ${{output}}

COMMAND:
${{cmdMap[type]}}

STATUS: Command ready for execution
COPY THIS COMMAND AND RUN IN TERMINAL

╚════════════════════════════════════════════════════════════════════════════════╝
            `);
            
            document.getElementById('report-output-display').textContent = `Command: ${{cmdMap[type]}}\\nStatus: Ready`;
        }}
        
        function updateThresholdDisplay() {{
            const value = document.getElementById('regression-threshold').value;
            document.getElementById('threshold-value').textContent = (value * 100).toFixed(0) + '%';
        }}
        
        function showTrend() {{
            const capability = document.getElementById('trend-capability').value;
            const range = document.getElementById('trend-range').value;
            const format = document.getElementById('trend-format').value;
            
            if (!capability) {{
                updateResults('⚠️ Please select a capability to view its trend.');
                return;
            }}
            
            const cmd = `python -m scripts.space_traversal.audit_runner show-trend ${{capability}} --limit ${{range}} --format ${{format}}`;
            updateResults(`
╔════════════════════════════════════════════════════════════════════════════════╗
║  EXECUTING: Trend Analysis                                                     ║
╠════════════════════════════════════════════════════════════════════════════════╣

CAPABILITY: ${{capability}}
TIME RANGE: Last ${{range}} runs
FORMAT: ${{format}}

COMMAND:
${{cmd}}

STATUS: Command ready for execution
COPY THIS COMMAND AND RUN IN TERMINAL

╚════════════════════════════════════════════════════════════════════════════════╝
            `);
        }}
        
        function testWebhook() {{
            const type = document.getElementById('webhook-type').value;
            const url = document.getElementById('webhook-url').value;
            
            if (!url) {{
                updateResults('⚠️ Please enter a webhook URL to test.');
                return;
            }}
            
            updateResults(`
╔════════════════════════════════════════════════════════════════════════════════╗
║  WEBHOOK TEST                                                                  ║
╠════════════════════════════════════════════════════════════════════════════════╣

TYPE: ${{type}}
URL: ${{url}}

PYTHON CODE TO TEST:
from scripts.space_traversal.webhooks import AuditEvent, send_${{type}}_notification
import time

event = AuditEvent(
    event_type="test",
    repo_name="{repo_name}",
    timestamp=time.time(),
    avg_score=0.85,
    capability_count=18,
    regression_count=0,
    details={{}}
)

result = send_${{type}}_notification("${{url}}", event)
print(f"Success: {{result.success}}")

╚════════════════════════════════════════════════════════════════════════════════╝
            `);
        }}
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('Agent Control Interface v{version} loaded');
            console.log('Available commands:', JSON.parse(document.getElementById('agent-commands').textContent));
        }});
    </script>
</body>
</html>
"""


def generate_agent_interface(
    output_path: Path,
    repo_name: str = "Repository",
    version: str = "1.5.5",
) -> None:
    """
    Generate an AI agent-friendly control interface.

    This interface is specifically designed for ChatGPT 5.1 Agent mode
    to navigate, understand, and trigger actions on the audit pipeline.

    Args:
        output_path: Path to write the HTML file
        repo_name: Repository name for display
        version: Pipeline version
    """
    html = AGENT_INTERFACE_TEMPLATE.format(
        repo_name=repo_name,
        version=version,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    import sys

    output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("agent_interface.html")
    repo = sys.argv[2] if len(sys.argv) > 2 else "Aries-Serpent/_codex_"
    generate_agent_interface(output, repo)
    print(f"Generated agent interface: {output}")
