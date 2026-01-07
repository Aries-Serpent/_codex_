# Agent Mapping Implementation Outline

**Purpose**: Detailed technical mapping for implementing the 12-agent ecosystem  
**Date**: 2025-12-31  
**Version**: 1.0.0

---

## Table: Complete Agent Mapping

| Agent ID | Use Case (Aries-Serpent/_codex_) | Scenario | Entry Paths | Triggers (Pro+/Team) | Target Metrics | Key Steps | Outputs | Risks & Guardrails | PDA/AfterMath & Cognitive Brain Updates |
|---|---|---|---|---|---|---|---|---|---|
| ci-testing-agent.v1 | Raise coverage to ≥85% for Phase 9.x | Add 150–200 tests across modules | src/, agents/, scripts/, tests/ | Pro+: MCP test-gen; Team: coverage workflows | coverage_delta ≥ +10%, tests_created 150–200 | Baseline → Generate tests → Run → Validate → Report → Docs update | baseline_coverage.txt, coverage.html, PHASE9_1_TEST_SUMMARY.md | tests-only writes; no src/ changes; timeouts enforced | Persist metrics to Cognitive Brain; AfterMath summary with gaps and next steps |
| flaky-triage-agent.v1 | Quarantine intermittent test failures | Identify and mark flaky tests | tests/*, Actions logs | Team: nightly triage; Pro+: report on demand | flakes_detected ↓, MTTR ↓ | Parse logs → detect flakes → label/quarantine → annotate PRs | flake_index.json, quarantine_list.md | advisory-only; human confirmation for quarantine | Record flake patterns; PDA loop to prioritize fixes |
| dep-upgrade-agent.v1 | Safe dependency bumps | Propose minor/patch upgrades | requirements.txt, .github/agents/requirements.txt | Pro+: plan; Team: open draft PR | CI pass rate 100%, vuln reduction | Analyze deps → plan changes → draft PR → run CI | upgrade_plan.md, draft PR | no auto-merge; prohibit sensitive dirs | Log decisions; AfterMath risks/benefits analysis |
| security-scan-agent.v1 | Advisory SCA/SAST on PRs | Annotate potential issues | src/, agents/, scripts/ | Team: PR CI; Pro+: summarize | findings_count ↓, false_positive_rate ↓ | Run scan → parse SARIF → annotate PR → summary | sarif.json, PR comments | non-blocking unless policy; sanitize outputs | Feed recurring patterns; PDA track mitigations |
| release-gate-agent.v1 | Enforce release readiness | Gate main/release merges | .github/workflows/, repo status | Team: tag/release workflows | gate_pass_rate 100% | Evaluate gates → status report → approvals → notes | gate_status.json, release_notes.md | approvals required; rollback path | Capture gate outcomes; AfterMath learning points |
| doc-reporter-agent.v1 | Publish run summaries & dashboards | Keep docs fresh | docs/system/, docs/testing/ | Team: post-job; Pro+: render | freshness (≤24h), reports_published | Fetch artifacts → generate MD → publish docs | PHASE_TEST_SUMMARY.md, CODEBASE_DASHBOARD.md | docs-only writes; link checks | Append insights; PDA link to next actions |
| code-review-summarizer.v1 | Accelerate PR reviews | Summarize diffs and suggest tests | PR diffs in agents/, src/ | Pro+: PR chat | suggestions_accepted_rate ↑ | Diff → summarize → suggest fixes/tests | review_summary.md, PR comments | advisory-only; no commits | Store heuristics; AfterMath impact report |
| issue-triage-agent.v1 | Label and route issues | Maintain backlog hygiene | .github/ISSUE_TEMPLATE*, issues | Team: nightly; Pro+: ad-hoc | backlog_age ↓, triage_accuracy ↑ | Dedupe → label → assign → summary | triage_summary.md | no closures w/o human review | Update taxonomy; PDA continuous improvement |
| infra-linter-agent.v1 | Harden workflows/secrets | Lint Actions config | .github/workflows/* | Team: CI | violations_count ↓ | Lint → report → PR comments | lint_report.md | advisory-only; permissions minimal | Capture policies; AfterMath common fixes |
| data-rag-helper.v1 | Repo docs Q&A with citations | Onboard contributors | .github/agents/*.md, docs/system/* | Pro+: Q&A | answer_accuracy ≥90%, citation_rate 100% | Index → retrieve → cite → answer | Q&A.md | read-only; must cite sources | Add Q&A to Cognitive Brain; PDA fill knowledge gaps |
| mcp-registry-adapter.v1 | Curate MCP tools for repo | Improve tool discovery | docs/, registry URL | Team: admin; Pro+: install | tools_adopted ↑, validation_pass_rate 100% | Validate → publish catalog → usage | tools_catalog.json | policy gate; admin-only writes | Log catalog changes; AfterMath adoption trends |
| compliance-checker-agent.v1 | Enforce coding standards & coverage | Block non-compliant merges | src/, agents/, scripts/, tests/ | Team: required check | pass_rate ↑, violation_types ↓ | Evaluate rules → status → hints → approvals | compliance_status.json, hints.md | block merges only if configured; override path | Track violations; AfterMath recommendations |

---

## Implementation Mapping Structure

### Per-Agent Implementation Template

Each agent follows this directory structure:

```
.github/agents/{agent-id}/
├── manifest.yaml           # Agent configuration (triggers, metrics, capabilities)
├── cli.py                  # Entry point (standardized interface)
├── requirements.txt        # Dependencies
├── Dockerfile             # Container spec
├── agent/
│   ├── __init__.py
│   ├── perception.py      # PDA: Perception phase
│   ├── decision.py        # PDA: Decision phase
│   ├── action.py          # PDA: Action phase
│   └── aftermath.py       # AfterMath tagging & reporting
├── tests/
│   ├── unit/
│   ├── contract/
│   └── integration/
└── docs/
    ├── README.md          # Quick start
    └── runbook.md         # Operations guide
```

### Standard manifest.yaml Schema

```yaml
name: {Agent Name}
version: 1.0.0
agent_id: {agent-id}.v1
description: {One-line description}
created: YYYY-MM-DD
updated: YYYY-MM-DD

# Use case mapping
use_case:
  title: {Use case from table}
  scenario: {Scenario from table}
  
# Entry points
entry_paths:
  - path/to/files
  - another/path
  
# Trigger configuration
triggers:
  pro_plus:
    - {Trigger description}
  team:
    - {Trigger description}
    
# Target metrics
metrics:
  - name: {metric_name}
    target: {target_value}
    direction: increase|decrease|maintain
    
# Execution steps
steps:
  - name: {Step name}
    description: {What it does}
    timeout: {seconds}
    
# Output specifications
outputs:
  - name: {output_file}
    format: json|markdown|sarif
    location: {path}
    
# Risk management
risks:
  - risk: {Risk description}
    guardrail: {Mitigation}
    
# Cognitive Brain integration
cognitive_brain:
  perception: {What data is collected}
  decision: {How decisions are made}
  action: {What actions are taken}
  aftermath:
    tags:
      - {AfterMath tag type}
    updates:
      - {File to update}
```

---

## Detailed Implementation Maps

### 1. ci-testing-agent.v1 (✅ IMPLEMENTED)

**manifest.yaml**:
```yaml
name: CI Testing Agent
version: 1.0.0
agent_id: ci-testing-agent.v1
use_case:
  title: Raise coverage to ≥85% for Phase 9.x
  scenario: Add 150–200 tests across modules
entry_paths:
  - src/
  - agents/
  - scripts/
  - tests/
triggers:
  pro_plus:
    - MCP test-gen command
  team:
    - Coverage workflow on PR
metrics:
  - name: coverage_delta
    target: "+10%"
    direction: increase
  - name: tests_created
    target: "150-200"
    direction: maintain
steps:
  - name: baseline
    description: Capture baseline coverage
    timeout: 300
  - name: generate
    description: Generate test scaffolds
    timeout: 600
  - name: execute
    description: Run test suite
    timeout: 900
  - name: validate
    description: Validate coverage delta
    timeout: 60
  - name: report
    description: Generate reports
    timeout: 120
outputs:
  - name: baseline_coverage.txt
    format: text
    location: ./
  - name: coverage.html
    format: html
    location: htmlcov/
  - name: PHASE9_1_TEST_SUMMARY.md
    format: markdown
    location: docs/testing/
risks:
  - risk: Unintended src/ modifications
    guardrail: Tests-only write whitelist
  - risk: Infinite test generation
    guardrail: Timeout enforcement (600s)
cognitive_brain:
  perception: Parse coverage reports, identify gaps via AST
  decision: Prioritize critical paths, select test strategy
  action: Generate tests, execute, validate
  aftermath:
    tags:
      - "#AFTERMATH_METRIC"
      - "#AFTERMATH_QUALITY_CHECK"
    updates:
      - docs/system/CODEBASE_DASHBOARD.md
```

**Implementation**: `.github/agents/ci-testing-agent/` (complete)

---

### 2. flaky-triage-agent.v1 (📋 PLANNED)

**manifest.yaml**:
```yaml
name: Flaky Test Triage Agent
version: 1.0.0
agent_id: flaky-triage-agent.v1
use_case:
  title: Quarantine intermittent test failures
  scenario: Identify and mark flaky tests
entry_paths:
  - tests/*
  - .github/workflows/*/logs
