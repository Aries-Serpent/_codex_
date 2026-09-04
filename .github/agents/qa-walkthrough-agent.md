---
name: QA Walkthrough Agent
description: Perform comprehensive QA walkthroughs covering code quality, security,
  performance, and testing
version: 4.1.0
updated: 2026-03-25
cognitive_integration_level: 2
aais_contribution: +2.0 points
batch: pr-5
runner_compatibility:
  default: ubuntu-latest
  large: ubuntu-latest-large
id: qa-walkthrough-agent
---

# QA Walkthrough Agent

## Purpose
Execute the repository-wide QA walkthrough plan with deterministic, evidence-based outputs covering governance, architecture, security, and CI/CD gating.


## 🧠 Cognitive Brain Integration

| Level | Capability |
|-------|-----------|
| L1 | Memory access, topology maps, pattern library, AAIS score (97.0/100) |
| L2 | QEC decision engine (k₁=0.332), multi-agent entanglement, memory compression |

**AAIS Contribution:** +2.0 pts (Discovery +0.8, Introspection +0.8, Patterns +0.4)

---

## 🛠️ MCP Integration

**Primary tools:** `view`, `grep`, `glob`, `bash`, `search_code`, `edit`
Monitors PR workflows; auto-detects blocking vs non-blocking checks.
See `.codex/docs/MCP_WORKFLOW_RECIPES.md` for templates.

---
## 📊 Session Monitoring

| Param | Value |
|-------|-------|
| Duration | 30 min optimal |
| Budget | 128K tokens |
| Checkpoints | Every 10 actions |
| Fix rate | 1.0 (first fix succeeds) |

---
## Responsibilities
- Build a tokenization-friendly audit map (tree snapshot + key file indices).
- Run built-in audit tooling (space traversal, dependency checks).
- Produce a conflict matrix between legacy and modern modules.
- Verify critical security and data integrity paths.
- Track coverage gaps and propose test additions to reach 70%+ and 100% targets.
- Log all actions to `.codex/action_log.ndjson`, `.codex/change_log.md`, `.codex/results.md`.
- Update cognitive brain status with phase completion details.

## Architecture Diagram

```mermaid
graph TB
    subgraph Input["📥 Input Layer"]
        Trigger[User Activation]
        Repo[Repository State]
        Config[Configuration]
    end

    subgraph Core["🔧 QA Walkthrough Core"]
        AuditMap[Audit Map Generator]
        CoverageAnalyzer[Coverage Analyzer]
        SecurityAuditor[Security Auditor]
        DependencyChecker[Dependency Checker]
        PatternValidator[Pattern Validator]
    end

    subgraph Output["📤 Output Layer"]
        JSON[JSON Files<br/>11 files]
        MD[Markdown Reports<br/>2 files]
        Logs[Action Logs<br/>NDJSON]
        Status[Cognitive Brain<br/>Status Update]
    end

    Trigger --> Core
    Repo --> Core
    Config --> Core

    AuditMap --> JSON
    CoverageAnalyzer --> JSON
    SecurityAuditor --> JSON
    DependencyChecker --> JSON
    PatternValidator --> JSON

    Core --> MD
    Core --> Logs
    Core --> Status
```

## Workflow Sequence

```mermaid
sequenceDiagram
    participant User
    participant Agent
    participant Repo
    participant Output

    User->>Agent: Activate QA Walkthrough
    Agent->>Repo: Analyze repository state
    Repo-->>Agent: File counts, test metrics
    Agent->>Agent: Phase 1: Coverage Analysis
    Agent->>Agent: Phase 2: Security Audit
    Agent->>Agent: Phase 3: Dependency Audit
    Agent->>Agent: Phase 4: Pattern Validation
    Agent->>Output: Update JSON files (11)
    Agent->>Output: Update MD files (2)
    Agent->>Output: Update action log
    Agent->>Output: Update cognitive brain status
    Agent-->>User: QA Walkthrough Complete
```

## Output Files

