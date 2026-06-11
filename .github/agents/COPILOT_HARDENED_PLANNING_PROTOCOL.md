# Copilot Hardened Planning Protocol (CHPP)

**Version:** 1.0.0
**Effective Date:** 2026-06-11
**Status:** Mandatory — enforced for ALL Copilot planning sessions
**Owner:** `@mbaetiong`
**Enforcement Path:** `.codex/CODEBASE_AGENCY_POLICY.md` § Custom Agent Delegation Mandate

---

## Purpose

This document defines the **Copilot Hardened Planning Protocol (CHPP)** — the canonical, binding operating procedure that every Copilot agent session in this repository MUST follow. Its purpose is to guarantee that:

1. **Custom Agents are always the primary executors**, never ad-hoc shell scripting or manual file edits where a purpose-built agent exists.
2. **Every plan is structured around the agent ecosystem** defined in `AGENT_REGISTRY.yaml` and `AGENT_ECOSYSTEM_MAP.md`.
3. **Session memory and accountability are always updated** via the Cognitive Brain and PDA Loop after each task.
4. **No plan silently bypasses** specialized tooling already built and maintained in this repository.

---

## 1. Complete Agent Ecosystem Reference

The repository currently has **153+ active custom agents** (145 listed in `AGENT_REGISTRY.yaml` v2.0.0) spanning eight architectural layers. The agent ecosystem is the authoritative source of truth for how any category of work should be delegated.

### 1.1 Orchestration Layer

| Agent | Purpose | File |
|-------|---------|------|
| `orchestrator-agent` | Routes tasks via FAISS + `AGENT_REGISTRY.yaml` capability matching | `orchestrator-agent.md` |
| `agent-orchestrator` | Coordinates multi-agent workflows and task distribution | `agent-orchestrator.md` |
| `cognitive-ooda-loop-agent` | Full OODA loop (Observe→Orient→Decide→Act) via FastAPI `:8765` | `cognitive-ooda-loop-agent.md` |
| `skills-master-agent` | Discovers, installs, scores, and deploys new Skills and Agents | `skills-master-agent.md` |

### 1.2 CI/CD & Build Layer

| Agent | Purpose | File |
|-------|---------|------|
| `ci-testing-agent` | Debug pipelines, test failures, P19 shadow imports | `ci-testing-agent.md` |
| `ci-auto-healer-agent` | Detect + heal CI failures using embedded fix patterns | `ci-auto-healer-agent.md` |
| `ci-failure-resolution-agent` | Diagnose and resolve pipeline failures with self-healing loops | `ci-failure-resolution-agent.md` |
| `ci-emergency-response-agent` | Rapid diagnosis for blocking failures preventing merges | `ci-emergency-response-agent.md` |
| `ci-triage-pipeline-agent` | Triage CI failures by severity + route to resolution agents | `ci-triage-pipeline-agent.md` |
| `ci-pattern-guardian` | Monitor, record, enforce CI pattern knowledge graph | `ci-pattern-guardian.md` |
| `ci-health-alert-agent` | Auto-responds to `ci-health-alert` GitHub issues | `ci-health-alert-agent.md` |
| `artifact-monitor-agent` | Monitor CI/CD artifact health, track outputs, pattern recognition | `artifact-monitor-agent.md` |
| `ci-importerror-agent` | Diagnose/remediate ImportError/ModuleNotFoundError | `ci-importerror-agent.md` |
| `ci-docker-build-healer` | Fix Docker build failures in multi-stage CI Dockerfiles | `ci-docker-build-healer.md` |
| `ci-parameter-mismatch-healer` | Detect + fix reusable workflow caller/callee mismatches | `ci-parameter-mismatch-healer.md` |
| `ci-optimization-agent` | Analyze + optimize pipeline performance | `ci-optimization-agent.md` |
| `workflow-ci-fixer` | Fix YAML syntax errors, job failures, configuration issues | `workflow-ci-fixer.agent.md` |
| `workflow-management-agent` | Manage workflow operations (create, update, consolidate) | `workflow-management-agent.md` |
| `workflow-compliance-guardian` | Enforce branch-scoped concurrency + timeout rules | `workflow-compliance-guardian.md` |
| `workflow-analytics-agent` | Analyze workflow performance, trends, optimization opportunities | `workflow-analytics-agent.md` |
| `workflow-optimization-agent` | Optimize for parallelism, caching, execution efficiency | `workflow-optimization-agent.md` |
| `workflow-health-monitor` | Monitor workflow health, alert on failures and slowdowns | `workflow-health-monitor.agent.md` |
| `self-healing-orchestrator-agent` | Orchestrate autonomous self-healing loops (RP-001 through RP-004+) | `self-healing-orchestrator-agent.md` |

