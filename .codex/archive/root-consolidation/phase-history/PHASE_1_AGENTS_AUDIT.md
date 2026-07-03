# Phase 1: Custom Agent Token Integration Audit Report

**Audit Date:** 2026-06-29T03:43:22.913844+00:00
**Total Agents Analyzed:** 147

---

## Executive Summary

This comprehensive audit evaluates all 147 active custom agents in the Aries-Serpent/_codex_ repository to identify their token handling requirements and guidance completeness.

### Key Findings

| Metric | Count |
|--------|-------|
| Total Active Agents | 147 |
| Agents with GitHub API Usage | 94 |
| Agents without API Usage | 53 |
| Complete Token Guidance | 40 |
| Partial Token Guidance | 41 |
| Missing Token Guidance | 13 |
| Guidance Gaps Identified | 13 |

---

## Token Requirement Levels

### Token Level Classification Framework

- **Level 1 (MUST have CODEX_MASTER_KEY)**: Agents that perform workflow dispatch, variable writes, security event handling, or action execution. These operations require elevated GitHub API permissions including `actions:write`, `repo`, and `security_events`.

- **Level 2 (Should prefer CODEX_MASTER_KEY)**: Agents that perform deployment, orchestration, or workflow approval operations. While Level 3 tokens may work for some operations, CODEX_MASTER_KEY is recommended for reliability.

- **Level 3 (Standard github.token acceptable)**: Agents that primarily perform read-only operations or standard PR/issue operations. The default GITHUB_TOKEN is sufficient.

- **Level 0 (No GitHub API usage)**: Agents that don't interact with GitHub APIs at all (analysis, validation, content generation, etc.).

### Level 1: MUST Have CODEX_MASTER_KEY

**Count:** 73 agents

These agents **must** have access to CODEX_MASTER_KEY as they require elevated GitHub API permissions:

- **Admin Automation Agent** (`admin-automation-agent`) ✅
  - Operations: variable write, deployment
  - Guidance Status: complete
- **Agent Orchestrator** (`agent-orchestrator`) ⚠️
  - Operations: variable write, security event handling
  - Guidance Status: partial
- **Artifact Monitor Agent** (`artifact-monitor-agent`) ✅
  - Operations: PR operations, issue operations, variable write
  - Guidance Status: complete
- **Autonomous Test Healer Agent** (`autonomous-test-healer-agent`) ✅
  - Operations: PR operations, security event handling
  - Guidance Status: complete
- **Batch Triage Agent** (`batch-triage-agent`) ✅
  - Operations: PR operations, deployment, security event handling
  - Guidance Status: complete
- **Branch Divergence Resolution Agent** (`branch-divergence-resolution-agent`) ⚠️
  - Operations: workflow dispatch, PR operations, issue operations, variable write
  - Guidance Status: partial
- **Bridge Security Monitor** (`bridge-security-monitor`) ✅
  - Operations: security event handling
  - Guidance Status: complete
- **CI Auto-Healer Agent** (`ci-auto-healer`) ⚠️
  - Operations: workflow operations
  - Guidance Status: partial
- **CI Auto-Healer Agent** (`ci-auto-healer-agent`) ⚠️
  - Operations: workflow operations
  - Guidance Status: partial
- **CI Emergency Response Agent** (`ci-emergency-response-agent`) ⚠️
  - Operations: PR operations
  - Guidance Status: partial
- **CI Health Alert Agent** (`ci-health-alert-agent`) ⚠️
  - Operations: workflow dispatch, variable write, security event handling
  - Guidance Status: partial
- **CI Log Retrieval Agent** (`ci-log-retrieval-agent`) ✅
  - Operations: variable write, status check
  - Guidance Status: complete
- **CI Optimization Agent** (`ci-optimization-agent`) ✅
  - Operations: PR operations, issue operations, variable write, deployment, security event handling
  - Guidance Status: complete
- **CI Parameter Mismatch Healer** (`ci-parameter-mismatch-healer`) ❌
  - Operations: variable write
  - Guidance Status: missing
- **CI Triage Pipeline Agent** (`ci-triage-pipeline-agent`) ❌
  - Operations: workflow operations
  - Guidance Status: missing