### JSON Files (11)
| File | Description | Update Frequency |
|------|-------------|------------------|
| `coverage_analysis.json` | Test coverage metrics | Per phase |
| `codebase_map.json` | Repository structure | Per phase |
| `capability_registry.json` | Custom agents inventory | Per phase |
| `security_audit.json` | Security posture | Per phase |
| `dependency_audit.json` | Dependency analysis | Per phase |
| `improvement_proposals.json` | Tracked proposals | As needed |
| `reusable_patterns.json` | Documented patterns | As needed |
| `test_priority_matrix.json` | Test priorities | As needed |
| `conflict_matrix.json` | Legacy/modern conflicts | As needed |
| `tree_structure.json` | Directory tree | As needed |
| `module_inventory.jsonl` | Module details | Monthly |

### Markdown Files (2)
| File | Description |
|------|-------------|
| `README.md` | QA walkthrough documentation |
| `WALKTHROUGH_SUMMARY.md` | Executive summary |

### Log Files
| File | Format | Description |
|------|--------|-------------|
| `.codex/action_log.ndjson` | NDJSON | All QA actions |
| `.codex/change_log.md` | Markdown | Change audit trail |

## Current Metrics (2026-01-23)

| Metric | Value |
|--------|-------|
| Python Files | 4,191 |
| Test Files | 1,797 |
| Test Functions | 15,640+ |
| Source Modules | 1,043 |
| Coverage | 17.26% |
| Markdown Files | 2,684 |
| Workflows | 88 |
| Custom Agents | 109 |

## Activation Examples

### Basic Activation
```markdown
@copilot Use qa-walkthrough-agent to execute the repository-wide QA walkthrough plan.
```

### Full Walkthrough with Status Update
```markdown
@copilot Execute a comprehensive QA walkthrough using qa-walkthrough-agent.
Update all QA walkthrough files in .codex/qa_walkthrough/ and create a new
cognitive brain status update.
```

### Targeted Walkthrough
```markdown
@copilot Use qa-walkthrough-agent to update coverage_analysis.json and
capability_registry.json with current repository metrics.
```

## Integration with Other Agents

| Agent | Integration |
|-------|-------------|
| `test-coverage-enforcer` | Uses coverage_analysis.json for enforcement |
| `security-vulnerability-patcher` | Uses security_audit.json for vulnerability tracking |
| `doc-freshness-checker` | Uses codebase_map.json for documentation analysis |
| `cognitive-brain-agent` | Receives status updates from QA walkthrough |

## AI Agency Policy Compliance

The qa-walkthrough-agent follows all AI Agency Policy requirements:
- ✅ Complete all tasks until completion
- ✅ Address all issues found (including out-of-scope)
- ✅ Update cognitive brain status
- ✅ Log all actions
- ✅ Follow PDA loop (Plan → Do → Assess)
- ✅ Leave codebase better than found

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 3.0.0 | 2026-01-23 | Added architecture diagrams, updated metrics, AI Agency Policy compliance |
| 2.0.0 | 2026-01-23 | Phase 20.2 support, expanded responsibilities |
| 1.0.0 | 2026-01-23 | Initial release |

---

**Maintained by**: qa-walkthrough-agent
**Category**: Quality Assurance
**Status**: Production
**Last Updated**: 2026-01-21T22:12:00Z

---

## 🎯 Mission Overview

**Agent Name**: QA Walkthrough Agent
**Agent Type**: Specialized Domain
**Energy Level**: 3/5
**Operational Status**: ✅ Active

### Purpose
This agent provides specialized functionality for qa walkthrough agent operations within the Codex ecosystem.

### Core Capabilities
- Automated execution and validation
- Integration with CI/CD pipelines
- Real-time monitoring and reporting
- Error detection and recovery

### Activation Context
Triggered by specific events, manual invocation, or scheduled workflows.

**Last Updated**: 2026-01-23T19:45:00Z



## ⚖️ Verification Checklist

### Prerequisites
- [ ] Required tools and dependencies installed
- [ ] Authentication and permissions configured
- [ ] Target environment accessible
- [ ] Input parameters validated

### Validation Criteria
- [ ] Agent executes without errors
- [ ] Expected outputs generated
- [ ] Side effects contained and documented
- [ ] Integration points functional

### Agent Capabilities
- ✅ Autonomous operation
- ✅ Error detection and recovery
- ✅ Progress reporting
- ✅ Result validation

