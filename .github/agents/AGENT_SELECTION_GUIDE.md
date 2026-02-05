# Agent Selection Guide for Future AI Sessions

**Version:** 1.0.0  
**Purpose:** Help AI agents quickly select the right custom agent(s) for any task  
**Last Updated:** 2026-02-05T08:40:00Z

---

## Quick Decision Tree

```
START: What type of task?
│
├─ CI/CD Issues? → See [CI/CD Agents](#cicd-agents)
├─ Test Issues? → See [Testing Agents](#testing-agents)
├─ Security Issues? → See [Security Agents](#security-agents)
├─ Documentation Issues? → See [Documentation Agents](#documentation-agents)
├─ Configuration Issues? → See [Configuration Agents](#configuration-agents)
├─ RAG/ML Issues? → See [RAG/ML Agents](#ragml-agents)
├─ Repository Issues? → See [Repository Management Agents](#repository-management-agents)
└─ Other? → See [Specialized Agents](#specialized-agents)
```

---

## Agent Selection by Task Type

### CI/CD Agents

#### 🔥 **CI Pipeline is Failing**
**Primary Agent:** `ci-testing-agent`
- **Use When:** GitHub Actions workflow failing, build errors, test failures
- **Location:** `.github/agents/ci-testing-agent.md`
- **Chains To:** 
  - `ci-log-retrieval-agent` (get detailed logs)
  - `dependency-conflict-agent` (if dependency issues)
  - `workflow-ci-fixer` (to apply fixes)

**Example Activation:**
```
@copilot Use the CI Testing Agent to diagnose the workflow failure in run #12345
```

#### 📋 **Need CI Logs**
**Primary Agent:** `ci-log-retrieval-agent`
- **Use When:** Need authenticated access to GitHub Actions logs
- **Location:** `.github/agents/ci-log-retrieval-agent.md`
- **Best For:** Fetching logs, summarizing failures, extracting error patterns

#### ⚡ **Emergency CI Fixes**
**Primary Agent:** `ci-emergency-response-agent`
- **Use When:** Production broken, urgent fixes needed, all workflows failing
- **Location:** `.github/agents/ci-emergency-response-agent.md`
- **Authority Level:** High (can make immediate changes)

#### 🔍 **Monitor CI Health**
**Primary Agent:** `artifact-monitor-agent`
- **Use When:** Proactive monitoring, pattern detection, flakiness analysis
- **Location:** `.github/agents/artifact-monitor-agent.md`
- **Orchestrates:** Routes to 6+ specialized agents based on failure type
- **Best For:** Automated health checks, issue creation, trend analysis

#### 🔧 **Fix Workflow Syntax**
**Primary Agent:** `workflow-ci-fixer`
- **Use When:** YAML syntax errors, permission issues, workflow configuration problems
- **Location:** `.github/agents/workflow-ci-fixer.agent.md`
- **Best For:** Automated workflow repairs, syntax validation

#### 📦 **Dependency Conflicts**
**Primary Agent:** `dependency-conflict-agent`
- **Use When:** pip resolver conflicts, version incompatibilities, dependency hell
- **Location:** `.github/agents/dependency-conflict-agent.md`
- **Chains To:** `dependency-vulnerability-scanner` (security check after resolution)

#### 🛡️ **Dependency Vulnerabilities**
**Primary Agent:** `dependency-vulnerability-scanner`
- **Use When:** CVE scanning, security audit of dependencies, supply chain security
- **Location:** `.github/agents/dependency-vulnerability-scanner.agent.md`

#### 📊 **Workflow Analytics**
**Primary Agent:** `workflow-analytics-agent`
- **Use When:** Performance analysis, trend tracking, optimization opportunities
- **Location:** `.github/agents/workflow-analytics-agent.md`

---

### Testing Agents

#### ✅ **Improve Test Coverage**
**Primary Agent:** `coverage-roadmap-agent`
- **Use When:** Coverage below threshold, need systematic improvement strategy
- **Location:** `.github/agents/coverage-roadmap-agent.md`
- **Orchestrates:** Plans and delegates to test-writing agents
- **Chains To:**
  - `coverage-gapfill-agent` (fill specific gaps)
  - `test-enhancement-agent` (improve existing tests)
  - `tokenization-coverage-agent` (specialized for tokenization module)