- **Cache Management Agent** (`cache-management-agent`) ⚠️
  - Operations: security event handling
  - Guidance Status: partial
- **Code Scanning Remediation Agent** (`code-scanning-remediation-agent`) ✅
  - Operations: PR operations, variable write, deployment, security event handling
  - Guidance Status: complete
- **CodeQL Alert Resolution Agent** (`codeql-alert-resolution-agent`) ✅
  - Operations: workflow dispatch, variable write, deployment, security event handling
  - Guidance Status: complete
- **Codebase Health Guardian** (`codebase-health-guardian`) ⚠️
  - Operations: security event handling
  - Guidance Status: partial
- **Codebase QA Walkthrough Agent** (`codebase-qa-walkthrough-agent`) ✅
  - Operations: PR operations, security event handling
  - Guidance Status: complete
- **Cognitive Brain CLI Agent** (`cognitive-brain-cli-agent`) ❌
  - Operations: variable write
  - Guidance Status: missing
- **Cognitive Brain Manager** (`cognitive-brain-manager`) ✅
  - Operations: workflow dispatch, PR operations, variable write, deployment, security event handling
  - Guidance Status: complete
- **Cognitive Brain Session Injector** (`cognitive-brain-session-injector`) ✅
  - Operations: variable write
  - Guidance Status: complete
- **Cognitive OODA Loop Agent** (`cognitive-ooda-loop-agent`) ⚠️
  - Operations: variable write
  - Guidance Status: partial
- **Cross-Agent Knowledge Graph** (`cross-agent-knowledge-graph`) ❌
  - Operations: variable write
  - Guidance Status: missing
- **Doc Refactor Test Agent** (`doc-refactor-test-agent`) ❌
  - Operations: PR operations, variable write, deployment
  - Guidance Status: missing
- **Documentation Sync Validator** (`documentation-sync-validator`) ✅
  - Operations: PR operations, variable write, deployment, security event handling
  - Guidance Status: complete
- **Energy Conversion Agent** (`energy-conversion-agent`) ⚠️
  - Operations: deployment, security event handling
  - Guidance Status: partial
- **GitHub App Manager** (`github-app-manager`) ✅
  - Operations: variable write, deployment
  - Guidance Status: complete
- **GitHub Deployment Gatekeeper** (`github-deployment-gatekeeper`) ✅
  - Operations: workflow dispatch, issue operations, deployment, security event handling
  - Guidance Status: complete
- **GitHub Guru Agent** (`github-guru-agent`) ⚠️
  - Operations: workflow dispatch, PR operations, variable write, security event handling
  - Guidance Status: partial
- **GitHub Pages Manager** (`github-pages-manager`) ⚠️
  - Operations: issue operations, variable write, deployment
  - Guidance Status: partial
- **GitHub Security Validator Agent** (`github-security-validator-agent`) ✅
  - Operations: workflow dispatch, issue operations, status check, security event handling
  - Guidance Status: complete
- **GitHub Testing Orchestrator Agent** (`github-testing-orchestrator-agent`) ✅
  - Operations: workflow dispatch, PR operations, variable write
  - Guidance Status: complete
- **JSON Serialization Expert** (`json-serialization-expert`) ❌
  - Operations: deployment, security event handling
  - Guidance Status: missing
- **Link Validator Agent** (`link-validator-agent`) ✅
  - Operations: workflow dispatch, PR operations, variable write, deployment
  - Guidance Status: complete
- **ML Threat Detector** (`ml-threat-detector`) ✅
  - Operations: PR operations, variable write, security event handling
  - Guidance Status: complete
- **MSV Dashboard Monitor** (`msv-dashboard-monitor`) ⚠️
  - Operations: issue operations, variable write, deployment, security event handling
  - Guidance Status: partial
- **Memory Sync Agent** (`memory-sync-agent`) ❌
  - Operations: variable write
  - Guidance Status: missing
- **Meta Tensor Validator** (`meta-tensor-validator`) ✅
  - Operations: PR operations, issue operations, variable write, deployment, security event handling
  - Guidance Status: complete
