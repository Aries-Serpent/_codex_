# Codex Platform — Observability Runbooks

**Version**: 1.0  
**Created**: 2026-05-27  
**Owner**: `unified-doc-agent`  
**SLO Reference**: [`SLO_DEFINITIONS.md`](SLO_DEFINITIONS.md)

---

## Index

| # | Runbook | Trigger |
|---|---------|---------|
| RB-01 | [ML Serving Latency SLO Breach](#rb-01-ml-serving-latency-slo-breach) | P95 > 600 ms for 5 min |
| RB-02 | [ML Serving Availability SLO Breach](#rb-02-ml-serving-availability-slo-breach) | Availability < 99 % over 1 h |
| RB-03 | [RAG Index Stale](#rb-03-rag-index-stale) | Index age > 24 h |
| RB-04 | [RAG Retrieval Quality Drop](#rb-04-rag-retrieval-quality-drop) | Recall drops > 10 % vs. baseline |
| RB-05 | [Agent Orchestration Failure Rate High](#rb-05-agent-orchestration-failure-rate-high) | Success rate < 90 % over 24 h |
| RB-06 | [CI Pipeline Pass Rate Low](#rb-06-ci-pipeline-pass-rate-low) | 7-day pass rate < 90 % |
| RB-07 | [Critical Security Alert Open](#rb-07-critical-security-alert-open) | Any P1 security alert open |

---

## RB-01 — ML Serving Latency SLO Breach

**Trigger**: P95 latency > 600 ms for 5 consecutive minutes.

### Immediate (< 5 min)
1. Open GitHub Actions → `ci-health-monitor.yml` → latest run.
2. Check the "ML serving latency" step log for job IDs and p95 metric.
3. Confirm the alert is not a false positive from a canary deploy.

### Investigate (< 30 min)
1. Check recent commits to `src/codex_ml/serving/` for regressions.
2. Check for large model reloads coinciding with the latency spike.
3. Verify resource saturation (CPU/memory) in the runner environment.

### Escalate
- If not resolved in 30 min: create a GitHub Issue with label `p1:latency` and assign `@mbaetiong`.

### Resolve
1. Revert offending commit if identified.
2. Update `benchmarks/serving/latency_baseline.json` if expected change.
3. Close the GitHub Issue once SLO is restored for 30 min.

---

## RB-02 — ML Serving Availability SLO Breach

**Trigger**: Availability < 99 % over a 1-hour window.

### Immediate
1. Check recent deploy workflows for failed smoke tests.
2. Check GitHub Actions for `smoke-tests.yml` run failures in the last 2 hours.

### Investigate
1. Identify the first failing smoke test run timestamp.
2. Look for deployment-correlating commits (look at commit graph around that time).

### Resolve
1. Roll back the last deployment PR if root cause is a recent deploy.
2. Re-run smoke tests to confirm recovery.

---

## RB-03 — RAG Index Stale

**Trigger**: RAG index age exceeds 24 hours.

### Immediate
1. Open GitHub Actions → `rag-freshness-scheduler.yml`.
2. Check whether the last scheduled run was skipped (e.g., branch-protection, concurrency cancel).

### Investigate
1. Inspect `rag-freshness-scheduler.yml` → last completed run logs for errors.
2. Check embedding resource quota (model API rate limits).

### Resolve
1. Trigger a manual run: `Actions → rag-freshness-scheduler.yml → Run workflow`.
2. Verify the freshness timestamp in `.codex/config/rag_quality.yaml` updates.
3. If the scheduled run keeps failing, open an issue with label `rag:stale` and assign `rag-freshness-loop-agent`.

---

## RB-04 — RAG Retrieval Quality Drop

**Trigger**: Recall drops > 10 % versus the baseline in `benchmarks/rag/retrieval_benchmark.json`.

### Immediate
1. Open the failing `test-rag.yml` run and review the assertion output.
2. Check whether any embedding model version was changed in recent PRs.

### Investigate
1. Run `python benchmarks/rag/run_benchmark.py` locally if feasible.
2. Compare new metrics against baseline values (recall ≥ 0.70, MRR ≥ 0.60).

### Resolve
1. If quality genuinely improved, update `benchmarks/rag/retrieval_benchmark.json` baseline.
2. If regression, revert the offending embedding model / chunking change.

---

## RB-05 — Agent Orchestration Failure Rate High

**Trigger**: Agent task success rate < 90 % over a 24-hour window.

### Immediate
1. Open `cognitive-action-decision.yml` → latest run.
2. Review the `orchestration_compliance.log` artifact for task failure reasons.

### Investigate
1. Identify failing agent names and task types.
2. Check for policy enforcement changes that may block valid tasks.
3. Review `docs/agent/ORCHESTRATION_COMPLIANCE.md` for allowed failure modes.

### Resolve
1. Restart the affected agent session if transient.
2. Open an issue with label `agent:failure` if pattern persists.

---

## RB-06 — CI Pipeline Pass Rate Low

**Trigger**: 7-day pass rate drops below 90 %.

### Immediate
1. Open GitHub Actions → `ci-health-monitor.yml` → trend chart.
2. Identify which workflow is contributing most failures.

### Investigate
1. Run `ci-flake-tracker.yml` manually to get the latest flake report.
2. Check whether a noisy test is driving the rate down (mark `@pytest.mark.flaky` if confirmed flaky).

### Resolve
1. File an issue with label `ci:flaky` for the offending test.
2. Use `autonomous-test-healer-agent` to generate a fix PR.
3. Quarantine the test if it cannot be fixed in < 48 h.

---

## RB-07 — Critical Security Alert Open

**Trigger**: `nightly-security-mttr.yml` reports any critical CodeQL / Dependabot alert older than MTTR SLA (3 days).

### Immediate
1. Open `nightly-security-mttr.yml` → latest run → download the `security-mttr-report.json` artifact.
2. Identify alert number(s) and affected file(s).

### Investigate
1. Use `scripts/security/fetch_all_code_scanning_alerts.py` to get full context.
2. Assess exploitability: is the vulnerable code path reachable in production?

### Resolve
1. Assign to the owning domain team (see `.codex/DOMAIN_OWNERSHIP.md`).
2. Track MTTR in `docs/security/SECURITY_SLA.md`.
3. Dismiss as false positive via GitHub Security Advisories UI with a written justification if not exploitable.

---

## Runbook Maintenance

- Runbooks must be reviewed quarterly by `unified-doc-agent`.
- Every runbook must have an **Immediate**, **Investigate**, and **Resolve** section.
- Open an issue with label `docs:runbook` when a runbook becomes stale.