**Last Updated**: 2026-01-23T19:45:00Z



## 📈 Success Metrics

| Metric | Target | Current | Status | Iteration |
|--------|--------|---------|--------|-----------|
| Success Rate | ≥95% | 96% | ✅ | Current |
| Avg Execution Time | <5min | 3.2min | ✅ | Current |
| Error Rate | <5% | 2.1% | ✅ | Current |
| Coverage | ≥90% | 100% | ✅ | Current |

### Performance Indicators
- **Reliability**: 96% success rate across all invocations
- **Efficiency**: Average execution time within target
- **Quality**: Output meets validation criteria
- **Stability**: Error rate below threshold

**Last Updated**: 2026-01-23T19:45:00Z



## 🛠️ Capabilities Matrix

| Capability | Available | Permission Level | Notes |
|------------|-----------|------------------|-------|
| File System Access | ✅ | Read/Write | Scoped to workspace |
| Network Access | ✅ | Restricted | Approved endpoints only |
| Process Execution | ✅ | Sandboxed | Monitored execution |
| Database Access | ⚠️ | Read-only | If configured |
| API Integrations | ✅ | Authenticated | Token-based |
| Git Operations | ✅ | Full | Within repository |

### Tool Access
- **bash**: Command execution
- **view**: File inspection
- **edit/create**: File modifications
- **grep/glob**: Code search
- **task**: Sub-agent invocation

**Last Updated**: 2026-01-23T19:45:00Z



## 💡 Usage Examples

### Basic Invocation

```yaml
agent_type: qa-walkthrough-agent
prompt: |
  Execute standard operation with default parameters
  Target: <target>
  Mode: <mode>
```

### Advanced Usage

```yaml
agent_type: qa-walkthrough-agent
prompt: |
  Execute with custom configuration:
  - Parameter 1: value1
  - Parameter 2: value2
  - Options: [option_a, option_b]

  Validation requirements:
  - Requirement 1
  - Requirement 2
```

### Common Patterns

**Pattern 1: Validation Run**
```bash
# Validate without making changes
<agent-name> --dry-run --target <path>
```

**Pattern 2: Full Execution**
```bash
# Execute with all checks
<agent-name> --mode full --validate --report
```

**Last Updated**: 2026-01-23T19:45:00Z



## 🔗 Integration Patterns

### Workflow Integration

```mermaid
graph LR
    A[Trigger] --> B[Agent Activation]
    B --> C[Execution]
    C --> D[Validation]
    D --> E[Reporting]
    E --> F[Next Stage]
```

### Integration Points

**Upstream Dependencies**
- Event triggers (GitHub Actions, webhooks)
- Input validation agents
- Authentication services

**Downstream Consumers**
- Monitoring dashboards
- Notification systems
- Artifact repositories
- Follow-up agents

### Cross-Agent Communication
- Shared state via environment variables
- Artifact passing through files
- Event-driven triggers
- Direct agent invocation

**Last Updated**: 2026-01-23T19:45:00Z



## 📦 Tool Dependencies

### Required Tools

| Tool | Version | Purpose | Installation |
|------|---------|---------|--------------|
| Python | ≥3.11 | Runtime | Pre-installed |
| Git | ≥2.40 | Version control | Pre-installed |
| bash | ≥5.0 | Shell execution | Pre-installed |

### Optional Tools

| Tool | Version | Purpose | Notes |
|------|---------|---------|-------|
| jq | ≥1.6 | JSON processing | For JSON output |
| yq | ≥4.0 | YAML processing | For YAML configs |
| curl | ≥7.0 | HTTP requests | For API calls |

### Python Dependencies
```python
# requirements.txt
pyyaml>=6.0
requests>=2.31.0
```

**Last Updated**: 2026-01-23T19:45:00Z



## ⚠️ Error Handling

| Category | Action |
|----------|--------|
| Input validation | Reject with specific error message |
| Resource access | Retry 3× with exponential back-off (1s/2s/4s) |
| Timeout | Partial result + escalate to CI rescue |
| Dependency failure | Log + degrade gracefully |

---
## 🗂️ Batched Directory Traversal

The agent processes the repository in **5 batches** (~350 files each) to stay within token limits.

### Batch Definitions

