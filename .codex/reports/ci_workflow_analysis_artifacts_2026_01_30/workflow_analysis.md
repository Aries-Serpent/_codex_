# GitHub Actions Workflow Analysis Report

**Generated**: Auto-analysis of `.github/workflows/`
**Repository**: `Aries-Serpent/_codex_`

## 📊 Executive Summary

- **Total Workflows**: 116
- **Active Workflows**: 101
- **Guarded Workflows**: 0 (if: false or disabled)
- **Archived Workflows**: 15 (.disabled, .alt, .tombstone)
- **Parse Errors**: 1
- **Unique Secrets**: 19

## 🖥️ Runner Types in Use

- `${{ fromJSON(vars.RUNS_ON || '["self-hosted","linux"]') }}`: 1 workflows
- `${{ matrix.os }}`: 1 workflows
- `linux`: 2 workflows
- `self-hosted`: 2 workflows
- `ubuntu-latest`: 98 workflows

## 🔧 Most Used GitHub Actions

- `actions/checkout`: 97 workflows
- `actions/upload-artifact`: 37 workflows
- `actions/github-script`: 22 workflows
- `actions/setup-python`: 13 workflows
- `actions/download-artifact`: 9 workflows
- `actions/setup-node`: 7 workflows
- `actions/cache`: 7 workflows
- `github/codeql-action/upload-sarif`: 4 workflows
- `codecov/codecov-action`: 4 workflows
- `github/codeql-action/analyze`: 4 workflows
- `github/codeql-action/init`: 4 workflows
- `actions/deploy-pages`: 3 workflows
- `actions/upload-pages-artifact`: 3 workflows
- `dtolnay/rust-toolchain`: 2 workflows
- `peter-evans/create-pull-request`: 2 workflows

## 📋 Detailed Workflow Analysis