#### 📈 **Monitor Coverage**
**Primary Agent:** `test-coverage-monitor`
- **Use When:** Track coverage over time, enforce thresholds, detect regressions
- **Location:** `.github/agents/test-coverage-monitor.agent.md`
- **Best For:** Continuous monitoring, coverage gate enforcement

#### 🎯 **Fill Coverage Gaps**
**Primary Agent:** `coverage-gapfill-agent`
- **Use When:** Specific modules have low coverage, need targeted tests
- **Location:** `.github/agents/coverage-gapfill-agent.md`
- **Best For:** Adding tests to uncovered code paths

#### 🔧 **Tests Broken After API Change**
**Primary Agent:** `test-alignment-fixer`
- **Use When:** API changed, tests need updating, assertion mismatches
- **Location:** `.github/agents/test-alignment-fixer.agent.md`
- **Best For:** Batch test updates, assertion fixes

#### 🏃 **Run Integration Tests**
**Primary Agent:** `integration-test-runner`
- **Use When:** Need cross-service testing, E2E validation
- **Location:** `.github/agents/integration-test-runner.agent.md`
- **Best For:** Multi-component testing, service integration

#### 🎭 **QA Audit**
**Primary Agent:** `qa-walkthrough-agent`
- **Use When:** Comprehensive QA needed, audit requirements, release validation
- **Location:** `.github/agents/qa-walkthrough-agent.md`
- **Orchestrates:** Parallel execution of coverage + alignment + integration checks
- **Best For:** Full repository QA, audit evidence generation

#### 🩺 **Auto-Fix Test Failures**
**Primary Agent:** `autonomous-test-healer-agent`
- **Use When:** Known test failure patterns, flaky tests, environment issues
- **Location:** `.github/agents/autonomous-test-healer-agent.md`
- **Best For:** Automated test repairs

#### 🧬 **Mutation Testing**
**Primary Agent:** `mutation-testing-agent`
- **Use When:** Validate test effectiveness, find weak tests
- **Location:** `.github/agents/mutation-testing-agent.md`
- **Best For:** Test quality assessment

#### 🔬 **Analyze Test Failures**
**Primary Agent:** `test-failure-analyzer-agent`
- **Use When:** Debugging test failures, root cause analysis
- **Location:** `.github/agents/test-failure-analyzer-agent.md`

#### 📝 **Tokenization Module Testing**
**Primary Agent:** `tokenization-coverage-agent`
- **Use When:** Working on src/tokenization/, need specialized tokenization tests
- **Location:** `.github/agents/tokenization-coverage-agent.md`
- **Specialty:** Deep tokenization knowledge, CLI validation

---

### Security Agents

#### 🚨 **GitHub Security Alert**
**Primary Agent:** `security-alert-verification-agent`
- **Use When:** Dependabot alert, CodeQL finding, security advisory
- **Location:** `.github/agents/security-alert-verification-agent.md`
- **Chains To:** `code-scanning-remediation-agent` (to fix issues)
- **Best For:** Alert triage, remediation planning

#### 🔍 **Code Scanning Issues**
**Primary Agent:** `code-scanning-remediation-agent`
- **Use When:** CodeQL alerts, SAST findings, code quality issues
- **Location:** `.github/agents/code-scanning-remediation-agent.md`
- **Best For:** Automated security fixes

#### ⚖️ **CodeQL Alert Resolution**
**Primary Agent:** `codeql-alert-resolution-agent`
- **Use When:** Specific CodeQL queries failing, need resolution guidance
- **Location:** `.github/agents/codeql-alert-resolution-agent.md`

#### 🛡️ **Security Audit**
**Primary Agent:** `security-audit-agent`
- **Use When:** Comprehensive security review, compliance check
- **Location:** `.github/agents/security-audit-agent.md`
- **Best For:** Full security assessment

#### 🔒 **IPC Bridge Security**
**Primary Agent:** `bridge-security-monitor`
- **Use When:** Inter-process communication security, message validation
- **Location:** `.github/agents/bridge-security-monitor.agent.md`
- **Specialty:** IPC security monitoring

#### 📊 **Performance Regression**
**Primary Agent:** `performance-regression-detector`
- **Use When:** Detect performance degradation, latency increases
- **Location:** `.github/agents/performance-regression-detector.agent.md`
- **Best For:** Performance monitoring, regression alerts

