# Ops: Visual Regression Baselines (v1.2)
> Generated: Previous Cycle-11-02 16:16:14 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Visual QA Lead], [Secondary: CI Maintainer] ⚡ Energy: 5

Policy
- Baselines live in visual_baseline/ and are reviewed like code.
- Threshold default: SSIM ≥ 0.98; justify deviations in PR description.

CI Integration
- html_visual_baseline.yml renders, screenshots, then compares with baseline.
- Failing similarity blocks PR; refresh baseline only after human review.
