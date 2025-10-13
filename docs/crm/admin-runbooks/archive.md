# Archive runbook

## Archive a file
```bash
python -m codex.cli archive store _codex_ src/legacy/zendesk_v1.py --reason dead --by "marc" --commit d3e8729 --mime text/x-python --lang python
```
Output includes the **tombstone** (UUID) and **sha256**. Replace the file with a brief stub that points to the tombstone and restoration command.

## Auto-plan and apply (batch archival)
```bash
# 1) Build the plan (age threshold = 180 days)
python -m codex.cli archive plan --sha HEAD --age 180 --root . --out artifacts/archive_plan.json
# 2) Apply the plan (store blobs + write tombstone stubs)
python -m codex.cli archive apply-plan artifacts/archive_plan.json --repo _codex_ --by "marc"
```
Artifacts:
- `artifacts/archive_plan.json` — deterministic plan with scored entries
- `.codex/evidence/archive_ops.jsonl` — append-only evidence
- In-tree files replaced by **tombstone stubs** with restore command