#### 🔐 **PII Compliance**
**Primary Agent:** `pii-scrubber`
- **Use When:** GDPR/CCPA compliance, remove PII from logs/data
- **Location:** `.github/agents/pii-scrubber.agent.md`
- **Best For:** Data privacy, compliance automation

---

### Documentation Agents

#### 📚 **Consolidate Documentation**
**Primary Agent:** `documentation-consolidator`
- **Use When:** Multiple overlapping docs, need consolidation, reduce duplication
- **Location:** `.github/agents/documentation-consolidator.md`
- **Chains To:**
  - `link-validator-agent` (fix broken links)
  - `reference-updater-agent` (update references)
- **Best For:** Documentation cleanup, deduplication

#### ✅ **Documentation Quality Check**
**Primary Agent:** `documentation-quality-agent`
- **Use When:** Assess doc quality, find issues, validate MkDocs build
- **Location:** `.github/agents/documentation-quality-agent.md`
- **Orchestrates:** Parallel checks for freshness, links, quality
- **Best For:** Documentation audits, quality scores

#### 🔗 **Validate Links**
**Primary Agent:** `link-validator-agent`
- **Use When:** Check for broken links, validate cross-references, anchor validation
- **Location:** `.github/agents/link-validator-agent.md`
- **Best For:** Link checking, reference validation

#### 📅 **Check Documentation Freshness**
**Primary Agent:** `doc-freshness-checker`
- **Use When:** Find stale docs, identify outdated content
- **Location:** `.github/agents/doc-freshness-checker.agent.md`
- **Best For:** Freshness monitoring, staleness detection

#### 🔍 **Semantic Search**
**Primary Agent:** `semantic-search`
- **Use When:** Find relevant documentation, semantic code search
- **Location:** `.github/agents/semantic-search.agent.md`
- **Best For:** Intelligent search over codebase and docs

#### ✓ **Verify Claims**
**Primary Agent:** `claim-verification-agent`
- **Use When:** Validate commit messages match reality, verify documentation claims
- **Location:** `.github/agents/claim-verification-agent.md`
- **Best For:** Accuracy validation

---

### Configuration Agents

#### 🔄 **Migrate Configurations**
**Primary Agent:** `config-migration-assistant`
- **Use When:** Migrate to Hydra, convert legacy configs, modernize configuration
- **Location:** `.github/agents/config-migration-assistant.agent.md`
- **Best For:** Configuration migration, backward compatibility

#### ✅ **Validate Configurations**
**Primary Agent:** `config-validator`
- **Use When:** Validate Hydra configs, schema compliance, type checking
- **Location:** `.github/agents/config-validator.agent.md`
- **Best For:** Configuration validation, schema enforcement

#### 🦀 **Rust Configuration**
**Primary Agent:** `rust-config-validator`
- **Use When:** Validate Cargo.toml, feature flags, Rust-specific configs
- **Location:** `.github/agents/rust-config-validator.md`
- **Specialty:** Rust configuration expertise

---

### RAG/ML Agents

#### 🧠 **RAG Index Management**
**Primary Agent:** `rag-index-manager`
- **Use When:** Build/update/query RAG indices, vector database operations
- **Location:** `.github/agents/rag-index-manager.agent.md`
- **Best For:** RAG pipeline management

#### ⚡ **PyTorch Meta Tensor Issues**
**Primary Agent:** `meta-tensor-validator`
- **Use When:** Meta tensor errors, PyTorch 2.6+ issues, model initialization problems
- **Location:** `.github/agents/meta-tensor-validator.md`
- **Best For:** Preventing meta tensor regressions, validation

#### 🛡️ **RAG Meta Tensor Protection**
**Primary Agent:** `rag-meta-tensor-regression-agent`
- **Use When:** RAG module initialization issues, SentenceTransformer problems
- **Location:** `.github/agents/rag-meta-tensor-regression-agent.md`
- **Specialty:** RAG-specific tensor validation

#### 👁️ **RAG Tensor Guardian**
**Primary Agent:** `rag-meta-tensor-guardian`
- **Use When:** Guard RAG operations, prevent tensor issues
- **Location:** `.github/agents/rag-meta-tensor-guardian.md`
- **Best For:** Proactive RAG protection

#### 🗂️ **RAG Module Management**
**Primary Agent:** `rag-module-management-agent`
- **Use When:** Manage RAG modules, coordinate RAG operations
- **Location:** `.github/agents/rag-module-management-agent.md`
- **Best For:** RAG ecosystem coordination

---