### 1.3 Security Layer

| Agent | Purpose | File |
|-------|---------|------|
| `unified-security-scanner` | Comprehensive SAST + dependency + secrets detection | `unified-security-scanner.md` | <!-- pragma: allowlist secret -->
| `security-audit-agent` | Full security audit: SAST, CVEs, compliance checks | `security-audit-agent.md` |
| `code-scanning-remediation-agent` | Fix GitHub Advanced Security + static analysis alerts | `code-scanning-remediation-agent.md` |
| `codeql-alert-resolution-agent` | Resolve CodeQL alerts via Playwright scraping + auto-fix pipeline | `codeql-alert-resolution-agent.md` |
| `secret-detection-agent` | Detect accidentally committed secrets and provide remediation | `secret-detection-agent.md` | <!-- pragma: allowlist secret -->
| `dependency-vulnerability-scanner` | Scan project dependencies for known CVEs | `dependency-vulnerability-scanner.agent.md` |
| `dependency-security-review-agent` | Review dependencies for vulnerabilities + recommend upgrades | `dependency-security-review-agent.md` |
| `bridge-security-monitor` | Monitor IPC bridge security, detect unauthorized access | `bridge-security-monitor.agent.md` |

### 1.4 Testing Layer

| Agent | Purpose | File |
|-------|---------|------|
| `unified-coverage-agent` | Monitor thresholds, fill gaps, maintain CI enforcement, drive roadmap | `unified-coverage-agent.md` |
| `autonomous-test-healer-agent` | Auto-detect, diagnose, and fix failing tests | `autonomous-test-healer-agent.md` |
| `fragile-test-guardian` | Detect and stabilize flaky tests | `fragile-test-guardian.md` |
| `mutation-testing-agent` | Mutation testing to assess test suite effectiveness | `mutation-testing-agent.md` |
| `qa-walkthrough-agent` | Comprehensive QA walkthroughs (quality, security, performance, testing) | `qa-walkthrough-agent.md` |
| `test-enhancement-agent` | Enhance test quality by adding edge cases and improving assertions | `test-enhancement-agent.md` |
| `test-failure-analyzer-agent` | Analyze test failures to identify root causes | `test-failure-analyzer-agent.md` |
| `test-alignment-fixer-enhanced` | Fix test alignment issues after API changes | `test-alignment-fixer-enhanced.md` |
| `test-alignment-fixer` | Fix test alignment issues after refactors/signature updates | `test-alignment-fixer.agent.md` |
| `test-pattern-guardian` | Guard against anti-patterns in tests | `test-pattern-guardian.md` |
| `integration-test-runner` | Run integration tests across services, validate e2e workflows | `integration-test-runner.agent.md` |
| `tokenization-coverage-agent` | Improve coverage for tokenization module | `tokenization-coverage-agent.md` | <!-- pragma: allowlist secret -->

### 1.5 Documentation Layer

