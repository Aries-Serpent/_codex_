# ADR-20260302: Self-Healing CI Governance (Phases 5–6)
> Generated: 2026-06-22T07:00:00Z | Author: copilot-swe-agent[bot]
> Status: Accepted
> Related PRs: #3447

## 1. Context

Phases 1–4 of the Soft→GROUNDED conversion established the enforcement
infrastructure (schema, gates, embeddings, FSM). However, without ongoing
governance, these structures could regress:

- A Tier-1 workflow could be downgraded to Tier-2 without detection.
- Soft enforcement patterns (`::warning::` without `exit 1`) could be
  introduced in new workflows.
- CODEOWNERS entries for governance paths could be removed.
- Semgrep rules could be disabled without audit.

Phases 5 and 6 provide the self-healing and observability layer that
prevents structural regression.

## 2. Problem Statement

Establish automated detection and reporting for governance regressions
across CI workflows, enforcement tiers, and ownership controls, ensuring
that the GROUNDED state is maintained over time.

## 3. Decision

Implement a three-pillar governance backbone:

### Pillar 1: Actionlint Audit (Tier-1 GROUNDED)

`actionlint-audit.yml` validates all workflow files for:
- YAML syntax correctness
- GitHub Actions expression validity
- Shell script lint (via ShellCheck integration)
- Runs on every PR touching `.github/workflows/`
- Tier-1: `exit 1` on any finding

### Pillar 2: Semgrep Soft Enforcement Rules

`semgrep/soft_enforcement.yaml` defines 6 regression detection rules:

| Rule | Detects |
|------|---------|
| `soft-warning-without-exit` | `::warning::` in workflow without corresponding `exit 1` |
| `tier2-canary-annotation` | Leftover "Tier-2 canary" comments after promotion |
| `missing-concurrency-group` | Workflows without branch-scoped concurrency |
| `missing-timeout-minutes` | Jobs without `timeout-minutes` |
| `heredoc-in-run-block` | `<< 'EOF'` patterns in `run:` blocks (YAML conflict) |
| `bare-except-pass` | Python `except: pass` without logging |

### Pillar 3: Enforcement KPI Dashboard

`scripts/ci/enforcement_kpi_dashboard.py` generates a tier distribution
table from AGENT_REGISTRY.yaml:

```
Tier        Count  Percentage
──────────  ─────  ──────────
GROUNDED        8       5.3%
PARTIAL       142      93.4%
SOFT            2       1.3%
```

Integrated into `ci-health-monitor.yml` as a job summary step.

### Supporting Artifacts

| Artifact | Purpose |
|----------|---------|
| `.github/CODEOWNERS` | 12 entries covering all governance paths |
| `auto_promote_tier.py` | Dry-run tier promotion stub generator |
| `auto_append_accountability.py` | Appends accountability entries to reports |
| `docs/AGENTIC_REPO_SYSTEM_GUIDE.md` | Canonical 12-section operating reference |
| `docs/audits/AGENTIC_FINAL_KPI_REPORT.md` | Phase completion KPI report |

## 4. Decision Drivers

| Driver | Notes |
|--------|-------|
| Regression prevention | Phases 1–4 artifacts must not silently degrade |
| Observability | Tier distribution must be visible in CI summaries |
| Developer guardrails | Common mistakes (heredocs, missing timeouts) caught early |
| Ownership accountability | CODEOWNERS enforces review for governance changes |
| Self-healing | Detection rules enable automated fix suggestions |

## 5. Considered Alternatives

| Alternative | Rejected Because |
|-------------|------------------|
| Manual quarterly audits only | Regressions can merge between audits |
| Custom Python linter for workflows | Reinvents actionlint; maintenance burden |
| GitHub branch protection rules only | Cannot detect content-level regressions |
| Post-merge monitoring only | Allows regressions to reach main; harder to fix |
| Single monolithic governance workflow | Violates separation of concerns; hard to maintain |

## 6. Consequences

### Positive
- Workflow regressions are caught in PR CI before merge.
- Tier distribution is visible in every CI health report.
- CODEOWNERS prevents unauthorized governance changes.
- Semgrep rules are version-controlled and auditable.
- KPI dashboard provides quantitative governance metrics.

### Negative
- Additional CI execution time (~45 seconds for actionlint + semgrep).
- Semgrep rules may produce false positives for intentional patterns.
- CODEOWNERS requires `@Aries-Serpent/owners` availability for reviews.

### Risks & Mitigations
- **Risk**: Semgrep false positives block legitimate PRs.
  **Mitigation**: Rules use `severity: WARNING` (not `ERROR`); `# nosemgrep`
  inline suppression available for documented exceptions.
- **Risk**: Actionlint not installed in CI runner.
  **Mitigation**: Workflow includes `brew install actionlint` setup step.
- **Risk**: CODEOWNERS team membership changes.
  **Mitigation**: Organization-level team management; documented in
  `docs/admin/GENESIS_SETUP_GUIDE.md`.

## 7. Provenance & Compliance
- **Actionlint**: `.github/workflows/actionlint-audit.yml` (Tier-1 GROUNDED)
- **Semgrep**: `semgrep/soft_enforcement.yaml` (6 rules)
- **KPI dashboard**: `scripts/ci/enforcement_kpi_dashboard.py`
- **CODEOWNERS**: `.github/CODEOWNERS` (12 governance entries)
- **Operating guide**: `docs/AGENTIC_REPO_SYSTEM_GUIDE.md`
- **KPI report**: `docs/audits/AGENTIC_FINAL_KPI_REPORT.md`
- **Change log**: PR #3447 merged to main