### Repository Management Agents

#### 🧹 **Repository Cleanup**
**Primary Agent:** `repository-hygiene-agent`
- **Use When:** General cleanup, code health, remove cruft
- **Location:** `.github/agents/repository-hygiene-agent.md`
- **Orchestrates:** Delegates to organizer, consolidator, validator agents
- **Best For:** Comprehensive repository maintenance

#### 📂 **Organize Root Directory**
**Primary Agent:** `root-organizer-agent`
- **Use When:** Root folder cluttered, need reorganization, zero-break guarantee needed
- **Location:** `.github/agents/root-organizer-agent.md`
- **Chains To:** `reference-updater-agent` (update references after moves)
- **Best For:** Safe file reorganization

#### 🔗 **Update References**
**Primary Agent:** `reference-updater-agent`
- **Use When:** Files moved, need to update imports/links, atomic reference updates
- **Location:** `.github/agents/reference-updater-agent.md`
- **Best For:** Transaction-like reference updates, link fixing

#### 📋 **Repository Organization**
**Primary Agent:** `repository-organization-agent`
- **Use When:** Broader organizational changes, structure improvements
- **Location:** `.github/agents/repository-organization-agent.md`
- **Best For:** Repository restructuring

---

### Specialized Agents

#### ⏰ **Datetime Modernization**
**Primary Agent:** `datetime-modernizer`
- **Use When:** Timezone issues, need UTC conversion, datetime object problems
- **Location:** `.github/agents/datetime-modernizer.agent.md`
- **Best For:** Datetime refactoring

#### 📝 **Code Review**
**Primary Agent:** `codex-reviewer`
- **Use When:** PR review needed, code quality checks, quantum-inspired analysis
- **Location:** `.github/agents/codex-reviewer.agent.yml`
- **Best For:** Automated PR reviews

#### 🔬 **Code Analysis**
**Primary Agent:** `code-analysis-agent`
- **Use When:** General code quality analysis, pattern detection
- **Location:** `.github/agents/code-analysis-agent.md`

#### 🧠 **Cognitive Brain Management**
**Primary Agent:** `cognitive-brain-manager`
- **Use When:** Manage cognitive system, knowledge base operations
- **Location:** `.github/agents/cognitive-brain-manager.md`
- **Specialty:** Cognitive system expertise

#### 💻 **Cross-Platform Filenames**
**Primary Agent:** `cross-platform-filename-validator`
- **Use When:** Windows compatibility issues, filename validation
- **Location:** `.github/agents/cross-platform-filename-validator.md`
- **Best For:** Filename compliance

#### ✓ **Approval Guard**
**Primary Agent:** `owner-approval-guard`
- **Use When:** Require human approval, cost-incurring operations, safety checkpoint
- **Location:** `.github/agents/owner-approval-guard.agent.md`
- **Best For:** Approval enforcement

#### 📊 **Performance Monitoring**
**Primary Agent:** `performance-monitor-agent`
- **Use When:** Real-time performance tracking, latency monitoring
- **Location:** `.github/agents/performance-monitor-agent.md`
- **Best For:** Performance metrics

---

## Common Orchestration Scenarios

### Scenario 1: CI Pipeline Failing
**Goal:** Diagnose and fix CI failure

**Orchestration:**
```
1. artifact-monitor-agent (detects failure, routes to appropriate agent)
   ↓
2. ci-testing-agent (diagnoses root cause)
   ↓
3. ci-log-retrieval-agent (fetches detailed logs)
   ↓
4. CONDITIONAL:
   - If dependency issue → dependency-conflict-agent
   - If test failure → test-failure-analyzer-agent
   - If workflow syntax → workflow-ci-fixer
   ↓
5. Apply appropriate fixes
   ↓
6. test-coverage-monitor (validate no coverage regression)
```

**Command:**
```
@copilot The CI pipeline is failing. Use artifact-monitor-agent to detect 
the issue type, then chain to appropriate diagnostic agents.
```

### Scenario 2: Improve Test Coverage
**Goal:** Systematically improve test coverage

**Orchestration:**
```
1. test-coverage-monitor (identify current coverage)
   ↓
2. coverage-roadmap-agent (create improvement strategy)
   ↓
3. PARALLEL:
   - coverage-gapfill-agent (fill general gaps)
   - tokenization-coverage-agent (specialized for tokenization)
   - test-enhancement-agent (improve existing tests)
   ↓
4. test-coverage-monitor (validate improvements)
   ↓
5. qa-walkthrough-agent (comprehensive validation)
```