| Agent | Purpose | File |
|-------|---------|------|
| `unified-doc-agent` | Unified documentation management across all formats | `unified-doc-agent.md` |
| `documentation-consolidator` | Consolidate redundant docs, eliminate duplication | `documentation-consolidator.md` |
| `documentation-quality-agent` | Assess and improve doc quality (completeness, accuracy) | `documentation-quality-agent.md` |
| `doc-freshness-checker` | Validate links, timestamps, accuracy against current code | `doc-freshness-checker.agent.md` |
| `link-validator-agent` | Validate internal/external links, fix broken references | `link-validator-agent.md` |
| `post-merge-doc-alignment-agent` | Align docs with codebase after merging promotion branches | `post-merge-doc-alignment-agent.md` |
| `doc-refactor-test-agent` | Refactor and test documentation for accuracy and structure | `doc-refactor-test-agent.md` |
| `github-pages-manager` | Manage GitHub Pages deployment, configure themes, sync live docs | `github-pages-manager.md` |
| `terminology-consistency-agent` | Enforce consistent use of terminology across docs/code/APIs | `terminology-consistency-agent.md` |
| `tracking-document-qa-agent` | QA tracking documents for accuracy, completeness, consistency | `tracking-document-qa-agent.md` |
| `claim-verification-agent` | Verify claims in commit messages, PRs, and documentation | `claim-verification-agent.md` |

### 1.6 Repository Management Layer

| Agent | Purpose | File |
|-------|---------|------|
| `repository-hygiene-agent` | Clean up stale files, maintain overall repo hygiene | `repository-hygiene-agent.md` |
| `root-organizer-agent` | Safely reorganize root directory in incremental steps with rollback | `root-organizer-agent.md` |
| `repository-organization-agent` | Organize and restructure repository layout | `repository-organization-agent.md` |
| `reference-updater-agent` | Atomically update cross-repo references, import paths, symbol names | `reference-updater-agent.md` |
| `cross-platform-filename-validator` | Validate filenames for Windows/Linux/macOS compatibility | `cross-platform-filename-validator.md` |
| `packaging-validation-agent` | Validate pyproject.toml, dependency lock files, PEP 621 compliance | `packaging-validation-agent.md` |
| `repo-var-sync-agent` | Bidirectionally sync `.codex/agent_context.json` with GitHub repo variables | `repo-var-sync-agent.md` |
| `datetime-modernizer` | Modernize datetime handling to timezone-aware objects | `datetime-modernizer.agent.md` |
| `python-312-type-fixer` | Fix Python 3.12 type annotation and compatibility issues | `python-312-type-fixer.md` |
| `json-serialization-expert` | Diagnose and fix JSON serialization/deserialization issues | `json-serialization-expert.md` |
| `mypy-manager-agent` | Type-checking health guardian for the codebase | `mypy-manager-agent.md` |

### 1.7 Session / Cognitive Brain Layer

| Agent | Purpose | File |
|-------|---------|------|
| `cognitive-brain-session-injector` | Inject recency-ranked patterns + store_memory facts at session start | `cognitive-brain-session-injector.md` |
| `session-analysis-agent` | Analyze sessions, verify commits, track objectives, force-archive stale sessions | `session-analysis-agent.md` |
| `memory-sync-agent` | Consolidate STM→LTM at 80% capacity, prune stale LTM | `memory-sync-agent.md` |
| `rag-index-manager` | Manage RAG index: build, update, query, maintain embeddings | `rag-index-manager.agent.md` |
| `rag-freshness-loop-agent` | Maintain RAG index freshness via incremental updates | `rag-freshness-loop-agent.md` |
| `rag-meta-tensor-guardian` | Guard RAG tensor ops against meta-tensor materialization issues | `rag-meta-tensor-guardian.md` |
| `rag-meta-tensor-regression-agent` | Prevent regressions in RAG meta-tensor handling | `rag-meta-tensor-regression-agent.md` |
| `rag-module-management-agent` | Manage RAG module lifecycle (indexing, retrieval, updates) | `rag-module-management-agent.md` |
| `cognitive-brain-cli-agent` | Operate the Cognitive Brain CLI console | `cognitive-brain-cli-agent.md` |
| `cognitive-ooda-loop-agent` | Full OODA loop execution via FastAPI | `cognitive-ooda-loop-agent.md` |