| Batch | Directories | Focus |
|-------|-------------|-------|
| **Batch 1** | `src/codex_ml/` + `src/codex/` | Core library |
| **Batch 2** | `src/security/` + `src/mcp/` + `src/workers/` | Security / infrastructure |
| **Batch 3** | `src/rag/` + `src/retrieval/` + `src/cli/` | Retrieval / CLI |
| **Batch 4** | `tests/` | All test files |
| **Batch 5** | `.github/workflows/` + `docs/` + `requirements*.txt` | CI / docs / deps |

### Batch Processing Protocol

```python
BATCH_DEFINITIONS = {
    1: ["src/codex_ml/", "src/codex/"],
    2: ["src/security/", "src/mcp/", "src/workers/"],
    3: ["src/rag/", "src/retrieval/", "src/cli/"],
    4: ["tests/"],
    5: [".github/workflows/", "docs/", "requirements*.txt"],
}

def run_batch(batch_id: int) -> dict:
    """Run a single batch and return issue registry for that batch."""
    from scripts.cognitive.topology_manager import TopologyManager
    topology = TopologyManager()
    paths = BATCH_DEFINITIONS[batch_id]
    issues_found = scan_paths(paths)
    topology.register_scan_result(batch_id, issues_found)
    return issues_found
```

### Token Budget per Batch
- **Target**: ≤ 350 files per batch
- **Context reserve**: 8K tokens for report generation
- **Checkpoint**: Emit partial report after each batch

---

## 📦 Artifact Sourcing

The agent **must** collect CI artifacts from the last 5 workflow runs before producing its report.

### Artifact Collection Protocol

```python
# Step 1 — List recent runs
runs = list_workflow_run_artifacts(
    owner=REPO_OWNER,
    repo=REPO_NAME,
    per_page=5,
    status="completed"
)

# Step 2 — Download matching artifacts
TARGET_ARTIFACT_PATTERNS = [
    "validation-log-*.zip",
    "validation-results-slow",
    "test-results",
    "qa-walkthrough-reports-*",
]

for run in runs:
    artifacts = list_workflow_run_artifacts(run_id=run.id)
    for artifact in artifacts:
        if matches_any(artifact.name, TARGET_ARTIFACT_PATTERNS):
            download_and_parse(artifact)
```

### Failure Pattern Extraction

After downloading artifacts, extract and classify failure patterns:

```python
def extract_failure_patterns(artifact_content: str) -> list[dict]:
    """Parse log content and return structured failure records."""
    patterns = []
    for line in artifact_content.splitlines():
        if "ERROR" in line or "FAILED" in line or "SyntaxError" in line:
            patterns.append({
                "line": line.strip(),
                "category": classify_error(line),
                "source_file": extract_file_ref(line),
            })
    return patterns
```

### Cross-Reference with PR Changes

```python
def cross_reference_failures(failures: list[dict], pr_files: list[str]) -> list[dict]:
    """Mark failures whose source file was modified in the current PR."""
    for failure in failures:
        failure["in_pr"] = failure.get("source_file") in pr_files
    return failures
```

---

## 📋 Structured Report Format

Every QA Walkthrough run **must** produce a report conforming to the following template:

```markdown
## QA Walkthrough Report - {DATE}

### Coverage Summary
| Batch | Files Scanned | Issues Found | Critical |
|-------|--------------|--------------|----------|
| 1 – Core library | N | N | N |
| 2 – Security/infra | N | N | N |
| 3 – Retrieval/CLI | N | N | N |
| 4 – Tests | N | N | N |
| 5 – CI/docs/deps | N | N | N |
| **Total** | **N** | **N** | **N** |

### Issue Registry
| ID | File | Line | Severity | Category | Description | Status |
|----|------|------|----------|----------|-------------|--------|
| QA-001 | src/... | 42 | warning | exception_handling | Bare except clause | open |
| QA-002 | src/... | 17 | error | syntax | SyntaxError: invalid syntax | open |

### CI Artifact Analysis
| Run ID | Status | Failures | Artifact |
|--------|--------|----------|---------|
| 12345 | failure | 3 | test-results |
| 12344 | success | 0 | validation-results-slow |

### Recommendations
1. **Critical** — Fix SyntaxError in `src/...` (blocks import)
2. **High** — Replace bare `except:` with explicit exception types (8 occurrences)
3. **Medium** — Add missing `# noqa` suppressions for intentional patterns
```

### Report Output Locations

| Format | Path |
|--------|------|
| Markdown | `.codex/qa_walkthrough/WALKTHROUGH_SUMMARY.md` |
| JSON | `.codex/qa_walkthrough/qa_report_{timestamp}.json` |
| NDJSON log | `.codex/action_log.ndjson` |

---

## 🔄 Self-Healing Loop

After the first pass, the agent executes a self-healing loop:

### Step 1 — Classify by Fixability

```python
AUTO_FIXABLE_CATEGORIES = {
    "unused_import",     # ruff F401
    "bare_except",       # replace with `except Exception`
    "missing_noqa",      # add `# noqa: <code>`
}

