# Codex Platform — Completion Governance

**Version**: 1.0.0  
**Created**: 2026-05-27  
**Dashboard**: [`../.codex/COMPLETION_DASHBOARD.md`](../COMPLETION_DASHBOARD.md)  
**Rubric**: [`../../docs/rubrics/completion_rubric_v1.md`](../../docs/rubrics/completion_rubric_v1.md)  
**Domain ownership**: [`../DOMAIN_OWNERSHIP.md`](../DOMAIN_OWNERSHIP.md)

---

## Purpose

This document defines the operational procedures that keep the completion rubric alive
and actionable: who rescores, on what cadence, what blocks a release, and how to
manage the 90-day remediation roadmap.

---

## Phase 2 — Stabilisation

**Goal**: Reach rubric score ≥ 75 % (Operational but needs hardening).  
**Horizon**: 4–6 weeks from baseline.

### 2.1 Eliminate CI Flakiness

| Action | Owner | Evidence |
|--------|-------|---------|
| Enable `pytest-rerunfailures` tracking and report flake rate weekly | CI owner | flake-rate metric in `ci-health-monitor.yml` |
| File a GitHub Issue for each test flaking > 2 times in a week | CI owner | Issue labelled `flaky-test` |
| Gate PRs to `main` when flake rate exceeds 1 % | CI owner | `workflow-execution-gate.yml` threshold |
| Run determinism checks (`determinism.yml`) on every merge | CI owner | Green badge on main |

### 2.2 Enforce Security Remediation SLA

| Action | Owner | Evidence |
|--------|-------|---------|
| Define SLA: critical ≤ 3 business days; high ≤ 10 business days | Security owner | Document in `docs/security/SECURITY_SLA.md` |
| Automate MTTR tracking via `nightly-codeql-alert-triage.yml` | Security owner | MTTR report in `reports/security/` |
| Weekly burn-down review: block release if critical > 0 | Security owner | `security-alert-notification.yml` |
| Confirm dependency allowlist (`security_allowlist.json`) is current | Security owner | Reviewed in prior 30 days |

### 2.3 Add RAG Freshness and Quality Gates

| Action | Owner | Evidence |
|--------|-------|---------|
| Define freshness SLA: index age ≤ 24 h | RAG owner | Documented in `docs/rag/RAG_QUICKSTART.md` |
| Add retrieval quality threshold (top-k recall) to `test-rag.yml` | RAG owner | Gate passes on `main` |
| Configure drift alert: fire when quality drops > 10 % vs baseline | RAG owner | Alert tested via canary |
| Commit benchmark baseline to `benchmarks/rag/` | RAG owner | File exists with version tag |

### 2.4 Add Orchestration Reliability KPIs

| Action | Owner | Evidence |
|--------|-------|---------|
| Instrument orchestration success/failure counters in Cognitive Brain | Agent owner | Metric in monitoring dashboard |
| Report success rate (target ≥ 95 %) in `cognitive-action-decision.yml` | Agent owner | Logged to `reports/orchestration/` |
| Add policy-violation alert: fires within 5 min of violation | Agent owner | Tested via integration test |
| Nightly integration test validating OODA loop recovery | Agent owner | Job green on `main` |

---

## Phase 3 — Hardening

**Goal**: Reach rubric score ≥ 90 % (Production-complete).  
**Horizon**: 8–12 weeks from baseline.

### 3.1 Dependency / Supply-Chain Controls

| Action | Owner | Evidence |
|--------|-------|---------|
| Generate SBOM (CycloneDX) on every release via `sbom.yml` | Release owner | SBOM artifact in GitHub Release |
| Sign release artifacts with Sigstore | Release owner | Provenance attestation in release |
| Gate `pypi-publish.yml` on rubric score ≥ 80 % | Release owner | Score check step in workflow |
| Review and pin all unpinned transitive deps | Security owner | `uv.lock` / `requirements*.txt` audited |

### 3.2 Performance / Cost Regression Gates