**Command:**
```
@copilot Use coverage-roadmap-agent to create a systematic plan to improve 
test coverage from 72% to 90%, then orchestrate the implementation.
```

### Scenario 3: Security Alert Response
**Goal:** Handle GitHub security alert

**Orchestration:**
```
1. security-alert-verification-agent (verify and triage)
   ↓
2. CONDITIONAL:
   - If code issue → code-scanning-remediation-agent
   - If dependency → dependency-vulnerability-scanner
   ↓
3. security-audit-agent (comprehensive check)
   ↓
4. owner-approval-guard (require approval for fixes)
   ↓
5. Apply fixes
   ↓
6. security-alert-verification-agent (re-verify)
```

**Command:**
```
@copilot Security alert #42 was triggered. Use security-alert-verification-agent 
to triage, then orchestrate appropriate remediation agents.
```

### Scenario 4: Documentation Cleanup
**Goal:** Consolidate and improve documentation

**Orchestration:**
```
1. documentation-quality-agent (assess current state)
   ↓
2. PARALLEL:
   - doc-freshness-checker (find stale docs)
   - link-validator-agent (find broken links)
   - claim-verification-agent (verify accuracy)
   ↓
3. documentation-consolidator (merge duplicates)
   ↓
4. reference-updater-agent (update all references)
   ↓
5. link-validator-agent (re-validate links)
   ↓
6. documentation-quality-agent (final assessment)
```

**Command:**
```
@copilot The documentation needs cleanup. Use documentation-quality-agent 
to assess, then orchestrate consolidation and validation agents.
```

### Scenario 5: Repository Maintenance
**Goal:** Comprehensive repository cleanup

**Orchestration:**
```
1. repository-hygiene-agent (coordinator)
   ↓
2. HIERARCHICAL:
   ├─ root-organizer-agent
   │  ├─ reference-updater-agent
   │  └─ link-validator-agent
   ├─ documentation-consolidator
   │  ├─ documentation-quality-agent
   │  └─ doc-freshness-checker
   └─ code-analysis-agent
   ↓
3. test-coverage-monitor (ensure no breakage)
   ↓
4. qa-walkthrough-agent (final validation)
```

**Command:**
```
@copilot Run comprehensive repository maintenance using repository-hygiene-agent 
to coordinate all cleanup operations.
```

---

## Agent Selection Decision Matrix

| If Task Involves... | Primary Agent | Secondary Agents |
|---------------------|---------------|------------------|
| CI failing | ci-testing-agent | ci-log-retrieval-agent, dependency-conflict-agent |
| Need CI logs | ci-log-retrieval-agent | - |
| Workflow syntax error | workflow-ci-fixer | - |
| Dependency conflict | dependency-conflict-agent | dependency-vulnerability-scanner |
| Low test coverage | coverage-roadmap-agent | coverage-gapfill-agent, test-enhancement-agent |
| Tests broken after API change | test-alignment-fixer | - |
| Need QA audit | qa-walkthrough-agent | test-coverage-monitor, integration-test-runner |
| Security alert | security-alert-verification-agent | code-scanning-remediation-agent |
| CodeQL findings | codeql-alert-resolution-agent | code-scanning-remediation-agent |
| Documentation cleanup | documentation-consolidator | link-validator-agent, doc-freshness-checker |
| Broken links | link-validator-agent | reference-updater-agent |
| Config migration | config-migration-assistant | config-validator |
| Meta tensor errors | meta-tensor-validator | rag-meta-tensor-regression-agent |
| RAG issues | rag-index-manager | rag-module-management-agent |
| File reorganization | root-organizer-agent | reference-updater-agent |
| Repository cleanup | repository-hygiene-agent | root-organizer-agent, documentation-consolidator |
| Performance issues | performance-regression-detector | performance-monitor-agent |
| Datetime issues | datetime-modernizer | - |

---

## Quick Reference Commands

### Activate Single Agent
```
@copilot Use the [agent-name] to [specific task]
```

### Activate with Chaining
```
@copilot Use [agent-1] to [task-1], then chain to [agent-2] for [task-2]
```

### Activate with Orchestration
```
@copilot Orchestrate [primary-agent] to coordinate [agent-2], [agent-3], 
and [agent-4] for [overall-goal]
```