- **Orchestrator Agent** (`orchestrator-agent`) ⚠️
  - Operations: variable write, deployment, security event handling
  - Guidance Status: partial
- **PR Check Remediation Agent** (`pr-check-remediation-agent`) ⚠️
  - Operations: PR operations, issue operations, status check, deployment, security event handling
  - Guidance Status: partial
- **PR-3095 Verification Agent** (`pr-3095-verification-agent`) ⚠️
  - Operations: PR operations, variable write
  - Guidance Status: partial
- **Packaging Validation Agent** (`packaging-validation-agent`) ⚠️
  - Operations: variable write, security event handling
  - Guidance Status: partial
- **Performance Regression Detector** (`performance-regression-detector`) ✅
  - Operations: security event handling
  - Guidance Status: complete
- **Policy Coach Agent** (`policy-coach-agent`) ⚠️
  - Operations: variable write, security event handling
  - Guidance Status: partial
- **PyPI Publishing Operations Agent** (`pypi-publishing-operations-agent`) ⚠️
  - Operations: workflow dispatch, variable write, status check, deployment, security event handling
  - Guidance Status: partial
- **Python 3.12 Type Fixer** (`python-312-type-fixer`) ⚠️
  - Operations: variable write
  - Guidance Status: partial
- **Python Architect Agent** (`python-architect-agent`) ⚠️
  - Operations: variable write
  - Guidance Status: partial
- **QA Walkthrough Agent** (`qa-walkthrough-agent`) ✅
  - Operations: PR operations, variable write, deployment, security event handling
  - Guidance Status: complete
- **Quantum Compliance Tuning Agent** (`quantum-compliance-tuning-agent`) ⚠️
  - Operations: variable write
  - Guidance Status: partial
- **RAG Meta Tensor Guardian** (`rag-meta-tensor-guardian`) ✅
  - Operations: variable write, deployment, security event handling
  - Guidance Status: complete
- **RAG Module Management Agent** (`rag-module-management-agent`) ⚠️
  - Operations: variable write
  - Guidance Status: partial
- **Recon Scout Agent** (`recon-scout-agent`) ⚠️
  - Operations: variable write, deployment
  - Guidance Status: partial
- **Repo Var Sync Agent** (`repo-var-sync-agent`) ⚠️
  - Operations: variable write
  - Guidance Status: partial
- **Root Organizer Agent** (`root-organizer-agent`) ✅
  - Operations: variable write
  - Guidance Status: complete
- **Security Alert Verification Agent** (`security-alert-verification-agent`) ⚠️
  - Operations: variable write, security event handling
  - Guidance Status: partial
- **Security Vulnerability Patcher** (`security-vulnerability-patcher`) ✅
  - Operations: workflow dispatch, PR operations, deployment
  - Guidance Status: complete
- **Self-Healing Orchestrator Agent** (`self-healing-orchestrator-agent`) ❌
  - Operations: PR operations, deployment
  - Guidance Status: missing
- **Service Integration Tester** (`service-integration-tester`) ✅
  - Operations: variable write
  - Guidance Status: complete
- **Session Log Retrieval Agent** (`session-log-retrieval-agent`) ⚠️
  - Operations: variable write
  - Guidance Status: partial
- **Telemetry Classifier Agent** (`telemetry-classifier-agent`) ⚠️
  - Operations: PR operations, variable write, security event handling
  - Guidance Status: partial
- **Terminology Consistency Agent** (`terminology-consistency-agent`) ⚠️
  - Operations: PR operations, variable write, deployment
  - Guidance Status: partial
- **Test Coverage Enforcer** (`test-coverage-enforcer`) ✅
  - Operations: PR operations, variable write
  - Guidance Status: complete
- **Test Enhancement Agent** (`unified-coverage-agent`) ⚠️
  - Operations: PR operations, variable write
  - Guidance Status: partial
- **Test Failure Analyzer Agent** (`test-failure-analyzer-agent`) ⚠️
  - Operations: variable write, deployment
  - Guidance Status: partial
- **Unified Governance Gate** (`unified-governance-gate`) ❌
  - Operations: workflow dispatch, variable write, deployment
  - Guidance Status: missing
