# 🌳 AGENT SELECTION DECISION TREE

**Version:** 2.0.0  
**Generated:** 2026-06-20T06:52:13.009408  
**Purpose:** Comprehensive flowchart for choosing the right agent

---

## Quick Start

```
START: What is your goal?
  ├─ Fix CI/CD failures? → Branch A: CI/CD Agents
  ├─ Improve tests? → Branch B: Testing & Quality
  ├─ Ensure security? → Branch C: Security Agents
  ├─ Manage documentation? → Branch D: Documentation Agents
  ├─ Manage repository? → Branch E: Repository Operations
  ├─ Optimize performance? → Branch F: Infrastructure Agents
  ├─ Coordinate multi-agent? → Branch G: Orchestration
  └─ Specialized task? → Branch H: Domain-Specific
```

---

## BRANCH A: CI/CD & AUTOMATION AGENTS

```
"Fix CI/CD failures?"
  ├─ "What severity?"
  │  ├─ "CRITICAL - blocking production"
  │  │  └─ → ci-emergency-response-agent
  │  ├─ "HIGH - blocking PR merge"
  │  │  └─ → ci-failure-resolution-agent
  │  └─ "MEDIUM - warning/alert"
  │     └─ → ci-triage-pipeline-agent
  │
  ├─ "What type of failure?"
  │  ├─ "ImportError / ModuleNotFoundError"
  │  │  └─ → ci-importerror-agent
  │  ├─ "Docker build failure"
  │  │  └─ → ci-docker-build-healer
  │  ├─ "Parameter mismatch"
  │  │  └─ → ci-parameter-mismatch-healer
  │  └─ "Pattern-based"
  │     └─ → ci-pattern-guardian
  │
  └─ "Need automatic healing?"
     ├─ "YES - auto-fix if possible"
     │  └─ → self-healing-orchestrator-agent
     └─ "NO - analyze only"
        └─ → ci-testing-agent
```

### Recommended Agents by Scenario

| Scenario | Agent | Runtime | Model |
|----------|-------|---------|-------|
| CI failing, 100+ errors | ci-emergency-response-agent | 15m | Sonnet |
| Test import errors | ci-importerror-agent | 5m | Haiku |
| Docker build broken | ci-docker-build-healer | 10m | Sonnet |
| Workflow validation needed | workflow-compliance-guardian | 10m | Haiku |
| Pattern learning | ci-pattern-guardian | 20m | Sonnet |

---

## BRANCH B: TESTING & QUALITY AGENTS

```
"Improve test quality?"
  ├─ "What's the main goal?"
  │  ├─ "Increase coverage"
  │  │  ├─ "Coverage < 50%?"
  │  │  │  └─ → unified-coverage-agent (aggressive gap-fill)
  │  │  ├─ "Coverage 50-80%?"
  │  │  │  └─ → unified-coverage-agent (targeted gap-fill)
  │  │  └─ "Coverage > 80%?"
  │  │     └─ → unified-coverage-agent (maintenance mode)
  │  │
  │  ├─ "Fix failing tests"
  │  │  ├─ "Tests fail inconsistently?"
  │  │  │  └─ → fragile-test-guardian (stabilize)
  │  │  └─ "Tests fail consistently?"
  │  │     └─ → autonomous-test-healer-agent (heal)
  │  │
  │  ├─ "Assess test quality"
  │  │  ├─ "Need mutation testing?"
  │  │  │  └─ → mutation-testing-agent
  │  │  └─ "Analyze test failures?"
  │  │     └─ → test-failure-analyzer-agent
  │  │
  │  └─ "Align tests to code"
  │     └─ → test-alignment-fixer-enhanced
```

### Recommended Agents by Scenario

| Scenario | Agent | Runtime |
|----------|-------|---------|
| Coverage below threshold | unified-coverage-agent | 10m |
| Flaky tests detected | fragile-test-guardian | 15m |
| Tests broken by code change | test-alignment-fixer | 5m |
| Need quality assessment | mutation-testing-agent | 45m |

---