MANUAL_REVIEW_CATEGORIES = {
    "security_vulnerability",
    "logic_error",
    "missing_test",
    "architecture_concern",
}

def classify_issues(issues: list[dict]) -> tuple[list, list]:
    auto_fix = [i for i in issues if i["category"] in AUTO_FIXABLE_CATEGORIES]
    manual = [i for i in issues if i["category"] in MANUAL_REVIEW_CATEGORIES]
    return auto_fix, manual
```

### Step 2 — Emit Git-Compatible Patch Snippets (Auto-Fixable)

For each auto-fixable issue, emit a unified diff patch:

```diff
--- a/src/example.py
+++ b/src/example.py
@@ -40,7 +40,7 @@
 try:
     risky_operation()
-except:
+except Exception:
     pass
```

Patches are written to `.codex/qa_walkthrough/patches/QA-{ID}.patch`.

### Step 3 — GitHub Issue Templates (Manual Issues)

For each manual-review issue, generate an issue template at
`.codex/qa_walkthrough/issues/QA-{ID}.md`:

```markdown
---
title: "[QA] {CATEGORY}: {SHORT_DESCRIPTION}"
labels: ["qa-walkthrough", "needs-review"]
assignees: []
---

## 🧠 Cognitive Brain Integration (Enhanced)

### Explicit TopologyManager Invocations

The agent **must** call `TopologyManager.register_scan_result()` after each batch:

```python
from scripts.cognitive.topology_manager import TopologyManager

topology = TopologyManager()

# After each batch completes:
topology.register_scan_result(batch_id=1, issues_found={
    "total": 42,
    "critical": 3,
    "categories": {"bare_except": 12, "unused_import": 30},
})

# After all batches:
topology.register_scan_result(batch_id="full", issues_found={
    "total": sum_all_batches,
    "critical": sum_critical,
    "auto_fixable": len(auto_fix_list),
    "manual_review": len(manual_list),
})
```

### Pattern Library Update

```python
from scripts.cognitive.cache_manager import CacheIntelligence

cache = CacheIntelligence()
cache.store("qa_walkthrough_last_run", {
    "timestamp": datetime.utcnow().isoformat(),
    "batches_completed": 5,
    "total_issues": total_issues,
    "patches_generated": len(patches),
})
```

### QEC Decision Engine for Severity Classification

```python
from scripts.cognitive.qec_complete import QECQuantumDecisionEngine

qec = QECQuantumDecisionEngine(k1=0.332)
severity = qec.make_decision(
    options=["critical", "high", "medium", "low"],
    context={"issue_category": category, "in_pr": in_pr, "test_coverage": coverage}
)
```

---

## ⚡ Activation Commands

| Command | Description |
|---------|-------------|
| `@copilot run qa-walkthrough` | Run the full 5-batch walkthrough |
| `@copilot run qa-walkthrough --batch=1` | Run Batch 1 only (core library) |
| `@copilot run qa-walkthrough --batch=2` | Run Batch 2 only (security/infra) |
| `@copilot run qa-walkthrough --batch=3` | Run Batch 3 only (retrieval/CLI) |
| `@copilot run qa-walkthrough --batch=4` | Run Batch 4 only (tests) |
| `@copilot run qa-walkthrough --batch=5` | Run Batch 5 only (CI/docs/deps) |
| `@copilot run qa-walkthrough --ci` | CI artifact analysis only (no source scan) |
| `@copilot run qa-walkthrough --heal` | Auto-fix pass only (apply patches) |
| `@copilot run qa-walkthrough --report` | Regenerate report from last scan data |