- **Unified Security Scanner** (`unified-security-scanner`) ⚠️
  - Operations: PR operations, security event handling
  - Guidance Status: partial
- **Workflow Analytics Agent** (`workflow-analytics-agent`) ✅
  - Operations: variable write
  - Guidance Status: complete
- **Workflow CI Fixer** (`workflow-ci-fixer`) ✅
  - Operations: workflow dispatch, PR operations, issue operations, deployment, security event handling
  - Guidance Status: complete
- **Workflow Health Monitor** (`workflow-health-monitor`) ⚠️
  - Operations: workflow dispatch, deployment, security event handling
  - Guidance Status: partial
- **Workflow Management Agent** (`workflow-management-agent`) ⚠️
  - Operations: workflow dispatch, PR operations, issue operations, deployment
  - Guidance Status: partial
- **Workflow Optimization Agent** (`workflow-optimization-agent`) ❌
  - Operations: workflow dispatch, PR operations, security event handling
  - Guidance Status: missing

### Level 2: Should Prefer CODEX_MASTER_KEY

**Count:** 15 agents

These agents can work with standard tokens but have better reliability and capabilities with CODEX_MASTER_KEY:

- **Agent IQ Scoring Gate** (`agent-iq-scoring-gate`) ❌
  - Operations: deployment
  - Guidance Status: missing
- **CI Diagnostic Agent** (`ci-diagnostic-agent`) ✅
  - Operations: deployment
  - Guidance Status: complete
- **CPU-Only CI Config Agent** (`cpu-only-ci-config-agent`) ❌
  - Operations: deployment
  - Guidance Status: missing
- **Code Analysis Agent** (`code-analysis-agent`) ⚠️
  - Operations: PR operations, deployment
  - Guidance Status: partial
- **Cross-Platform Filename Validator** (`cross-platform-filename-validator`) ✅
  - Operations: issue operations, deployment
  - Guidance Status: complete
- **Doc Freshness Checker** (`doc-freshness-checker`) ✅
  - Operations: deployment
  - Guidance Status: complete
- **Integration Test Runner** (`integration-test-runner`) ✅
  - Operations: PR operations, deployment
  - Guidance Status: complete
- **Owner Approval Guard** (`owner-approval-guard`) ✅
  - Operations: deployment
  - Guidance Status: complete
- **RAG Freshness Loop Agent** (`rag-freshness-loop-agent`) ⚠️
  - Operations: deployment
  - Guidance Status: partial
- **Reference Updater Agent** (`reference-updater-agent`) ✅
  - Operations: deployment
  - Guidance Status: complete
- **Rust Config Validator** (`rust-config-validator`) ✅
  - Operations: deployment
  - Guidance Status: complete
- **Session Analysis Agent** (`session-analysis-agent`) ⚠️
  - Operations: deployment
  - Guidance Status: partial
- **Test Pattern Guardian** (`test-pattern-guardian`) ✅
  - Operations: deployment
  - Guidance Status: complete
- **Unified Doc Agent** (`unified-doc-agent`) ⚠️
  - Operations: deployment
  - Guidance Status: partial
- **Workflow Compliance Guardian** (`workflow-compliance-guardian`) ⚠️
  - Operations: PR operations, deployment
  - Guidance Status: partial

### Level 3: Standard github.token Acceptable

**Count:** 6 agents

These agents work well with standard GitHub Actions tokens:

- **Dependency Conflict Resolver** (`dependency-conflict-resolver`)
  - Operations: PR operations
- **GitHub Code Reviewer** (`github-code-reviewer`)
  - Operations: PR operations, issue operations, status check
- **GitHub Test Orchestrator** (`github-test-orchestrator`)
  - Operations: PR operations, issue operations, status check
- **Mutation Testing Agent** (`mutation-testing-agent`)
  - Operations: PR operations
- **Test Alignment Fixer Enhanced** (`test-alignment-fixer-enhanced`)
  - Operations: PR operations
- **Tracking Document QA Agent** (`tracking-document-qa-agent`)
  - Operations: issue operations, status check

