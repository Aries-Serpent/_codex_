# Codex Platform — Completion Rubric v1

**Version**: 1.0.0  
**Created**: 2026-05-27  
**Owner**: DevOps + Agent Team  
**Canonical dashboard**: [`.codex/COMPLETION_DASHBOARD.md`](../../.codex/COMPLETION_DASHBOARD.md)  
**Domain ownership & exit criteria**: [`.codex/DOMAIN_OWNERSHIP.md`](../../.codex/DOMAIN_OWNERSHIP.md)  
**Governance procedures**: [`.codex/plans/COMPLETION_GOVERNANCE.md`](../../.codex/plans/COMPLETION_GOVERNANCE.md)

---

## Purpose

This rubric provides a single, evidence-based framework for measuring how "done" the Codex
platform is across all of its major concerns. Completion is not defined by feature count but
by **reliability evidence**: reproducible runs, passing gates, and traceable artifacts.

---

## Scoring Model

Each domain is scored **0–5**.

| Band | Score | Meaning |
|------|-------|---------|
| Non-existent | 0 | No artefacts, ad-hoc or absent |
| Initiated | 1 | Early implementation; unstable |
| Developing | 2 | Partial; key gaps remain |
| Established | 3 | Core functionality reliable; polish needed |
| Mature | 4 | Gates enforced; evidence collected; SLA tracked |
| Complete | 5 | All exit criteria met; continuously validated |

**Weighted total**:

```
Total % = Σ ( (domain_score / 5) × domain_weight_percent )
```

Readiness bands:

| Range | Band |
|-------|------|
| 90–100 | Production-complete |
| 75–89 | Operational but needs hardening |
| 60–74 | Functional but risk-heavy |
| < 60 | Foundation incomplete |

---

## Domains

### 1 · Platform Architecture & Boundaries — 8 %

**Intent**: Clean separation of concerns across the monorepo; enforced ownership and
dependency rules so teams can change code without fear of inadvertent coupling.

| Score | Description |
|-------|-------------|
| 0 | Ad hoc structure; no ownership; imports go anywhere |
| 1 | High-level domains named but not enforced |
| 2 | Major packages separated; inter-package imports informal |
| 3 | Domain map documented; most boundaries respected |
| 4 | Ownership file current; import-linter or similar enforces rules |
| 5 | Architecture map, ownership file, import policy all CI-gated; violations block PRs |

**Required evidence**: architecture map, `DOMAIN_OWNERSHIP.md`, passing import-linter check.

---

### 2 · Core ML Lifecycle (Train / Eval / Serve) — 12 %

**Intent**: A developer can reproduce a training run, evaluate it, register the model, and
promote it to serving using documented, version-controlled commands.

| Score | Description |
|-------|-------------|
| 0 | Only partial pipeline; cannot reproduce end-to-end |
| 1 | Training runs; eval/serving absent or manual |
| 2 | Train + eval scripted; serving inconsistent or unversioned |
| 3 | Reproducible train/eval; serving works but lacks version pinning |
| 4 | Versioned artifacts; model registry consistent; serving smoke tests pass in CI |
| 5 | Full E2E gate in CI; reproducibility signed off; rollback procedure documented |

**Required evidence**: `dvc repro` or equivalent produces identical artifacts across runs;
model registry shows versioned entries; serving smoke test in CI green.

---

### 3 · Agent Orchestration & Cognitive Brain Reliability — 12 %

**Intent**: The Cognitive Brain and multi-agent system operate predictably, log decisions,
enforce policies, and recover from failures without human intervention.

| Score | Description |
|-------|-------------|
| 0 | Agents unstable or require manual invocation |
| 1 | Basic orchestration demonstrated; no policy enforcement |
| 2 | Orchestration works; fallback paths absent |
| 3 | Policy-driven routing; partial fallback; outcomes partially monitored |
| 4 | Deterministic fallbacks; compliance logs collected; OKR tracking active |
| 5 | Success/fallback/recovery metrics gated in CI; policy violations alert within SLA |

**Required evidence**: orchestration success-rate metric > 95 %; policy compliance log;
automated recovery demonstrated in integration tests.

---

### 4 · RAG Quality & Freshness — 10 %

**Intent**: The retrieval-augmented generation pipeline serves current, relevant content
within defined SLAs; staleness and quality degradation are detected automatically.

| Score | Description |
|-------|-------------|
| 0 | Index stale; no quality measurement |
| 1 | Index built; no scheduled refresh |
| 2 | Periodic refresh; relevance untested |
| 3 | Nightly/scheduled refresh; manual spot-checks |
| 4 | Freshness SLA defined; retrieval quality metric collected; drift alerts configured |
| 5 | Freshness and quality gates enforced in CI; alerts fire to on-call within SLA |

**Required evidence**: freshness job green in last 24 h; retrieval benchmark score above
threshold; drift alert configured and tested.

---

### 5 · Security Posture (Code, Deps, Secrets, Runtime) — 14 %

**Intent**: Zero open critical/high findings; vulnerabilities are detected, tracked, and
remediated within defined SLAs; hardened defaults prevent introduction of new issues.

| Score | Description |
|-------|-------------|
| 0 | Critical findings unresolved; no scanning |
| 1 | Scans exist but rarely run |
| 2 | Regular scans; remediation ad hoc |
| 3 | Scans gate PRs; critical/high backlog tracked |
| 4 | Zero open criticals; MTTR tracked; hardened defaults (e.g., defusedxml, filelock) |
| 5 | MTTR SLA enforced; supply-chain provenance; dependency pinning CI-gated |