| Workflow | Status | Jobs | Triggers | Runner | Secrets | Dependencies | Priority |
|----------|--------|------|----------|--------|---------|--------------|----------|
| aftermath.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | None | ⚪ Unknown |
| agent-runtime.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | None | ⚪ Unknown |
| api-documentation.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | None | 🟢 Low |
| artifact-monitoring.yml | ✅ Active | 1 |  | ubuntu-latest | 2 | None | 🟡 Medium |
| audit-improvement-pipeline.yml | ✅ Active | 3 |  | ubuntu-latest | 0 | pytest | 🟡 Medium |
| auth-compliance-report.yml | ✅ Active | 1 |  | ubuntu-latest | 3 | None | ⚪ Unknown |
| auth-mfa-enrollment.yml | ✅ Active | 1 |  | ubuntu-latest | 2 | None | ⚪ Unknown |
| auth-oauth-app-sync.yml | ✅ Active | 1 |  | ubuntu-latest | 4 | None | ⚪ Unknown |
| auth-secret-rotation.yml | ✅ Active | 1 |  | ubuntu-latest | 5 | None | ⚪ Unknown |
| auth-security-audit.yml | ✅ Active | 2 |  | ubuntu-latest | 0 | None | 🔴 Critical |
| auth-tests.yml | ✅ Active | 2 |  | ubuntu-latest | 1 | pytest | 🔴 Critical |
| auth-token-rotation.yml | ✅ Active | 1 |  | ubuntu-latest | 3 | None | ⚪ Unknown |
| auto-update-configs.yml | ✅ Active | 1 |  | ubuntu-latest | 1 | None | ⚪ Unknown |
| autonomous-agent.yml | ✅ Active | 2 |  | ubuntu-latest | 1 | None | ⚪ Unknown |
| batch-ci-triage.yml | ✅ Active | 1 |  | ubuntu-latest | 1 | None | 🔴 Critical |
| biweekly-research-digest.yml | ✅ Active | 1 |  | ubuntu-latest | 1 | None | ⚪ Unknown |
| build-chatgpt-package.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | None | 🟠 High |
| cache-cleanup.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | None | 🟢 Low |
| cache-management.yml | ✅ Active | 3 |  | ubuntu-latest | 0 | None | 🟢 Low |
| cache-suite.yml | ✅ Active | 5 | schedule, workflow_dispatch... | ubuntu-latest | 0 | pytest | 🟢 Low |
| cache-warmup.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | None | 🟢 Low |
| ci-diagnostic-automation.yml | ✅ Active | 1 |  | ubuntu-latest | 1 | None | 🔴 Critical |
| ci-health-monitor.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | None | 🔴 Critical |
| ci-health-suite.yml | ✅ Active | 5 | schedule, workflow_dispatch... | ubuntu-latest | 0 | None | 🔴 Critical |
| code-quality.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | None | ⚪ Unknown |
| codebase-qa-walkthrough.yml | ✅ Active | 2 |  | ubuntu-latest | 1 | pytest | ⚪ Unknown |
| codeql-analysis.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | None | ⚪ Unknown |
| codeql-chunked.yml | ✅ Active | 4 |  | ubuntu-latest | 0 | None | ⚪ Unknown |
| cognitive-action.yml | ✅ Active | 1 |  | ubuntu-latest | 1 | None | ⚪ Unknown |
| cognitive-aftermath.yml | ✅ Active | 1 |  | ubuntu-latest | 1 | None | ⚪ Unknown |
| cognitive-decision.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | None | 🔴 Critical |
| cognitive-perception.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | None | ⚪ Unknown |
| copilot-cascade-review.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | None | ⚪ Unknown |
| copilot-self-evolution.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | None | ⚪ Unknown |
| copilot-setup-steps.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | pytest | ⚪ Unknown |
| coverage_report.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | pytest | ⚪ Unknown |
| data_validation.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | None | ⚪ Unknown |
| decode-validate-artifact.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | None | ⚪ Unknown |
| dependency-scan.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | None | 🟡 Medium |
| deploy-cognitive-app.yml | ✅ Active | 2 |  | ubuntu-latest | 0 | None | 🟠 High |
| detect-duplicates.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | None | ⚪ Unknown |
| determinism.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | Docker, pytest | ⚪ Unknown |
| docker-build-push.yml | ✅ Active | 3 |  | linux | 1 | Docker | 🟠 High |
| documentation-link-checker.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | None | 🟢 Low |
| documentation-suite.yml | ✅ Active | 4 | push, pull_request... | ubuntu-latest | 0 | None | 🟢 Low |
| draft-audit-pr.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | None | 🟡 Medium |
| flatten-repo-download.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | pytest | ⚪ Unknown |
| generate-repository-structure.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | None | ⚪ Unknown |
| genesis-bootstrap.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | None | ⚪ Unknown |
| html_visual_baseline.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | None | ⚪ Unknown |
| html_visual_regression.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | None | ⚪ Unknown |
| integration-gated.yml | ✅ Active | 2 |  | ubuntu-latest | 1 | None | ⚪ Unknown |
| labeler.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | None | ⚪ Unknown |
| monthly-model-retraining.yml | ✅ Active | 1 |  | ubuntu-latest | 1 | None | ⚪ Unknown |
| notebooklm-sync.yml | ✅ Active | 1 |  | ubuntu-latest | 3 | None | ⚪ Unknown |
| nox_gates.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | nox | ⚪ Unknown |
| optimized-ci.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | None | 🔴 Critical |
| pages-mkdocs.yml | ✅ Active | 2 |  | ubuntu-latest | 0 | None | 🟢 Low |
| phase10-automated-secrets-setup.yml | ✅ Active | 1 |  | ubuntu-latest | 1 | None | ⚪ Unknown |
| phase34-codeql-alert-fetch.yml | ✅ Active | 1 |  | ubuntu-latest | 1 | None | ⚪ Unknown |
| post-merge-validation-optimized.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | None | ⚪ Unknown |
| pr-checks.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | uv, pytest | 🔴 Critical |
| pr-followup-generator.yml | ✅ Active | 1 |  | ubuntu-latest | 1 | None | ⚪ Unknown |
| pre-release-deployment.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | None | 🟠 High |
| publish_dashboard_release.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | None | 🟠 High |
| pypi-publish.yml | ✅ Active | 4 |  | ubuntu-latest | 1 | None | 🟠 High |
| ratelimit_history_prune.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | None | ⚪ Unknown |
| repo-organization.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | None | ⚪ Unknown |
| repository-health-monitoring.yml | ✅ Active | 1 |  | ubuntu-latest | 1 | None | 🟡 Medium |
| root-org-validation.yml | ✅ Active | 4 |  | ubuntu-latest | 0 | pytest | ⚪ Unknown |
| runner-diagnostics.yml | ✅ Active | 1 |  | ${{ fromJSON(vars.RUNS_ON || '["self-hosted","linux"]') }} | 0 | Docker | ⚪ Unknown |
| rust_swarm_ci.yml | ✅ Active | 9 |  | ${{ matrix.os }} | 2 | Docker, pytest | 🔴 Critical |
| sbom.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | None | ⚪ Unknown |
| scan-secrets-variables.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | None | 🟡 Medium |
| scheduled-archival.yml | ✅ Active | 3 |  | ubuntu-latest | 0 | None | ⚪ Unknown |
| scheduled-dependency-audit.yml | ✅ Active | 5 |  | ubuntu-latest | 0 | Docker | 🟡 Medium |
| security-alert-notification.yml | ✅ Active | 1 |  | ubuntu-latest | 1 | None | 🔴 Critical |
| security-scan.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | Docker | 🔴 Critical |
| security-scanning-suite.yml | ✅ Active | 5 | push, pull_request... | ubuntu-latest | 0 | None | 🔴 Critical |
| security-suite.yml | ✅ Active | 5 |  | ubuntu-latest | 2 | None | 🔴 Critical |
| security-tools-bootstrap.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | None | 🔴 Critical |
| self-healing-ci.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | None | 🔴 Critical |
| self-healing-feedback-loop.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | None | ⚪ Unknown |
| self-healing.yml | ✅ Active | 5 |  | ubuntu-latest | 1 | None | ⚪ Unknown |
| semgrep_sarif.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | None | ⚪ Unknown |
| status_gate.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | None | ⚪ Unknown |
| sync-env-vars.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | None | ⚪ Unknown |
| template_lint.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | None | ⚪ Unknown |
| test-analytics-failure-sim.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | None | 🔴 Critical |
| test-comprehensive.yml | ✅ Active | 2 |  | ubuntu-latest | 1 | Docker, pytest | 🔴 Critical |
| test-rag.yml | ✅ Active | 1 | push, pull_request | ubuntu-latest | 1 | Docker, pytest | 🔴 Critical |
| token-rotation.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | None | ⚪ Unknown |
| validate-secrets-documentation.yml | ✅ Active | 1 |  | ubuntu-latest | 1 | None | 🟢 Low |
| wiki-assemble.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | None | 🟢 Low |
| workflow-analytics-manual.yml | ✅ Active | 1 |  | ubuntu-latest | 1 | None | ⚪ Unknown |
| workflow-analytics-scheduled.yml | ✅ Active | 1 |  | ubuntu-latest | 1 | None | ⚪ Unknown |
| workflow-expiry-enforcer.yml | ✅ Active | 1 |  | linux | 0 | None | ⚪ Unknown |
| workflow-link-validation.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | None | ⚪ Unknown |
| workflow-restore.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | None | ⚪ Unknown |
| zendesk-knowledge-sync.yml | ✅ Active | 1 |  | ubuntu-latest | 6 | None | ⚪ Unknown |
| zendesk-quantum-packaging.yml | ✅ Active | 1 |  | ubuntu-latest | 0 | None | ⚪ Unknown |

