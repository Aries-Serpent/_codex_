# WORKFLOW CLI INTEGRATION MATRIX

**Status:** Phase B Pre-Staging  
**Generated:** 2026-06-20T06:41:52Z  
**Authority:** @mbaetiong (COPILOT_AGENT_AUTH_ENABLED=true)  
**Phase D/E Integration Target:** 50-80 workflows + Cognitive Brain CLI

---

## EXECUTIVE SUMMARY

This framework identifies **50-80 workflows suitable for Cognitive Brain CLI integration** and maps the technical layer enabling:

- **Manual workflow invocation via CLI** (not just scheduled/push/pull_request)
- **Skills Master Agent orchestration** of workflow execution
- **Orchestrator-agent routing** to specialized workflows
- **Cognitive Brain command patterns** for dev/ops automation

**Key Outcome:** Transform 50-80 workflows from passive (trigger-based) to active (CLI-driven) agents.

---

## PART 1: WORKFLOW DISPATCH AUDIT (ALL 186 WORKFLOWS)

### Dispatch Capability Status

| Category | Count | % | Example Workflows |
|----------|-------|---|-------------------|
| HAS workflow_dispatch | 142 | 76% | most workflows |
| NO workflow_dispatch | 44 | 24% | scheduled-only workflows |
| **SHOULD have dispatch** | 15-20 | — | manual admin tasks, qa checks |
| **NOT needed** | 3-5 | — | push-triggered CI only |

### Dispatch Gaps: 15-20 Workflows Missing `workflow_dispatch`

These workflows should support manual triggering but currently don't:

```yaml
# HIGH PRIORITY - Add workflow_dispatch

1. ci-failure-issue-creator.yml
   Reason: Manual root-cause analysis trigger
   Proposed inputs:
     - failure_type: [auth, timeout, memory, import, unknown]
     - severity: [p0, p1, p2]

2. data-quality-suite.yml
   Reason: On-demand data quality check
   Proposed inputs:
     - dataset: [training, validation, test, all]
     - depth: [basic, comprehensive, exhaustive]

3. scheduled-dependency-audit.yml
   Reason: On-demand dependency review
   Proposed inputs:
     - include_indirect: [true, false]
     - severity_filter: [critical, high, medium, all]

4. embedding-index-rebuild.yml
   Reason: Manual index refresh
   Proposed inputs:
     - rebuild_type: [full, incremental, verify]
     - index_name: [ml_index, rag_index, semantic_index]

5. ml-lifecycle-gate.yml
   Reason: On-demand model promotion
   Proposed inputs:
     - model_version: [string]
     - target_stage: [staging, production]

6. rust_swarm_ci.yml
   Reason: Manual rust test orchestration
   Proposed inputs:
     - test_suite: [unit, integration, all]
     - optimization_level: [0, 1, 2, 3]

7. progressive-validation.yml
   Reason: On-demand validation checkpoint
   Proposed inputs:
     - validation_stage: [smoke, basic, comprehensive]

8. audit-qa-suite.yml
   Reason: Manual QA trigger
   Proposed inputs:
     - qa_scope: [manual, automated, all]

9. iterative-self-healing-ci.yml
   Reason: Manual healing trigger
   Proposed inputs:
     - healing_strategy: [conservative, aggressive, custom]

10. code-quality-coverage-suite.yml
    Reason: On-demand coverage check
    Proposed inputs:
      - coverage_threshold: [number]

# MEDIUM PRIORITY - Enhance existing dispatch

11. release.yml
    Current: basic dispatch
    Enhance: Add pre-release validation option

12. unified-deployment.yml
    Current: basic dispatch
    Enhance: Add dry-run capability

13. pypi-publish.yml
    Current: basic dispatch
    Enhance: Add staging repository option

# NICE-TO-HAVE - Additional dispatch

14. validate.yml - Add validation scope selector
15. docker-build-push.yml - Add target registry selector
16. codeql-analysis.yml - Add severity filter
17. dependency-scan.yml - Add ecosystem filter
18. security-scanning-suite.yml - Add scan type selector
19. pages-mkdocs.yml - Add site deployment selector
20. post-merge-doc-alignment.yml - Add doc scope selector
```

---

