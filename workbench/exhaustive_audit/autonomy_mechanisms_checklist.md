# Autonomy Mechanisms Checklist

Legend: ✅ present/validated, ⚠️ partial/manual, ❌ missing.

| Mechanism | Status | Notes |
| --- | --- | --- |
| Pre-commit hooks | ⚠️ | `.pre-commit-config.yaml` exists but not enforced in CI; no evidence of routine execution. |
| Nox/Tox gates | ⚠️ | `noxfile.py` defines tests/hygiene sessions, but no CI invocation or coverage thresholds. |
| Deterministic seeding | ⚠️ | `training/config.py` exposes `seed`/`deterministic`, but no global enforcement or test harness. |
| Drift detection | ❌ | No config/data drift checks or hash comparisons on load. |
| Auto-remediation | ❌ | No scripts to auto-fix failed runs, repair checkpoints, or regenerate configs. |
| Health checks | ❌ | Services lack liveness/readiness probes; CLI returns not wrapped with health endpoints. |
| Alerting | ❌ | No alert rules or notifications for failed jobs, drift, or anomalies. |
| Self-improvement loop | ❌ | No mechanism to ingest gap registry and open remediation tasks automatically. |
| Evidence capture | ⚠️ | Nox evidence helpers exist but optional; not enforced or summarized in CI. |
| Coverage gate | ❌ | `pytest.ini` uses `-q` with no `--cov` or `--cov-fail-under` default. |
| Secrets/keys guard | ⚠️ | Bandit/detect-secrets configs present, but enforcement in pipelines unclear. |
| Dependency drift guard | ⚠️ | Vendor purge/evidence optional; no automated upgrade cadence or lockfile checks. |
| Rollback/resume | ⚠️ | Checkpoint manifests emitted, but corruption detection/repair missing. |
| Chaos testing | ❌ | No failure injection or chaos scenarios for training/serving. |