## 🗄️ Archived/Disabled Workflows

- `archive-gates.yml.disabled`
- `ci-pytest.yml.disabled`
- `ci.yml.disabled`
- `comprehensive_tests.yml.disabled`
- `ml-tests.yml.disabled`
- `multi-python-ci.yml.disabled`
- `pages-static.yml.alt`
- `pages_publish_tiles.yml.tombstone`
- `secrets_baseline_check.yml.disabled`
- `security-scanning.yml.disabled`
- `security.yml.disabled`
- `security_gates.yml.disabled`
- `security_policy_gate.yml.disabled`
- `tests.yml.disabled`
- `validate.yml.disabled`

## ⚠️ Parse Errors

- **test-suite.yml**: YAML parse error: while scanning a simple key
  in "<unicode string>", line 178, column 1:
    import xml.etree.ElementTree as ET
    ^
could not find expected ':'
  in "<unicode string>", line 179, column 1:
    try:
    ^

## 🔐 Secrets Usage Analysis

| Secret Name | Used In | Count |
|-------------|---------|-------|
| `AWS_ACCESS_KEY_ID` | zendesk-knowledge-sync.yml | 1 |
| `AWS_SECRET_ACCESS_KEY` | zendesk-knowledge-sync.yml | 1 |
| `CODECOV_TOKEN` | test-comprehensive.yml, auth-tests.yml, rust_swarm_ci.yml, ... (+1 more) | 4 |
| `CODEX_MASTER_KEY` | auth-secret-rotation.yml, auth-token-rotation.yml, auth-oauth-app-sync.yml, ... (+3 more) | 6 |
| `COMPLIANCE_REPORT_KEY` | auth-compliance-report.yml | 1 |
| `ENABLE_LIVE_TESTS` | integration-gated.yml | 1 |
| `GDRIVE_SERVICE_ACCOUNT_JSON` | notebooklm-sync.yml | 1 |
| `GITHUB_OAUTH_CLIENT_ID` | auth-oauth-app-sync.yml | 1 |
| `GITHUB_OAUTH_CLIENT_SECRET` | auth-secret-rotation.yml, auth-oauth-app-sync.yml | 2 |
| `GITHUB_TOKEN` | self-healing.yml, phase10-automated-secrets-setup.yml, security-alert-notification.yml, ... (+25 more) | 28 |
| `GITLEAKS_LICENSE` | security-suite.yml | 1 |
| `GOOGLE_CLIENT_SECRET` | notebooklm-sync.yml | 1 |
| `NOTEBOOKLM_WEBHOOK_URL` | notebooklm-sync.yml | 1 |
| `SESSION_ENCRYPTION_KEY` | auth-secret-rotation.yml | 1 |
| `TEST_PYPI_API_TOKEN` | pypi-publish.yml | 1 |
| `TOKEN_SECRET_KEY` | auth-secret-rotation.yml, auth-token-rotation.yml | 2 |
| `ZENDESK_TOKEN` | zendesk-knowledge-sync.yml | 1 |
| `ZENDESK_URL` | zendesk-knowledge-sync.yml | 1 |
| `ZENDESK_USER` | zendesk-knowledge-sync.yml | 1 |

