# GitHub Actions Workflow Index

This directory contains all GitHub Actions workflows for the _codex_ repository, organized into categories for easy navigation and understanding.

## 📑 Quick Navigation

- [Testing Workflows](#testing-workflows) - Test execution and coverage
- [Security Workflows](#security-workflows) - Security scanning and compliance
- [CI/CD Health](#cicd-health-workflows) - Pipeline monitoring and diagnostics
- [Cache Management](#cache-management-workflows) - Cache optimization and maintenance
- [Documentation](#documentation-workflows) - Documentation building and validation
- [Deployment](#deployment-workflows) - Deployment and release management
- [Authentication](#authentication-workflows) - Auth and secrets management
- [Cognitive Brain](#cognitive-brain-workflows) - AI agent and cognitive operations
- [Monitoring](#monitoring-workflows) - Repository and workflow monitoring
- [Maintenance](#maintenance-workflows) - Cleanup and maintenance tasks

## 📊 Consolidated Workflow Suites

These are the new consolidated workflow suites that combine multiple workflows for improved efficiency:

### 🧪 [test-suite.yml](test-suite.yml)
**Consolidated Testing Suite** - Replaces 6 individual test workflows
- **Jobs:** Core tests, RAG tests, Auth tests, Integration tests, Determinism tests
- **Triggers:** Pull requests, Push to main, Manual, workflow_call
- **Cache Tier:** Live
- **Replaces:** test-comprehensive.yml, test-rag.yml, auth-tests.yml, coverage_report.yml, determinism.yml, integration-gated.yml

### 💾 [cache-suite.yml](cache-suite.yml)
**Cache Management Suite** - Replaces 3 cache-related workflows
- **Jobs:** Cache warmup, Cache cleanup, Cache management, Cache validation
- **Triggers:** Schedule (6h warmup, daily cleanup, weekly management), Manual, workflow_call
- **Cache Tier:** Live
- **Replaces:** cache-warmup.yml, cache-management.yml, cache-cleanup.yml

### 🏥 [ci-health-suite.yml](ci-health-suite.yml)
**CI/CD Health Monitoring Suite** - Replaces 5 monitoring workflows
- **Jobs:** Health monitor, Artifact monitoring, Runner diagnostics, CI diagnostics
- **Triggers:** Schedule (3h health, 6h diagnostics), Manual, workflow_call
- **Cache Tier:** Common
- **Replaces:** ci-health-monitor.yml, ci-diagnostic-automation.yml, artifact-monitoring.yml, repository-health-monitoring.yml, runner-diagnostics.yml

### 🔒 [security-scanning-suite.yml](security-scanning-suite.yml)
**Security Scanning Suite** - Consolidates security scanning workflows
- **Jobs:** CodeQL scan, Dependency scan, Secret scan, SBOM generation
- **Triggers:** Push, Pull request, Schedule (daily, weekly), Manual, workflow_call
- **Cache Tier:** Common
- **Replaces:** codeql-analysis.yml, dependency-scan.yml, security-scan.yml, semgrep_sarif.yml (partially)

### 📚 [documentation-suite.yml](documentation-suite.yml)
**Documentation Suite** - Consolidates documentation workflows
- **Jobs:** MkDocs build, Link check, Deploy pages
- **Triggers:** Push, Pull request, Manual, workflow_call
- **Cache Tier:** Common
- **Replaces:** pages-mkdocs.yml, api-documentation.yml, wiki-assemble.yml (partially), documentation-link-checker.yml

## 📂 Workflow Categories

### Testing Workflows

Active workflows for running tests and collecting coverage:

| Workflow | Description | Trigger | Status |
|----------|-------------|---------|--------|
| [test-suite.yml](test-suite.yml) | 🆕 Consolidated testing suite | PR, Push, Manual | ✅ Active |
| [test-comprehensive.yml](test-comprehensive.yml) | Comprehensive test execution | PR, Push | ✅ Active |
| [ml-tests.yml.disabled](ml-tests.yml.disabled) | ML model testing | Manual | ⏸️ Disabled |
| [rust_swarm_ci.yml](rust_swarm_ci.yml) | Rust swarm testing | PR, Push | ✅ Active |

### Security Workflows

Security scanning, vulnerability detection, and compliance:

| Workflow | Description | Trigger | Status |
|----------|-------------|---------|--------|
| [security-scanning-suite.yml](security-scanning-suite.yml) | 🆕 Consolidated security scanning | PR, Push, Schedule | ✅ Active |
| [codeql-analysis.yml](codeql-analysis.yml) | CodeQL security analysis | PR, Push, Schedule | ✅ Active |
| [codeql-chunked.yml](codeql-chunked.yml) | Chunked CodeQL analysis | Schedule | ✅ Active |
| [dependency-scan.yml](dependency-scan.yml) | Dependency vulnerability scan | Schedule | ✅ Active |
| [security-scan.yml](security-scan.yml) | General security scanning | PR, Push | ✅ Active |
| [security-suite.yml](security-suite.yml) | Security test suite | PR, Push | ✅ Active |
| [semgrep_sarif.yml](semgrep_sarif.yml) | Semgrep SARIF analysis | PR, Push | ✅ Active |
| [sbom.yml](sbom.yml) | Software Bill of Materials | Release | ✅ Active |

### CI/CD Health Workflows

Pipeline health monitoring and diagnostics:

| Workflow | Description | Trigger | Status |
|----------|-------------|---------|--------|
| [ci-health-suite.yml](ci-health-suite.yml) | 🆕 Consolidated CI/CD health monitoring | Schedule, Manual | ✅ Active |
| [batch-ci-triage.yml](batch-ci-triage.yml) | Batch CI issue triage | Schedule | ✅ Active |
| [repository-health-monitoring.yml](repository-health-monitoring.yml) | Repository health checks | Schedule | ✅ Active |

### Cache Management Workflows

Cache optimization and maintenance:

| Workflow | Description | Trigger | Status |
|----------|-------------|---------|--------|
| [cache-suite.yml](cache-suite.yml) | 🆕 Consolidated cache management | Schedule, Manual | ✅ Active |

### Documentation Workflows

Documentation building, validation, and deployment:

| Workflow | Description | Trigger | Status |
|----------|-------------|---------|--------|
| [documentation-suite.yml](documentation-suite.yml) | 🆕 Consolidated documentation suite | PR, Push, Manual | ✅ Active |
| [pages-mkdocs.yml](pages-mkdocs.yml) | MkDocs documentation build | Push to main | ✅ Active |
| [documentation-link-checker.yml](documentation-link-checker.yml) | Documentation link validation | PR, Schedule | ✅ Active |

### Deployment Workflows

Release and deployment management:

| Workflow | Description | Trigger | Status |
|----------|-------------|---------|--------|
| [pre-release-deployment.yml](pre-release-deployment.yml) | Pre-release deployment | Manual | ✅ Active |
| [docker-build-push.yml](docker-build-push.yml) | Docker image build and push | Push, Release | ✅ Active |
| [pypi-publish.yml](pypi-publish.yml) | PyPI package publishing | Release | ✅ Active |

### Authentication Workflows

Authentication, secrets, and token management:

| Workflow | Description | Trigger | Status |
|----------|-------------|---------|--------|
| [auth-tests.yml](auth-tests.yml) | Authentication testing | PR, Push | ✅ Active |
| [auth-security-audit.yml](auth-security-audit.yml) | Auth security audit | Schedule | ✅ Active |
| [auth-secret-rotation.yml](auth-secret-rotation.yml) | Secret rotation | Schedule | ✅ Active |
| [auth-token-rotation.yml](auth-token-rotation.yml) | Token rotation | Schedule | ✅ Active |
| [auth-compliance-report.yml](auth-compliance-report.yml) | Auth compliance reporting | Schedule | ✅ Active |

### Cognitive Brain Workflows

AI agent operations and cognitive processes:

| Workflow | Description | Trigger | Status |
|----------|-------------|---------|--------|
| [autonomous-agent.yml](autonomous-agent.yml) | Autonomous agent execution | Schedule, Manual | ✅ Active |
| [cognitive-perception.yml](cognitive-perception.yml) | Cognitive perception | Schedule | ✅ Active |
| [cognitive-decision.yml](cognitive-decision.yml) | Cognitive decision making | Schedule | ✅ Active |
| [cognitive-action.yml](cognitive-action.yml) | Cognitive action execution | Schedule | ✅ Active |
| [cognitive-aftermath.yml](cognitive-aftermath.yml) | Cognitive aftermath analysis | Schedule | ✅ Active |

### Monitoring Workflows

Repository and workflow monitoring:

| Workflow | Description | Trigger | Status |
|----------|-------------|---------|--------|
| [artifact-monitoring.yml](artifact-monitoring.yml) | Artifact monitoring and tracking | Schedule | ✅ Active |
| [workflow-analytics-scheduled.yml](workflow-analytics-scheduled.yml) | Scheduled workflow analytics | Schedule | ✅ Active |
| [workflow-analytics-manual.yml](workflow-analytics-manual.yml) | Manual workflow analytics | Manual | ✅ Active |

### Maintenance Workflows

Cleanup and maintenance operations:

| Workflow | Description | Trigger | Status |
|----------|-------------|---------|--------|
| [scheduled-archival.yml](scheduled-archival.yml) | Scheduled archival | Schedule | ✅ Active |
| [scheduled-dependency-audit.yml](scheduled-dependency-audit.yml) | Dependency audit | Schedule | ✅ Active |

## 🔧 Workflow Architecture

### Cache Tiers

All workflows use a tiered caching strategy for optimal performance:

- **Live Tier** (Permanent): Critical workflows that run frequently
- **Common Tier** (7 days): Standard workflows
- **Ephemeral Tier** (1 day): Infrequent workflows

### Python Version

All workflows standardized on **Python 3.12** for consistency and performance.

### AI Agent Integration

All consolidated workflows support `workflow_call` for programmatic invocation by AI agents.

## 📖 Documentation

- [Consolidation Guide](CONSOLIDATION_GUIDE.md) - How workflows were consolidated
- [Deprecation Plan](DEPRECATION_PLAN.md) - Deprecation timeline and process
- [Optimization Summary](OPTIMIZATION_SUMMARY.md) - Performance improvements
- [Cache Architecture](CACHE_ARCHITECTURE_DIAGRAMS.md) - Cache design and strategy

## 🚀 Usage Examples

### Running Tests

```bash
# Run all tests
gh workflow run test-suite.yml -f test-scope=all

# Run specific test scope
gh workflow run test-suite.yml -f test-scope=rag

# Via AI agent (workflow_call)
uses: ./.github/workflows/test-suite.yml
with:
  test-scope: core
```

### Managing Cache

```bash
# Warm cache
gh workflow run cache-suite.yml -f operation=warmup

# Clean cache
gh workflow run cache-suite.yml -f operation=cleanup

# Run all cache operations
gh workflow run cache-suite.yml -f operation=all
```

### Monitoring CI Health

```bash
# Full health check
gh workflow run ci-health-suite.yml -f operation=all

# Specific check
gh workflow run ci-health-suite.yml -f operation=health-monitor
```

## 🔗 Related Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Agent Integration Guide](../../docs/agent/AI_AGENT_WORKFLOW_INTEGRATION.md)
- [Workflow Validation Script](../../scripts/validate_workflows.py)
- [Performance Monitoring](../../scripts/monitor_workflow_performance.py)

## 📞 Support

For issues or questions about workflows:
1. Check the [CI/CD Health Suite](ci-health-suite.yml) for automated diagnostics
2. Review workflow run logs
3. Create an issue with `ci-health` or `workflow-consolidation` label
4. Contact @mbaetiong for critical issues

---

**Last Updated:** 2026-01-26  
**Total Workflows:** 94 (5 consolidated suites + 89 individual)  
**Python Version:** 3.12  
**Cache Coverage:** 75%  
**Status:** Production Ready ✅
