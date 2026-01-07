# Template: Security Policy (v1.2)
> Generated: 2024-11-02 15:21:24 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Security Policy Author], [Secondary: Reviewer] ⚡ Energy: 5

Schema
- Path: configs/schemas/security_policy.schema.json

Fields (examples)
- sast.bandit_fail_on: none|low|medium|high
- secrets.baseline_required: true|false
- dependencies.max_critical, dependencies.max_high: integers ≥ 0

Usage
- Validate with tools/schema_validate.py
- Gate decisions in CI (fail or warn) based on policy
