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

## Domain Escalation Contacts

| Domain | Code | Description | Escalation Agent | Fallback Contact |
|--------|------|-------------|------------------|-----------------|
| Architecture & Layer Boundaries | D1 | Import contracts, layer isolation | `code-analysis-agent` | `orchestrator-agent` |
| ML Lifecycle | D2 | Training, serving, registry, reproducibility | `ml-validation-suite-agent` | `performance-monitor-agent` |
| Agent Autonomy | D3 | Agent health, orchestration compliance | `codebase-health-guardian` | `orchestrator-agent` |
| RAG Quality | D4 | Retrieval accuracy, freshness, drift | `rag-index-manager` | `rag-freshness-loop-agent` |
| Test Coverage | D5 | Coverage thresholds, mutation score | `unified-coverage-agent` | `test-enhancement-agent` |
| CI/CD Health | D6 | Workflow compliance, pass rates, SLOs | `workflow-compliance-guardian` | `ci-testing-agent` |
| Security | D7 | CodeQL, secrets scanning, SAST | `unified-security-scanner` | `security-audit-agent` |

---

## Workflow Ownership

| Workflow | Domain | Owner Agent | Escalation |
|----------|--------|------------|------------|
| `workflow-compliance-gate.yml` | D6 CI/CD Health | `workflow-compliance-guardian` | `ci-testing-agent` |
| `ci-pass-rate-gate.yml` | D6 CI/CD Health | `workflow-health-monitor` | `ci-testing-agent` |
| `coverage-ratchet.yml` | D5 Test Coverage | `unified-coverage-agent` | `test-enhancement-agent` |
| `mutation-testing.yml` | D5 Test Coverage | `mutation-testing-agent` | `unified-coverage-agent` |
| `rag-quality-nightly.yml` | D4 RAG Quality | `rag-index-manager` | `rag-freshness-loop-agent` |
| `ml-lifecycle-gate.yml` | D2 ML Lifecycle | `ml-validation-suite-agent` | `performance-monitor-agent` |
| `performance-gate.yml` | D2 ML Lifecycle | `performance-monitor-agent` | `ml-validation-suite-agent` |
| `slo-canary-check.yml` | D6 CI/CD Health | `performance-monitor-agent` | `workflow-health-monitor` |
| `agent-health-check.yml` | D3 Agent Autonomy | `codebase-health-guardian` | `orchestrator-agent` |
| `test-pyramid-report.yml` | D5 Test Coverage | `unified-coverage-agent` | `test-pattern-guardian` |
| `docs-code-alignment.yml` | D1 Architecture | `doc-freshness-checker` | `unified-doc-agent` |
| `release.yml` | D2 ML Lifecycle | `pypi-publishing-operations-agent` | `ml-validation-suite-agent` |
| `sbom.yml` | D2 ML Lifecycle | `dependency-security-review-agent` | `unified-security-scanner` |
| `pre-merge-validation.yml` | D6 CI/CD Health | `ci-testing-agent` | `workflow-compliance-guardian` |
| `validate.yml` | D6 CI/CD Health | `ci-testing-agent` | `workflow-compliance-guardian` |
| `security-scanning-suite.yml` | D7 Security | `unified-security-scanner` | `security-audit-agent` |
| `codeql-analysis.yml` | D7 Security | `codeql-alert-resolution-agent` | `unified-security-scanner` |
| `nightly-codeql-alert-triage.yml` | D7 Security | `security-alert-verification-agent` | `codeql-alert-resolution-agent` |
| `import-linter.yml` | D1 Architecture | `code-analysis-agent` | `orchestrator-agent` |
| `actionlint-audit.yml` | D6 CI/CD Health | `workflow-compliance-guardian` | `ci-testing-agent` |

---

## Coverage Summary

- **Total workflows audited**: see `scripts/ci/workflow_owner_audit.py` output
- **Ownership threshold**: ≥ 80 % of active workflows must have declared owners
- **Last audit**: 2026-05-27

---

*Update this file whenever a new workflow is added or ownership changes.*
