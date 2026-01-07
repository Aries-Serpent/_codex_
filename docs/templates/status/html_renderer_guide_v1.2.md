# Guide: Status HTML Renderer (v1.2)
> Generated: 2024-11-02 16:00:04 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Publisher], [Secondary: Reviewer] ⚡ Energy: 5

Purpose
- Render a shareable HTML status report from the v1.2 JSON.

Commands
- Default template:
  - python scripts/status/render_html_report.py --json reports/daily/YYYY-MM-DD.json --out reports/daily/YYYY-MM-DD.html
- Custom template:
  - python scripts/status/render_html_report.py --json reports/daily/YYYY-MM-DD.json --out reports/daily/YYYY-MM-DD.html --template docs/templates/status/report_template.html

Notes
- Keep output HTML under reports/daily/.
- Use compute_delta.py to populate coverage deltas prior to rendering.
