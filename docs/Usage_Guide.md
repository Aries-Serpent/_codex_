# [Guide]: Copilot Space Audit Usage (v1.1.0)
> Generated: 2025-10-10 02:53:25 UTC | Author: mbaetiong
Roles: [Workflow Steward], [Reliability Analyst]  Energy: 5

## 1. Quick Run
```bash
python scripts/space_traversal/audit_runner.py run
```

## 2. Single Stage Invocation
```bash
python scripts/space_traversal/audit_runner.py stage S4
```

## 3. Explain a Capability Score
```bash
python scripts/space_traversal/audit_runner.py explain checkpointing
```

## 4. Update Weights
Edit `.copilot-space/workflow.yaml` → rerun S4–S7:
```bash
python scripts/space_traversal/audit_runner.py stage S4
python scripts/space_traversal/audit_runner.py stage S5
python scripts/space_traversal/audit_runner.py stage S6
python scripts/space_traversal/audit_runner.py stage S7
```

## 5. Add a New Capability
| Step | Action |
|------|--------|
| 1 | Create detector in `scripts/space_traversal/detectors/` |
| 2 | Implement `detect()` contract |
| 3 | Run `stage S3` or full `run` |
| 4 | Inspect `capabilities_raw.json` |
| 5 | Confirm matrix entry |

## 6. Determinism Validation
Two sequential runs (no source changes) must produce identical:
- `repo_root_sha`
- `capabilities_scored.json` (excluding timestamp)

*End of Guide*
