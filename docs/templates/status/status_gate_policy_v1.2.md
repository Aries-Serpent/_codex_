# Policy: Status Gate (.statusrc) (v1.2)
> Generated: 2024-11-02 15:42:47 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Policy Author], [Secondary: Reviewer] ⚡ Energy: 5

Goal
- Define local gate thresholds and expectations enforced by tools/status_gate_from_statusrc.py and CI.

Fields
| Field | Type | Meaning | Example |
|---|---|---|---|
| fail_under_coverage | number | Minimum overall coverage (%) | 35 |
| lint_required | boolean | Require lint gate | true |
| typecheck_required | boolean | Require typecheck | false |
| security.allow_high_vulns | number | Max HIGH vulns | 0 |
| security.allow_critical_vulns | number | Max CRITICAL vulns | 0 |
| status_template_version | string | Expected template schema version | v1.2 |
| report_storage | string | Where reports are stored | reports/daily |

Usage
- Local: python tools/status_gate_from_statusrc.py
- CI: .github/workflows/status_gate.yml
