# Cheat Sheet: Copilot — Status v1.2
> Generated: 2025-11-02 15:50:14 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Copilot Operator], [Secondary: Reviewer] ⚡ Energy: 5

Daily flow (commands)
- Generate skeleton:
  - python tools/status_report.py --title "📍 `_codex_` : Status Update $(date -u +%Y-%m-%d-%H:%M:UTC)" --out reports/daily/$(date -u +%Y-%m-%d).json
- Validate example + configs:
  - pytest -q tests/status/test_example_report_schema.py
  - python tools/validate_configs.py --root configs/training --schema configs/schemas/training.schema.yaml
- Build audit & enrich:
  - bash scripts/status/refresh_artifacts_and_update_report.sh
- Render MD:
  - python scripts/status/render_full_markdown_report.py --json reports/daily/$(date -u +%Y-%m-%d).json --out reports/daily/$(date -u +%Y-%m-%d).md
