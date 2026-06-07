# Evidence-First Intake Baseline

Source of truth for artifact names/retention: `.github/workflow-archive/ARTIFACT_CATALOG.md`.

## Latest workflow evidence snapshot

> Snapshot note: run links and artifact states below are a baseline capture and must be refreshed at the start of each wave.

| Workflow | Latest run | Conclusion | Artifact evidence | Failed job logs | Pattern classification |
|---|---|---|---|---|---|
| `telemetry-collection.yml` | https://github.com/Aries-Serpent/_codex_/actions/runs/26992618604 | success | `telemetry-report-26992618604` | n/a | n/a |
| `ci-health-monitor.yml` | https://github.com/Aries-Serpent/_codex_/actions/runs/27033774730 | success | none uploaded (uses summary + repo vars) | n/a | n/a |
| `proactive-ci-monitor.yml` | https://github.com/Aries-Serpent/_codex_/actions/runs/27033063057 | failure | expected `proactive-ci-monitor-report-27033063057` missing (upload step had no file) | https://github.com/Aries-Serpent/_codex_/actions/runs/27033063057/job/79790010763 | `unknown` via `scripts/ci/collect_telemetry.py` classifier |
| `iterative-self-healing-ci.yml` | https://github.com/Aries-Serpent/_codex_/actions/runs/27043392132 | skipped | none | no failed jobs in latest run | n/a |

## Correlated failure evidence (current blocking sample)

- Workflow: `proactive-ci-monitor.yml` run `27033063057`
- Failed step: `Set up Python 3.12` in job `79790010763`
- Log signature: `No file in ... matched to [**/requirements.txt or **/pyproject.toml]`
- Artifact impact: runner-temp report file `proactive_report.json` was not produced; upload step warned and no artifact was retained
- Existing pattern-system result: `collect_telemetry.classify_failure(...) -> unknown` (escalation path applies)
- Recurrence trend source: `scripts/ci/pattern_recorder.py` (current local summary reports no stored occurrences)

## Intake protocol before each wave

1. Pull latest runs + artifacts for telemetry, CI health, proactive monitor, and iterative self-healing workflows.
2. For each failed job, collect logs and correlate with missing/present artifacts.
3. Classify failures with `scripts/ci/collect_telemetry.py` and record recurrence with `scripts/ci/pattern_recorder.py`.
4. Route failures to remediation lanes only after classification + evidence linking is complete.
