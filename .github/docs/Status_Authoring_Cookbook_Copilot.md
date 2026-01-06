# Cookbook: Copilot Status Authoring (v1.2)
> Generated: Previous Cycle-11-02 15:29:01 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Copilot Workflow Author], [Secondary: Reviewer] ⚡ Energy: 5

Recipes
- Generate skeleton JSON
  - "Run: python tools/status_report.py --title '📍 `_codex_` : Status Update $(date -u +%Y-%m-%d-%H:%M:UTC)' --out reports/daily/$(date -u +%Y-%m-%d).json"
- Validate schema
  - "Run: pytest -q tests/status/test_example_report_schema.py"
- Merge automation artifacts
  - "Run: python scripts/status/validate_and_publish.py > status_validation_summary.json"
- Build audit chain
  - "Run: python scripts/audit/build_integrity_chain.py"
