# GitHub Actions Workflow Index

This directory contains all GitHub Actions workflows for the _codex_ repository, organized into categories for easy navigation and understanding.

## Active baseline policy

Only the repo's current baseline workflows remain enabled in the live `.github/workflows/` directory. Experimental, duplicate, and low-frequency automation is intentionally disabled by renaming the workflow file to `.disabled` and keeping it out of the active runtime path. This keeps the active maintenance surface limited to CI, security, release, and governance flows that are actually used today.

The reusable workflow `cost-gate.yml` is part of the active baseline and is still invoked by several active jobs; it is not a historical artifact and should remain enabled.

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

## 📊 Consolidated Workflow Suites (Phase 1 & 2)

These are the unified workflow suites created during Phase 1 & 2 consolidation that combine multiple workflows for improved efficiency:

### 🧠 [cognitive-action-decision.yml](cognitive-action-decision.yml)
**Cognitive Decision & Action Suite** - Unified cognitive decision-making and action execution
- **Jobs:** Decision engine, Action executor, Full-cycle processing
- **Triggers:** Schedule (6h), Manual, workflow_run
- **Modes:** decision-only, action-only, full-cycle
- **Replaces:** cognitive-decision.yml, cognitive-action.yml

### 📊 [cognitive-analysis-feed.yml](cognitive-analysis-feed.yml)
**Cognitive Analysis & Pattern Feed Suite** - Unified aftermath evaluation and pattern learning
- **Jobs:** Aftermath evaluation, Pattern feeding, Learning analysis
- **Triggers:** Schedule (per-iteration), Manual, workflow_run
- **Modes:** aftermath-only, pattern-feed-only, full-analysis
- **Replaces:** cognitive-aftermath.yml, cognitive-brain-feed.yml

### 🤖 [agent-orchestration-unified.yml](agent-orchestration-unified.yml)
**Agent Orchestration Suite** - Unified multi-agent coordination
- **Jobs:** Chain orchestration, Agent handoff, Multi-agent coordination
- **Triggers:** Manual, workflow_run
- **Modes:** chain-orchestration, handoff-execution, full-orchestration
- **Replaces:** agent-chain-orchestrator.yml, agent_handoff.yml

### 🔄 [copilot-evolution-suite.yml](copilot-evolution-suite.yml)
**Copilot Evolution Suite** - Unified Copilot review and self-evolution
- **Jobs:** Cascade review, Self-evolution, Full suite
- **Triggers:** Schedule (4h), PR, Manual
- **Modes:** evolution-only, review-only, full-suite
- **Replaces:** copilot-cascade-review.yml, copilot-self-evolution.yml

### 📋 [audit-qa-suite.yml](audit-qa-suite.yml)
**Audit & QA Suite** - Unified audit and quality assurance
- **Jobs:** Audit gap analysis, Codebase QA walkthrough, Quality checks
- **Triggers:** Schedule (per-phase), PR, Manual, workflow_call
- **Modes:** audit-only, qa-only, full-suite
- **Replaces:** audit-improvement-pipeline.yml, codebase-qa-walkthrough.yml

### 🚀 [unified-deployment.yml](unified-deployment.yml)
**Unified Deployment Suite** - Consolidated deployment operations
- **Jobs:** Cognitive app deployment, Pre-release deployment
- **Triggers:** Manual, workflow_run
- **Modes:** cognitive-app, pre-release, full-deployment
- **Replaces:** deploy-cognitive-app.yml, pre-release-deployment.yml

### 📊 [code-quality-coverage-suite.yml](code-quality-coverage-suite.yml)
**Code Quality & Coverage Suite** - Unified quality and coverage analysis
- **Jobs:** Coverage reporting, Code quality analysis
- **Triggers:** PR, Push, Manual, workflow_call
- **Modes:** coverage-only, quality-only, full-analysis
- **Replaces:** coverage_report.yml, code-quality.yml

### 🔍 [data-quality-suite.yml](data-quality-suite.yml)
**Data Quality & Determinism Suite** - Unified data validation and determinism testing
- **Jobs:** Data validation, Determinism testing, Manifest validation
- **Triggers:** PR, Push, Manual, workflow_call
- **Modes:** validation-only, determinism-only, full-suite
- **Replaces:** data_validation.yml, determinism.yml

### 📈 [workflow-analytics-unified.yml](workflow-analytics-unified.yml)
**Workflow Analytics Suite** - Unified workflow performance analytics
- **Jobs:** Analytics collection, Trend analysis, Performance reporting
- **Triggers:** Schedule, Manual, workflow_run
- **Modes:** scheduled, manual, on-demand
- **Replaces:** workflow-analytics-scheduled.yml, workflow-analytics-manual.yml

### 🔒 [security-scanning-suite.yml](security-scanning-suite.yml)
**Security Scanning Suite** - Consolidated security scanning
- **Jobs:** CodeQL scan, Dependency scan, Secret scan, SBOM generation
- **Triggers:** Push, Pull request, Schedule (per-iteration, per-phase), Manual, workflow_call
- **Cache Tier:** Common
- **Replaces:** Multiple security workflows (see Phase 1 report)