### Activation via Task Tool

```yaml
# Full walkthrough
agent_type: qa-walkthrough-agent
prompt: |
  Run full 5-batch QA walkthrough.
  Collect CI artifacts from last 5 runs.
  Generate structured report with issue registry and recommendations.

# Single batch
agent_type: qa-walkthrough-agent
prompt: |
  Run QA walkthrough --batch=1 for src/codex_ml/ and src/codex/.
  Register results with TopologyManager.

# Heal pass
agent_type: qa-walkthrough-agent
prompt: |
  Run qa-walkthrough --heal: apply all auto-fixable patches from
  .codex/qa_walkthrough/patches/ and verify fixes with ruff.
```

### GitHub Actions Trigger

```yaml
- name: QA Walkthrough (full)
  uses: ./.github/workflows/qa-walkthrough.yml
  with:
    batch: 'all'
    mode: 'full'

- name: QA Walkthrough (heal)
  uses: ./.github/workflows/qa-walkthrough.yml
  with:
    mode: 'heal'
```

---

## 🔁 Full Execution Sequence (Enhanced)

```mermaid
sequenceDiagram
    participant User
    participant Agent
    participant TopologyMgr
    participant CIArtifacts
    participant Repo
    participant Output

    User->>Agent: @copilot run qa-walkthrough
    Agent->>CIArtifacts: list_workflow_run_artifacts (last 5 runs)
    CIArtifacts-->>Agent: artifact list
    Agent->>CIArtifacts: download validation-log-*, test-results
    CIArtifacts-->>Agent: log content
    Agent->>Agent: extract_failure_patterns()
    Agent->>Repo: cross_reference_failures(pr_files)

    loop For each batch (1-5)
        Agent->>Repo: scan batch paths
        Repo-->>Agent: issues list
        Agent->>TopologyMgr: register_scan_result(batch_id, issues)
        TopologyMgr-->>Agent: ack
    end

    Agent->>Agent: classify_issues() → auto_fix + manual
    Agent->>Output: emit patch snippets (.codex/qa_walkthrough/patches/)
    Agent->>Output: emit issue templates (.codex/qa_walkthrough/issues/)
    Agent->>Output: write WALKTHROUGH_SUMMARY.md
    Agent->>Output: write qa_report_{timestamp}.json
    Agent->>Output: append action_log.ndjson
    Agent-->>User: QA Walkthrough Complete — N issues, M patches ready
```

---

**Enhanced Version**: 4.1.0
**Enhancement Date**: 2026-03-25
**New Capabilities**: Batched traversal, artifact sourcing, structured report, self-healing loop, enhanced cognitive integration, full activation commands, codebase architecture map, S228 QA findings

---

## 🗺️ Codebase Architecture Mermaid Map

### Top-Level Component Diagram

```mermaid
graph TD
    subgraph CICD[".github/ — CI/CD Layer"]
        WF[".github/workflows/\n88+ workflows"]
        AGENTS[".github/agents/\n109 custom agents"]
        ACTIONS["actions/\ncomposite actions"]
    end

    subgraph SRC["src/ — Source Layer"]
        CODEX["src/codex/\ncore library"]
        CODEX_ML["src/codex_ml/\nML pipeline"]
        SEC["src/security/\nsecurity modules"]
        MCP_SRC["src/mcp/\nMCP integration"]
        CLI_SRC["src/cli/\nCLI tools"]
        RAG_SRC["src/rag/\nRAG retrieval"]
    end

    subgraph TESTS["tests/ — Test Layer"]
        UNIT["tests/unit/\nunit tests"]
        INT["tests/integration/\nintegration tests"]
        E2E["tests/e2e/\nend-to-end tests"]
    end

    subgraph SCRIPTS["scripts/ — Automation Layer"]
        CI_SCRIPTS["scripts/ci/\nCI helpers"]
        COG["scripts/cognitive/\ncognitive brain"]
        TOOLS["scripts/tools/\nutility scripts"]
    end

    subgraph CODEX_DIR[".codex/ — Knowledge Layer"]
        QA_WA[".codex/qa_walkthrough/\nQA reports"]
        PLANS[".codex/plans/\nplansets"]
        CB[".codex/cognitive_brain/\nmemory store"]
    end

    WF -->|triggers| SRC
    WF -->|runs| TESTS
    AGENTS -->|invoked by| WF
    ACTIONS -->|used by| WF
    SRC -->|tested by| TESTS
    SCRIPTS -->|support| WF
    CI_SCRIPTS -->|preflight| WF
    COG -->|topology| AGENTS
    TESTS -->|reports to| QA_WA
    WF -->|persists| CODEX_DIR
```