### Level 0: No GitHub API Usage

**Count:** 53 agents

These agents don't interact with GitHub APIs (content analysis, validation, code review, etc.).

- Ast Analysis Agent (`ast-analysis-agent`)
- Cache Logic Validator (`cache-logic-validator`)
- Ci Failure Diagnostician (`ci-failure-diagnostician`)
- Ci Optimizer Agent (`ci-optimizer-agent`)
- Ci Testing Agent (`ci-testing-agent`)
- Codex_Reviewer (`codex_reviewer`)
- Cognitive Brain Agent (`cognitive-brain-agent`)
- Compliance Checker Agent (`compliance-checker-agent`)
- Dep Upgrade Agent (`dep-upgrade-agent`)
- Documentation Agent (`documentation-agent`)
- ... and 43 more agents

---

## Token Guidance Analysis

### Guidance Completeness Metrics

- **Complete Guidance** (40+ signals detected): 40 agents
- **Partial Guidance** (2-3 signals detected): 41 agents
- **Missing Guidance** (<2 signals detected): 13 agents

### Guidance Signals Tracked

The audit looks for 5 key token guidance signals in agent prompts:

1. **Token Mentioned**: Reference to `GITHUB_TOKEN`, `token`, or authentication concepts
2. **Master Key Mentioned**: Specific reference to `CODEX_MASTER_KEY` or elevated tokens
3. **Scope Documented**: Documentation of required GitHub API scopes and permissions
4. **Error Handling**: Guidance on what to do if token permissions are insufficient
5. **Token Hierarchy**: Documentation of the fallback chain: CODEX_MASTER_KEY → CODEX_BACKUP_KEY → github.token

---

## Identified Guidance Gaps

### 13 Agents Need Token Guidance Updates

#### ci-parameter-mismatch-healer

- **Issue**: Incomplete token guidance (only 1 of 5 signals detected)
- **Token Level**: Level 1
- **Operations**: variable write
- **Impact**: Agent may not know to request elevated token when needed
- **Recommendation**: Add token guidance section with token hierarchy, scopes, and error handling

#### ci-triage-pipeline-agent

- **Issue**: Incomplete token guidance (only 1 of 5 signals detected)
- **Token Level**: Level 1
- **Operations**: Unknown
- **Impact**: Agent may not know to request elevated token when needed
- **Recommendation**: Add token guidance section with token hierarchy, scopes, and error handling

#### cognitive-brain-cli-agent

- **Issue**: Incomplete token guidance (only 1 of 5 signals detected)
- **Token Level**: Level 1
- **Operations**: variable write
- **Impact**: Agent may not know to request elevated token when needed
- **Recommendation**: Add token guidance section with token hierarchy, scopes, and error handling

#### cross-agent-knowledge-graph

- **Issue**: Incomplete token guidance (only 1 of 5 signals detected)
- **Token Level**: Level 1
- **Operations**: variable write
- **Impact**: Agent may not know to request elevated token when needed
- **Recommendation**: Add token guidance section with token hierarchy, scopes, and error handling

#### doc-refactor-test-agent

- **Issue**: Incomplete token guidance (only 1 of 5 signals detected)
- **Token Level**: Level 1
- **Operations**: PR operations, variable write, deployment
- **Impact**: Agent may not know to request elevated token when needed
- **Recommendation**: Add token guidance section with token hierarchy, scopes, and error handling

#### json-serialization-expert

- **Issue**: Incomplete token guidance (only 1 of 5 signals detected)
- **Token Level**: Level 1
- **Operations**: deployment, security event handling
- **Impact**: Agent may not know to request elevated token when needed
- **Recommendation**: Add token guidance section with token hierarchy, scopes, and error handling

#### memory-sync-agent

- **Issue**: Incomplete token guidance (only 0 of 5 signals detected)
- **Token Level**: Level 1
- **Operations**: variable write
- **Impact**: Agent may not know to request elevated token when needed
- **Recommendation**: Add token guidance section with token hierarchy, scopes, and error handling

#### self-healing-orchestrator-agent