| Action | Owner | Evidence |
|--------|-------|---------|
| Run `benchmarks.yml` on every PR to `main`; block on regression ≥ 10 % | Perf owner | Gate in `pr-checks.yml` |
| Define P50/P99 latency budgets for serving and RAG retrieval | Perf owner | Documented in `docs/PERFORMANCE_OPTIMIZATION_GUIDE.md` |
| Generate weekly CI cost report via `pr-cost-check.yml` | CI owner | Report posted to Discussion |
| Track cache hit ratio; alert when < 90 % | CI owner | `cache-health-monitor.yml` metric |

### 3.3 Incident-Grade Observability Runbooks

| Action | Owner | Evidence |
|--------|-------|---------|
| Create runbook for ML serving failure (`docs/runbooks/serving_failure.md`) | ML owner | File committed |
| Create runbook for RAG pipeline failure (`docs/runbooks/rag_failure.md`) | RAG owner | File committed |
| Create runbook for agent orchestration failure (`docs/runbooks/agent_failure.md`) | Agent owner | File committed |
| Define SLO dashboards (tools/dashboards/) for each critical surface | Ops owner | Dashboards linked from `docs/runbooks/` |
| Test alerts by triggering canary failures; document results | Ops owner | Test report in `reports/observability/` |

### 3.4 End-to-End Reproducibility Validation

| Action | Owner | Evidence |
|--------|-------|---------|
| Run `dvc repro` twice on identical inputs; diff artefacts (expect zero diff) | ML owner | Report in `reports/reproducibility/` |
| Validate model registry: every released model has a version entry | ML owner | Registry audit in `reports/` |
| Document rollback procedure for each environment | ML owner | `docs/PRODUCTION_DEPLOYMENT_GUIDE.md` updated |
| Add E2E gate (train → eval → register → serve) to `nox -s ml_tests` | ML owner | Nox session green on `main` |

---

## Phase 4 — Completion Governance

**Goal**: Sustain score ≥ 90 % indefinitely.

### 4.1 Monthly Rescoring Procedure

1. Domain owner for each of the 11 domains reviews exit criteria and updates their score
   in `.codex/completion_scores.yaml`.
2. Run `python scripts/ci/score_completion.py --scores .codex/completion_scores.yaml`.
3. Update `.codex/COMPLETION_DASHBOARD.md` — add a row to the Score History table.
4. Open a PR titled `chore: monthly completion rescore YYYY-MM` with the updated files.
5. At least one other contributor reviews and approves the PR.

### 4.2 Release-Blocking Rules

A release (tag + PyPI publish) is **blocked** if any of the following are true:

| Condition | Checked by |
|-----------|-----------|
| Any domain has score < 2 | `score_completion.py --fail-below 40` in `pypi-publish.yml` |
| Security domain score < 4 | Hard check in `pypi-publish.yml` |
| Total weighted score < 60 % | `score_completion.py --fail-below 60` in `pypi-publish.yml` |
| Any open **critical** security alert | `security-alert-notification.yml` gate |
| CI pass rate < 90 % in last 7 days | `workflow-execution-gate.yml` |

### 4.3 90-Day Remediation Roadmap Template

Each scoring session produces a rolling 90-day plan.  Use the template below and commit it
to `.codex/plans/REMEDIATION_ROADMAP_YYYY_MM.md`.

```markdown
# Remediation Roadmap — YYYY-MM

Baseline score: XX.X %  Band: <band>

| Domain | Current | Target | Actions | Owner | Due |
|--------|---------|--------|---------|-------|-----|
| <domain> | X | Y | <specific actions> | @owner | YYYY-MM-DD |
```

### 4.4 Definition of Done

A domain is **Done** (score = 5) when:

1. All exit criteria in `DOMAIN_OWNERSHIP.md` are checked off.
2. The evidence artefacts are committed and linked.
3. The CI gates for that domain are **continuously green** for ≥ 30 consecutive days.
4. The domain owner has signed off in the monthly rescore PR.

---

## Contacts & Escalation

| Role | Responsibility | Escalation path |
|------|---------------|-----------------|
| Rubric owner | Maintains scoring methodology and governance doc | Repo maintainer |
| Domain owner | Maintains exit criteria and monthly score for their domain | Rubric owner |
| Release gate owner | Enforces release-blocking rules | Repo maintainer |

---

## Change Log

| Date | Version | Change |
|------|---------|--------|
| 2026-05-27 | 1.0.0 | Initial version |
