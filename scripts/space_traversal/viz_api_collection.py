#!/usr/bin/env python3
"""
Viz Api Collection

Purpose:
    [To be documented - Viz Api Collection]

Usage:
    python scripts/space_traversal/viz_api_collection.py [options]

    Examples:
    $ python scripts/space_traversal/viz_api_collection.py --help

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
from typing import Optional

__all__ = ["generate_api_collection", "API_COLLECTION_TEMPLATE"]


API_COLLECTION_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Audit API Collection - {repo_name} v{version}</title>
    <style>
        :root {{
            --bg-primary: #0d1117;
            --bg-secondary: #161b22;
            --bg-tertiary: #21262d;
            --bg-hover: #30363d;
            --accent: #58a6ff;
            --accent-green: #3fb950;
            --accent-orange: #d29922;
            --accent-red: #f85149;
            --accent-purple: #a371f7;
            --text-primary: #c9d1d9;
            --text-secondary: #8b949e;
            --border: #30363d;
            --shadow: rgba(0,0,0,0.3);
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            line-height: 1.5;
        }}

        /* Layout */
        .app-container {{
            display: grid;
            grid-template-columns: 280px 1fr 350px;
            min-height: 100vh;
        }}
        @media (max-width: 1200px) {{
            .app-container {{ grid-template-columns: 250px 1fr; }}
            .right-panel {{ display: none; }}
        }}
        @media (max-width: 768px) {{
            .app-container {{ grid-template-columns: 1fr; }}
            .left-panel {{ display: none; }}
        }}

        /* Left Panel - Collection List */
        .left-panel {{
            background: var(--bg-secondary);
            border-right: 1px solid var(--border);
            display: flex;
            flex-direction: column;
        }}
        .panel-header {{
            padding: 16px;
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .panel-header h2 {{
            font-size: 14px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--text-secondary);
        }}
        .panel-header .btn-icon {{
            width: 28px;
            height: 28px;
            border-radius: 6px;
            border: none;
            background: transparent;
            color: var(--text-secondary);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
        }}
        .panel-header .btn-icon:hover {{
            background: var(--bg-hover);
            color: var(--text-primary);
        }}

        /* Collection Tree */
        .collection-tree {{
            flex: 1;
            overflow-y: auto;
            padding: 8px;
        }}
        .collection-folder {{
            margin-bottom: 4px;
        }}
        .folder-header {{
            display: flex;
            align-items: center;
            padding: 8px 12px;
            border-radius: 6px;
            cursor: pointer;
            gap: 8px;
            transition: background 0.15s;
        }}
        .folder-header:hover {{
            background: var(--bg-hover);
        }}
        .folder-header .folder-icon {{
            font-size: 14px;
        }}
        .folder-header .folder-name {{
            flex: 1;
            font-size: 13px;
            font-weight: 500;
        }}
        .folder-header .folder-count {{
            font-size: 11px;
            color: var(--text-secondary);
            background: var(--bg-tertiary);
            padding: 2px 6px;
            border-radius: 10px;
        }}
        .folder-items {{
            margin-left: 20px;
            display: none;
        }}
        .folder-items.expanded {{
            display: block;
        }}
        .collection-item {{
            display: flex;
            align-items: center;
            padding: 8px 12px;
            border-radius: 6px;
            cursor: pointer;
            gap: 8px;
            margin: 2px 0;
            transition: background 0.15s;
        }}
        .collection-item:hover {{
            background: var(--bg-hover);
        }}
        .collection-item.active {{
            background: var(--accent);
            color: white;
        }}
        .collection-item .method-badge {{
            font-size: 10px;
            font-weight: 700;
            padding: 2px 6px;
            border-radius: 4px;
            text-transform: uppercase;
        }}
        .method-get {{ background: var(--accent-green); color: #000; }}
        .method-post {{ background: var(--accent-orange); color: #000; }}
        .method-run {{ background: var(--accent-purple); color: #fff; }}
        .method-check {{ background: var(--accent); color: #000; }}
        .collection-item .item-name {{
            font-size: 13px;
            flex: 1;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}

        /* Main Panel */
        .main-panel {{
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }}
        .main-header {{
            padding: 16px 24px;
            border-bottom: 1px solid var(--border);
            background: var(--bg-secondary);
        }}
        .main-header h1 {{
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 4px;
        }}
        .main-header .subtitle {{
            font-size: 13px;
            color: var(--text-secondary);
        }}

        /* Tabs */
        .tabs {{
            display: flex;
            border-bottom: 1px solid var(--border);
            background: var(--bg-secondary);
            padding: 0 24px;
        }}
        .tab {{
            padding: 12px 16px;
            font-size: 13px;
            color: var(--text-secondary);
            cursor: pointer;
            border-bottom: 2px solid transparent;
            transition: all 0.15s;
        }}
        .tab:hover {{
            color: var(--text-primary);
        }}
        .tab.active {{
            color: var(--accent);
            border-bottom-color: var(--accent);
        }}

        /* Main Content */
        .main-content {{
            flex: 1;
            overflow-y: auto;
            padding: 24px;
        }}

        /* Adjusters Section */
        .adjusters-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 24px;
        }}
        .adjuster-card {{
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
        }}
        .adjuster-card h4 {{
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--text-secondary);
            margin-bottom: 16px;
        }}

        /* Rotary Knob */
        .knob-wrapper {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 12px;
        }}
        .rotary-knob {{
            position: relative;
            width: 100px;
            height: 100px;
            border-radius: 50%;
            background: conic-gradient(
                from 225deg,
                var(--bg-tertiary) 0deg,
                var(--accent) calc(var(--value, 50) * 2.7deg),
                var(--bg-tertiary) calc(var(--value, 50) * 2.7deg),
                var(--bg-tertiary) 270deg
            );
            cursor: grab;
            box-shadow: 0 4px 20px var(--shadow),
                        inset 0 1px 0 rgba(255,255,255,0.1);
            user-select: none;
        }}
        .rotary-knob::before {{
            content: '';
            position: absolute;
            top: 10px;
            left: 10px;
            right: 10px;
            bottom: 10px;
            background: linear-gradient(135deg, var(--bg-tertiary), var(--bg-secondary));
            border-radius: 50%;
            box-shadow: inset 0 2px 10px rgba(0,0,0,0.5);
        }}
        .rotary-knob::after {{
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 4px;
            height: 25px;
            background: var(--accent);
            border-radius: 2px;
            transform-origin: bottom center;
            transform: translate(-50%, -100%) rotate(calc((var(--value, 50) * 2.7deg) - 135deg));
            box-shadow: 0 0 10px var(--accent);
        }}
        .rotary-knob:active {{
            cursor: grabbing;
        }}
        .knob-value {{
            font-size: 24px;
            font-weight: 700;
            font-family: 'SF Mono', 'Consolas', monospace;
            color: var(--accent);
        }}
        .knob-label {{
            font-size: 11px;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .knob-range {{
            font-size: 10px;
            color: var(--text-secondary);
        }}

        /* Slider Adjuster */
        .slider-adjuster {{
            width: 100%;
        }}
        .slider-header {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 12px;
        }}
        .slider-label {{
            font-size: 13px;
            color: var(--text-primary);
        }}
        .slider-value {{
            font-family: 'SF Mono', 'Consolas', monospace;
            font-size: 13px;
            color: var(--accent);
            font-weight: 600;
        }}
        .slider-track {{
            position: relative;
            height: 8px;
            background: var(--bg-tertiary);
            border-radius: 4px;
            cursor: pointer;
        }}
        .slider-fill {{
            position: absolute;
            height: 100%;
            background: linear-gradient(90deg, var(--accent), var(--accent-purple));
            border-radius: 4px;
            transition: width 0.1s;
        }}
        .slider-thumb {{
            position: absolute;
            top: 50%;
            width: 20px;
            height: 20px;
            background: var(--text-primary);
            border-radius: 50%;
            transform: translate(-50%, -50%);
            cursor: grab;
            box-shadow: 0 2px 8px var(--shadow);
            transition: transform 0.1s;
        }}
        .slider-thumb:hover {{
            transform: translate(-50%, -50%) scale(1.1);
        }}
        .slider-thumb:active {{
            cursor: grabbing;
            transform: translate(-50%, -50%) scale(1.2);
        }}
        .slider-marks {{
            display: flex;
            justify-content: space-between;
            margin-top: 8px;
            font-size: 10px;
            color: var(--text-secondary);
        }}

        /* Toggle Switch */
        .toggle-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px solid var(--border);
        }}
        .toggle-row:last-child {{
            border-bottom: none;
        }}
        .toggle-info {{
            flex: 1;
        }}
        .toggle-title {{
            font-size: 13px;
            font-weight: 500;
            margin-bottom: 2px;
        }}
        .toggle-desc {{
            font-size: 11px;
            color: var(--text-secondary);
        }}
        .toggle-switch {{
            position: relative;
            width: 44px;
            height: 24px;
            background: var(--bg-tertiary);
            border-radius: 12px;
            cursor: pointer;
            transition: background 0.2s;
        }}
        .toggle-switch.active {{
            background: var(--accent-green);
        }}
        .toggle-switch::after {{
            content: '';
            position: absolute;
            top: 3px;
            left: 3px;
            width: 18px;
            height: 18px;
            background: var(--text-primary);
            border-radius: 50%;
            transition: transform 0.2s;
        }}
        .toggle-switch.active::after {{
            transform: translateX(20px);
        }}

        /* Stepper Input */
        .stepper {{
            display: flex;
            align-items: center;
            background: var(--bg-tertiary);
            border-radius: 8px;
            overflow: hidden;
        }}
        .stepper-btn {{
            width: 36px;
            height: 36px;
            border: none;
            background: transparent;
            color: var(--text-primary);
            font-size: 18px;
            cursor: pointer;
            transition: background 0.15s;
        }}
        .stepper-btn:hover {{
            background: var(--bg-hover);
        }}
        .stepper-btn:active {{
            background: var(--accent);
        }}
        .stepper-input {{
            width: 60px;
            height: 36px;
            border: none;
            background: var(--bg-primary);
            color: var(--text-primary);
            text-align: center;
            font-family: 'SF Mono', 'Consolas', monospace;
            font-size: 14px;
            font-weight: 600;
        }}
        .stepper-input:focus {{
            outline: none;
        }}

        /* Checkbox Group */
        .checkbox-group {{
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}
        .checkbox-item {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 10px 14px;
            background: var(--bg-tertiary);
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.15s;
            border: 2px solid transparent;
        }}
        .checkbox-item:hover {{
            background: var(--bg-hover);
            border-color: var(--border);
        }}
        .checkbox-item.checked {{
            background: rgba(88, 166, 255, 0.1);
            border-color: var(--accent);
        }}
        .checkbox-box {{
            width: 20px;
            height: 20px;
            border: 2px solid var(--text-secondary);
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.15s;
            flex-shrink: 0;
        }}
        .checkbox-item.checked .checkbox-box {{
            background: var(--accent);
            border-color: var(--accent);
        }}
        .checkbox-box::after {{
            content: '✓';
            color: var(--bg-primary);
            font-size: 12px;
            font-weight: bold;
            opacity: 0;
            transition: opacity 0.15s;
        }}
        .checkbox-item.checked .checkbox-box::after {{
            opacity: 1;
        }}
        .checkbox-label {{
            flex: 1;
        }}
        .checkbox-title {{
            font-size: 13px;
            font-weight: 500;
            margin-bottom: 2px;
        }}
        .checkbox-desc {{
            font-size: 11px;
            color: var(--text-secondary);
        }}

        /* Radio Group */
        .radio-group {{
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        .radio-group.horizontal {{
            flex-direction: row;
            flex-wrap: wrap;
        }}
        .radio-item {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 14px;
            background: var(--bg-tertiary);
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.15s;
            border: 2px solid transparent;
        }}
        .radio-item:hover {{
            background: var(--bg-hover);
        }}
        .radio-item.selected {{
            background: rgba(63, 185, 80, 0.1);
            border-color: var(--accent-green);
        }}
        .radio-circle {{
            width: 20px;
            height: 20px;
            border: 2px solid var(--text-secondary);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.15s;
            flex-shrink: 0;
        }}
        .radio-item.selected .radio-circle {{
            border-color: var(--accent-green);
        }}
        .radio-circle::after {{
            content: '';
            width: 10px;
            height: 10px;
            background: var(--accent-green);
            border-radius: 50%;
            opacity: 0;
            transition: opacity 0.15s;
        }}
        .radio-item.selected .radio-circle::after {{
            opacity: 1;
        }}
        .radio-label {{
            font-size: 13px;
        }}

        /* Dropdown Select */
        .dropdown-container {{
            position: relative;
        }}
        .dropdown-trigger {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 12px 16px;
            background: var(--bg-tertiary);
            border: 2px solid var(--border);
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.15s;
        }}
        .dropdown-trigger:hover {{
            border-color: var(--text-secondary);
        }}
        .dropdown-trigger.open {{
            border-color: var(--accent);
            border-bottom-left-radius: 0;
            border-bottom-right-radius: 0;
        }}
        .dropdown-selected {{
            font-size: 13px;
            color: var(--text-primary);
        }}
        .dropdown-arrow {{
            font-size: 10px;
            color: var(--text-secondary);
            transition: transform 0.2s;
        }}
        .dropdown-trigger.open .dropdown-arrow {{
            transform: rotate(180deg);
        }}
        .dropdown-menu {{
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: var(--bg-tertiary);
            border: 2px solid var(--accent);
            border-top: none;
            border-bottom-left-radius: 8px;
            border-bottom-right-radius: 8px;
            max-height: 200px;
            overflow-y: auto;
            z-index: 100;
            display: none;
        }}
        .dropdown-menu.open {{
            display: block;
        }}
        .dropdown-option {{
            padding: 10px 16px;
            font-size: 13px;
            cursor: pointer;
            transition: background 0.15s;
        }}
        .dropdown-option:hover {{
            background: var(--bg-hover);
        }}
        .dropdown-option.selected {{
            background: rgba(88, 166, 255, 0.2);
            color: var(--accent);
        }}
        .dropdown-option .option-desc {{
            font-size: 11px;
            color: var(--text-secondary);
            margin-top: 2px;
        }}

        /* Multi-Select Tags */
        .multiselect-container {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            padding: 12px;
            background: var(--bg-tertiary);
            border: 2px solid var(--border);
            border-radius: 8px;
            min-height: 48px;
        }}
        .multiselect-tag {{
            display: flex;
            align-items: center;
            gap: 6px;
            padding: 4px 10px;
            background: var(--accent);
            color: var(--bg-primary);
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
        }}
        .multiselect-tag .remove-tag {{
            cursor: pointer;
            opacity: 0.7;
        }}
        .multiselect-tag .remove-tag:hover {{
            opacity: 1;
        }}
        .multiselect-options {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 12px;
        }}
        .multiselect-option {{
            padding: 6px 12px;
            background: var(--bg-tertiary);
            border: 1px solid var(--border);
            border-radius: 6px;
            font-size: 12px;
            cursor: pointer;
            transition: all 0.15s;
        }}
        .multiselect-option:hover {{
            border-color: var(--accent);
        }}
        .multiselect-option.selected {{
            background: var(--accent);
            color: var(--bg-primary);
            border-color: var(--accent);
        }}

        /* Button Group */
        .button-group {{
            display: flex;
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid var(--border);
        }}
        .button-group-item {{
            flex: 1;
            padding: 10px 16px;
            background: var(--bg-tertiary);
            border: none;
            color: var(--text-secondary);
            font-size: 12px;
            cursor: pointer;
            transition: all 0.15s;
            border-right: 1px solid var(--border);
        }}
        .button-group-item:last-child {{
            border-right: none;
        }}
        .button-group-item:hover {{
            background: var(--bg-hover);
            color: var(--text-primary);
        }}
        .button-group-item.active {{
            background: var(--accent);
            color: var(--bg-primary);
            font-weight: 600;
        }}

        /* Number Input with +/- */
        .number-input-container {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .number-input-wrapper {{
            display: flex;
            align-items: center;
            background: var(--bg-tertiary);
            border-radius: 8px;
            overflow: hidden;
        }}
        .number-btn {{
            width: 40px;
            height: 40px;
            border: none;
            background: transparent;
            color: var(--text-primary);
            font-size: 20px;
            cursor: pointer;
            transition: background 0.15s;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .number-btn:hover {{
            background: var(--accent);
        }}
        .number-display {{
            width: 80px;
            height: 40px;
            background: var(--bg-primary);
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'SF Mono', 'Consolas', monospace;
            font-size: 16px;
            font-weight: 600;
        }}

        /* Command Preview */
        .command-section {{
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 12px;
            overflow: hidden;
        }}
        .command-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 12px 16px;
            background: var(--bg-tertiary);
            border-bottom: 1px solid var(--border);
        }}
        .command-header h3 {{
            font-size: 13px;
            font-weight: 600;
        }}
        .command-actions {{
            display: flex;
            gap: 8px;
        }}
        .command-actions .btn {{
            padding: 6px 12px;
            font-size: 12px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.15s;
        }}
        .btn-copy {{
            background: var(--bg-hover);
            color: var(--text-primary);
        }}
        .btn-copy:hover {{
            background: var(--accent);
        }}
        .btn-run {{
            background: var(--accent-green);
            color: #000;
            font-weight: 600;
        }}
        .btn-run:hover {{
            filter: brightness(1.1);
        }}
        .command-body {{
            padding: 16px;
            font-family: 'SF Mono', 'Consolas', monospace;
            font-size: 13px;
            line-height: 1.6;
            overflow-x: auto;
        }}
        .cmd-prompt {{
            color: var(--accent-green);
            user-select: none;
        }}
        .cmd-python {{
            color: var(--accent-purple);
        }}
        .cmd-module {{
            color: var(--text-primary);
        }}
        .cmd-command {{
            color: var(--accent-orange);
        }}
        .cmd-flag {{
            color: var(--accent);
        }}
        .cmd-value {{
            color: var(--accent-green);
        }}

        /* Right Panel - Details/History */
        .right-panel {{
            background: var(--bg-secondary);
            border-left: 1px solid var(--border);
            display: flex;
            flex-direction: column;
        }}
        .right-panel .panel-header {{
            flex-shrink: 0;
        }}
        .details-content {{
            flex: 1;
            overflow-y: auto;
            padding: 16px;
        }}
        .detail-section {{
            margin-bottom: 20px;
        }}
        .detail-section h4 {{
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--text-secondary);
            margin-bottom: 12px;
        }}
        .detail-item {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid var(--border);
            font-size: 12px;
        }}
        .detail-item:last-child {{
            border-bottom: none;
        }}
        .detail-label {{
            color: var(--text-secondary);
        }}
        .detail-value {{
            color: var(--text-primary);
            font-family: 'SF Mono', 'Consolas', monospace;
        }}

        /* History List */
        .history-item {{
            padding: 12px;
            background: var(--bg-tertiary);
            border-radius: 8px;
            margin-bottom: 8px;
            cursor: pointer;
            transition: all 0.15s;
        }}
        .history-item:hover {{
            background: var(--bg-hover);
        }}
        .history-item .time {{
            font-size: 10px;
            color: var(--text-secondary);
            margin-bottom: 4px;
        }}
        .history-item .command {{
            font-size: 11px;
            font-family: 'SF Mono', 'Consolas', monospace;
            color: var(--text-primary);
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}

        /* Save Collection Modal */
        .modal-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.7);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 1000;
        }}
        .modal-overlay.visible {{
            display: flex;
        }}
        .modal {{
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 12px;
            width: 400px;
            max-width: 90vw;
            box-shadow: 0 20px 50px var(--shadow);
        }}
        .modal-header {{
            padding: 16px 20px;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .modal-header h3 {{
            font-size: 16px;
            font-weight: 600;
        }}
        .modal-close {{
            background: none;
            border: none;
            color: var(--text-secondary);
            font-size: 20px;
            cursor: pointer;
        }}
        .modal-close:hover {{
            color: var(--text-primary);
        }}
        .modal-body {{
            padding: 20px;
        }}
        .modal-footer {{
            padding: 16px 20px;
            border-top: 1px solid var(--border);
            display: flex;
            justify-content: flex-end;
            gap: 12px;
        }}
        .form-group {{
            margin-bottom: 16px;
        }}
        .form-label {{
            display: block;
            font-size: 12px;
            color: var(--text-secondary);
            margin-bottom: 6px;
        }}
        .form-input {{
            width: 100%;
            padding: 10px 12px;
            background: var(--bg-tertiary);
            border: 1px solid var(--border);
            border-radius: 6px;
            color: var(--text-primary);
            font-size: 13px;
        }}
        .form-input:focus {{
            outline: none;
            border-color: var(--accent);
        }}
        .form-select {{
            width: 100%;
            padding: 10px 12px;
            background: var(--bg-tertiary);
            border: 1px solid var(--border);
            border-radius: 6px;
            color: var(--text-primary);
            font-size: 13px;
            cursor: pointer;
        }}
        .btn-primary {{
            padding: 10px 20px;
            background: var(--accent);
            color: #000;
            border: none;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
        }}
        .btn-primary:hover {{
            filter: brightness(1.1);
        }}
        .btn-secondary {{
            padding: 10px 20px;
            background: var(--bg-tertiary);
            color: var(--text-primary);
            border: none;
            border-radius: 6px;
            font-size: 13px;
            cursor: pointer;
        }}
        .btn-secondary:hover {{
            background: var(--bg-hover);
        }}
    </style>
</head>
<body>
    <div class="app-container">
        <!-- Left Panel - Collection List -->
        <div class="left-panel">
            <div class="panel-header">
                <h2>Collections</h2>
                <button class="btn-icon" onclick="showSaveModal()" title="New Collection">+</button>
            </div>
            <div class="collection-tree">
                <!-- Audit Commands -->
                <div class="collection-folder">
                    <div class="folder-header" onclick="toggleFolder(this)">
                        <span class="folder-icon">📁</span>
                        <span class="folder-name">Audit Commands</span>
                        <span class="folder-count">6</span>
                    </div>
                    <div class="folder-items expanded">
                        <div class="collection-item active" onclick="selectItem(this, 'run')" data-cmd="run">
                            <span class="method-badge method-run">RUN</span>
                            <span class="item-name">Full Pipeline</span>
                        </div>
                        <div class="collection-item" onclick="selectItem(this, 'validate')" data-cmd="validate">
                            <span class="method-badge method-check">CHK</span>
                            <span class="item-name">Validate Gates</span>
                        </div>
                        <div class="collection-item" onclick="selectItem(this, 'stage')" data-cmd="stage">
                            <span class="method-badge method-run">RUN</span>
                            <span class="item-name">Single Stage</span>
                        </div>
                        <div class="collection-item" onclick="selectItem(this, 'explain')" data-cmd="explain">
                            <span class="method-badge method-get">GET</span>
                            <span class="item-name">Explain Score</span>
                        </div>
                        <div class="collection-item" onclick="selectItem(this, 'diff')" data-cmd="diff">
                            <span class="method-badge method-get">GET</span>
                            <span class="item-name">Diff Reports</span>
                        </div>
                        <div class="collection-item" onclick="selectItem(this, 'dashboard')" data-cmd="dashboard">
                            <span class="method-badge method-post">GEN</span>
                            <span class="item-name">Dashboard</span>
                        </div>
                    </div>
                </div>

                <!-- Trend Commands -->
                <div class="collection-folder">
                    <div class="folder-header" onclick="toggleFolder(this)">
                        <span class="folder-icon">📁</span>
                        <span class="folder-name">Trend Analysis</span>
                        <span class="folder-count">4</span>
                    </div>
                    <div class="folder-items">
                        <div class="collection-item" onclick="selectItem(this, 'store-trend')" data-cmd="store-trend">
                            <span class="method-badge method-post">POST</span>
                            <span class="item-name">Store Trend</span>
                        </div>
                        <div class="collection-item" onclick="selectItem(this, 'show-trend')" data-cmd="show-trend">
                            <span class="method-badge method-get">GET</span>
                            <span class="item-name">Show Trend</span>
                        </div>
                        <div class="collection-item" onclick="selectItem(this, 'check-regressions')" data-cmd="check-regressions">
                            <span class="method-badge method-check">CHK</span>
                            <span class="item-name">Check Regressions</span>
                        </div>
                        <div class="collection-item" onclick="selectItem(this, 'compare-runs')" data-cmd="compare-runs">
                            <span class="method-badge method-get">GET</span>
                            <span class="item-name">Compare Runs</span>
                        </div>
                    </div>
                </div>

                <!-- Saved Presets -->
                <div class="collection-folder">
                    <div class="folder-header" onclick="toggleFolder(this)">
                        <span class="folder-icon">⭐</span>
                        <span class="folder-name">Saved Presets</span>
                        <span class="folder-count" id="preset-count">0</span>
                    </div>
                    <div class="folder-items" id="saved-presets">
                        <!-- Dynamically populated -->
                    </div>
                </div>
            </div>
        </div>

        <!-- Main Panel -->
        <div class="main-panel">
            <div class="main-header">
                <h1 id="command-title">Full Pipeline Execution</h1>
                <div class="subtitle" id="command-subtitle">Run complete audit S1→S7</div>
            </div>

            <div class="tabs">
                <div class="tab active" onclick="switchTab('adjusters')">Adjusters</div>
                <div class="tab" onclick="switchTab('raw')">Raw Command</div>
                <div class="tab" onclick="switchTab('docs')">Documentation</div>
            </div>

            <div class="main-content">
                <!-- Adjusters Tab -->
                <div id="tab-adjusters" class="tab-content">
                    <div class="adjusters-grid" id="adjusters-container">
                        <!-- Dynamically populated based on command -->
                    </div>

                    <!-- Command Preview -->
                    <div class="command-section">
                        <div class="command-header">
                            <h3>Generated Command</h3>
                            <div class="command-actions">
                                <button class="btn btn-copy" onclick="copyCommand()">📋 Copy</button>
                                <button class="btn btn-run" onclick="showRunInstructions()">▶ Run</button>
                            </div>
                        </div>
                        <div class="command-body">
                            <span class="cmd-prompt">$ </span>
                            <span id="command-output">python -m scripts.space_traversal.audit_runner run</span>
                        </div>
                    </div>
                </div>

                <!-- Raw Command Tab -->
                <div id="tab-raw" class="tab-content" style="display:none;">
                    <div class="command-section">
                        <div class="command-header">
                            <h3>Edit Raw Command</h3>
                        </div>
                        <div class="command-body">
                            <textarea id="raw-command" style="width:100%;height:200px;background:transparent;border:none;color:var(--text-primary);font-family:'SF Mono',monospace;font-size:13px;resize:vertical;" oninput="parseRawCommand()">python -m scripts.space_traversal.audit_runner run</textarea>
                        </div>
                    </div>
                </div>

                <!-- Documentation Tab -->
                <div id="tab-docs" class="tab-content" style="display:none;">
                    <div id="docs-content" style="padding:20px;background:var(--bg-secondary);border-radius:12px;border:1px solid var(--border);">
                        <!-- Dynamically populated -->
                    </div>
                </div>
            </div>
        </div>

        <!-- Right Panel - Details/History -->
        <div class="right-panel">
            <div class="panel-header">
                <h2>Details</h2>
            </div>
            <div class="details-content">
                <div class="detail-section">
                    <h4>Current Parameters</h4>
                    <div id="param-details">
                        <!-- Dynamically populated -->
                    </div>
                </div>

                <div class="detail-section">
                    <h4>Recent History</h4>
                    <div id="history-list">
                        <!-- Dynamically populated -->
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Save Modal -->
    <div class="modal-overlay" id="save-modal">
        <div class="modal">
            <div class="modal-header">
                <h3>Save to Collection</h3>
                <button class="modal-close" onclick="hideSaveModal()">&times;</button>
            </div>
            <div class="modal-body">
                <div class="form-group">
                    <label class="form-label">Preset Name</label>
                    <input type="text" class="form-input" id="preset-name" placeholder="My Custom Audit">
                </div>
                <div class="form-group">
                    <label class="form-label">Folder</label>
                    <select class="form-select" id="preset-folder">
                        <option value="saved">Saved Presets</option>
                    </select>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn-secondary" onclick="hideSaveModal()">Cancel</button>
                <button class="btn-primary" onclick="savePreset()">Save</button>
            </div>
        </div>
    </div>

    <script>
        // State
        let currentCommand = 'run';
        let params = {{}};
        let history = [];
        let savedPresets = [];

        // Command definitions
        const commands = {{
            'run': {{
                title: 'Full Pipeline Execution',
                subtitle: 'Run complete audit S1→S7',
                docs: 'Executes all 7 stages of the audit pipeline: Index → Facets → Capabilities → Scoring → Gaps → Render → Manifest. This is the standard way to run a complete self-audit.',
                adjusters: [
                    {{ type: 'toggle', id: 'verbose', label: 'Verbose Output', desc: 'Show detailed progress information', flag: '--verbose' }},
                    {{ type: 'toggle', id: 'strict', label: 'Strict Mode', desc: 'Fail on any validation error', flag: '--strict' }},
                    {{ type: 'checkbox-group', id: 'skip_stages', label: 'Skip Stages', options: [
                        {{value: 'S5', label: 'Gaps', desc: 'Skip gap analysis'}},
                        {{value: 'S6', label: 'Render', desc: 'Skip report generation'}},
                        {{value: 'S7', label: 'Manifest', desc: 'Skip manifest creation'}}
                    ], flag: '--skip' }}
                ]
            }},
            'validate': {{
                title: 'Validate Quality Gates',
                subtitle: 'Check policy thresholds',
                docs: 'Validates that all capabilities meet quality gates. Checks for low maturity scores and missing detectors based on workflow.yaml configuration.',
                adjusters: [
                    {{ type: 'toggle', id: 'fail_on_warn', label: 'Fail on Warnings', desc: 'Exit with error code on warnings', flag: '--fail-on-warn' }},
                    {{ type: 'radio', id: 'severity', label: 'Minimum Severity', options: [
                        {{value: 'error', label: 'Errors only'}},
                        {{value: 'warning', label: 'Warnings+'}},
                        {{value: 'info', label: 'All issues'}}
                    ], default: 'warning', flag: '--severity' }}
                ]
            }},
            'stage': {{
                title: 'Single Stage Execution',
                subtitle: 'Run one pipeline stage',
                docs: 'Run a specific stage of the pipeline. Useful for debugging or re-running individual stages.',
                adjusters: [
                    {{ type: 'dropdown', id: 'stage_id', label: 'Stage', options: [
                        {{value: 'S1', label: 'S1 - Index', desc: 'Scan repository structure'}},
                        {{value: 'S2', label: 'S2 - Facets', desc: 'Extract feature facets'}},
                        {{value: 'S3', label: 'S3 - Capabilities', desc: 'Detect capabilities'}},
                        {{value: 'S4', label: 'S4 - Scoring', desc: 'Calculate scores'}},
                        {{value: 'S5', label: 'S5 - Gaps', desc: 'Identify gaps'}},
                        {{value: 'S6', label: 'S6 - Render', desc: 'Generate reports'}},
                        {{value: 'S7', label: 'S7 - Manifest', desc: 'Create manifest'}},
                        {{value: 'TRENDS', label: 'TRENDS', desc: 'Trend aggregation'}}
                    ], default: 'S1' }}
                ]
            }},
            'explain': {{
                title: 'Explain Capability Score',
                subtitle: 'Detailed score breakdown',
                docs: 'Shows detailed breakdown of how a capability score was calculated, including component scores and evidence.',
                adjusters: [
                    {{ type: 'text', id: 'capability', label: 'Capability ID', placeholder: 'e.g., checkpointing', required: true }},
                    {{ type: 'radio', id: 'format', label: 'Output Format', options: [
                        {{value: 'text', label: 'Text'}},
                        {{value: 'json', label: 'JSON'}},
                        {{value: 'markdown', label: 'Markdown'}}
                    ], default: 'text', flag: '--format', horizontal: true }}
                ]
            }},
            'diff': {{
                title: 'Diff Reports',
                subtitle: 'Compare two audit reports',
                docs: 'Compare two audit report files and show differences in capability scores.',
                adjusters: [
                    {{ type: 'text', id: 'old', label: 'Old File', placeholder: 'path/to/old.json', required: true, flag: '--old' }},
                    {{ type: 'text', id: 'new', label: 'New File', placeholder: 'path/to/new.json', required: true, flag: '--new' }},
                    {{ type: 'toggle', id: 'color', label: 'Color Output', desc: 'Use colored diff output', flag: '--color', default: true }}
                ]
            }},
            'dashboard': {{
                title: 'Generate Dashboard',
                subtitle: 'Create HTML dashboard',
                docs: 'Generates an interactive HTML dashboard with charts and visualizations of audit results.',
                adjusters: [
                    {{ type: 'text', id: 'output', label: 'Output Path', placeholder: 'audit_artifacts/dashboard.html', flag: '--output' }},
                    {{ type: 'checkbox-group', id: 'sections', label: 'Include Sections', options: [
                        {{value: 'summary', label: 'Summary', desc: 'Executive summary'}},
                        {{value: 'trends', label: 'Trends', desc: 'Trend charts'}},
                        {{value: 'details', label: 'Details', desc: 'Capability details'}},
                        {{value: 'gaps', label: 'Gaps', desc: 'Gap analysis'}}
                    ], default: ['summary', 'trends', 'details'], flag: '--sections' }},
                    {{ type: 'button-group', id: 'theme', label: 'Theme', options: [
                        {{value: 'dark', label: 'Dark'}},
                        {{value: 'light', label: 'Light'}},
                        {{value: 'auto', label: 'Auto'}}
                    ], default: 'dark', flag: '--theme' }}
                ]
            }},
            'store-trend': {{
                title: 'Store Trend Data',
                subtitle: 'Save audit to trend database',
                docs: 'Stores the current audit results in the SQLite trend database for historical tracking and analysis.',
                adjusters: [
                    {{ type: 'text', id: 'tag', label: 'Tag', placeholder: 'e.g., release-v1.0', flag: '--tag' }},
                    {{ type: 'toggle', id: 'force', label: 'Force Overwrite', desc: 'Overwrite existing entry with same ID', flag: '--force' }}
                ]
            }},
            'show-trend': {{
                title: 'Show Capability Trend',
                subtitle: 'View historical trend',
                docs: 'Shows the historical trend of scores for a specific capability over time.',
                adjusters: [
                    {{ type: 'text', id: 'capability', label: 'Capability ID', placeholder: 'e.g., checkpointing', required: true }},
                    {{ type: 'number', id: 'limit', label: 'Number of Entries', min: 5, max: 100, default: 30, step: 5, flag: '--limit' }},
                    {{ type: 'text', id: 'branch', label: 'Branch Filter', placeholder: 'e.g., main', flag: '--branch' }},
                    {{ type: 'radio', id: 'output', label: 'Output Format', options: [
                        {{value: 'table', label: 'Table'}},
                        {{value: 'sparkline', label: 'Sparkline'}},
                        {{value: 'json', label: 'JSON'}}
                    ], default: 'table', flag: '--output', horizontal: true }}
                ]
            }},
            'check-regressions': {{
                title: 'Check Regressions',
                subtitle: 'Detect score regressions',
                docs: 'Analyzes recent audit history to detect capabilities with declining scores that may indicate regressions.',
                adjusters: [
                    {{ type: 'slider', id: 'threshold', label: 'Regression Threshold', min: 0.01, max: 0.10, step: 0.01, default: 0.02, flag: '--threshold', format: 'percent' }},
                    {{ type: 'number', id: 'lookback', label: 'Lookback Runs', min: 2, max: 20, default: 5, step: 1, flag: '--lookback' }},
                    {{ type: 'radio', id: 'severity_filter', label: 'Severity Filter', options: [
                        {{value: 'all', label: 'All'}},
                        {{value: 'high', label: 'High Only'}},
                        {{value: 'medium+', label: 'Medium+'}}
                    ], default: 'all', flag: '--severity' }},
                    {{ type: 'toggle', id: 'exit_code', label: 'Exit on Regression', desc: 'Return non-zero exit code if regressions found', flag: '--exit-on-regression', default: true }}
                ]
            }},
            'compare-runs': {{
                title: 'Compare Audit Runs',
                subtitle: 'Detailed comparison',
                docs: 'Compare two audit runs with detailed component-level analysis and regression detection.',
                adjusters: [
                    {{ type: 'text', id: 'old', label: 'Old File', placeholder: 'path/to/old.json', required: true, flag: '--old' }},
                    {{ type: 'text', id: 'new', label: 'New File', placeholder: 'path/to/new.json', required: true, flag: '--new' }},
                    {{ type: 'text', id: 'output', label: 'Report Output', placeholder: 'comparison.md', flag: '--output' }},
                    {{ type: 'knob', id: 'threshold', label: 'Threshold', min: 0.01, max: 0.10, step: 0.01, default: 0.02, flag: '--threshold', format: 'percent' }},
                    {{ type: 'checkbox-group', id: 'include', label: 'Include in Report', options: [
                        {{value: 'regressions', label: 'Regressions', desc: 'Show declining scores'}},
                        {{value: 'improvements', label: 'Improvements', desc: 'Show improving scores'}},
                        {{value: 'unchanged', label: 'Unchanged', desc: 'Show stable scores'}}
                    ], default: ['regressions', 'improvements'], flag: '--include' }}
                ]
            }}
        }};

        // Initialize
        document.addEventListener('DOMContentLoaded', () => {{
            loadSavedPresets();
            renderAdjusters();
            updateCommand();
        }});

        function toggleFolder(header) {{
            const items = header.nextElementSibling;
            items.classList.toggle('expanded');
            const icon = header.querySelector('.folder-icon');
            icon.textContent = items.classList.contains('expanded') ? '📂' : '📁';
        }}

        function selectItem(el, cmd) {{
            document.querySelectorAll('.collection-item').forEach(i => i.classList.remove('active'));
            el.classList.add('active');
            currentCommand = cmd;
            params = {{}};

            const cmdDef = commands[cmd];
            document.getElementById('command-title').textContent = cmdDef.title;
            document.getElementById('command-subtitle').textContent = cmdDef.subtitle;

            renderAdjusters();
            updateCommand();
            renderDocs();
        }}

        function switchTab(tab) {{
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.style.display = 'none');

            event.target.classList.add('active');
            document.getElementById('tab-' + tab).style.display = 'block';

            if (tab === 'raw') {{
                document.getElementById('raw-command').value = buildCommandString();
            }}
        }}

        function renderAdjusters() {{
            const container = document.getElementById('adjusters-container');
            const cmdDef = commands[currentCommand];

            if (!cmdDef.adjusters || cmdDef.adjusters.length === 0) {{
                container.innerHTML = '<div class="adjuster-card"><p style="color:var(--text-secondary);text-align:center;">No adjustable parameters for this command.</p></div>';
                return;
            }}

            let html = '';
            cmdDef.adjusters.forEach(adj => {{
                html += '<div class="adjuster-card">';
                html += '<h4>' + adj.label + (adj.required ? ' <span style="color:var(--accent-red)">*</span>' : '') + '</h4>';

                if (adj.type === 'knob') {{
                    const value = params[adj.id] || adj.default;
                    const percent = ((value - adj.min) / (adj.max - adj.min)) * 100;
                    html += '<div class="knob-wrapper">';
                    html += '<div class="rotary-knob" style="--value:' + percent + '" data-id="' + adj.id + '" data-min="' + adj.min + '" data-max="' + adj.max + '" data-step="' + (adj.step || 1) + '" data-format="' + (adj.format || '') + '"></div>';
                    html += '<div class="knob-value" id="knob-value-' + adj.id + '">' + formatValue(value, adj.format) + '</div>';
                    html += '<div class="knob-label">' + adj.label + '</div>';
                    html += '<div class="knob-range">' + adj.min + ' — ' + adj.max + '</div>';
                    html += '</div>';
                }} else if (adj.type === 'slider') {{
                    const value = params[adj.id] || adj.default;
                    const percent = ((value - adj.min) / (adj.max - adj.min)) * 100;
                    html += '<div class="slider-adjuster">';
                    html += '<div class="slider-header"><span class="slider-label">' + adj.label + '</span><span class="slider-value" id="slider-value-' + adj.id + '">' + formatValue(value, adj.format) + '</span></div>';
                    html += '<div class="slider-track" data-id="' + adj.id + '" data-min="' + adj.min + '" data-max="' + adj.max + '" data-step="' + (adj.step || 1) + '" data-format="' + (adj.format || '') + '">';
                    html += '<div class="slider-fill" style="width:' + percent + '%"></div>';
                    html += '<div class="slider-thumb" style="left:' + percent + '%"></div>';
                    html += '</div>';
                    html += '<div class="slider-marks"><span>' + adj.min + '</span><span>' + adj.max + '</span></div>';
                    html += '</div>';
                }} else if (adj.type === 'text') {{
                    html += '<input type="text" class="form-input" id="input-' + adj.id + '" placeholder="' + (adj.placeholder || '') + '" oninput="updateParam(\'' + adj.id + '\', this.value)">';
                }} else if (adj.type === 'select') {{
                    html += '<select class="form-select" id="input-' + adj.id + '" onchange="updateParam(\'' + adj.id + '\', this.value)">';
                    adj.options.forEach(opt => {{
                        html += '<option value="' + opt.value + '"' + (opt.value === adj.default ? ' selected' : '') + '>' + opt.label + '</option>';
                    }});
                    html += '</select>';
                    params[adj.id] = adj.default;
                }} else if (adj.type === 'toggle') {{
                    const active = params[adj.id] || false;
                    html += '<div class="toggle-row">';
                    html += '<div class="toggle-info"><div class="toggle-title">' + adj.label + '</div><div class="toggle-desc">' + (adj.desc || '') + '</div></div>';
                    html += '<div class="toggle-switch' + (active ? ' active' : '') + '" data-id="' + adj.id + '" onclick="toggleSwitch(this)"></div>';
                    html += '</div>';
                }}

                html += '</div>';
            }});

            container.innerHTML = html;

            // Attach knob handlers
            document.querySelectorAll('.rotary-knob').forEach(knob => {{
                setupKnobDrag(knob);
            }});

            // Attach slider handlers
            document.querySelectorAll('.slider-track').forEach(slider => {{
                setupSliderDrag(slider);
            }});
        }}

        function formatValue(value, format) {{
            if (format === 'percent') {{
                return (value * 100).toFixed(0) + '%';
            }}
            return typeof value === 'number' && !Number.isInteger(value) ? value.toFixed(2) : value;
        }}

        function setupKnobDrag(knob) {{
            let dragging = false;
            let startY, startValue;

            const id = knob.dataset.id;
            const min = parseFloat(knob.dataset.min);
            const max = parseFloat(knob.dataset.max);
            const step = parseFloat(knob.dataset.step) || 1;
            const format = knob.dataset.format;

            knob.addEventListener('mousedown', (e) => {{
                dragging = true;
                startY = e.clientY;
                startValue = params[id] !== undefined ? params[id] : commands[currentCommand].adjusters.find(a => a.id === id).default;
                document.body.style.cursor = 'grabbing';
            }});

            document.addEventListener('mousemove', (e) => {{
                if (!dragging) return;

                const delta = (startY - e.clientY) / 100;
                let newValue = startValue + delta * (max - min);
                newValue = Math.round(newValue / step) * step;
                newValue = Math.max(min, Math.min(max, newValue));

                params[id] = newValue;
                const percent = ((newValue - min) / (max - min)) * 100;
                knob.style.setProperty('--value', percent);
                document.getElementById('knob-value-' + id).textContent = formatValue(newValue, format);
                updateCommand();
            }});

            document.addEventListener('mouseup', () => {{
                if (dragging) {{
                    dragging = false;
                    document.body.style.cursor = '';
                }}
            }});
        }}

        function setupSliderDrag(slider) {{
            let dragging = false;

            const id = slider.dataset.id;
            const min = parseFloat(slider.dataset.min);
            const max = parseFloat(slider.dataset.max);
            const step = parseFloat(slider.dataset.step) || 1;
            const format = slider.dataset.format;

            const updateSlider = (e) => {{
                const rect = slider.getBoundingClientRect();
                let percent = (e.clientX - rect.left) / rect.width;
                percent = Math.max(0, Math.min(1, percent));

                let value = min + percent * (max - min);
                value = Math.round(value / step) * step;

                params[id] = value;
                slider.querySelector('.slider-fill').style.width = (percent * 100) + '%';
                slider.querySelector('.slider-thumb').style.left = (percent * 100) + '%';
                document.getElementById('slider-value-' + id).textContent = formatValue(value, format);
                updateCommand();
            }};

            slider.addEventListener('mousedown', (e) => {{
                dragging = true;
                updateSlider(e);
            }});

            document.addEventListener('mousemove', (e) => {{
                if (dragging) updateSlider(e);
            }});

            document.addEventListener('mouseup', () => {{
                dragging = false;
            }});
        }}

        function toggleSwitch(el) {{
            const id = el.dataset.id;
            el.classList.toggle('active');
            params[id] = el.classList.contains('active');
            updateCommand();
        }}

        function updateParam(id, value) {{
            params[id] = value;
            updateCommand();
        }}

        function updateCommand() {{
            const cmdStr = buildCommandString();
            document.getElementById('command-output').innerHTML = highlightCommand(cmdStr);
            updateParamDetails();
        }}

        function buildCommandString() {{
            let cmd = 'python -m scripts.space_traversal.audit_runner ' + currentCommand;
            const cmdDef = commands[currentCommand];

            cmdDef.adjusters.forEach(adj => {{
                const value = params[adj.id];
                if (value === undefined || value === '' || value === adj.default) return;

                if (adj.flag) {{
                    cmd += ' ' + adj.flag + ' ' + value;
                }} else {{
                    cmd += ' ' + value;
                }}
            }});

            return cmd;
        }}

        function highlightCommand(cmd) {{
            return cmd
                .replace(/(python)/, '<span class="cmd-python">$1</span>')
                .replace(/(-m [\\w.]+)/, '<span class="cmd-module">$1</span>')
                .replace(/(\\s)(run|validate|stage|explain|diff|dashboard|store-trend|show-trend|check-regressions|compare-runs)(\\s|$)/, '$1<span class="cmd-command">$2</span>$3')
                .replace(/(--\\w+)/g, '<span class="cmd-flag">$1</span>')
                .replace(/(\\s)(S[1-7]|TRENDS)(\\s|$)/g, '$1<span class="cmd-value">$2</span>$3');
        }}

        function updateParamDetails() {{
            const container = document.getElementById('param-details');
            const cmdDef = commands[currentCommand];

            let html = '';
            cmdDef.adjusters.forEach(adj => {{
                const value = params[adj.id] !== undefined ? params[adj.id] : (adj.default || '—');
                html += '<div class="detail-item">';
                html += '<span class="detail-label">' + adj.label + '</span>';
                html += '<span class="detail-value">' + formatValue(value, adj.format) + '</span>';
                html += '</div>';
            }});

            if (!html) html = '<div class="detail-item"><span class="detail-label">No parameters</span></div>';
            container.innerHTML = html;
        }}

        function renderDocs() {{
            const cmdDef = commands[currentCommand];
            document.getElementById('docs-content').innerHTML = '<h3 style="margin-bottom:12px;">' + cmdDef.title + '</h3><p style="color:var(--text-secondary);line-height:1.8;">' + cmdDef.docs + '</p>';
        }}

        function copyCommand() {{
            const cmd = buildCommandString();
            navigator.clipboard.writeText(cmd).then(() => {{
                addToHistory(cmd);
            }});
        }}

        function showRunInstructions() {{
            const cmd = buildCommandString();
            alert('Copy and run in terminal:\\n\\n' + cmd);
            addToHistory(cmd);
        }}

        function addToHistory(cmd) {{
            history.unshift({{ time: new Date().toLocaleTimeString(), command: cmd }});
            if (history.length > 10) history.pop();
            renderHistory();
        }}

        function renderHistory() {{
            const container = document.getElementById('history-list');
            container.innerHTML = history.map(h =>
                '<div class="history-item" onclick="loadFromHistory(\\'' + h.command.replace(/'/g, "\\'") + '\\')">' +
                '<div class="time">' + h.time + '</div>' +
                '<div class="command">' + h.command + '</div>' +
                '</div>'
            ).join('');
        }}

        function loadFromHistory(cmd) {{
            document.getElementById('raw-command').value = cmd;
            switchTab('raw');
        }}

        function showSaveModal() {{
            document.getElementById('save-modal').classList.add('visible');
        }}

        function hideSaveModal() {{
            document.getElementById('save-modal').classList.remove('visible');
        }}

        function savePreset() {{
            const name = document.getElementById('preset-name').value;
            if (!name) return;

            savedPresets.push({{
                name: name,
                command: currentCommand,
                params: {{...params}}
            }});

            localStorage.setItem('audit-presets', JSON.stringify(savedPresets));
            loadSavedPresets();
            hideSaveModal();
        }}

        function loadSavedPresets() {{
            try {{
                savedPresets = JSON.parse(localStorage.getItem('audit-presets') || '[]');
            }} catch {{
                savedPresets = [];
            }}

            document.getElementById('preset-count').textContent = savedPresets.length;
            const container = document.getElementById('saved-presets');
            container.innerHTML = savedPresets.map((p, i) =>
                '<div class="collection-item" onclick="loadPreset(' + i + ')">' +
                '<span class="method-badge method-run">PRE</span>' +
                '<span class="item-name">' + p.name + '</span>' +
                '</div>'
            ).join('');
        }}

        function loadPreset(index) {{
            const preset = savedPresets[index];
            currentCommand = preset.command;
            params = {{...preset.params}};

            const cmdDef = commands[currentCommand];
            document.getElementById('command-title').textContent = cmdDef.title;
            document.getElementById('command-subtitle').textContent = cmdDef.subtitle;

            renderAdjusters();
            updateCommand();
        }}

        // Initial render
        renderAdjusters();
        renderDocs();
    </script>
</body>
</html>
"""


def generate_api_collection(
    output_path: Path,
    repo_name: str = "Repository",
    version: str = "1.5.4",
    presets: Optional[list[dict]] = None,
) -> None:
    """
    Generate API collection HTML page with adjustable controls.

    Args:
        output_path: Path to write HTML file
        repo_name: Repository name for display
        version: Pipeline version
        presets: Optional list of preset configurations
    """
    html = API_COLLECTION_TEMPLATE.format(
        repo_name=repo_name,
        version=version,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
