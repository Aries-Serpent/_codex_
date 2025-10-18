# [Guide]: Copilot Space Audit Usage (v1.1.0)

 Roles: [Primary: Workflow Steward], [Secondary: Reliability Analyst]  Energy: 5

## 1. Quick Run
```bash
python scripts/space_traversal/audit_runner.py run
```

## 2. Single Stage Invocation
```bash
python scripts/space_traversal/audit_runner.py stage S4
```

## 3. Explain a Capability Score
```python
from scripts/space_traversal.capability_scoring import explain_score
import json
data = json.load(open("audit_artifacts/capabilities_scored.json"))
weights = {"functionality":0.25,"consistency":0.2,"tests":0.25,"safeguards":0.15,"documentation":0.15}
print(explain_score(data["capabilities"][0], weights))
```
CLI alternative:
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

## 5. Determinism Validation
Two sequential runs (no source changes) must produce identical:
- `repo_root_sha`
- `capabilities_scored.json` (excluding timestamp)
If mismatch: review detector randomness or unsorted enumeration.

*End of guide*
