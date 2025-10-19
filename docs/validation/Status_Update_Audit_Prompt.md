# [Prompt]: Codex Status Update Audit (v1.1.0)
> Generated: 2025-10-18 09:47:17 UTC | Author: mbaetiong

 Roles: [Audit Orchestrator], [Capability Cartographer]  Energy: 5


## Objective
Synthesize a concise status update from the latest audit artifacts, highlighting low-maturity areas, changes vs baseline, effective weights, and integrity signals.

## Inputs
- audit_artifacts/capabilities_scored.json
- audit_artifacts/gaps.json (optional)
- audit_run_manifest.json (optional)
- Baseline scored JSON (optional; pass to --base)

## Commands
- Full status update:
```bash
python scripts/space_traversal/status_update_report.py
```
- With baseline comparison:
```bash
python scripts/space_traversal/status_update_report.py --base baseline/capabilities_scored.json
```

## Report Sections
| Section | What to include |
|---------|------------------|
| Executive Summary | counts, average score, # low (< low threshold), warnings |
| Low Maturity Focus | top 25 low-scoring capabilities + primary_deficit |
| Movement Since Baseline | top improvements/regressions by Δ score |
| Weights | effective normalized weights |
| Integrity | repo_root_sha, template_hash from manifest |

## Acceptance
- Report saved under reports/codex_status_update_<timestamp>.md
- Deterministic output given identical inputs (ignoring timestamp)
- No network operations

## Follow-ups
- File a remediation task for each low maturity item below policy
- Attach status report and diff table to weekly update PR

*End of Prompt*