### 1.8 Governance & Compliance Layer

| Agent | Purpose | File |
|-------|---------|------|
| `unified-governance-gate` | Enforce unified governance policies across PRs and deployments | `unified-governance-gate.md` |
| `owner-approval-guard` | Enforce owner approval for sensitive autonomous operations | `owner-approval-guard.agent.md` |
| `policy-coach-agent` | Coach contributors on repo policies, coding standards, compliance | `policy-coach-agent.md` |
| `agent-iq-scoring-gate` | Gate and score agent IQ metrics before deployment | `agent-iq-scoring-gate.md` |
| `codebase-health-guardian` | Monitor and maintain overall codebase health | `codebase-health-guardian.md` |
| `pr-check-remediation-agent` | Remediate failing PR checks with automated fixes | `pr-check-remediation-agent.md` |
| `pr-test-infrastructure-fixer` | Fix broken test infrastructure in PRs | `pr-test-infrastructure-fixer.md` |
| `branch-divergence-resolution-agent` | Detect, classify, and resolve branch divergence | `branch-divergence-resolution-agent.md` |

---

## 2. Hardened Planning Rules (Hard Rules — CI-Enforced)

These three rules are **mandatory** for all Copilot agent planning sessions. Violating them is equivalent to violating the Codebase Agency Policy (§ Custom Agent Delegation Mandate).

---

### Rule 1: Agent-First Delegation (AFD)

**Statement:** Every task category that has a dedicated Custom Agent MUST be delegated to that agent via the `task` tool. Manual shell scripting or direct file editing in place of an available Custom Agent is a policy violation.

**Decision Checklist:**

```
Before writing ANY bash command, grep, or file edit, ask:
  → Does a Custom Agent exist for this category of work?
  → Consult AGENT_SELECTION_GUIDE.md Quick Decision Tree first.

If YES → Use task(agent_type="...", mode="background")
If NO  → Proceed with direct tooling AND document why no agent covers this case
```

**Examples of Correct Delegation:**

| Task Category | ❌ Do NOT do | ✅ Delegate to |
|---------------|-------------|---------------|
| Fix test coverage gap | `pytest --cov` + manually add tests | `unified-coverage-agent` |
| Fix CI import error | `grep` for import + manual fix | `ci-importerror-agent` |
| Find security vulnerability | `grep -r "eval("` | `unified-security-scanner` |
| Update stale docs link | `sed -i` on markdown files | `link-validator-agent` |
| Fix CodeQL alert | Manually edit flagged code | `codeql-alert-resolution-agent` |
| Resolve dep conflicts | `pip install --upgrade ...` | `dependency-conflict-agent` |
| Fix workflow YAML | Direct YAML edits | `workflow-ci-fixer` |
| Clean stale repo files | `find . -delete` | `repository-hygiene-agent` |

**Exception Clause:** Direct tooling is permitted ONLY when:
- No agent covers the exact capability needed (document this gap in `.github/agents/GAP_ANALYSIS.md`).
- The task is trivially scoped to 1-3 file lines and completing it directly is faster than agent invocation.
- An agent has already been dispatched and its targeted output requires a minor follow-up edit.

---

### Rule 2: Mandatory Session Pre-Load Validation (MSPV)

**Statement:** Before executing ANY plan, the Copilot MUST complete the following validation sequence in order:

```
Step 1: Verify environment integrity
  → Read .codex/agent_context.json
  → Confirm COPILOT_AGENT_CCA_VERSION_LOCK=stable
  → Confirm COPILOT_AGENT_DEDUPLICATION_ENABLED=true
  → Confirm COPILOT_AGENT_TURN_ISOLATION_ENABLED=true

Step 2: Load policy and accountability state
  → Re-read .codex/CODEBASE_AGENCY_POLICY.md
  → Re-read docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md
  → Check last 5 lines of .codex/aftermath/pda_iterations.jsonl

Step 3: Resolve applicable agents
  → Consult .github/agents/AGENT_REGISTRY.yaml capability_tags
  → Identify the minimum set of agents whose capability_tags cover the task
  → If more than one agent is viable, prefer the one with maturity: production

Step 4: Confirm no deferral intent
  → Scan your planned response for any of the phrases listed in AGENTS.md
    "Deferral Language Trigger Protocol"
  → If found: STOP. Remove phrase. Fix the issue now.
```

---

### Rule 3: CTEP-Aligned Plan Structure (CAPS)

**Statement:** Every plan produced by a Copilot agent session MUST follow the CTEP (Copilot Task Execution Protocol) structure, with each task explicitly bound to an `agent_type`.

**Required Plan Format:**

```markdown
## 📊 Task Execution Progress

### Phase N: [Phase Name] — X% Complete
- [ ] Task N.1: [Description] → agent_type: `<agent_id>` ⏳ PENDING
- [x] Task N.2: [Description] → agent_type: `<agent_id>` ✅ COMPLETE

## 🔍 Agent Binding Map
| Task | Agent | Mode | Priority |
|------|-------|------|----------|
| Fix import error | ci-importerror-agent | background | P0 |
| Fill coverage gaps | unified-coverage-agent | background | P1 |

## ✅ Completion Summary
Total Tasks: X | Completed: X ✅ | Skipped: 0 ❌
CTEP Compliance: ✅ PASS
CAD-Mandate Compliance: ✅ PASS (all tasks delegated to agents)
```

**Forbidden Plan Patterns:**

```
❌ "I will run `pytest tests/` to check coverage"
   → Must be: task(agent_type="unified-coverage-agent", ...)

❌ "I'll grep for the failing import and fix it"
   → Must be: task(agent_type="ci-importerror-agent", ...)

❌ "Let me update the docs manually"
   → Must be: task(agent_type="unified-doc-agent", ...)
```

---

## 3. Implementation Workflow (Four Phases)

All plans produced by Copilot agents MUST follow this four-phase workflow.

### Phase 1: Diagnosis & Routing

**Goal:** Map the problem statement to the narrowest set of applicable Custom Agents.

```
1. Read the problem statement.
2. Identify the primary category (CI/CD, Security, Testing, Documentation,
   Repository, Session/Cognitive, Governance).
3. Open AGENT_ECOSYSTEM_MAP.md and find the matching layer.
4. Open AGENT_SELECTION_GUIDE.md Quick Decision Tree for the category.
5. Identify the primary agent and any secondary chain agents.
6. Record the binding in the Agent Binding Map (see Rule 3 format above).
```

**Routing Examples:**

| Problem | Primary Agent | Secondary Chain |
|---------|--------------|-----------------|
| CI fails with `ImportError` | `ci-importerror-agent` | `ci-testing-agent` |
| Test coverage drops below threshold | `unified-coverage-agent` | `test-enhancement-agent` |
| CodeQL alert raised on PR | `codeql-alert-resolution-agent` | `code-scanning-remediation-agent` |
| Documentation link is broken | `link-validator-agent` | `unified-doc-agent` |
| Workflow YAML fails to parse | `workflow-ci-fixer` | `workflow-compliance-guardian` |
| Dependency CVE discovered | `dependency-vulnerability-scanner` | `dependency-security-review-agent` |
| Flaky test causing intermittent failures | `fragile-test-guardian` | `autonomous-test-healer-agent` |

---

### Phase 2: Parallel Task Dispatch

**Goal:** Launch agents in parallel using the `task` tool with `mode: "background"`, minimizing wall-clock time.

**Execution Pattern:**