**Required evidence**: CodeQL/SAST/secret-scan all green; zero open critical alerts;
MTTR metric reported; dependency allowlist enforced.

---

### 6 · CI/CD Health & Workflow Governance — 12 %

**Intent**: CI passes reliably and quickly; workflows are owned, documented, and policy-
compliant; flaky tests are tracked and eliminated.

| Score | Description |
|-------|-------------|
| 0 | Frequent red pipelines; no governance |
| 1 | CI sometimes green; many orphan workflows |
| 2 | CI mostly green; workflows not consolidated |
| 3 | Green most of the time; flake tracked; compliance checks run |
| 4 | < 2 % flake rate; median run < 5 min; compliance gate blocks PRs |
| 5 | Flake eliminated; full cache utilisation; cost budgeted; all workflows owned |

**Required evidence**: 7-day pass-rate ≥ 95 %; flake report; workflow compliance
report green; median runtime in budget.

---

### 7 · Test System Maturity — 10 %

**Intent**: The test suite is trusted, deterministic, and risk-weighted; critical code paths
have integration tests; coverage ratchet prevents regression.

| Score | Description |
|-------|-------------|
| 0 | Low-trust tests; coverage unknown |
| 1 | Unit tests exist; integration tests absent |
| 2 | Broad unit coverage; integration tests intermittent |
| 3 | Coverage ≥ 80 %; integration tests run in CI; some flake |
| 4 | Coverage ≥ 90 %; pyramid balanced; flake rate < 1 % |
| 5 | Coverage ratchet enforced; critical-path integration tests gated; mutation score tracked |

**Required evidence**: coverage report ≥ 90 % on critical paths; integration test suite
green; flake metric < 1 %; coverage ratchet blocks regression.

---

### 8 · Observability & Operational Telemetry — 6 %

**Intent**: Actionable dashboards and runbooks exist for all production surfaces; SLOs are
defined; alerts fire to the right person within the SLA.

| Score | Description |
|-------|-------------|
| 0 | Little or no visibility |
| 1 | Some logs; no dashboards |
| 2 | Partial dashboards; alerts not configured |
| 3 | Dashboards for key services; alerts partially configured |
| 4 | SLOs defined; alerts configured; runbooks drafted |
| 5 | All critical surfaces have SLO dashboards; runbooks tested; MTTD/MTTR tracked |

**Required evidence**: SLO dashboard for ML serving, RAG, and agent orchestration;
alert runbooks reviewed; MTTD metric reported.

---

### 9 · Documentation & Developer Experience — 6 %

**Intent**: A new contributor can onboard in under one hour using documented steps;
all documentation is fresh, linked, and tested.

| Score | Description |
|-------|-------------|
| 0 | Outdated or missing docs |
| 1 | Some docs; not maintained |
| 2 | Core docs present; links broken; no freshness check |
| 3 | Docs broadly current; link-checker runs; some stale pages |
| 4 | Freshness gate in CI; onboarding checklist validated; all links pass |
| 5 | Docs, tests, and workflows aligned; onboarding time measured; feedback loop active |

**Required evidence**: doc-freshness gate green; link-checker passing; onboarding
checklist validated by a recent contributor.

---

### 10 · Performance & Cost Efficiency — 5 %

**Intent**: Resource usage is measured and budgeted; performance regressions are caught
in CI; cache and infrastructure costs are tracked.

| Score | Description |
|-------|-------------|
| 0 | No performance or cost visibility |
| 1 | Ad hoc benchmarks only |
| 2 | Benchmark suite exists; not automated |
| 3 | Benchmarks run in CI; cost informally monitored |
| 4 | Regression gate blocks PRs; cost budget defined; cache hit ratio reported |
| 5 | P50/P99 latency gated; cost trends reported weekly; cache efficiency ≥ 90 % |

**Required evidence**: benchmark regression gate green; CI cost report; cache-hit
ratio metric ≥ 90 %.

---

### 11 · Release / Versioning / Supply-Chain Integrity — 5 %

**Intent**: Releases are reproducible, signed, and accompanied by a complete SBOM;
the supply chain is auditable from source to published artifact.

| Score | Description |
|-------|-------------|
| 0 | Manual, unreliable releases |
| 1 | Release script exists; not gated |
| 2 | Repeatable release; no signing or SBOM |
| 3 | SBOM generated; release checklist used |
| 4 | Artifacts signed; provenance verified; release gate enforced |
| 5 | Signed artifacts + SBOM + provenance attestation; release blocked on rubric gate |

**Required evidence**: signed release artifact; SBOM in release; Sigstore or similar
provenance; release gate green.

---

## Scoring Script

Use `scripts/ci/score_completion.py` to compute the weighted total from a YAML scores file:

```bash
python scripts/ci/score_completion.py --scores .codex/completion_scores.yaml
```

Example `completion_scores.yaml`:

```yaml
architecture: 4
ml_lifecycle: 3
agent_orchestration: 4
rag_quality: 4
security: 5
cicd_health: 4
test_maturity: 4
observability: 4
documentation: 4
performance: 2
release_integrity: 2
```

---

## Change Log

| Date | Version | Change |
|------|---------|--------|
| 2026-05-27 | 1.1.0 | Updated example YAML to current scores (76.4 %); bumped band to "Operational but needs hardening" |
| 2026-05-27 | 1.0.0 | Initial version |