## BRANCH C: SECURITY AGENTS

```
"Ensure security?"
  ├─ "Scope of check?"
  │  ├─ "Full comprehensive audit"
  │  │  └─ → unified-security-scanner (full mode)
  │  ├─ "Pre-commit only"
  │  │  └─ → unified-security-scanner (fast mode)
  │  └─ "Specific vulnerability type"
  │     ├─ "CodeQL alerts"
  │     │  └─ → codeql-alert-resolution-agent
  │     ├─ "Secret leaks"  # pragma: allowlist secret
  │     │  └─ → secret-detection-agent  # pragma: allowlist secret
  │     ├─ "Dependency vulns"
  │     │  └─ → dependency-vulnerability-scanner
  │     └─ "Custom scanning"
  │        └─ → security-audit-agent
  │
  └─ "When do you need it?"
     ├─ "Before every commit"
     │  └─ → unified-security-scanner (pre-commit profile)
     ├─ "Before PR merge"
     │  └─ → unified-security-scanner (standard profile)
     └─ "Before release"
        └─ → unified-security-scanner (comprehensive profile)
```

### Recommended Agents by Scenario

| Scenario | Agent | Runtime | Cost |
|----------|-------|---------|------|
| Quick pre-commit | unified-security-scanner (fast) | 5m | <$0.05 |
| Full PR security | unified-security-scanner (std) | 20m | $0.15 |
| Pre-release audit | unified-security-scanner (full) | 45m | $0.40 |
| CodeQL alerts | codeql-alert-resolution-agent | 25m | $0.20 |

---

## BRANCH D: DOCUMENTATION AGENTS

```
"Manage documentation?"
  ├─ "What's the main issue?"
  │  ├─ "Links are broken"
  │  │  └─ → unified-doc-agent (link validation)
  │  ├─ "Documentation out of sync"
  │  │  └─ → unified-doc-agent (post-merge alignment)
  │  ├─ "Redundant docs"
  │  │  └─ → unified-doc-agent (consolidation)
  │  ├─ "Quality issues"
  │  │  └─ → unified-doc-agent (quality check)
  │  └─ "Terminology inconsistent"
  │     └─ → unified-doc-agent (terminology)
  │
  └─ "When?"
     ├─ "Before merging new docs"
     │  └─ → unified-doc-agent (pre-merge check)
     ├─ "After merge (post-release)"
     │  └─ → unified-doc-agent (alignment)
     └─ "Scheduled maintenance"
        └─ → unified-doc-agent (maintenance)
```

### Recommended Agents by Scenario

| Scenario | Agent | Runtime |
|----------|-------|---------|
| Fix broken links | unified-doc-agent | 8m |
| Post-merge alignment | unified-doc-agent | 15m |
| Consolidate duplication | unified-doc-agent | 20m |
| Quality check | unified-doc-agent | 12m |

---

## BRANCH E: REPOSITORY OPERATIONS

```
"Manage repository?"
  ├─ "What operation?"
  │  ├─ "Analyze PR / merge request"
  │  │  └─ → github-guru-agent
  │  ├─ "Triage issues"
  │  │  └─ → github-guru-agent
  │  ├─ "Clean up repository"
  │  │  └─ → repository-hygiene-agent
  │  ├─ "Reorganize structure"
  │  │  └─ → root-organizer-agent
  │  ├─ "Track dependencies"
  │  │  └─ → dependency-conflict-agent
  │  ├─ "Validate links"
  │  │  └─ → link-validator-agent
  │  └─ "Check code quality"
  │     └─ → code-analysis-agent
  │
  └─ "Scope?"
     ├─ "Single PR"
     │  └─ → github-guru-agent
     ├─ "Entire repository"
     │  └─ → repository-hygiene-agent
     └─ "Cross-repository"
        └─ → recon-scout-agent
```

### Recommended Agents by Scenario

| Scenario | Agent | Runtime |
|----------|-------|---------|
| PR review | github-guru-agent | 5m |
| Issue triage | github-guru-agent | 3m |
| Repo cleanup | repository-hygiene-agent | 10m |
| Dependency check | dependency-vulnerability-scanner | 8m |

