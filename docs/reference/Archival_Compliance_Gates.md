# [Reference]: Archival Compliance Gates (CI & Local)
> Generated: Previous Cycle-11-06 23:16:52 UTC | Author: mbaetiong  
Roles: [Audit Orchestrator], [Capability Cartographer]  Energy: 5

## 1) Purpose
Enforce the Archival Inventory Process for any terminating action (remove, delete, sunset, prune) across code, docs, workflows, tests.

## 2) Required Steps (Summary)
| Step | Requirement |
|------|-------------|
| ADR | docs/arch/ADR-*.md drafted and linked |
| Tombstone | Replace removed artifact with TOMBSTONE stub referencing ADR |
| Evidence | Append .codex/evidence/archive_ops.jsonl entry |
| CHANGELOG | Deprecations added |
| Pointer (conditional) | For large removals, compress originals and write pointer JSON |

## 3) CI Gate
- Workflow: .github/workflows/archival_compliance.yml
- Script: scripts/archival/check_archival_compliance.py
- Behavior:
  - Fails if a removed path lacks a tombstone stub or ADR reference.
  - Warns if evidence append is missing.

## 4) Local Run
```bash
python scripts/archival/check_archival_compliance.py --base HEAD~1 --head HEAD
```text

## 5) Manifest Visibility (P6)
When MANIFEST_EXTENDED_ENABLE=1, manifest includes: archival_events_count and related provenance fields.

*End of Archival Compliance Reference*