## 📂 Workflow Categories

### Testing Workflows

Active workflows for running tests and collecting coverage:

| Workflow | Description | Trigger | Status |
|----------|-------------|---------|--------|
| [auth-tests.yml](auth-tests.yml) | Authentication testing | PR, Push | ✅ Active |
| [ml-tests.yml.disabled](ml-tests.yml.disabled) | ML model testing | Manual | ⏸️ Disabled |
| [optimized-ci.yml](optimized-ci.yml) | Optimized CI pipeline | PR, Push | ✅ Active |
| [rust_swarm_ci.yml](rust_swarm_ci.yml) | Rust swarm testing | PR, Push | ✅ Active |
| [test-rag.yml](test-rag.yml) | RAG model testing | Manual | ✅ Active |

### Security Workflows

Security scanning, vulnerability detection, and compliance:

| Workflow | Description | Trigger | Status |
|----------|-------------|---------|--------|
| [security-scanning-suite.yml](security-scanning-suite.yml) | 🆕 Consolidated security scanning | PR, Push, Schedule | ✅ Active |
| [codeql-analysis.yml](codeql-analysis.yml) | CodeQL security analysis | PR, Push, Schedule | ✅ Active |
| [dependency-scan.yml](dependency-scan.yml) | Dependency vulnerability scan | Schedule | ✅ Active |
| [semgrep_sarif.yml](semgrep_sarif.yml) | Semgrep SARIF analysis | PR, Push | ✅ Active |
| [sbom.yml](sbom.yml) | Software Bill of Materials | Release | ✅ Active |

### CI/CD Health Workflows

Pipeline health monitoring and diagnostics:

| Workflow | Description | Trigger | Status |
|----------|-------------|---------|--------|
| [artifact-monitoring.yml](artifact-monitoring.yml) | Artifact monitoring and tracking | Schedule | ✅ Active |
| [batch-ci-triage.yml](batch-ci-triage.yml) | Batch CI issue triage | Schedule | ✅ Active |
| [ci-health-monitor.yml](ci-health-monitor.yml) | CI/CD health monitoring | Schedule | ✅ Active |
| [repository-health-monitoring.yml](repository-health-monitoring.yml) | Repository health checks | Schedule | ✅ Active |

### Cache Management Workflows

Cache optimization and maintenance:

| Workflow | Description | Trigger | Status |
|----------|-------------|---------|--------|
| _No standalone cache management workflows - distributed caching pattern used_ | Each workflow manages its own cache | N/A | ℹ️ Info |

### Documentation Workflows

Documentation building, validation, and deployment:

| Workflow | Description | Trigger | Status |
|----------|-------------|---------|--------|
| [documentation-link-checker.yml](documentation-link-checker.yml) | Documentation link validation | PR, Schedule | ✅ Active |
| [pages-mkdocs.yml](pages-mkdocs.yml) | MkDocs documentation build | Push to main | ✅ Active |
| [api-documentation.yml](api-documentation.yml) | API documentation generation | Push, Manual | ✅ Active |

### Deployment Workflows

Release and deployment management:

| Workflow | Description | Trigger | Status |
|----------|-------------|---------|--------|
| [unified-deployment.yml](unified-deployment.yml) | 🆕 Unified deployment suite | Manual | ✅ Active |
| [docker-build-push.yml](docker-build-push.yml) | Docker image build and push | Push, Release | ✅ Active |
| [pypi-publish.yml](pypi-publish.yml) | PyPI package publishing | Release | ✅ Active |

### Authentication Workflows

Authentication, secrets, and token management:

| Workflow | Description | Trigger | Status |
|----------|-------------|---------|--------|
| [agent-auth-delegation.yml](agent-auth-delegation.yml) | 🆕 Agent session auth with cognitive pre-flight gate (REQ-1–5) | PR, Manual | ✅ Active |
| [session-watchdog.yml](session-watchdog.yml) | 🆕 Timebox, exploration session & continuity enforcement | PR comment | ✅ Active |
| [token-probe.yml](token-probe.yml) | 🆕 On-demand CODEX_MASTER_KEY + CODEX_BACKUP_KEY read/write validation | Manual | ✅ Active |
| [auth-tests.yml](auth-tests.yml) | Authentication testing | PR, Push | ✅ Active |

**Cognitive Pre-flight Gate** (`cognitive-preflight` job inside `agent-auth-delegation.yml`):
- REQ-1: Posts mandatory checklist as PR comment BEFORE `@copilot continue` fires
- REQ-2: Parses `.codex/patterns/ci_failure_patterns.yaml` → outputs all patterns to job summary
- REQ-3: Verifies `.gitignore` allows `.codex/agent_auth_session.json`
- REQ-4: Verifies `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` was touched in last commit
- REQ-5 (WF-002): Reads `SESSION_TIMEBOX_START`/`SESSION_TYPE_EXPLORATION` markers → injects enforcement items

