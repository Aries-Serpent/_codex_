# Guide: HTML Visual Checks (v1.2)
> Generated: Previous Cycle-11-02 16:14:10 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Visual QA], [Secondary: Publisher] ⚡ Energy: 5

Goal
- Ensure HTML renderers produce consistent, loadable documents and screenshots.

Tools
- Renderer: scripts/status/render_html_report.py
- Screenshot: scripts/status/screenshot_html.py (Playwright)
- CI: .github/workflows/html_visual_regression.yml

Local
- python scripts/status/render_html_report.py --json docs/templates/status/example_report_v1.2.json --out reports/daily/TEST.html --template docs/templates/status/report_template_themed.html
- python scripts/status/screenshot_html.py --html reports/daily/TEST.html --out reports/daily/TEST.png