## 💰 Resource Requirements by Category

### AI & Automation (8 workflows)

- ✅ **agent-runtime.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **autonomous-agent.yml**
  - Runners: ubuntu-latest
  - Jobs: 2
  - Triggers: 
- ✅ **cognitive-action.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **cognitive-aftermath.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **cognitive-perception.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **copilot-cascade-review.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **copilot-self-evolution.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **copilot-setup-steps.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 

### Authentication (7 workflows)

- ✅ **auth-compliance-report.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **auth-mfa-enrollment.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **auth-oauth-app-sync.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **auth-secret-rotation.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **auth-token-rotation.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **phase10-automated-secrets-setup.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **token-rotation.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 

### Build & Deploy (6 workflows)

- ✅ **build-chatgpt-package.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **deploy-cognitive-app.yml**
  - Runners: ubuntu-latest
  - Jobs: 2
  - Triggers: 
- ✅ **docker-build-push.yml**
  - Runners: linux, self-hosted
  - Jobs: 3
  - Triggers: 
- ✅ **pre-release-deployment.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **publish_dashboard_release.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **pypi-publish.yml**
  - Runners: ubuntu-latest
  - Jobs: 4
  - Triggers: 

### Documentation (6 workflows)

- ✅ **api-documentation.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **documentation-link-checker.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **documentation-suite.yml**
  - Runners: ubuntu-latest
  - Jobs: 4
  - Triggers: push, pull_request, workflow_dispatch, workflow_call
- ✅ **pages-mkdocs.yml**
  - Runners: ubuntu-latest
  - Jobs: 2
  - Triggers: 
- ✅ **validate-secrets-documentation.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **wiki-assemble.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 

### Maintenance (5 workflows)

- ✅ **cache-cleanup.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **cache-management.yml**
  - Runners: ubuntu-latest
  - Jobs: 3
  - Triggers: 
- ✅ **cache-suite.yml**
  - Runners: ubuntu-latest
  - Jobs: 5
  - Triggers: schedule, workflow_dispatch, workflow_call
