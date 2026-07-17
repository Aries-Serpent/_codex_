# High-Risk Workflows Quick Reference
**Last Updated:** 2026-07-11
**Version:** v0.2.0

## Quick Lookup by File Reference Type

### By Configuration File

#### pyproject.toml (41 workflows)

### *.xml (1 workflows)
- coverage-with-timeout.yml

### .codex/ (86 workflows)
- adaptive-agent-delegation.yml
- admin-action-t03.yml
- admin_setup_verification.yml
- agent-auth-delegation.yml
- agent-handoff-gate.yml
- agent-health-check.yml
- agent-orchestration-unified.yml
- agent-registry-validation.yml
- agent-var-writer.yml
- agent_infrastructure_manager.yml
- ... and 76 more

### .github/docs/ (2 workflows)
- agent-auth-delegation.yml
- session-watchdog.yml

### .github/workflows/ (55 workflows)
- actionlint-audit.yml
- admin-action-t03.yml
- admin_setup_verification.yml
- agent-auth-delegation.yml
- agent-handoff-gate.yml
- auth-tests.yml
- auto-fix-common-issues.yml
- auto-fix-pr-check.yml
- batch-ci-triage.yml
- branch-divergence-monitor.yml
- ... and 45 more

### .mypy_baseline (2 workflows)
- ci-pattern-prevention-gate.yml
- mypy-baseline.yml

### Cargo.lock (1 workflows)
- rust_swarm_ci.yml

### Cargo.toml (1 workflows)
- rust_swarm_ci.yml

### Dockerfile (4 workflows)
- build-preview-image.yml
- container-scan.yml
- docker-build-push.yml
- scheduled-dependency-audit.yml

### README.md (6 workflows)
- app-package-download.yml
- automated-rollback-generation.yml
- docs-code-alignment.yml
- documentation-link-checker.yml
- root-org-validation.yml
- scheduled-archival.yml

### conftest.py (1 workflows)
- pre-flight-validation.yml

### coverage.json (3 workflows)
- auth-tests.yml
- code-quality-coverage-suite.yml
- resilient_validation.yml

### mkdocs.yml (8 workflows)
- codex-manifest-refresh.yml
- docs-health.yml
- pages-health-guard.yml
- pages-mkdocs.yml
- pages-pre-merge-validation.yml
- pages-scheduled-validation.yml
- root-org-validation.yml
- unified-deployment.yml

### mypy.ini (2 workflows)
- ci-pattern-prevention-gate.yml
- mypy-baseline.yml

### noxfile.py (1 workflows)
- auto-fix-pr-check.yml

### package-lock.json (2 workflows)
- har-capture.yml
- unified-deployment.yml

### package.json (3 workflows)
- pages-mkdocs.yml
- pages-pre-merge-validation.yml
- pages-scheduled-validation.yml

### pyproject.toml (18 workflows)
- agent_infrastructure_manager.yml
- auto-fix-pr-check.yml
- build-agent-env-cache.yml
- build-preview-image.yml
- chatops_copilot_trigger.yml
- ci-checkpoint-validation.yml
- copilot-iterative-self-healing.yml
- copilot-setup-steps.yml
- coverage-ratchet.yml
- mypy-baseline.yml
- ... and 8 more

### pytest.ini (1 workflows)
- pre-flight-validation.yml

### requirements-dev.txt (7 workflows)
- agent-health-check.yml
- ml-lifecycle-gate.yml
- mutation-testing.yml
- rag-quality-nightly.yml
- scheduled-dependency-audit.yml
- slo-canary-check.yml
- test-pyramid-report.yml

### requirements-eval.txt (1 workflows)
- ci-checkpoint-validation.yml

### requirements-test.txt (1 workflows)
- auth-tests.yml

### requirements.txt (5 workflows)
- app-package-download.yml
- dependabot-preflight.yml
- restore-pipeline-ci.yml
- scheduled-dependency-audit.yml
- sigstore-verify.yml

### setup.py (2 workflows)
- auth-tests.yml
- validate-token-health.yml

### tests/ (30 workflows)
- auth-tests.yml
- auto-fix-common-issues.yml
- auto-fix-pr-check.yml
- automated-post-deployment-verification.yml
- autonomy-phase-ci-matrix.yml
- chatops_copilot_trigger.yml
- code-quality-coverage-suite.yml
- codex-master-key-validation.yml
- copilot-agent-checkin.yml
- copilot-evolution-suite.yml
- ... and 20 more

### uv.lock (2 workflows)
- optimized-ci.yml
- sigstore-verify.yml