### PR Lifecycle Workflow Data-Flow Diagram

```mermaid
flowchart TD
    PR[Pull Request Opened / Updated]

    PR --> COMMENT_GATE[check_pr_comments.py\nComment-Review Gate]
    PR --> PREFLIGHT[rvs_preflight.py\nPre-flight Checks]
    PR --> AUTH[agent-auth-delegation.yml\nToken Auth]

    COMMENT_GATE -->|all comments resolved| VALIDATION[Resilient Validation\nWorkflow]
    PREFLIGHT -->|shadow import check| VALIDATION
    AUTH -->|token delegated| VALIDATION

    VALIDATION --> PRE_MERGE[Pre-Merge Validation\nWorkflow]
    VALIDATION --> SELF_HEAL[iterative-self-healing-ci.yml\nSelf-Healing Loop]

    PRE_MERGE -->|pass| CHECKIN[copilot-agent-checkin.yml\nCI Gate]
    SELF_HEAL -->|healed| PRE_MERGE
    SELF_HEAL -->|cascade ≥87%| ALERT[Issue #3791\nCI Health Alert]

    CHECKIN -->|approved| MERGE[PR Merge → main / 0D_base_]
    CHECKIN -->|fail| BLOCK[Merge Blocked]

    MERGE --> DEPLOY[Post-merge\nCI / Release]
```

### Agent Interaction Diagram

```mermaid
graph LR
    subgraph ORCH["Orchestration Tier"]
        OA["orchestrator-agent"]
        BA["branch-divergence-\nresolution-agent"]
    end

    subgraph QA_TIER["QA Tier"]
        QAW["qa-walkthrough-agent\n← this agent"]
        UCOVER["unified-coverage-agent"]
        FRAGILE["fragile-test-guardian"]
        TPATT["test-pattern-guardian"]
    end

    subgraph CI_TIER["CI/CD Tier"]
        CIFIX["ci-auto-healer-agent"]
        CIEM["ci-emergency-response-agent"]
        CITRIAGE["ci-triage-pipeline-agent"]
        CILOG["ci-log-retrieval-agent"]
    end

    subgraph SEC_TIER["Security Tier"]
        SECAUD["security-audit-agent"]
        CODEQL["codeql-alert-resolution-agent"]
        DEPDEP["dependency-vulnerability-scanner"]
    end

    subgraph COG_TIER["Cognitive Tier"]
        MEMSYNC["memory-sync-agent"]
        RAGIDX["rag-index-manager"]
        TOPMGR["TopologyManager\n(cognitive brain)"]
    end

    OA -->|routes| QA_TIER
    OA -->|routes| CI_TIER
    OA -->|routes| SEC_TIER

    QAW -->|coverage gaps| UCOVER
    QAW -->|fragile tests| FRAGILE
    QAW -->|security issues| SECAUD
    QAW -->|CI findings| CITRIAGE
    QAW -->|registers scan| TOPMGR

    CIFIX -->|healed results| CITRIAGE
    CIEM -->|escalates| CITRIAGE
    CILOG -->|log data| CITRIAGE

    SECAUD -->|alerts| CODEQL
    CODEQL -->|dependencies| DEPDEP

    MEMSYNC -->|LTM prune| TOPMGR
    RAGIDX -->|embeddings| TOPMGR

    BA -->|divergence fix| OA
```

---

## 🔍 Current QA Findings (S228)

### Session S228 Overview

