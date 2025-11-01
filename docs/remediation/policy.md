# [Playbook]: Gate Policy and Tuning
Roles: [Audit Orchestrator], [Capability Cartographer] Energy: 5

Defaults:
- thresholds.low = 0.70, thresholds.medium = 0.85
- regression gate: fail_on_score_regression with delta 0.02
- low threshold gate: fail_on_low_maturity = true
- missing detector gate: fail_on_missing_detector = true

Tuning scenarios:
- Noisy detectors inflating zeros → temporarily set fail_on_low_maturity=false while refining detectors.
- New capability rollout → add alias under capability_map.overrides before code lands to enforce presence.
- Stabilizing phase → keep regression delta at 0.02 and revisit monthly.

Notes:
- All policy toggles live in .copilot-space/workflow.yaml.
- CI gate behavior comes from audit_runner validate exit codes.