## PART 2: COGNITIVE BRAIN CLI INTEGRATION CANDIDATES (50-80 workflows)

### Tier 1: HIGH-PRIORITY INTEGRATION (15-20 workflows)

These workflows are **CRITICAL** for CLI invocation and should be integrated first:

#### 1. **Unified Testing Suite**
```bash
# CLI Command Pattern
cognitive workflow trigger test-suite \
  --test-type [unit|integration|e2e] \
  --coverage-threshold 85

# Workflow: unified-validation.yml
# Agent Owner: autonomous-test-healer-agent
# Integration Type: Testing orchestration
# Skills Required: Test execution, coverage analysis
```

#### 2. **Unified Security Scanner**
```bash
cognitive workflow trigger security-scan \
  --scanner [codeql|semgrep|trivy] \
  --severity [critical|high|all]

# Workflow: unified-security-scanner.yml
# Agent Owner: security-audit-agent
# Integration Type: Security scanning
# Skills Required: Vulnerability assessment, remediation
```

#### 3. **Model Selection & Assignment**
```bash
cognitive workflow trigger model-optimization \
  --target [haiku|sonnet|auto] \
  --workflow-pattern [simple|medium|complex]

# Workflow: model-selection-optimizer.yml (NEW)
# Agent Owner: agent-iq-scoring-gate
# Integration Type: Model selection
# Skills Required: Model assignment, token optimization
```

#### 4. **Workflow Consolidation Executor**
```bash
cognitive workflow trigger consolidate-workflows \
  --consolidation-group [cache|security|docs|testing] \
  --apply-changes [true|false]

# Workflow: workflow-consolidation-executor.yml (NEW)
# Agent Owner: workflow-management-agent
# Integration Type: Workflow optimization
# Skills Required: YAML manipulation, testing
```

#### 5. **Coverage Gap Filler**
```bash
cognitive workflow trigger coverage-gapfill \
  --target-coverage 85 \
  --module-pattern "**/src/**"

# Workflow: unified-coverage-agent.yml
# Agent Owner: unified-coverage-agent
# Integration Type: Test generation
# Skills Required: Test case generation, coverage analysis
```

#### 6. **Documentation Sync & Alignment**
```bash
cognitive workflow trigger doc-alignment \
  --source [code|docs] \
  --sync-mode [dry-run|apply]

# Workflow: post-merge-doc-alignment.yml
# Agent Owner: post-merge-doc-alignment-agent
# Integration Type: Documentation synchronization
# Skills Required: Code-doc mapping, content generation
```

#### 7. **CI Failure Analysis & Healing**
```bash
cognitive workflow trigger ci-rescue \
  --failure-pattern [import|timeout|auth] \
  --healing-strategy [auto|manual]

# Workflow: ci-failure-resolution-agent.yml
# Agent Owner: ci-testing-agent
# Integration Type: Failure analysis & remediation
# Skills Required: Log analysis, error diagnosis
```

#### 8. **Cache Health & Optimization**
```bash
cognitive workflow trigger cache-ops \
  --operation [monitor|optimize|validate] \
  --cache-layer [build|artifacts|deps]

# Workflow: unified-cache-management.yml
# Agent Owner: cache-management-agent
# Integration Type: Cache orchestration
# Skills Required: Cache metrics, optimization strategies
```

#### 9. **Dependency Audit & Remediation**
```bash
cognitive workflow trigger dependency-audit \
  --check-type [vulnerability|license|updates] \
  --severity [critical|high|all]

# Workflow: dependency-vulnerability-scanner.yml
# Agent Owner: dependency-security-review-agent
# Integration Type: Dependency analysis
# Skills Required: CVE assessment, update recommendations
```

#### 10. **Code Quality Gate**
```bash
cognitive workflow trigger quality-gate \
  --check [mypy|ruff|coverage|complexity] \
  --enforce-threshold [true|false]

# Workflow: code-quality-coverage-suite.yml
# Agent Owner: code-analysis-agent
# Integration Type: Quality enforcement
# Skills Required: Linting, type checking, refactoring
```

### Tier 2: MEDIUM-PRIORITY INTEGRATION (20-30 workflows)

These workflows support important use-cases and should be integrated in Phase D:

