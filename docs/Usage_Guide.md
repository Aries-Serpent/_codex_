# [Guide]: Copilot Space Audit Usage (v1.1.0)
> Generated: 2025-10-10 01:58:00 UTC | Author: mbaetiong
Roles: [Workflow Steward], [Reliability Analyst]  Energy: 5

## Quick Run
```bash
python scripts/space_traversal/audit_runner.py run
```

## Single Stage
```bash
python scripts/space_traversal/audit_runner.py stage S4
```

## Explain Score
```bash
python scripts/space_traversal/audit_runner.py explain checkpointing
```

## Update Weights then Rerun S4–S7
```bash
python scripts/space_traversal/audit_runner.py stage S4
python scripts/space_traversal/audit_runner.py stage S5
python scripts/space_traversal/audit_runner.py stage S6
python scripts/space_traversal/audit_runner.py stage S7
```

## CI (Optional)
```bash
python scripts/space_traversal/audit_runner.py run
python scripts/space_traversal/audit_runner.py diff --old baseline/capabilities_scored.json --new audit_artifacts/capabilities_scored.json
```

## Red Flags & Mitigations
| Symptom | Cause | Action |
|---------|-------|--------|
| Sudden score drop | Deleted/renamed evidence | Restore or adjust detectors |
| Zero safeguards | Stale keyword set | Update SAFEGUARD_KEYWORDS |
| High duplication penalty | Broad facet regex | Narrow patterns |

*End of Guide*
