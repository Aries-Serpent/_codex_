# Pruning Candidate Registry

Lifecycle is `CANDIDATE → QUARANTINE → CONSOLIDATED/ARCHIVED`.  A record must
include dependency and parity evidence before it can be archived.

| workflow_name | stage | candidate_date | owner | dependency_map_path | parity_report_path | rollback_sha |
|---|---|---|---|---|---|---|
| _No candidates registered_ | — | — | — | — | — | — |

Use `scripts/ci/simulate_trigger_paths.py` before quarantine and
`scripts/ci/prune_validation_checklist.py` before consolidation or archival.