triggers:
  team:
    - Nightly triage workflow (cron: 0 2 * * *)
  pro_plus:
    - On-demand report command
metrics:
  - name: flakes_detected
    target: "decrease"
    direction: decrease
  - name: MTTR
    target: "<24h"
    direction: decrease
steps:
  - name: parse_logs
    description: Parse Actions workflow logs
    timeout: 300
  - name: detect_flakes
    description: Identify flaky tests via pass/fail ratio
    timeout: 180
  - name: label_quarantine
    description: Mark tests with @pytest.mark.flaky
    timeout: 120
  - name: annotate_prs
    description: Add flake report to related PRs
    timeout: 60
outputs:
  - name: flake_index.json
    format: json
    location: .reports/flakes/
  - name: quarantine_list.md
    format: markdown
    location: docs/testing/
risks:
  - risk: False positive quarantine
    guardrail: Advisory-only, human confirmation required
  - risk: Missed flaky tests
    guardrail: Configurable sensitivity threshold
cognitive_brain:
  perception: Parse workflow logs, track test history
  decision: Classify flake severity, determine quarantine
  action: Label tests, create quarantine suite
  aftermath:
    tags:
      - "#AFTERMATH_PATTERN_IDENTIFIED"
      - "#AFTERMATH_DECISION"
    updates:
      - .github/flake_registry.yaml