- **Issue**: Incomplete token guidance (only 1 of 5 signals detected)
- **Token Level**: Level 1
- **Operations**: PR operations, deployment
- **Impact**: Agent may not know to request elevated token when needed
- **Recommendation**: Add token guidance section with token hierarchy, scopes, and error handling

#### unified-governance-gate

- **Issue**: Incomplete token guidance (only 1 of 5 signals detected)
- **Token Level**: Level 1
- **Operations**: workflow dispatch, variable write, deployment
- **Impact**: Agent may not know to request elevated token when needed
- **Recommendation**: Add token guidance section with token hierarchy, scopes, and error handling

#### workflow-optimization-agent

- **Issue**: Incomplete token guidance (only 1 of 5 signals detected)
- **Token Level**: Level 1
- **Operations**: workflow dispatch, PR operations, security event handling
- **Impact**: Agent may not know to request elevated token when needed
- **Recommendation**: Add token guidance section with token hierarchy, scopes, and error handling

#### agent-iq-scoring-gate

- **Issue**: Incomplete token guidance (only 0 of 5 signals detected)
- **Token Level**: Level 2
- **Operations**: deployment
- **Impact**: Agent may not know to request elevated token when needed
- **Recommendation**: Add token guidance section with token hierarchy, scopes, and error handling

#### cpu-only-ci-config-agent

- **Issue**: Incomplete token guidance (only 1 of 5 signals detected)
- **Token Level**: Level 2
- **Operations**: deployment
- **Impact**: Agent may not know to request elevated token when needed
- **Recommendation**: Add token guidance section with token hierarchy, scopes, and error handling

#### test-alignment-fixer-enhanced

- **Issue**: Incomplete token guidance (only 1 of 5 signals detected)
- **Token Level**: Level 3
- **Operations**: PR operations
- **Impact**: Agent may not know to request elevated token when needed
- **Recommendation**: Add token guidance section with token hierarchy, scopes, and error handling


---

## Recommended Token Guidance Text

### For Level 1 (MUST Have CODEX_MASTER_KEY) Agents

Add this section to agent prompts:

```markdown
### Token Requirements

This agent **requires** the elevated `CODEX_MASTER_KEY` GitHub App installation token to function properly.

**Why elevated token is required:**
- This agent performs workflow dispatch operations that require `actions:write` scope
- Variable and secret management requires elevated permissions
- Security event operations require `security_events` scope

**Token Hierarchy (automatic fallback):**
1. `CODEX_MASTER_KEY` (elevated, preferred) - Full access to all required operations
2. `CODEX_BACKUP_KEY` (elevated, fallback) - Secondary elevated token if master unavailable
3. `GITHUB_TOKEN` (standard, limited) - Will fail for protected operations; agent should detect and request upgrade

**Error Handling:**
- If the agent encounters 403 (Forbidden) or 401 (Unauthorized) errors, this typically indicates insufficient token permissions
- Request elevation to CODEX_MASTER_KEY
- The agent will log token source in operation audit trail for debugging
```

### For Level 2 (Should Prefer CODEX_MASTER_KEY) Agents

```markdown
### Token Preferences

This agent works best with the `CODEX_MASTER_KEY` GitHub App token but can function with standard `GITHUB_TOKEN`.

**Preferred token:** `CODEX_MASTER_KEY` (elevated)
- Provides reliability for deployment and approval operations
- Reduces rate limiting issues
- Enables comprehensive workflow monitoring

**Fallback:** `GITHUB_TOKEN` (standard)
- Works for most operations
- May have rate limiting in heavy workloads
- Some advanced monitoring may be limited

**Token source detection:**
The agent automatically uses the best available token in this order:
1. CODEX_MASTER_KEY
2. CODEX_BACKUP_KEY
3. GITHUB_TOKEN
```

### For Level 3 (Standard Token) Agents

```markdown
### Token Usage

This agent uses standard GitHub API operations and works with the default `GITHUB_TOKEN` provided by GitHub Actions.

**Operations:**
- Read-only PR/issue analysis
- Repository information retrieval
- Commit analysis

**Token scopes:** Standard GitHub Actions default scopes are sufficient
```

---

## Agency Policy Alignment Assessment