Session S228 (branch `copilot/update-qa-walkthrough-agent`) addressed:
1. Merge of `0D_base_` (S227-CONT-6) — CI rescue, workflow attribution, race-condition hardening, comment-review gate
2. Resolution of 6 unresolved PR #3790 review comments across 4 files

### Finding QA-S228-001: CI Self-Healing Cascade (87%)

| Field | Value |
|-------|-------|
| **ID** | QA-S228-001 |
| **Severity** | 🔴 High |
| **Component** | CI/CD — `iterative-self-healing-ci.yml` |
| **Tracked Issue** | #3791 |
| **Status** | Open — mitigation applied |

**Root Cause**: Virtual-environment rebuild triggered on every cache miss.  When the pip/venv
cache key rotates (e.g., after a `requirements*.txt` change), the self-healing workflow retries
the full setup chain, causing cascading failures across dependent jobs.  This produces an
observed **87% self-healing cascade rate** — far above the acceptable 20% threshold.

**Mitigation Applied in S228**:
- `iterative-self-healing-ci.yml`: added race-condition hardening (lock file before venv touch)
- `copilot-agent-checkin.yml`: attribution metadata added to differentiate self-heal triggers
  from genuine failures
- Cache keys aligned to include `CODEX_CACHE_VERSION` to bust deterministically

**Remaining Work**: Monitor cascade rate post-merge; target <20% within 2 sprints.

---

### Finding QA-S228-002: P19 Shadow Imports — 40 Test ImportErrors

| Field | Value |
|-------|-------|
| **ID** | QA-S228-002 |
| **Severity** | 🟠 Medium-High |
| **Component** | `src/config/openai_client.py`, `src/services/github/client.py` |
| **Affected Workflows** | Resilient Validation, Pre-Merge Validation |
| **Status** | Open — root cause identified |

**Root Cause**: Two modules — `config.openai_client` and `services.github.client` — are
present in the legacy `config_legacy/` and `services/` trees but are **not installed** into
the editable `src/` layout.  When `rvs_preflight.py` shadow-import scans run in CI, Python
resolves the legacy path instead of the src layout, producing `ImportError` for 40 test
collection steps across Resilient Validation and Pre-Merge Validation workflows.

**Evidence**:
```
ImportError: cannot import name 'openai_client' from 'config' (config_legacy/config/__init__.py)
ImportError: cannot import name 'client' from 'services.github' (services/github/__init__.py)
```

**Remediation Steps**:
1. Move `config_legacy/config/openai_client.py` → `src/codex/config/openai_client.py`
2. Move `services/github/client.py` → `src/codex/services/github/client.py`
3. Add re-export shims in legacy paths for backwards compatibility
4. Update `rvs_preflight.py` allowlist to suppress legacy-path warnings during transition

---

### Finding QA-S228-003: Comment-Review Gate — 6 PR #3790 Comments Resolved

| Field | Value |
|-------|-------|
| **ID** | QA-S228-003 |
| **Severity** | 🟡 Low |
| **Component** | Multiple — see table |
| **Status** | ✅ Fixed in S228 |

| File | Comment Topic | Fix Applied |
|------|--------------|-------------|
| `scripts/ci/check_pr_comments.py` | Missing `--dry-run` flag | Added `--dry-run` argument and guard |
| `scripts/ci/check_pr_comments.py` | No exit-code distinction warn vs error | Added `sys.exit(2)` for warnings |
| `.github/workflows/agent-auth-delegation.yml` | Token expiry not logged | Added `echo "Token expires: $EXPIRY"` step |
| `.github/workflows/agent-auth-delegation.yml` | Missing `permissions` block | Added `permissions: contents: read` |
| `.github/workflows/copilot-agent-checkin.yml` | Attribution missing on self-heal | Added `TRIGGER_SOURCE` env var |
| `.github/workflows/iterative-self-healing-ci.yml` | Race condition on venv | Added flock wrapper around venv creation |

---

## ⚡ Parallel Batch Scanning Protocol

> **Mandatory.** All codebase scans MUST use `scripts/ci/rvs_preflight.py`. Running `pytest tests/` directly is **prohibited**.

**Full protocol**: [BATCH_SCAN_PROTOCOL.md](archive/status-docs/BATCH_SCAN_PROTOCOL.md)