**Session Watchdog** (`session-watchdog.yml`):
- Detects `~N minutes` in any PR comment → posts `SESSION_TIMEBOX_START` with expiry timestamp
- Detects `exploration session`/`capability discussion` → posts `SESSION_TYPE_EXPLORATION` + continuity rules
- Detects `Do NOT auto-proceed` → flags mandatory stop-gate in exploration comment
- Checks expiry on every subsequent PR comment → posts `SESSION_TIMEBOX_EXPIRED` when time runs out
- Policy: `.github/docs/SessionContinuityPolicy.md`

**Note:** Auth security, rotation, and compliance workflows exist as documentation (`.md` files) but are not yet implemented as active workflows. See `.github/workflows/*.md` for specifications.

### Cognitive Brain Workflows

AI agent operations and cognitive processes:

| Workflow | Description | Trigger | Status |
|----------|-------------|---------|--------|
| [cognitive-action-decision.yml](cognitive-action-decision.yml) | 🆕 Decision & action suite | Schedule, Manual | ✅ Active |
| [cognitive-analysis-feed.yml](cognitive-analysis-feed.yml) | 🆕 Analysis & pattern feed suite | Schedule, Manual | ✅ Active |
| [cognitive-perception.yml](cognitive-perception.yml) | Cognitive perception | Schedule | ✅ Active |
| [autonomous-agent.yml](autonomous-agent.yml) | Autonomous agent execution | Schedule, Manual | ✅ Active |

### Monitoring Workflows

Repository and workflow monitoring:

| Workflow | Description | Trigger | Status |
|----------|-------------|---------|--------|
| [artifact-monitoring.yml](artifact-monitoring.yml) | Artifact monitoring and tracking | Schedule | ✅ Active |
| [workflow-analytics-unified.yml](workflow-analytics-unified.yml) | 🆕 Unified workflow analytics | Schedule, Manual | ✅ Active |

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
- **Common Tier** (7 iterations): Standard workflows
- **Ephemeral Tier** (1 iteration): Infrequent workflows

### Python Version

All workflows standardized on **Python 3.12** for consistency and performance.

### AI Agent Integration

All consolidated workflows support `workflow_call` for programmatic invocation by AI agents.

## 📖 Documentation

- [Phase 1 Consolidation Report](../../.github/workflow-archive/phase1-consolidation/PHASE1_COMPLETION_REPORT.md) - Phase 1 consolidation details
- [Phase 2 Consolidation Report](../../.github/workflow-archive/phase2-consolidation/PHASE2_FINAL_COMPLETION_REPORT.md) - Phase 2 consolidation details
- [Consolidation Guide](CONSOLIDATION_GUIDE.md) - How workflows were consolidated
- [Deprecation Plan](DEPRECATION_PLAN.md) - Deprecation timeline and process
- [Optimization Summary](OPTIMIZATION_SUMMARY.md) - Performance improvements
- [Misc Workflows](../../.github/misc/README.md) - Low-usage workflows moved to misc/

## 🚀 Usage Examples

### Running Tests

```bash
# Run specific test workflow
gh workflow run auth-tests.yml

# Run RAG tests
gh workflow run test-rag.yml

# Run optimized CI
gh workflow run optimized-ci.yml
```

### Running Unified Suites

```bash
# Run cognitive decision only
gh workflow run cognitive-action-decision.yml -f mode=decision-only

# Run full cognitive analysis
gh workflow run cognitive-analysis-feed.yml -f mode=full-analysis

# Run audit only
gh workflow run audit-qa-suite.yml -f mode=audit-only

# Run deployment
gh workflow run unified-deployment.yml -f mode=cognitive-app
```

### Managing Documentation

```bash
# Check documentation links
gh workflow run documentation-link-checker.yml

# Build MkDocs
gh workflow run pages-mkdocs.yml

# Generate API docs
gh workflow run api-documentation.yml
```

### Monitoring Workflows

```bash
# Run workflow analytics
gh workflow run workflow-analytics-unified.yml -f mode=scheduled

# Monitor CI health
gh workflow run ci-health-monitor.yml

# Check artifact status
gh workflow run artifact-monitoring.yml
```

## 🔗 Related Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Phase 1 Consolidation Archive](../../.github/workflow-archive/phase1-consolidation/)
- [Phase 2 Consolidation Archive](../../.github/workflow-archive/phase2-consolidation/)
- [Misc Workflows Directory](../../.github/misc/)
- [Workflow Validation Script](../../scripts/validate_workflows.py)
- [Performance Monitoring](../../scripts/monitor_workflow_performance.py)

## 📞 Support

For issues or questions about workflows:
1. Check [CI Health Monitor](ci-health-monitor.yml) for automated diagnostics
2. Review workflow run logs in GitHub Actions
3. Check [Phase 2 Completion Report](../../.github/workflow-archive/phase2-consolidation/PHASE2_FINAL_COMPLETION_REPORT.md) for consolidation details
4. Create an issue with `ci-health` or `workflow-consolidation` label
5. Contact @mbaetiong for critical issues

---

**Last Updated:** 2026-02-07  
**Total Workflows:** 57 active workflows + 11 misc utilities  
**Consolidated Suites:** 10 unified workflows  
**Python Version:** 3.12  
**Cache Strategy:** Distributed (per-workflow)  
**Status:** Phase 2 Complete ✅
