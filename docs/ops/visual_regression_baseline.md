# Ops: Visual Regression Baselines (v1.2)
> Generated: 2026-06-22 (audited) | Author: mbaetiong  
🧠 Roles: [Primary: Visual QA Lead], [Secondary: CI Maintainer] ⚡ Energy: 5

Policy
- Baselines live in visual_baseline/ and are reviewed like code.
- Threshold default: SSIM ≥ 0.98; justify deviations in PR description.

CI Integration
- html_visual_baseline.yml renders, screenshots, then compares with baseline.
- Failing similarity blocks PR; refresh baseline only after human review.