```

**Key Modules**:

```python
# agent/perception.py
class FlakyPerception:
    def parse_workflow_logs(self, runs: List[WorkflowRun]) -> TestHistory:
        """Extract test results from workflow logs."""
        # Parse pytest output from Actions logs
        # Build test history: {test_name: [pass, fail, pass, ...]}
        
# agent/decision.py
class FlakyDecision:
    def classify_flakes(self, history: TestHistory) -> List[FlakyTest]:
        """Classify tests as flaky based on pass/fail ratio."""
        # Threshold: >20% failure rate with inconsistent results
        # Severity: critical (always fails) vs intermittent
        
# agent/action.py
class FlakyAction:
    def quarantine(self, flaky_tests: List[FlakyTest]):
        """Move flaky tests to quarantine suite."""
        # Add @pytest.mark.flaky decorator
        # Create tests/quarantine/ directory
        # Update pytest.ini to skip by default
```

---

### 3. dep-upgrade-agent.v1 (📋 PLANNED)

**manifest.yaml**:
```yaml
name: Dependency Upgrade Agent
version: 1.0.0
agent_id: dep-upgrade-agent.v1
use_case:
  title: Safe dependency bumps
  scenario: Propose minor/patch upgrades
entry_paths:
  - requirements.txt
  - requirements-*.txt
  - .github/agents/*/requirements.txt
triggers:
  pro_plus:
    - Plan upgrade command
  team:
    - Weekly draft PR (cron: 0 0 * * 1)
metrics:
  - name: CI_pass_rate
    target: "100%"
    direction: maintain
  - name: vuln_reduction
    target: "decrease"
    direction: decrease
steps:
  - name: analyze_deps
    description: Check current dependencies
    timeout: 120
  - name: check_updates
    description: Query PyPI for updates
    timeout: 180
  - name: plan_upgrade
    description: Create safe upgrade plan
    timeout: 120
  - name: draft_pr
    description: Create draft PR with changes
    timeout: 60
  - name: validate_ci
    description: Trigger CI validation
    timeout: 1800
outputs:
  - name: upgrade_plan.md
    format: markdown
    location: .reports/upgrades/
  - name: draft_pr
    format: github_pr
    location: null
risks:
  - risk: Breaking changes in minor/patch
    guardrail: No auto-merge, human review required
  - risk: Unintended major version bumps
    guardrail: Strict filtering (minor/patch only)
cognitive_brain:
  perception: Parse requirements files, query PyPI
  decision: Approve safe updates, reject major versions
  action: Generate plan, create draft PR
  aftermath:
    tags:
      - "#AFTERMATH_DECISION"
      - "#AFTERMATH_METRIC"
    updates:
      - .github/dependency_history.yaml
```

**Key Modules**:

```python
# agent/perception.py
class DependencyPerception:
    def scan_requirements(self) -> List[Dependency]:
        """Scan all requirements files."""
        # Find all requirements*.txt
        # Parse pinned versions
        # Check for security vulnerabilities (pip-audit)
        
# agent/decision.py
class DependencyDecision:
    def approve_updates(self, updates: List[Update]) -> List[Update]:
        """Filter to safe minor/patch updates only."""
        # Reject major version changes
        # Prioritize security fixes
        # Check for known breaking changes in changelog
        
# agent/action.py
class DependencyAction:
    def create_upgrade_pr(self, updates: List[Update]):
        """Create draft PR with dependency updates."""
        # Update requirements files
        # Generate upgrade plan markdown
        # Create draft PR via GitHub API
        # Trigger CI validation
```

---

### 4-12. Remaining Agents (Summary Mappings)

#### security-scan-agent.v1
- **Perception**: Run Bandit, Semgrep, parse SARIF
- **Decision**: Filter false positives (ML model), classify severity
- **Action**: Annotate PR, create summary, block if critical

#### release-gate-agent.v1
- **Perception**: Check tests, coverage, docs, approvals
- **Decision**: Evaluate all gates, determine readiness
- **Action**: Generate status, create release notes

#### doc-reporter-agent.v1
- **Perception**: Fetch artifacts from Actions
- **Decision**: Determine what changed, what needs updating
- **Action**: Generate reports, update dashboards

#### code-review-summarizer.v1
- **Perception**: Parse PR diff, analyze changes
- **Decision**: Identify patterns, suggest improvements
- **Action**: Create summary, add PR comments

#### issue-triage-agent.v1
- **Perception**: Parse issue body, check duplicates
- **Decision**: Classify, prioritize, assign labels
- **Action**: Update issue, assign team member

#### infra-linter-agent.v1
- **Perception**: Parse workflow YAML files
- **Decision**: Check against best practices, security rules
- **Action**: Create lint report, add PR comments

#### data-rag-helper.v1
- **Perception**: Index documentation, build embeddings
- **Decision**: Retrieve relevant docs, rank by relevance
- **Action**: Generate answer with citations

#### mcp-registry-adapter.v1
- **Perception**: Scan available MCP tools
- **Decision**: Validate compatibility, check policies
- **Action**: Publish catalog, track adoption

#### compliance-checker-agent.v1
- **Perception**: Scan code for violations (coverage, style, security)
- **Decision**: Classify violations, determine blocking
- **Action**: Generate status, provide remediation hints

---

## Cognitive Brain Integration Points

### Shared Data Structures

All agents write to standardized locations:

```
.codex/cognitive_brain/
├── agents/
│   ├── {agent-id}/
│   │   ├── metrics.yaml          # Agent-specific metrics
│   │   ├── decisions.yaml        # Decision log
│   │   └── patterns.yaml         # Learned patterns
├── sessions/
│   ├── session_{timestamp}.yaml  # Session-specific learnings
└── global/
    ├── metrics_aggregate.yaml    # Cross-agent metrics
    └── knowledge_graph.json      # Relationship graph
```

### AfterMath Reporting Standard

All agents generate AfterMath reports:

```markdown
# AfterMath Report - {agent-id}

**Session ID**: {timestamp}
**Status**: success|failure
**Duration**: {seconds}

## Perception
- Input: {what was analyzed}
- Context: {relevant background}

## Decision
- Strategy: {approach chosen}
- Rationale: {why}

## Action
- Executed: {what was done}
- Outputs: {artifacts created}

## AfterMath Tags
- #AFTERMATH_METRIC: {metric_name} = {value}
- #AFTERMATH_QUALITY_CHECK: {check_result}
- #AFTERMATH_PATTERN_IDENTIFIED: {pattern_description}

## Cognitive Brain Updates
- Updated: {files_modified}
- Added: {new_knowledge}

## Next Steps
- {recommended_actions}
```

---

## Testing Strategy Per Agent

### Unit Tests
- Mock all external APIs (GitHub, PyPI, etc.)
- Test each PDA phase independently
- Cover happy path + error cases
- Aim for 90%+ coverage

### Contract Tests
- Validate manifest.yaml schema
- Verify CLI interface consistency
- Check output format schemas
- Ensure backward compatibility

### Integration Tests
- Run in sandbox repository
- Test full PDA loop end-to-end
- Verify Cognitive Brain updates
- Check artifact generation

---

## Deployment Strategy

### Rollout Plan

**Phase 1: Canary** (1 week)
- Deploy to test repository
- Monitor metrics, gather feedback
- Fix critical issues

**Phase 2: Beta** (2 weeks)
- Deploy to main repository
- Advisory-only mode
- Collect false positive data

**Phase 3: Production** (Ongoing)
- Enable enforcement where configured
- Monitor performance
- Iterate based on learnings

---

## Monitoring & Alerting

### Per-Agent Dashboards

Track:
- Execution frequency
- Success rate
- Average duration
- Error rate
- False positive rate

### Ecosystem Dashboard

Track:
- Total agent executions
- Coverage across agents
- Cognitive Brain growth
- Developer satisfaction

---

## Next Steps for Implementation

1. **Immediate**: Commit this mapping document
2. **Short-term**: Implement security-scan-agent.v1 (highest priority after ci-testing)
3. **Medium-term**: Create agent framework base class (DRY across agents)
4. **Long-term**: Build agent analytics dashboard

---

**Document Status**: ✅ Complete  
**Next Review**: Weekly during Phase 1 (Current Cycle)  
**Owner**: Agent Development Team