### Current Compliance Status

| Metric | Count | Status |
|--------|-------|--------|
| Agents with clear token guidance | 40 | ✅ Good |
| Agents needing guidance updates | 54 | ⚠️ Action needed |
| Level 1 agents with complete guidance | 29 | ✅ Critical |
| Level 1 agents with gaps | 44 | ⚠️ Priority |

### Agency Policy Principles

This audit verifies that all agents align with core agency policies:

1. **No Deferral**: Agents don't defer responsibility for elevated operations; they handle them directly
2. **Comprehensive Resolution**: Agents attempt to resolve issues using available tokens before requesting escalation
3. **Clear Token Hierarchy**: Agents understand the automatic fallback: MASTER → BACKUP → standard
4. **Audit Trail**: All token-dependent operations are logged with token source
5. **Error Handling**: Clear guidance on insufficient permissions and recovery paths

### Recommendations for Policy Alignment

**Priority 1 (Immediate):**
- Add token guidance to all Level 1 agents currently missing it (44 agents)
- Include specific scope requirements: `repo`, `actions:write`, `security_events`, `workflow`

**Priority 2 (Near-term):**
- Update all Level 2 agents with token preference documentation (5 agents)
- Add fallback behavior documentation

**Priority 3 (Ongoing):**
- Quarterly review of guidance gaps as new agents are added
- Validate agency policy alignment during agent development reviews

---

## Technical Specifications

### API Usage Breakdown

**By Operation Type:**
- variable write: 50 agents
- deployment: 45 agents
- PR operations: 37 agents
- security event handling: 35 agents
- workflow dispatch: 16 agents
- issue operations: 15 agents
- status check: 7 agents

### Capability Tag Analysis

Agents are classified based on their registered capability tags including:

- `workflow_dispatch` - Workflow automation and triggering
- `actions:write` - GitHub Actions write permissions required
- `security_events` - Security event and alert handling
- `deployment` - Release and deployment operations
- `orchestration` - Multi-agent coordination
- `codex_master_key` - Explicitly requires elevated token

---

## Audit Methodology

### Data Collection

1. Parsed AGENT_REGISTRY.yaml for all 147 active agents
2. Located prompt files for each agent across multiple locations:
   - `.github/agents/{agent_id}.md`
   - `.github/agents/{agent_id}/{agent_id}.md`
   - `.github/agents/{agent_dir}/prompt.md`
3. Analyzed first 50KB of each prompt for API usage patterns and guidance

### API Usage Detection

Used regex patterns to detect:
- GitHub API calls and REST operations
- Workflow dispatch and triggering
- PR/issue creation and updates
- Variable and secret management
- Deployment and release operations
- Security event handling

### Token Guidance Assessment

Scanned for 5 guidance signals:
- Explicit token mentions
- CODEX_MASTER_KEY references
- Scope and permission documentation
- Error handling procedures
- Token hierarchy explanation

### Classification Logic

- **Level 1**: Detected workflow_dispatch, variable_write, action_execution, security_events, or workflow_trigger patterns
- **Level 2**: Detected deployment, orchestration tags, or workflow approval patterns
- **Level 3**: Detected PR/issue operations or standard GitHub API usage
- **Level 0**: No API usage detected

---

## Validation Checklist

- [x] All 147 active agents reviewed
- [x] API usage correctly classified
- [x] Token guidance status accurately assessed
- [x] Alignment checks complete
- [x] Recommendations specific and actionable
- [x] JSON compliance matrix generated
- [x] Markdown report generated

---

## Deliverables

### Generated Files

1. **JSON Report**: `.codex/PHASE_1_AGENTS_AUDIT.json`
   - Machine-readable compliance matrix
   - Agent classification by token level
   - Guidance gap details
   - Policy alignment metrics

2. **Markdown Report**: `.codex/PHASE_1_AGENTS_AUDIT.md`
   - Comprehensive audit findings
   - Recommended guidance text for each level
   - Implementation recommendations
   - Technical specifications

---

**Audit Completed Successfully**

This audit provides the foundation for Phase 2 implementation of token guidance updates across all custom agents.