---

## BRANCH F: INFRASTRUCTURE & PERFORMANCE

```
"Optimize performance?"
  ├─ "Focus area?"
  │  ├─ "Build / execution speed"
  │  │  ├─ "Need caching strategy?"
  │  │  │  └─ → cache-management-agent
  │  │  └─ "Optimize workflows?"
  │  │     └─ → workflow-optimization-agent
  │  │
  │  ├─ "Runtime performance"
  │  │  └─ → performance-monitor-agent
  │  │
  │  └─ "Regression detection"
  │     └─ → performance-regression-detector
  │
  └─ "When?"
     ├─ "Every build"
     │  └─ → cache-management-agent
     ├─ "Pre-release"
     │  └─ → performance-monitor-agent
     └─ "Continuous monitoring"
        └─ → workflow-health-monitor
```

---

## BRANCH G: ORCHESTRATION & MULTI-AGENT

```
"Coordinate multiple agents?"
  ├─ "Complexity?"
  │  ├─ "Simple sequence (2-3 agents)"
  │  │  └─ → Manual workflow / simple YAML
  │  ├─ "Medium complexity (4-10 agents)"
  │  │  └─ → orchestrator-agent
  │  └─ "Complex multi-domain"
  │     └─ → agent-orchestrator
  │
  └─ "Type?"
     ├─ "CI/CD multi-step"
     │  └─ → self-healing-orchestrator-agent
     ├─ "Security audit"
     │  └─ → orchestrator-agent (parallel 4 agents)
     └─ "Release pipeline"
        └─ → agent-orchestrator (gating + approval)
```

---

## BRANCH H: DOMAIN-SPECIFIC AGENTS

```
"Specialized task?"
  ├─ "Domain?"
  │  ├─ "Machine Learning"
  │  │  ├─ "Validate ML pipeline?"
  │  │  │  └─ → ml-validation-suite-agent
  │  │  └─ "RAG / embeddings?"
  │  │     └─ → rag-index-manager
  │  │
  │  ├─ "Infrastructure as Code"
  │  │  ├─ "Lint Terraform / K8s / CloudFormation?"
  │  │  │  └─ → INFRA_LINTER_AGENT_PROMPT
  │  │  └─ "Validate config?"
  │  │     └─ → config-validator
  │  │
  │  ├─ "Type annotations / Python"
  │  │  ├─ "Fix mypy errors?"
  │  │  │  └─ → mypy-manager-agent
  │  │  └─ "Python 3.12 compatibility?"
  │  │     └─ → python-312-type-fixer
  │  │
  │  └─ "Automation"
  │     ├─ "Google Home scripts?"
  │     │  └─ → google-home-script-agent
  │     └─ "CLI tool?"
  │        └─ → cognitive-brain-cli-agent
```

---

## Complete Decision Matrix

| Goal | Agent | Tier | Runtime | Model | Cost |
|------|-------|------|---------|-------|------|
| Fix CI emergency | ci-emergency-response-agent | Slow | 15m | Sonnet | $0.30 |
| Increase coverage | unified-coverage-agent | Med | 10m | Haiku | $0.05 |
| Security audit | unified-security-scanner | Slow | 25m | Sonnet | $0.20 |
| Fix docs | unified-doc-agent | Med | 12m | Sonnet | $0.10 |
| PR analysis | github-guru-agent | Fast | 5m | Haiku | $0.01 |
| Repo cleanup | repository-hygiene-agent | Med | 10m | Haiku | $0.05 |
| Stabilize tests | fragile-test-guardian | Med | 15m | Sonnet | $0.15 |
| Cache optimization | cache-management-agent | Med | 10m | Haiku | $0.05 |

---

## Metadata

- **Generated:** 2026-06-20T06:52:13.009418
- **Decision Points:** 8 branches, 40+ leaf nodes
- **Authority:** @mbaetiong
- **Next Update:** 2026-06-22T12:00Z
