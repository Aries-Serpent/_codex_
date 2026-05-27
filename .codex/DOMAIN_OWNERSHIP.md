# Domain Ownership Map

**Domain**: D1 — Architecture & Layer Boundaries  
**Owner**: `code-analysis-agent`  
**Last updated**: 2026-05-27

---

## Purpose

This document maps each GitHub Actions workflow to its owning domain/team.
It is consumed by `scripts/ci/workflow_owner_audit.py` to compute owner
coverage metrics (D6 exit criteria).

---

## Workflow Ownership

| Workflow | Domain | Owner Agent |
|----------|--------|------------|
| `workflow-compliance-gate.yml` | D6 CI/CD Health | `workflow-compliance-guardian` |
| `ci-pass-rate-gate.yml` | D6 CI/CD Health | `workflow-health-monitor` |
| `coverage-ratchet.yml` | D5 Test Coverage | `unified-coverage-agent` |
| `mutation-testing.yml` | D5 Test Coverage | `mutation-testing-agent` |
| `rag-quality-nightly.yml` | D4 RAG Quality | `rag-index-manager` |
| `ml-lifecycle-gate.yml` | D2 ML Lifecycle | `ml-validation-suite-agent` |
| `performance-gate.yml` | D2 ML Lifecycle | `performance-monitor-agent` |
| `slo-canary-check.yml` | D6 CI/CD Health | `performance-monitor-agent` |
| `agent-health-check.yml` | D3 Agent Autonomy | `codebase-health-guardian` |
| `test-pyramid-report.yml` | D5 Test Coverage | `unified-coverage-agent` |
| `docs-code-alignment.yml` | D1 Architecture | `doc-freshness-checker` |
| `release.yml` | D2 ML Lifecycle | `pypi-publishing-operations-agent` |
| `sbom.yml` | D2 ML Lifecycle | `dependency-security-review-agent` |
| `pre-merge-validation.yml` | D6 CI/CD Health | `ci-testing-agent` |
| `validate.yml` | D6 CI/CD Health | `ci-testing-agent` |
| `security-scanning-suite.yml` | D7 Security | `unified-security-scanner` |
| `codeql-analysis.yml` | D7 Security | `codeql-alert-resolution-agent` |
| `nightly-codeql-alert-triage.yml` | D7 Security | `security-alert-verification-agent` |

---

## Coverage Summary

- **Total workflows audited**: see `scripts/ci/workflow_owner_audit.py` output
- **Ownership threshold**: ≥ 80 % of active workflows must have declared owners
- **Last audit**: 2026-05-27

---

*Update this file whenever a new workflow is added or ownership changes.*
