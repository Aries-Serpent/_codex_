# Workflow Inventory Summary

**Generated**: 2025-12-28T08:09:06.587779Z

**Total Workflows**: 66

## Workflows by Category

### Other (66 workflows)

- 🔴  `agent-runtime.yml` - N/A
- 🔴  `api-documentation.yml` - N/A
- 🔴  `audit-improvement-pipeline.yml` - N/A
- 🔴  `auto-update-configs.yml` - N/A
- 🔴 ⚠️ `automation_ingest.yml` - N/A
- 🔴  `autonomous-agent.yml` - N/A
- 🔴 ⚠️ `build-container-cache.yml` - N/A
- 🔴 ⚠️ `cache-cleanup.yml` - N/A
- 🔴 ⚠️ `cache-warmer.yml` - N/A
- 🔴  `code-quality.yml` - N/A
- 🔴  `codeql-analysis.yml` - N/A
- 🔴 ⚠️ `container-build.yml` - N/A
- 🔴  `copilot-cascade-review.yml` - N/A
- 🔴  `copilot-self-evolution.yml` - N/A
- 🔴  `coverage_report.yml` - N/A
- 🔴 ⚠️ `daily_status_cron.yml` - N/A
- 🔴 ⚠️ `daily_status_enrich.yml` - N/A
- 🔴  `data_validation.yml` - N/A
- 🔴  `decode-validate-artifact.yml` - N/A
- 🔴  `dependency-scan.yml` - N/A
- 🔴  `detect-duplicates.yml` - N/A
- 🔴  `determinism.yml` - N/A
- 🔴  `docker-build-push.yml` - N/A
- 🔴 ⚠️ `docs.yml` - N/A
- 🔴  `documentation-link-checker.yml` - N/A
- 🔴  `draft-audit-pr.yml` - N/A
- 🔴  `duplicate-detection-weekly.yml` - N/A
- 🔴  `genesis-bootstrap.yml` - N/A
- 🔴  `github_connector_check.yml` - N/A
- 🔴  `html_visual_baseline.yml` - N/A
- 🔴  `html_visual_regression.yml` - N/A
- 🔴  `integration-gated.yml` - N/A
- 🔴  `labeler.yml` - N/A
- 🔴 ⚠️ `mcp-ci.yml` - N/A
- 🔴  `nox_gates.yml` - N/A
- 🔴  `optimized-ci.yml` - N/A
- 🔴  `pages-mkdocs.yml` - N/A
- 🔴  `post-merge-validation-optimized.yml` - N/A
- 🔴  `post-merge-validation.yml` - N/A
- 🔴  `pr-checks.yml` - N/A
- 🔴  `pre-release-deployment.yml` - N/A
- 🔴 ⚠️ `produce-trend.yml` - N/A
- 🔴  `publish_dashboard_release.yml` - N/A
- 🔴  `ratelimit_history_prune.yml` - N/A
- 🔴  `repo-organization.yml` - N/A
- 🔴 ⚠️ `report_publish.yml` - N/A
- 🔴  `runner-diagnostics.yml` - N/A
- 🔴  `sbom.yml` - N/A
- 🔴  `scheduled-archival.yml` - N/A
- 🔴  `scheduled-dependency-audit.yml` - N/A
- 🔴  `security-scan.yml` - N/A
- 🔴  `security-suite.yml` - N/A
- 🔴  `self-healing-ci.yml` - N/A
- 🔴  `self-healing-feedback-loop.yml` - N/A
- 🔴  `semgrep_sarif.yml` - N/A
- 🔴  `status_gate.yml` - N/A
- 🔴 ⚠️ `template-validation.yml` - N/A
- 🔴  `template_lint.yml` - N/A
- 🔴 ⚠️ `test-suite.yml` - N/A
- 🔴 ⚠️ `validate-docs-enhanced.yml` - N/A
- 🔴 ⚠️ `validate-docs.yml` - N/A
- 🔴  `wiki-assemble.yml` - N/A
- 🔴  `workflow-expiry-enforcer.yml` - N/A
- 🔴 ⚠️ `workflow-lint.yml` - N/A
- 🔴 ⚠️ `workflow-validator.yml` - N/A
- 🔴  `zendesk-quantum-packaging.yml` - N/A

## Consolidation Candidates (17 workflows)

### `automation_ingest.yml`

**Reason**: Consolidated into single pipeline with job dependencies

**Will be replaced by**: daily-status-pipeline.yml, publish_dashboard_release.yml

### `build-container-cache.yml`

**Reason**: Unified container build with matrix strategy for CPU/GPU variants

**Will be replaced by**: docker-build-push.yml

### `cache-cleanup.yml`

**Reason**: Unified cache operations with scheduled jobs

**Will be replaced by**: cache-management.yml

### `cache-warmer.yml`

**Reason**: Unified cache operations with scheduled jobs

**Will be replaced by**: cache-management.yml

### `container-build.yml`

**Reason**: Unified container build with matrix strategy for CPU/GPU variants

**Will be replaced by**: docker-build-push.yml

### `daily_status_cron.yml`

**Reason**: Consolidated into single pipeline with job dependencies

**Will be replaced by**: daily-status-pipeline.yml, publish_dashboard_release.yml

### `daily_status_enrich.yml`

**Reason**: Consolidated into single pipeline with job dependencies

**Will be replaced by**: daily-status-pipeline.yml, publish_dashboard_release.yml

### `docs.yml`

**Reason**: pages-mkdocs.yml handles all doc building and deployment

**Will be replaced by**: pages-mkdocs.yml, documentation-link-checker.yml

### `mcp-ci.yml`

**Reason**: Consolidated into optimized-ci.yml with MCP tests as additional job

**Will be replaced by**: optimized-ci.yml, integration-gated.yml

### `produce-trend.yml`

**Reason**: Consolidated into single pipeline with job dependencies

**Will be replaced by**: daily-status-pipeline.yml, publish_dashboard_release.yml

### `report_publish.yml`

**Reason**: Consolidated into single pipeline with job dependencies

**Will be replaced by**: daily-status-pipeline.yml, publish_dashboard_release.yml

### `template-validation.yml`

**Reason**: Single validation pipeline with sequential jobs

**Will be replaced by**: workflow-validation.yml

### `test-suite.yml`

**Reason**: Consolidated into optimized-ci.yml with MCP tests as additional job

**Will be replaced by**: optimized-ci.yml, integration-gated.yml

### `validate-docs-enhanced.yml`

**Reason**: pages-mkdocs.yml handles all doc building and deployment

**Will be replaced by**: pages-mkdocs.yml, documentation-link-checker.yml

### `validate-docs.yml`

**Reason**: pages-mkdocs.yml handles all doc building and deployment

**Will be replaced by**: pages-mkdocs.yml, documentation-link-checker.yml

### `workflow-lint.yml`

**Reason**: Single validation pipeline with sequential jobs

**Will be replaced by**: workflow-validation.yml

### `workflow-validator.yml`

**Reason**: Single validation pipeline with sequential jobs

**Will be replaced by**: workflow-validation.yml

## Secrets Usage