```python
# Launch parallel agents
agent_ids = [
    task(agent_type="security-audit-agent", mode="background",
         prompt="Scan for CVEs and CodeQL violations introduced in PR #NNNN"),
    task(agent_type="unified-coverage-agent", mode="background",
         prompt="Identify and fill coverage gaps in src/codex/..."),
]

# Wait for completion
for agent_id in agent_ids:
    result = read_agent(agent_id=agent_id, wait=True, timeout=120)
    # Process result...
```

**Parallelisation Rules:**
- Agents that operate on **different file paths** MUST be dispatched in parallel.
- Agents that have an explicit **chain dependency** (e.g., security scan → remediation) are dispatched sequentially.
- Always set `mode="background"` unless the agent result is needed to determine the next call's parameters.

---

### Phase 3: Automated Quality & Security Validation

**Goal:** Every completed plan MUST pass automated validation before a PR is raised.

```
1. After all agents complete, call parallel_validation(
       prTitle="...",
       prDescription="...",
       trivialChangeDeclaration={
           "codeql": {"isTrivial": false, "reason": "..."}
       }
   )

2. Review ALL feedback from Code Review and CodeQL Security Scan.

3. For each finding:
   - VALID finding with required changes → Fix it and re-dispatch the appropriate agent.
   - FALSE POSITIVE → Document in commit message why it is a false positive.
   - SECURITY VULNERABILITY → MUST be fixed before PR creation. No exceptions.

4. After merge, trigger post-merge doc alignment:
   task(agent_type="post-merge-doc-alignment-agent", mode="background",
        prompt="Align GitHub Pages and docs with codebase state after merge of PR #NNNN")
```

---

### Phase 4: Memory & Accountability Updates

**Goal:** Record agent utilization and outcomes in the Cognitive Brain for cross-session continuity.

```
1. Call store_memory() for any NEW repository conventions discovered during this session.
   - subject: "[category]"
   - fact: "[concise statement]"
   - citations: "[file:line]"
   - scope: "repository"

2. Update .codex/aftermath/pda_iterations.jsonl with:
   {
     "session_id": "<CODEX_SESSION_ID>",
     "timestamp": "<ISO8601Z>",
     "agents_used": ["<agent_id_1>", "<agent_id_2>"],
     "patterns_resolved": ["<pattern_1>"],
     "outcomes": {"<agent_id>": "success|partial|failed"}
   }

3. Delegate memory consolidation:
   task(agent_type="memory-sync-agent", mode="background",
        prompt="Consolidate STM→LTM and tag patterns from session <CODEX_SESSION_ID>")

4. Delegate session analysis:
   task(agent_type="session-analysis-agent", mode="background",
        prompt="Verify commits and update AGENT_ACCOUNTABILITY_REPORT.md for session <CODEX_SESSION_ID>")
```

---

## 4. Key Technologies Reference

| Technology | Role | Where Used |
|-----------|------|------------|
| Python 3.12+ | Agent implementation runtime | `src/agent.py` in every agent directory |
| Node.js 22+ | Playwright-based agents, GitHub Pages | `codeql-alert-resolution-agent`, `github-pages-manager` |
| FAISS | Capability-tag semantic search for routing | `orchestrator-agent`, `AGENT_REGISTRY.yaml` |
| SQLite | Agent Memory (STM/LTM), session logs | `.codex/session_logs.db`, `memory-sync-agent` |
| Click CLI | Standard CLI interface for all agent `src/agent.py` | `.github/agents/.template/src/agent.py` |
| Hydra | Configuration management | `configs/`, `agent_config.yaml` |
| Black + Ruff + isort | Code quality enforcement in every agent | `pre-commit` hooks |
| GitHub Actions | Deployment and trigger mechanism | `.github/workflows/` |
| `IntegratedEvolutionSystem` | CAPI deduplication for multi-turn loops | `.github/copilot-evolution/integrated_system.py` |

---

## 5. Agent Template Structure

All agents follow the standard template at `.github/agents/.template/`:

