# Guide: Visual Baselines for HTML Reports (v1.2)
> Generated: 2024-11-02 16:16:14 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Visual QA], [Secondary: Publisher] ⚡ Energy: 5

Purpose
- Maintain baseline screenshots to detect unintended visual regressions in rendered HTML reports.

Structure
| Path | Notes |
|---|---|
| visual_baseline/ | Root folder (committed) |
| visual_baseline/status_report_themed.png | Baseline for themed template |
| visual_baseline/status_report_default.png | Baseline for default template |

Workflow
- Render HTML using example JSON and chosen template.
- Capture screenshot to reports/daily/<date>.png.
- Compare with baseline via tools/visual_compare.py.

Commands
- Render:
  - python scripts/status/render_html_report.py --json docs/templates/status/example_report_v1.2.json --out reports/daily/TEST.html --template docs/templates/status/report_template_themed.html
- Screenshot:
  - python scripts/status/screenshot_html.py --html reports/daily/TEST.html --out reports/daily/TEST.png
- Compare:
  - python tools/visual_compare.py --baseline visual_baseline/status_report_themed.png --candidate reports/daily/TEST.png --metric ssim --threshold 0.98

Refreshing Baseline (when intended changes occur)
- Use scripts/status/update_visual_baseline.sh to copy candidate into visual_baseline/ after review.
