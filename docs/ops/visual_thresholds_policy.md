# Ops: Visual Thresholds & Rotation (v1.2)
> Generated: 2025-11-02 16:20:49 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Visual QA Lead], [Secondary: CI Maintainer] ⚡ Energy: 5

Policy
- Per-template thresholds and metrics live in visual_baseline/thresholds.json
- Rotation keeps last N baselines per template directory under visual_baseline/<template>/

Commands
- Compare with config:
  - python tools/visual_compare_config.py --config visual_baseline/thresholds.json --template report_template_themed.html --baseline visual_baseline/report_template_themed/LATEST.png --candidate reports/daily/TEST.png
- Rotate:
  - python tools/visual_baseline_rotate.py --template report_template_themed --keep 5

CI Integration
- Use html_visual_baseline.yml to render and compare.
- Add a step to rotate artifacts periodically if baselines are timestamped.