```
.github/agents/<agent-name>/
├── README.md           # Purpose, capabilities, usage, integration points
├── CHANGELOG.md        # Version history
├── prompts/
│   ├── main.md         # Primary directive: role, capabilities, Always/Never rules
│   ├── examples.md     # Usage examples
│   └── advanced.md     # Advanced scenarios
├── src/
│   ├── __init__.py
│   └── agent.py        # Click CLI implementation
├── tests/
│   ├── __init__.py
│   ├── test_agent.py
│   └── test_integration.py
└── config/
    └── agent_config.yaml  # Configuration schema + integration flags
```

**Single-file agents** (`.md` only) follow the condensed format:

```markdown
---
name: <agent-id>
version: x.y.z
---
# <Agent Name>
## Overview | ## Capabilities | ## Always/Never | ## Integration Pattern
```

---

## 6. Agent Interaction Patterns

### Pattern A: CI Self-Healing Cascade

```
iterative-self-healing-ci.yml
  → ci-auto-healer-agent        (apply known fix patterns)
  → [if exhausted]
  → ci-failure-resolution-agent (deep diagnosis)
  → ci-emergency-response-agent (if blocking)
```

### Pattern B: PR Quality Gate

```
agent-auth-delegation.yml
  → cognitive-preflight (REQ checks)
  → pr-body-checkpoint-guardian
  → unified-governance-gate
  → activate-delegation → Copilot agent session
```

### Pattern C: Security Scan Pipeline

```
PR push event
  → code-scanning-remediation-agent (CodeQL alerts)
  → codeql-alert-resolution-agent   (targeted fixes)
  → dependency-vulnerability-scanner (CVE check)
  → unified-security-scanner        (full SAST)
```

### Pattern D: Documentation Freshness

```
doc-freshness-checker
  → link-validator-agent
  → documentation-quality-agent
  → documentation-consolidator  (if duplicates found)
  → post-merge-doc-alignment-agent (after merge)
```

### Pattern E: Coverage Roadmap

```
unified-coverage-agent
  → test-enhancement-agent      (add edge cases)
  → test-alignment-fixer        (fix API mismatches)
  → mutation-testing-agent      (assess test effectiveness)
  → fragile-test-guardian       (stabilize flaky tests)
```

---

## 7. Quick Reference: Task → Agent Lookup

```
CI pipeline failing            → ci-testing-agent → ci-failure-resolution-agent
CI import error                → ci-importerror-agent
CI emergency (blocking PR)     → ci-emergency-response-agent
CI workflow YAML broken        → workflow-ci-fixer
Docker build failing           → ci-docker-build-healer
Test coverage below threshold  → unified-coverage-agent
Flaky/intermittent test        → fragile-test-guardian
Test assertions outdated       → test-alignment-fixer-enhanced
New test cases needed          → test-enhancement-agent
CodeQL security alert          → codeql-alert-resolution-agent
Secret detected in code        → secret-detection-agent  # pragma: allowlist secret
Dependency CVE found           → dependency-vulnerability-scanner
Full security audit            → security-audit-agent
Doc link broken                → link-validator-agent
Stale documentation            → doc-freshness-checker
Duplicate documentation        → documentation-consolidator
Post-merge doc drift           → post-merge-doc-alignment-agent
Stale repository files         → repository-hygiene-agent
Root directory reorganization  → root-organizer-agent
Import path refactor           → reference-updater-agent
Dependency version conflict    → dependency-conflict-agent
Python 3.12 type errors        → python-312-type-fixer
mypy type check failures       → mypy-manager-agent
Windows filename compatibility → cross-platform-filename-validator
RAG index stale                → rag-freshness-loop-agent
Session memory consolidation   → memory-sync-agent
Session objective tracking     → session-analysis-agent
Agent capability routing       → orchestrator-agent
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-06-11 | Initial creation — canonical CHPP for all Copilot sessions |