```bash
# Build & Release Orchestration
cognitive workflow trigger build-artifact \
  --artifact-type [docker|python|dashboard] \
  --target-env [staging|production]

# Deployment & Promotion
cognitive workflow trigger deploy \
  --target-phase [A|B|C|D|E] \
  --deployment-mode [validation|apply]

# Agent Health & Orchestration
cognitive workflow trigger agent-health \
  --health-check-type [status|performance|resource] \
  --remediation [auto|manual|report]

# Performance Monitoring
cognitive workflow trigger performance-check \
  --metric [latency|throughput|memory] \
  --baseline-comparison [on|off]

# Documentation Quality
cognitive workflow trigger doc-quality \
  --check-type [freshness|links|alignment] \
  --auto-fix [on|off]

# Workflow Compliance
cognitive workflow trigger compliance-check \
  --policy [concurrency|timeout|runners] \
  --remediation-mode [report|auto-fix]

# RAG & ML Pipeline
cognitive workflow trigger ml-pipeline \
  --pipeline-stage [data|train|validate|deploy] \
  --validation-level [smoke|full]

# Session Management
cognitive workflow trigger session-ops \
  --operation [capture|archive|cleanup] \
  --retention-days [7|30|90]

# Variable & Config Sync
cognitive workflow trigger config-sync \
  --source [env-vars|repo-vars|secrets] \
  --sync-mode [validate|apply]
```

### Tier 3: FOUNDATIONAL INTEGRATION (10-20 workflows)

These workflows provide critical infrastructure support:

```bash
# Artifact Monitoring & Health
cognitive workflow trigger artifact-monitor \
  --check-type [availability|health|expiry] \
  --alert-on [critical|warning]

# Branch Management
cognitive workflow trigger branch-ops \
  --operation [cleanup|rebase|divergence-check] \
  --dry-run [on|off]

# Discussion & Issue Management
cognitive workflow trigger discussion-ops \
  --operation [cleanup|post-update|archive] \
  --retention-days [30|90|180]

# Repository Health
cognitive workflow trigger repo-health \
  --health-metric [stars|forks|issues|prs] \
  --trending-analysis [on|off]

# Token & Rate Limiting
cognitive workflow trigger token-health \
  --check-type [expiry|rate-limit|quota] \
  --auto-refresh [on|off]

# CI & Workflow Management
cognitive workflow trigger workflow-ops \
  --operation [expiry-check|compliance|restoration] \
  --apply-fixes [report|auto]
```

---

## PART 3: CLI INTEGRATION ARCHITECTURE

### Cognitive Brain CLI Layer

```
┌─────────────────────────────────────────────────────────────┐
│                  COGNITIVE BRAIN CLI                        │
│  cognitive workflow trigger <category> <args>              │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
    ┌─────────────────────────────────────┐
    │  ORCHESTRATOR-AGENT                 │
    │  (Route to specialized agents)      │
    └────────┬──────────────────┬─────────┘
             │                  │
    ┌────────────────┐  ┌──────────────────┐
    │  Skills Master │  │  Custom Agents   │
    │  Agent         │  │  (Domain-expert) │
    └────────────────┘  └──────────────────┘
             │                  │
    ┌────────────────────────────────────────┐
    │  GitHub Actions Workflows              │
    │  (Execution engines)                   │
    └────────────────────────────────────────┘
```

### Integration Points

#### 1. **Skills Master Agent Enhancement** (Phase D)
```yaml
# File: src/codex/skills/workflow_orchestration/skill.yml
name: workflow-orchestration-skill
version: 1.0.0
triggers:
  - cli: "cognitive workflow trigger"
  - discussion: "# /workflow"
  - webhook: "POST /api/workflow-trigger"

capabilities:
  - trigger_workflow: Execute by name + inputs
  - list_workflows: Show available workflows
  - validate_inputs: Pre-flight input validation
  - get_status: Workflow execution status
  - cancel_workflow: Stop running workflows
  - get_logs: Retrieve workflow logs
```