- ✅ **cache-warmup.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **scheduled-archival.yml**
  - Runners: ubuntu-latest
  - Jobs: 3
  - Triggers: 

### Monitoring (3 workflows)

- ✅ **artifact-monitoring.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **repository-health-monitoring.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **runner-diagnostics.yml**
  - Runners: ${{ fromJSON(vars.RUNS_ON || '["self-hosted","linux"]') }}
  - Jobs: 1
  - Triggers: 

### Other (41 workflows)

- ✅ **aftermath.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **audit-improvement-pipeline.yml**
  - Runners: ubuntu-latest
  - Jobs: 3
  - Triggers: 
- ✅ **auto-update-configs.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **biweekly-research-digest.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **code-quality.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **codebase-qa-walkthrough.yml**
  - Runners: ubuntu-latest
  - Jobs: 2
  - Triggers: 
- ✅ **coverage_report.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **data_validation.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **decode-validate-artifact.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **detect-duplicates.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **determinism.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **draft-audit-pr.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **flatten-repo-download.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **generate-repository-structure.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **genesis-bootstrap.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **html_visual_baseline.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **html_visual_regression.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **integration-gated.yml**
  - Runners: ubuntu-latest
  - Jobs: 2
  - Triggers: 
- ✅ **labeler.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **monthly-model-retraining.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **notebooklm-sync.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **nox_gates.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **post-merge-validation-optimized.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **pr-followup-generator.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **ratelimit_history_prune.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **repo-organization.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **root-org-validation.yml**
  - Runners: ubuntu-latest
  - Jobs: 4
  - Triggers: 
- ✅ **sbom.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **scheduled-dependency-audit.yml**
  - Runners: ubuntu-latest
  - Jobs: 5
  - Triggers: 
- ✅ **self-healing-feedback-loop.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **self-healing.yml**
  - Runners: ubuntu-latest
  - Jobs: 5
  - Triggers: 
- ✅ **status_gate.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **sync-env-vars.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **template_lint.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **workflow-analytics-manual.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **workflow-analytics-scheduled.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **workflow-expiry-enforcer.yml**
  - Runners: linux, self-hosted
  - Jobs: 1
  - Triggers: 
- ✅ **workflow-link-validation.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **workflow-restore.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **zendesk-knowledge-sync.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **zendesk-quantum-packaging.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 

### Security (12 workflows)

- ✅ **auth-security-audit.yml**
  - Runners: ubuntu-latest
  - Jobs: 2
  - Triggers: 
- ✅ **codeql-analysis.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **codeql-chunked.yml**
  - Runners: ubuntu-latest
  - Jobs: 4
  - Triggers: 
- ✅ **dependency-scan.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **phase34-codeql-alert-fetch.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **scan-secrets-variables.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **security-alert-notification.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **security-scan.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **security-scanning-suite.yml**
  - Runners: ubuntu-latest
  - Jobs: 5
  - Triggers: push, pull_request, schedule, workflow_dispatch, workflow_call
- ✅ **security-suite.yml**
  - Runners: ubuntu-latest
  - Jobs: 5
  - Triggers: 
- ✅ **security-tools-bootstrap.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **semgrep_sarif.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 

### Testing & CI (13 workflows)

- ✅ **auth-tests.yml**
  - Runners: ubuntu-latest
  - Jobs: 2
  - Triggers: 
- ✅ **batch-ci-triage.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **ci-diagnostic-automation.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **ci-health-monitor.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **ci-health-suite.yml**
  - Runners: ubuntu-latest
  - Jobs: 5
  - Triggers: schedule, workflow_dispatch, workflow_call
- ✅ **cognitive-decision.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **optimized-ci.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **pr-checks.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **rust_swarm_ci.yml**
  - Runners: ${{ matrix.os }}, ubuntu-latest
  - Jobs: 9
  - Triggers: 
- ✅ **self-healing-ci.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **test-analytics-failure-sim.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: 
- ✅ **test-comprehensive.yml**
  - Runners: ubuntu-latest
  - Jobs: 2
  - Triggers: 
- ✅ **test-rag.yml**
  - Runners: ubuntu-latest
  - Jobs: 1
  - Triggers: push, pull_request
