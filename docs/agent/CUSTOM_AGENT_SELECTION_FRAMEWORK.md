# Custom Agent Selection Framework

> **Document:** Custom Agent Selection & Decision Framework  
> **Version:** 1.0.0  
> **Generated:** 2026-06-26  
> **Purpose:** Provide systematic methodology for selecting and activating appropriate custom agents for specific tasks  

---

## Table of Contents

1. [Overview](#overview)
2. [Selection Criteria Matrix](#selection-criteria-matrix)
3. [Domain-to-Agent Mapping](#domain-to-agent-mapping)
4. [Selection Algorithm](#selection-algorithm)
5. [Capability Tags Reference](#capability-tags-reference)
6. [Anti-Patterns & Pitfalls](#anti-patterns--pitfalls)
7. [Quick Reference Tables](#quick-reference-tables)

---

## Overview

### Purpose

This framework enables systematic selection of the most appropriate custom agent(s) for any given task, based on:
- **Domain classification** (CI/CD, Testing, Documentation, Security, etc.)
- **Capability matching** (what tools the agent has access to)
- **Autonomy level** (what decisions the agent can make independently)
- **Specialization** (narrowly focused vs. generalist agents)

### Key Principle

**Capability-based routing:** Select the agent whose declared capabilities best match the task requirements, with preference for specialized over generalist agents when both are viable.

---

## Selection Criteria Matrix

| Criterion | Values | Impact |
|-----------|--------|--------|
| **Task Domain** | CI/CD, Testing, Docs, Security, Config, RAG, Platform, Session | Primary selector |
| **Complexity Level** | Simple, Moderate, Complex, Multi-phase | Agent autonomy requirement |
| **Parallelization** | Single, Parallel (2-3), Parallel (4+) | Delegation vs. single agent |
| **Specialization** | Specialist, Unified, Generalist | Preference hierarchy |
| **Time Constraint** | Immediate, Standard, Extended | Async vs. sync execution |
| **Autonomy Model** | E (Advisory), D (Capable), C (Approval), B (Escalation), A (Autonomous) | Agent authority level |

---

## Domain-to-Agent Mapping

### CI/CD & Workflow Domain

**Primary Agents:**
- **ci-testing-agent** — Debug CI failures, test failures, import errors, build problems
- **ci-auto-healer-agent** — Apply automated fix patterns and healing loops
- **ci-emergency-response-agent** — Handle blocking CI incidents
- **workflow-ci-fixer** — Fix GitHub Actions syntax and job failures

**Selection Logic:**
- Syntax/YAML error → `workflow-ci-fixer`
- Test/build failure with known patterns → `ci-auto-healer-agent`
- Blocking incident requiring rapid response → `ci-emergency-response-agent`
- Complex multi-failure scenario → `ci-testing-agent` first (diagnosis), then specialists

**Parallel Potential:** ✅ HIGH (delegate 2-3 agents per category)

---

### Testing & Quality Domain

**Primary Agents:**
- **autonomous-test-healer-agent** — Detect and fix failing tests automatically
- **test-alignment-fixer** — Repair tests after API/signature changes
- **unified-coverage-agent** — Monitor coverage, fill gaps, maintain thresholds
- **fragile-test-guardian** — Identify and stabilize flaky tests
- **test-enhancement-agent** — Add edge cases and deepen test coverage
- **mutation-testing-agent** — Assess test suite effectiveness

**Selection Logic:**
- Failing tests → `autonomous-test-healer-agent` (parallel with coverage analysis)
- Flaky/intermittent tests → `fragile-test-guardian`
- Coverage gap → `unified-coverage-agent`
- Post-API-change alignment → `test-alignment-fixer`
- Test quality improvement → `test-enhancement-agent`

**Parallel Potential:** ✅ VERY HIGH (delegate 3-5 agents per cycle)

---

### Documentation Domain

**Primary Agents:**
- **unified-doc-agent** — Canonical entry point for all doc work
- **doc-freshness-checker** — Validate links, timestamps, accuracy
- **link-validator-agent** — Check internal/external link health
- **terminology-consistency-agent** — Enforce consistent terminology
- **post-merge-doc-alignment-agent** — Align GitHub Pages with codebase after merges

**Selection Logic:**
- Consolidation/structural work → `unified-doc-agent`
- Freshness/accuracy validation → `doc-freshness-checker`
- Link validation → `link-validator-agent`
- Terminology audit → `terminology-consistency-agent`
- Post-merge alignment → `post-merge-doc-alignment-agent`

**Parallel Potential:** ✅ MODERATE (2-3 agents for comprehensive doc audit)

---

### Security & Compliance Domain

**Primary Agents:**
- **unified-security-scanner** — Canonical entry point for security scanning
- **code-scanning-remediation-agent** — Fix GHAS/CodeQL findings
- **codeql-alert-resolution-agent** — Resolve specific CodeQL rules
- **dependency-vulnerability-scanner** — Check deps for known vulns
- **security-alert-verification-agent** — Verify and propose fixes
- **secret-detection-agent** — Find accidentally committed secrets

**Selection Logic:**
- Comprehensive security audit → `unified-security-scanner`
- Specific CodeQL alert → `codeql-alert-resolution-agent`
- Dependency vulnerability → `dependency-vulnerability-scanner`
- Secret detection → `secret-detection-agent`
- Code scanning findings → `code-scanning-remediation-agent`

**Parallel Potential:** ✅ HIGH (delegate all 3-4 for full audit)

---

### Configuration & Platform Domain

**Primary Agents:**
- **config-validator** — Validate Hydra/project config correctness
- **config-migration-assistant** — Migrate legacy to Hydra format
- **meta-tensor-validator** — Guard PyTorch initialization patterns
- **cross-platform-filename-validator** — Windows-safe filenames
- **rust-config-validator** — Validate Cargo configuration

**Selection Logic:**
- Config file validation → `config-validator`
- Legacy → modern migration → `config-migration-assistant`
- PyTorch model issues → `meta-tensor-validator`
- Filename cross-platform check → `cross-platform-filename-validator`

**Parallel Potential:** ✅ MODERATE (2-3 per platform update cycle)

---

### Session & Knowledge Domain

**Primary Agents:**
- **agent-orchestrator** — Coordinate multi-agent workflows
- **skills-master-agent** — Manage skills and custom agent lifecycle
- **session-analysis-agent** — Analyze sessions and completion patterns
- **session-log-retrieval-agent** — Recover prior sessions

**Selection Logic:**
- Multi-agent coordination needed → `agent-orchestrator`
- Skill maintenance/scoring → `skills-master-agent`
- Session post-mortem → `session-analysis-agent`
- Context recovery → `session-log-retrieval-agent`

**Parallel Potential:** ⚠️ LOW (orchestration requires sequential coordination)

---

## Selection Algorithm

### Step 1: Classify Task Domain

```
Input: Task description, problem statement
↓
Match to: CI/CD, Testing, Docs, Security, Config, RAG, Platform, Session
↓
Output: Primary domain (may be secondary)
```

### Step 2: Assess Complexity & Scope

```
Simple (single module, <100 loc)
  → Specialist agent preferred
  
Moderate (multiple modules, <1000 loc)
  → Specialist + optional helper
  
Complex (major refactor, >1000 loc)
  → Unified entry point + specialists
  
Multi-phase (staged delivery)
  → Orchestrator + specialists in sequence/parallel
```

### Step 3: Check Parallelization Viability

```
Independent tasks
  → Delegate to 2-4 agents in parallel
  
Sequential dependencies
  → Chain: Agent A → output → Agent B input
  
Blocking operations
  → Single agent until unblock
```

### Step 4: Verify Capability Alignment

```
Does agent's declared capabilities
  match task requirements?
  
YES → Select agent
NO  → Try next candidate
     or escalate to orchestrator
```

### Step 5: Apply Preference Ordering

```
1. Specialist agent (narrowly focused)
2. Unified agent (consolidation point)
3. Generalist agent (fallback)
4. Orchestrator (if multi-agent)
```

---

## Capability Tags Reference

### CI/CD Capabilities

| Tag | Agents | Purpose |
|-----|--------|---------|
| `workflow_syntax` | workflow-ci-fixer | GitHub Actions YAML parsing/fixing |
| `log_retrieval` | ci-log-retrieval-agent | Authenticated log access |
| `pattern_matching` | ci-auto-healer-agent, ci-testing-agent | Known failure pattern detection |
| `test_execution` | ci-testing-agent | Run test suites and analyze |
| `artifact_access` | artifact-monitor-agent | GitHub Actions artifact retrieval |

### Testing Capabilities

| Tag | Agents | Purpose |
|-----|--------|---------|
| `test_debugging` | autonomous-test-healer-agent | Fix failing tests |
| `test_alignment` | test-alignment-fixer | Post-refactor alignment |
| `coverage_analysis` | unified-coverage-agent | Coverage metrics and gaps |
| `flaky_detection` | fragile-test-guardian | Intermittent failure patterns |
| `mutation_testing` | mutation-testing-agent | Test effectiveness assessment |

### Documentation Capabilities

| Tag | Agents | Purpose |
|-----|--------|---------|
| `link_validation` | link-validator-agent | Internal/external link health |
| `freshness_check` | doc-freshness-checker | Timestamp and content accuracy |
| `consolidation` | unified-doc-agent | Multi-file coordination |
| `terminology_audit` | terminology-consistency-agent | Term consistency checking |
| `github_pages` | github-pages-manager | GitHub Pages deployment |

### Security Capabilities

| Tag | Agents | Purpose |
|-----|--------|---------|
| `codeql_analysis` | codeql-alert-resolution-agent | CodeQL rule fixes |
| `sast_scanning` | code-scanning-remediation-agent | Static analysis findings |
| `dependency_check` | dependency-vulnerability-scanner | Known vulnerability detection |
| `secret_detection` | secret-detection-agent | Credential leak detection |
| `audit_trail` | security-audit-agent | Comprehensive security audit |

---

## Anti-Patterns & Pitfalls

### ❌ Pitfall 1: Using Generalist When Specialist Available

```
WRONG:
Task: Fix CodeQL alert
Selection: orchestrator-agent (generalist)
Result: Slower, less authoritative fixes

CORRECT:
Task: Fix CodeQL alert
Selection: codeql-alert-resolution-agent (specialist)
Result: Direct, authoritative remediation
```

**Rule:** Always prefer specialist agents when their capabilities match the task.

---

### ❌ Pitfall 2: Sequential When Parallel Viable

```
WRONG:
delegate → ci-testing-agent (wait for complete)
→ fragile-test-guardian (wait)
→ unified-coverage-agent (wait)
Total time: 3x

CORRECT:
delegate → [ci-testing-agent, fragile-test-guardian, 
            unified-coverage-agent] (parallel)
Total time: 1x + coordination overhead

Use case: Multi-aspect testing audit
```

**Rule:** When tasks are independent, delegate in parallel and collect results.

---

### ❌ Pitfall 3: Missing Prerequisite Checks

```
WRONG:
Task: Fix failing tests
Selection: autonomous-test-healer-agent
(without checking if failures are config/build related)

CORRECT:
Task: Fix failing tests
Precondition check:
  - Is build succeeding? YES
  - Is config valid? YES
  - Environment stable? YES
Selection: autonomous-test-healer-agent
```

**Rule:** Verify prerequisites before delegating to avoid agent thrashing.

---

### ❌ Pitfall 4: Overloading Single Agent

```
WRONG:
"Fix all CI/CD issues" → ci-auto-healer-agent
(tries to handle workflow syntax, test failures, 
 config errors, dependency issues in one pass)

CORRECT:
"Fix all CI/CD issues" → decompose to:
  - workflow-ci-fixer (syntax)
  - ci-auto-healer-agent (patterns)
  - dependency-conflict-agent (versions)
  - config-validator (config)
(delegate in parallel/sequence)
```

**Rule:** Decompose large tasks into agent-sized chunks.

---

## Quick Reference Tables

### Agent Readiness by Domain

| Domain | Primary | Specialist | Readiness |
|--------|---------|------------|-----------|
| CI/CD | ci-auto-healer-agent | 5 available | ✅ Production |
| Testing | unified-coverage-agent | 8 available | ✅ Production |
| Docs | unified-doc-agent | 5 available | ✅ Production |
| Security | unified-security-scanner | 7 available | ✅ Production |
| Config | config-validator | 5 available | ✅ Production |
| RAG | rag-index-manager | 6 available | ✅ Production |
| Platform | cross-platform-filename-validator | 3 available | ⚠️ Partial |
| Session | agent-orchestrator | 4 available | ✅ Production |

### Delegation Patterns

| Pattern | When | Agents | Parallelism |
|---------|------|--------|-------------|
| **Audit** | Comprehensive review | Unified (primary) | ⭐⭐⭐ |
| **Fix** | Specific issue | Specialist | ⭐ |
| **Cascade** | Multi-phase workflow | Orchestrator + Specialists | ⭐⭐ |
| **Coverage** | Multiple failures across domains | 3-4 specialists | ⭐⭐⭐⭐ |

### Time Estimates

| Task Scope | Single Agent | Parallel (2-3) | Parallel (4+) |
|------------|--------------|----------------|---------------|
| Simple fix | 5-10 min | N/A | N/A |
| Moderate audit | 15-30 min | 10-15 min | 8-12 min |
| Complex refactor | 45-90 min | 25-40 min | 15-25 min |
| Multi-domain | 120+ min | 60-80 min | 30-45 min |

---

## Decision Tree Flowchart

```
TASK RECEIVED
    ↓
[Classify Domain] → CI/CD | Testing | Docs | Security | Config | Other
    ↓
[Assess Complexity] → Simple | Moderate | Complex
    ↓
[Check Parallelization] → Independent Tasks | Sequential | Blocking
    ↓
[Domain-Specific Routing]
    ├→ CI/CD:     [Syntax?] → workflow-ci-fixer
    │             [Patterns?] → ci-auto-healer-agent
    │             [Blocking?] → ci-emergency-response-agent
    ├→ Testing:   [Coverage?] → unified-coverage-agent
    │             [Flaky?] → fragile-test-guardian
    │             [Failing?] → autonomous-test-healer-agent
    ├→ Docs:      [Structure?] → unified-doc-agent
    │             [Links?] → link-validator-agent
    │             [Freshness?] → doc-freshness-checker
    ├→ Security:  [CodeQL?] → codeql-alert-resolution-agent
    │             [Secrets?] → secret-detection-agent
    │             [Audit?] → unified-security-scanner
    └→ Config:    [Validation?] → config-validator
                  [Migration?] → config-migration-assistant
    ↓
[Select Primary + Helpers] → Agent(s)
    ↓
[Delegate] → Execute in [Sequential | Parallel]
    ↓
[Collect Results] → Validation
    ↓
TASK COMPLETE
```

---

## Integration with Agent Registry

All agents referenced here are defined in `.github/agents/AGENT_REGISTRY.yaml` with:

- **id**: Unique identifier
- **name**: Human-readable name
- **capability_tags**: List of specialized capabilities
- **autonomy_model**: (E)Advisory → (D)Capable → (C)Approval → (B)Escalation → (A)Autonomous
- **maturity**: development | testing | production
- **description**: What the agent does

**To add new agent to selection framework:**
1. Register in AGENT_REGISTRY.yaml
2. Add capability_tags matching this taxonomy
3. Reference here with category and selection logic
4. Update capability tags reference table

---

## See Also

- [Multi-Agent Interaction Protocol](./CUSTOM_AGENT_INTERACTION_PROTOCOL.md)
- [Agent Workflow Coordination](./CUSTOM_AGENT_COORDINATION_WORKFLOWS.md)
- [Repeatable Processes](./CUSTOM_AGENT_REPEATABLE_PROCESSES.md)
- [AGENT_REGISTRY.yaml](../.github/agents/AGENT_REGISTRY.yaml)
- [Operational Guidelines](./OPERATIONAL_GUIDELINES.md)
