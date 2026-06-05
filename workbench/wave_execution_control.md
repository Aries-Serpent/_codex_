# Wave Execution Control Sheet

## Parallel orchestration model
- Dispatcher pool: `agent-orchestrator` and `orchestrator-agent`
- Dependency gate source: `workbench/codex_ready_task_sequence.yaml` (`dependencies`, `parallel_with`)
- Failed-check routing rule: `job logs -> collect_telemetry classification -> pattern_recorder trend/recurrence -> remediation agent assignment`
- Verification/log-analysis agents run continuously while implementation streams are capped by dependency cluster.

## Required outputs per wave
| Wave | Gap status updates done | Evidence links complete | Lane summary updated | Escalations captured |
|---|---|---|---|---|
| Wave 0 | [ ] | [ ] | [ ] | [ ] |
| Wave 1 | [ ] | [ ] | [ ] | [ ] |
| Wave 2 | [ ] | [ ] | [ ] | [ ] |
| Wave 3 | [ ] | [ ] | [ ] | [ ] |
| Wave 4 | [ ] | [ ] | [ ] | [ ] |

## Lane summary board
| Lane | Completed | Blocked | Escalated | Next handoff |
|---|---|---|---|---|
| Lane A — Security/Compliance | 0 | 0 | 0 | pending |
| Lane B — CI/Workflow resilience + alerting | 0 | 0 | 0 | pending |
| Lane C — Repro/platform hardening | 0 | 0 | 0 | pending |
| Lane D — QA/coverage/testing scale-up | 0 | 0 | 0 | pending |
| Lane E — ML drift and advanced capabilities | 0 | 0 | 0 | pending |
| Shared lane — cross-cutting/maintenance | 0 | 0 | 0 | pending |

## Feedback loop checkpoints
| Wave | Failure rate trend | Pattern distribution shift | Unknown bucket size | Self-healing cascade rate | collect_telemetry update | pattern_recorder update |
|---|---|---|---|---|---|---|
| Wave 0 | pending | pending | pending | pending | [ ] | [ ] |
| Wave 1 | pending | pending | pending | pending | [ ] | [ ] |
| Wave 2 | pending | pending | pending | pending | [ ] | [ ] |
| Wave 3 | pending | pending | pending | pending | [ ] | [ ] |
| Wave 4 | pending | pending | pending | pending | [ ] | [ ] |
