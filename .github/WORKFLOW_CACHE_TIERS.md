# Workflow Cache Tier Assignments

This document defines which cache tier each workflow should use for optimal performance and cost management.

## 🟢 LIVE Tier Workflows (Permanent Cache)

These workflows run frequently and are critical to development workflow. They should ALWAYS use the live tier for maximum performance.

### CI/CD & Quality
- `audit-improvement-pipeline.yml` - Core audit pipeline
- `code-quality.yml` - Code quality checks on every PR
- `pr-checks.yml` - PR validation checks
- `security-suite.yml` - Security scanning (critical)
- `security-scan.yml` - Additional security checks
- `optimized-ci.yml` - Main CI pipeline
- `post-merge-validation-optimized.yml` - Post-merge validation

### Testing & Coverage
- `determinism.yml` - Determinism tests
- `coverage_report.yml` - Coverage reporting
- `nox_gates.yml` - Nox-based test gates
- `integration-gated.yml` - Integration tests

### Documentation & Publishing
- `api-documentation.yml` - API docs generation
- `pages-mkdocs.yml` - MkDocs site building

### Security
- `codeql-analysis.yml` - CodeQL analysis
- `dependency-scan.yml` - Dependency vulnerability scanning
- `semgrep_sarif.yml` - Semgrep security scanning

### Core Workflows
- `self-healing-ci.yml` - Self-healing CI infrastructure
- `ci-health-monitor.yml` - CI health monitoring

**Total: ~18 workflows**

## 🟡 COMMON Tier Workflows (7-day Retention)

These workflows run periodically but not on every commit. They benefit from caching but don't need permanent cache storage.

### Scheduled Workflows
- `scheduled-dependency-audit.yml` - Weekly dependency audits
- `monthly-model-retraining.yml` - Monthly ML model updates
- `biweekly-research-digest.yml` - Biweekly digest generation
- `cache-warmup.yml` - Daily cache warming (NEW)
- `cache-management.yml` - Weekly cache cleanup (NEW)

### Automated Maintenance
- `auto-update-configs.yml` - Config file updates
- `copilot-self-evolution.yml` - Copilot evolution checks
- `self-healing-feedback-loop.yml` - Feedback loop processing
- `token-rotation.yml` - Token rotation checks
- `sync-env-vars.yml` - Environment variable sync

### Publishing & Releases
- `pre-release-deployment.yml` - Pre-release deployments
- `publish_dashboard_release.yml` - Dashboard releases
- `sbom.yml` - Software Bill of Materials generation
- `wiki-assemble.yml` - Wiki assembly

### Monitoring & Reporting
- `aftermath.yml` - Post-workflow cleanup
- `status_gate.yml` - Status gate checks
- `scan-secrets-variables.yml` - Secret scanning
- `repo-organization.yml` - Repository organization tasks
- `detect-duplicates.yml` - Duplicate detection

### Cognitive Workflows
- `cognitive-action.yml` - Cognitive action processing
- `cognitive-aftermath.yml` - Cognitive cleanup
- `cognitive-decision.yml` - Cognitive decision making
- `cognitive-perception.yml` - Cognitive perception

### Agent & Autonomous
- `agent-runtime.yml` - Agent runtime operations
- `autonomous-agent.yml` - Autonomous agent tasks

### Copilot Tools
- `copilot-cascade-review.yml` - Cascade review system
- `pr-followup-generator.yml` - PR followup generation
- `draft-audit-pr.yml` - Draft audit PRs

**Total: ~28 workflows**

## 🔴 EPHEMERAL Tier Workflows (1-day Retention)

These workflows are for one-off tasks, experiments, or testing. Their caches are frequently invalidated and should be cleaned up quickly.

### Validation & Testing
- `data_validation.yml` - Data validation checks
- `decode-validate-artifact.yml` - Artifact validation
- `html_visual_baseline.yml` - Visual baseline creation
- `html_visual_regression.yml` - Visual regression testing

### Build & Packaging
- `build-chatgpt-package.yml` - ChatGPT package building
- `zendesk-quantum-packaging.yml` - Quantum packaging
- `docker-build-push.yml` - Docker image builds (if exists)

### Security Bootstrap
- `security-tools-bootstrap.yml` - One-time security tool setup

**Total: ~7 workflows**

## Migration Priority

### Phase 1: Critical LIVE workflows (Priority: HIGH)
Update these first for immediate performance gains:
1. `audit-improvement-pipeline.yml` ✅ (Already updated with PYTHONPATH)
2. `code-quality.yml`
3. `pr-checks.yml`
4. `security-suite.yml`
5. `optimized-ci.yml`

### Phase 2: Remaining LIVE workflows (Priority: MEDIUM)
Update these for consistent LIVE tier coverage:
- All other workflows in LIVE tier list

### Phase 3: COMMON tier workflows (Priority: LOW)
Update these for cache optimization:
- All workflows in COMMON tier list

### Phase 4: EPHEMERAL tier workflows (Priority: LOW)
Update these last:
- All workflows in EPHEMERAL tier list

## Cache Key Examples

### LIVE Tier
```
live-pip-Linux-py3.11-a1b2c3d4e5f6
live-pip-Linux-py3.12-x9y8z7w6v5u4
```

### COMMON Tier
```
common-pip-Linux-py3.11-a1b2c3d4e5f6
common-pip-Linux-py3.12-x9y8z7w6v5u4
```

### EPHEMERAL Tier
```
ephemeral-pip-Linux-py3.11-a1b2c3d4e5f6
ephemeral-pip-Linux-py3.12-x9y8z7w6v5u4
```

## Fallback Strategy

All tiers can fallback to LIVE tier caches, ensuring workflows always benefit from shared caching:

1. Try exact match in specified tier
2. Try any cache in specified tier (same Python version)
3. **Fallback to LIVE tier** (same Python version)
4. Fallback to COMMON tier (same Python version)

This means even EPHEMERAL workflows benefit from LIVE cache when available!

## Monitoring

Use the Cache Management workflow to monitor tier usage:
- Run `workflow_dispatch` with action `report` to see current cache distribution
- Weekly automated reports via schedule
- Manual cleanup via `cleanup-ephemeral` or `cleanup-common` actions

## Notes

- Workflows not using Python/pip are not included in this document
- Some workflows Phase 5 use Python but have their own specialized caching (e.g., UV, pre-commit)
- This document should be updated when new workflows are added
- Cache tier can be overridden per workflow if needed for specific use cases