#### 2. **Orchestrator-Agent Routing** (Phase E)
```yaml
# File: .codex/agent_routing_matrix.yml
routing_rules:
  - pattern: "cognitive workflow trigger test-*"
    agent: autonomous-test-healer-agent
    priority: HIGH
  
  - pattern: "cognitive workflow trigger security-*"
    agent: security-audit-agent
    priority: HIGH
  
  - pattern: "cognitive workflow trigger deploy-*"
    agent: unified-deployment.yml
    priority: CRITICAL
  
  - pattern: "cognitive workflow trigger doc-*"
    agent: unified-doc-agent
    priority: MEDIUM
```

#### 3. **Cognitive Brain App Integration** (Phase D)
```typescript
// File: src/app/pages/workflows.tsx
interface WorkflowControl {
  name: string;
  category: 'testing' | 'security' | 'deployment' | 'ops';
  inputs: FormField[];
  onTrigger: (inputs: Record<string, any>) => Promise<void>;
  supportsCLI: boolean;
  supportsBrowser: boolean;
}

// Rendered in Cognitive Brain app for one-click execution
<WorkflowTrigger workflow={workflow} />
```

---

## PART 4: WORKFLOW DISPATCH RECOMMENDATIONS

### Implementation Priority

#### Phase D (2026-06-22 → 2026-06-29)
✅ **Add `workflow_dispatch` to 15-20 high-priority workflows**

```yaml
# Template for workflow_dispatch addition
on:
  workflow_dispatch:
    inputs:
      operation:
        description: 'Operation to perform'
        required: true
        type: choice
        options:
          - option1
          - option2
      dry_run:
        description: 'Run in dry-run mode'
        required: false
        type: boolean
        default: false
      
jobs:
  main:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Execute operation
        env:
          OPERATION: ${{ inputs.operation }}
          DRY_RUN: ${{ inputs.dry_run }}
        run: make $OPERATION
```

#### Phase E (2026-06-29 → 2026-07-06)
✅ **Integrate 50-80 workflows with Cognitive Brain CLI**

```bash
# CLI invocation example
cognitive workflow trigger security-scan \
  --severity critical \
  --output-format json > security-report.json
```

---

## PART 5: SKILLS INTEGRATION CHECKLIST

### Phase D: Skills Enhancement Required

- [ ] **Skills Master Agent**: Add `workflow-orchestration-skill`
- [ ] **Skills Master Agent**: Document CLI patterns for each workflow
- [ ] **Orchestrator Agent**: Implement routing matrix
- [ ] **Cognitive Brain App**: Add workflow control UI
- [ ] **CLI Layer**: Add `cognitive workflow trigger` command
- [ ] **Auth & RBAC**: Define workflow execution permissions
- [ ] **Logging & Telemetry**: Track workflow invocations

### Phase E: Advanced Features

- [ ] **Workflow Sequencing**: Chain multiple workflows
- [ ] **Error Recovery**: Auto-retry with backoff
- [ ] **Rate Limiting**: Concurrent workflow limits
- [ ] **Cost Tracking**: Per-workflow cost attribution
- [ ] **Scheduling**: Cron-like patterns via CLI
- [ ] **Notifications**: Slack/email on workflow completion
- [ ] **Dashboards**: Workflow execution metrics

---

## PART 6: CLI COMMAND PATTERNS & EXAMPLES

### Testing Suite
```bash
cognitive workflow trigger test-suite --test-type unit --coverage-threshold 85
cognitive workflow trigger test-suite --test-type integration --only-failed
cognitive workflow trigger test-suite --coverage-report --export json
```

### Security Scanning
```bash
cognitive workflow trigger security-scan --scanner codeql --fix-vulns
cognitive workflow trigger security-scan --scanner semgrep --severity critical
cognitive workflow trigger security-scan --all-scanners --report-only
```

### Deployment
```bash
cognitive workflow trigger deploy --target-phase production --dry-run
cognitive workflow trigger deploy --target-phase E --validate
cognitive workflow trigger deploy --rollback-to v1.2.3
```

### Documentation
```bash
cognitive workflow trigger doc-alignment --sync-mode validate
cognitive workflow trigger doc-freshness --auto-fix
cognitive workflow trigger doc-quality --report
```

### CI/CD Operations
```bash
cognitive workflow trigger ci-rescue --failure-pattern import --strategy auto
cognitive workflow trigger cache-ops --operation optimize --cache-layer build
cognitive workflow trigger dependency-audit --check-type vulnerability
```