### Activate with Conditions
```
@copilot Use [diagnostic-agent] to analyze the issue, then conditionally 
route to the appropriate fix agent based on the diagnosis
```

---

## Best Practices for Future AI Sessions

### 1. **Start with Diagnostic Agents**
- Use monitoring/diagnostic agents first to understand the problem
- Example: `artifact-monitor-agent`, `ci-testing-agent`, `documentation-quality-agent`

### 2. **Use Orchestration for Complex Tasks**
- Don't try to do everything yourself
- Leverage specialized agents with orchestration
- Let primary agent coordinate secondary agents

### 3. **Chain Related Agents**
- Follow the chains documented in each agent
- Example: `ci-testing-agent` → `ci-log-retrieval-agent` → `workflow-ci-fixer`

### 4. **Validate After Changes**
- Always use monitoring agents to validate
- Example: After coverage improvements → `test-coverage-monitor`

### 5. **Use Parallel Execution When Possible**
- Independent tasks can run in parallel
- Example: `doc-freshness-checker` + `link-validator-agent` + `claim-verification-agent`

---

## Agent Capability Matrix

| Capability | Agents with This Capability |
|------------|----------------------------|
| **Orchestration** | artifact-monitor-agent, coverage-roadmap-agent, repository-hygiene-agent, documentation-quality-agent, qa-walkthrough-agent |
| **Chaining Support** | 11 agents (see AGENT_CHAINING_GUIDE.md) |
| **Autonomous Fixes** | ci-testing-agent, workflow-ci-fixer, test-alignment-fixer, autonomous-test-healer-agent |
| **Log Analysis** | ci-log-retrieval-agent, test-failure-analyzer-agent |
| **Security Focus** | 6 security agents |
| **Documentation Focus** | 5 documentation agents |
| **Testing Focus** | 12 testing agents |
| **Approval Required** | owner-approval-guard |

---

## Summary: Agent Selection Strategy

1. **Identify Task Category** (CI/CD, Testing, Security, Docs, etc.)
2. **Find Primary Agent** (use tables above)
3. **Check for Orchestration Needs** (complex tasks need coordination)
4. **Identify Chain Opportunities** (related agents that should follow)
5. **Activate with Clear Intent** (specific task description)
6. **Validate Results** (use monitoring agents)

---

**Document Status:** ✅ COMPLETE  
**For:** Future AI Agent Sessions  
**Purpose:** Enable effective agent selection and orchestration  
**Maintainer:** AI Agent Ecosystem Team

---

## Session Management Agents

#### 📜 **Recall Previous Sessions**
**Primary Agent:** `session-log-retrieval-agent`
- **Use When:** Need to recall previous Copilot session work, extract uncommitted details, search conversation history
- **Location:** `.github/agents/session-log-retrieval-agent.md`
- **Best For:** Session continuity, recovering uncommitted work, conversation search

**Tools:**
- `python -m codex.logging.query_logs` - Query session database
- `python -m codex.logging.session_query` - Session-specific queries
- `python -m codex.logging.viewer` - Interactive log viewer

**Example Activation:**
```
@copilot Use the Session Log Retrieval Agent to find what we discussed 
about test coverage in yesterday's session and extract any uncommitted code.
```

**Common Use Cases:**
1. **Resume Previous Work:** Get context from last session
2. **Recover Uncommitted Code:** Extract code snippets discussed but not saved
3. **Find Command History:** Retrieve commands executed previously
4. **Search Conversations:** Find when topics were discussed
5. **Session Audit:** Review what an agent did in a session

**Query Examples:**
```bash
# Get last session summary
python -m codex.logging.query_logs --order desc --limit 1 --format json

# Find uncommitted work
python -m codex.logging.query_logs --session-id <ID> --contains "uncommitted"

# Search for errors
python -m codex.logging.query_logs --contains "error|failed" --role assistant

# Get command history
python -m codex.logging.query_logs --contains "bash|git" --role tool
```

---

## Updated Agent Selection Matrix

| If Task Involves... | Primary Agent | Secondary Agents |
|---------------------|---------------|------------------|
| ... (previous rows) ... |
| Recall previous session | session-log-retrieval-agent | cognitive-brain-manager |
| Recover uncommitted work | session-log-retrieval-agent | - |
| Search conversation history | session-log-retrieval-agent | - |
| Command history | session-log-retrieval-agent | - |