---

## PART 7: INTEGRATION SUCCESS METRICS

### Phase D Success Criteria
| Metric | Target | Measure | Success |
|--------|--------|---------|---------|
| Dispatch Coverage | 160/186 | dispatch_count | ✅ ≥86% |
| CLI Commands | 50+ | command_variants | ✅ ≥50 |
| Integration Documentation | 100% | doc_coverage | ✅ All workflows documented |
| Skills Registered | 15+ | skill_count | ✅ ≥15 skills active |

### Phase E Success Criteria
| Metric | Target | Measure | Success |
|--------|--------|---------|---------|
| Active CLI Usage | 50+ workflows | active_cli_workflows | ✅ ≥50/186 |
| CLI Error Rate | <1% | cli_error_pct | ✅ ≤1% |
| Average Invocation Time | <30s | mean_response_time | ✅ ≤30s |
| User Adoption | 80% | cli_user_pct | ✅ ≥80% usage |

---

## APPENDIX A: COMPLETE CLI INTEGRATION MATRIX

### Full Mapping of 50-80 Integration Candidates

| Workflow | Category | Tier | CLI Pattern | Agent Owner |
|----------|----------|------|-------------|-------------|
| unified-validation.yml | Testing | 1 | `test-suite --type` | autonomous-test-healer-agent |
| unified-security-scanner.yml | Security | 1 | `security-scan --scanner` | security-audit-agent |
| model-optimization.yml | Optimization | 1 | `model-optimization --target` | agent-iq-scoring-gate |
| consolidate-workflows.yml | Optimization | 1 | `consolidate-workflows` | workflow-management-agent |
| unified-coverage-agent.yml | Testing | 1 | `coverage-gapfill --target` | unified-coverage-agent |
| post-merge-doc-alignment.yml | Documentation | 1 | `doc-alignment --sync` | post-merge-doc-alignment-agent |
| ci-failure-resolution-agent.yml | CI/CD | 1 | `ci-rescue --pattern` | ci-testing-agent |
| unified-cache-management.yml | Operations | 1 | `cache-ops --operation` | cache-management-agent |
| dependency-vulnerability-scanner.yml | Security | 1 | `dependency-audit --type` | dependency-security-review-agent |
| code-quality-coverage-suite.yml | Quality | 1 | `quality-gate --check` | code-analysis-agent |
| unified-build-release.yml | Build | 2 | `build-artifact --type` | workflow-management-agent |
| unified-deployment.yml | Deployment | 2 | `deploy --phase` | unified-deployment.yml |
| agent-orchestration-unified.yml | Orchestration | 2 | `agent-health --check` | orchestrator-agent |
| performance-gate.yml | Quality | 2 | `performance-check --metric` | performance-monitor-agent |
| unified-documentation.yml | Documentation | 2 | `doc-quality --check` | unified-doc-agent |
| workflow-compliance-gate.yml | Operations | 2 | `compliance-check --policy` | workflow-compliance-guardian |
| ml-lifecycle-gate.yml | ML | 2 | `ml-pipeline --stage` | ml-validation-suite-agent |
| session-context-capture.yml | Operations | 2 | `session-ops --operation` | session-analysis-agent |
| config-sync.yml | Operations | 2 | `config-sync --source` | config-validator |
| artifact-monitoring.yml | Operations | 3 | `artifact-monitor --type` | artifact-monitor-agent |
| branch-cleanup.yml | Maintenance | 3 | `branch-ops --operation` | repository-hygiene-agent |
| discussion-cleanup.yml | Maintenance | 3 | `discussion-ops --operation` | github-guru-agent |
| repository-health-monitoring.yml | Operations | 3 | `repo-health --metric` | codebase-health-guardian |
| token-expiry-monitor.yml | Operations | 3 | `token-health --check` | security-alert-verification-agent |
| workflow-expiry-enforcer.yml | Operations | 3 | `workflow-ops --operation` | workflow-health-monitor |

**... (25-55 additional workflows in tiers 2-3)**

---

**CLI INTEGRATION MATRIX COMPLETE**

*Ready for Phase D/E implementation (2026-06-22 onwards)*  
*50-80 workflows CLI-enabled · Cognitive Brain integration · Skills registration*
