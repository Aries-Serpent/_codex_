# Custom GitHub Copilot Agents Catalog

**Version**: 1.0.0  
**Last Updated**: 2026-01-10  
**Purpose**: Comprehensive catalog of all available custom agents for GitHub Copilot task delegation  
**Status**: 🟢 Active - Production Reference

---

## Executive Summary

This document catalogs all **26 custom GitHub Copilot agents** available in the `_codex_` repository. These agents are specialized tools designed to automate specific tasks and can be invoked directly from GitHub Copilot using the MCP (Model Context Protocol) framework or agent-specific tool calls.

**Quick Reference**: When working with GitHub Copilot, you can delegate tasks to these agents instead of handling them manually. Simply use the appropriate agent tool or reference the agent by name in your prompt.

---

## How to Use Custom Agents

### From GitHub Copilot Interface

1. **In PR Comments**: `@copilot use the ci-testing-agent to generate tests for RAG modules`
2. **In Tool Calls**: Use the agent-specific tool (e.g., `ci-testing-agent`)
3. **In Prompts**: Reference the agent by name and describe the task

### Verification Status

✅ **Available in Copilot Dropdown**: Agents with `.agent.md` or `agent.yml` files  
🔧 **Requires Tool Call**: Agents accessed via custom tool invocation  
📋 **Planned**: Agents with specifications but not yet implemented

---

## Category 1: Testing & Quality Assurance

### 1. ✅ CI Testing Agent
**Tool Name**: `ci-testing-agent`  
**File**: `.github/agents/ci-testing-agent.md`  
**Status**: 🟢 Implemented & Production-Ready

**Capabilities**:
- Generate comprehensive test suites for uncovered code
- Validate test coverage against thresholds (85-90%+)
- Execute tests and generate coverage reports
- Auto-fix common test failures (imports, assertions, fixtures)
- Detect performance regressions
- Generate test summary reports

**Use Cases**:
- "Generate tests for the RAG module to achieve 90% coverage"
- "Add error path tests for retriever.py and indexer.py"
- "Run coverage analysis and report gaps"

**Example Invocation**:
```python
ci-testing-agent({
    "prompt": "Complete RAG module coverage - error paths & validation"
})
```

---

### 2. ✅ Test Coverage Monitor Agent
**Tool Name**: `test-coverage-monitor`  
**File**: `.github/agents/test-coverage-monitor.agent.md`  
**Status**: 🟢 Available

**Capabilities**:
- Monitor test coverage in real-time
- Identify uncovered code paths
- Enforce coverage thresholds (configurable)
- Generate coverage reports and dashboards
- Track coverage trends over time

**Use Cases**:
- "Monitor coverage for the entire codebase"
- "Alert if coverage drops below 85%"
- "Generate a coverage dashboard"

---

### 3. ✅ Test Alignment Fixer Agent
**Tool Name**: `test-alignment-fixer`  
**File**: `.github/agents/test-alignment-fixer.agent.md`  
**Status**: 🟢 Available

**Capabilities**:
- Fix test alignment issues after API changes
- Update test assertions to match new behavior
- Regenerate mocks and fixtures
- Fix import errors in tests
- Ensure test consistency across the codebase

**Use Cases**:
- "Fix tests after API changes in the authentication module"
- "Update all test assertions for the new response format"

---

### 4. ✅ Integration Test Runner Agent
**Tool Name**: `integration-test-runner`  
**File**: `.github/agents/integration-test-runner.agent.md`  
**Status**: 🟢 Available

**Capabilities**:
- Run integration tests across multiple services
- Validate cross-component interactions
- Generate comprehensive test reports
- Detect integration failures and conflicts
- Orchestrate test environments

**Use Cases**:
- "Run integration tests for the RAG pipeline"
- "Validate interactions between indexer and retriever"

---

### 5. ✅ Performance Regression Detector Agent
**Tool Name**: `performance-regression-detector`  
**File**: `.github/agents/performance-regression-detector.agent.md`  
**Status**: 🟢 Available

**Capabilities**:
- Detect performance regressions by comparing metrics
- Alert on significant performance degradation
- Generate performance comparison reports
- Identify performance bottlenecks
- Track performance trends

**Use Cases**:
- "Check for performance regressions in the latest commit"
- "Compare query latency against baseline"

---

## Category 2: CI/CD & Infrastructure

### 6. ✅ CI Optimizer Agent
**Tool Name**: `ci-optimizer-agent`  
**File**: `.github/agents/ci-optimizer-agent/agent.yml`  
**Status**: 🟢 Available

**Capabilities**:
- Self-optimizing CI workflows
- Test prioritization and parallelization
- Reduce CI execution time
- Optimize resource usage
- Intelligent test selection

**Use Cases**:
- "Optimize CI pipeline for faster execution"
- "Prioritize tests based on code changes"

---

### 7. 📋 Infra Linter Agent
**Tool Name**: `infra-linter-agent`  
**File**: `.github/agents/infra-linter-agent/README.md`  
**Status**: 📋 Planned

**Capabilities**:
- Validate GitHub Actions workflow files
- Lint Kubernetes manifests
- Check Docker configurations
- Validate secrets and environment variables
- Ensure infrastructure best practices

**Use Cases**:
- "Lint all workflow files for syntax errors"
- "Validate Kubernetes deployment manifests"

---

### 8. 📋 Flaky Triage Agent
**Tool Name**: `flaky-triage-agent`  
**File**: Referenced in `AGENT_ECOSYSTEM_MAP.md`  
**Status**: 📋 Planned

**Capabilities**:
- Detect flaky tests from CI logs
- Quarantine intermittent test failures
- Calculate flake rates per test
- Prioritize flaky test fixes
- Generate flake reports

**Use Cases**:
- "Identify all flaky tests in the last 30 days"
- "Quarantine flaky tests and create tracking issues"

---

## Category 3: Security & Compliance

### 9. ✅ Dependency Vulnerability Scanner Agent
**Tool Name**: `dependency-vulnerability-scanner`  
**File**: `.github/agents/dependency-vulnerability-scanner.agent.md`  
**Status**: 🟢 Available

**Capabilities**:
- Scan dependencies for known vulnerabilities
- Query multiple vulnerability databases (OSV, CVE, NVD)
- Generate security reports
- Suggest upgrade paths
- Prioritize vulnerabilities by severity

**Use Cases**:
- "Scan all dependencies for vulnerabilities"
- "Check if Werkzeug vulnerability affects our version"

---

### 10. 📋 Security Scan Agent
**Tool Name**: `security-scan-agent`  
**File**: Referenced in `AGENT_ECOSYSTEM_MAP.md`  
**Status**: 📋 Planned

**Capabilities**:
- Run SAST/SCA security scans (Bandit, Semgrep)
- Parse SARIF output
- Filter false positives
- Annotate PRs with security findings
- Generate security summary reports

**Use Cases**:
- "Run security scan on the authentication module"
- "Annotate PR with security findings"

---

### 11. ✅ Bridge Security Monitor Agent
**Tool Name**: `bridge-security-monitor`  
**File**: `.github/agents/bridge-security-monitor.agent.md`  
**Status**: 🟢 Available

**Capabilities**:
- Monitor IPC bridge security
- Detect unauthorized access attempts
- Validate message integrity
- Track security events
- Generate security audit logs

**Use Cases**:
- "Monitor bridge security for suspicious activity"
- "Validate message integrity for all IPC communications"

---

### 12. ✅ PII Scrubber Agent
**Tool Name**: `pii-scrubber`  
**File**: `.github/agents/pii-scrubber.agent.md`  
**Status**: 🟢 Available

**Capabilities**:
- Scrub PII from text content
- Ensure GDPR/CCPA compliance
- Detect credit cards, SSNs, emails, phone numbers
- Redact sensitive information
- Generate scrubbing reports

**Use Cases**:
- "Scrub PII from log files before processing"
- "Ensure RAG pipeline is GDPR compliant"

---

### 13. ✅ Owner Approval Guard Agent
**Tool Name**: `owner-approval-guard`  
**File**: `.github/agents/owner-approval-guard.agent.md`  
**Status**: 🟢 Available

**Capabilities**:
- Enforce owner approval requirements
- Guard cost-incurring operations
- Validate authorization for sensitive workflows
- Track approval history
- Generate approval audit logs

**Use Cases**:
- "Require owner approval before deploying to production"
- "Guard all cost-incurring API calls"

---

### 14. 📋 Compliance Checker Agent
**Tool Name**: `compliance-checker-agent`  
**File**: `.github/agents/compliance-checker-agent/`  
**Status**: 📋 Planned

**Capabilities**:
- Enforce coding standards
- Validate license compliance
- Check accessibility (WCAG)
- Ensure regulatory compliance
- Generate compliance reports

**Use Cases**:
- "Check all dependencies for license compliance"
- "Validate accessibility standards for UI components"

---

## Category 4: Documentation & Knowledge Management

### 15. ✅ Documentation Agent
**Tool Name**: `documentation-agent`  
**File**: `.github/agents/documentation-agent/agent.yml`  
**Status**: 🟢 Available

**Capabilities**:
- Auto-generate API documentation
- Create tutorials and guides
- Generate architecture diagrams
- Update changelogs
- Maintain documentation freshness

**Use Cases**:
- "Generate API docs for the RAG module"
- "Create a tutorial for using CachedRetriever"

---

### 16. ✅ Doc Freshness Checker Agent
**Tool Name**: `doc-freshness-checker`  
**File**: `.github/agents/doc-freshness-checker.agent.md`  
**Status**: 🟢 Available

**Capabilities**:
- Check documentation staleness
- Validate links across documentation
- Identify outdated content
- Generate freshness reports
- Suggest documentation updates

**Use Cases**:
- "Check all documentation for stale content"
- "Validate all links in the docs/ directory"

---

### 17. ✅ Semantic Search Agent
**Tool Name**: `semantic-search`  
**File**: `.github/agents/semantic-search.agent.md`  
**Status**: 🟢 Available

**Capabilities**:
- Semantic search over codebase and docs
- Vector embedding-based search
- Context-aware code search
- Natural language queries
- Relevance ranking

**Use Cases**:
- "Find all functions that handle authentication"
- "Search for examples of cache implementation"

---

### 18. ✅ RAG Index Manager Agent
**Tool Name**: `rag-index-manager`  
**File**: `.github/agents/rag-index-manager.agent.md`  
**Status**: 🟢 Available

**Capabilities**:
- Build and update RAG indices
- Manage multi-tenant indices
- Query knowledge base
- Optimize index performance
- Validate index integrity

**Use Cases**:
- "Build RAG index for the documentation"
- "Update index with latest code changes"

---

### 19. 📋 Data RAG Helper Agent
**Tool Name**: `data-rag-helper`  
**File**: Referenced in `AGENT_ECOSYSTEM_MAP.md`  
**Status**: 📋 Planned

**Capabilities**:
- Answer questions about repository documentation
- Provide context-aware responses
- Surface relevant code examples
- Generate documentation snippets
- Maintain conversation context

**Use Cases**:
- "How do I use the CachedRetriever class?"
- "Show me examples of tenant management"

---

## Category 5: Configuration & Migration

### 20. ✅ Config Validator Agent
**Tool Name**: `config-validator`  
**File**: `.github/agents/config-validator.agent.md`  
**Status**: 🟢 Available

**Capabilities**:
- Validate Hydra configuration files
- Check schema compliance
- Ensure type safety
- Validate cross-config consistency
- Generate validation reports

**Use Cases**:
- "Validate all Hydra config files"
- "Check config schema compliance"

---

### 21. ✅ Config Migration Assistant Agent
**Tool Name**: `config-migration-assistant`  
**File**: `.github/agents/config-migration-assistant.agent.md`  
**Status**: 🟢 Available

**Capabilities**:
- Migrate legacy configs to Hydra
- Ensure backward compatibility
- Validate migrated configs
- Generate migration reports
- Handle edge cases

**Use Cases**:
- "Migrate all legacy configs to Hydra format"
- "Validate migrated configuration files"

---

### 22. ✅ DateTime Modernizer Agent
**Tool Name**: `datetime-modernizer`  
**File**: `.github/agents/datetime-modernizer.agent.md`  
**Status**: 🟢 Available

**Capabilities**:
- Modernize datetime handling
- Convert to timezone-aware objects
- Use UTC-based timestamps
- Fix naive datetime usage
- Generate migration reports

**Use Cases**:
- "Modernize all datetime usage to be timezone-aware"
- "Convert timestamps to UTC format"

---

## Category 6: Advanced Intelligence & Coordination

### 23. ✅ Ecosystem Coordinator Agent
**Tool Name**: `ecosystem-coordinator-agent`  
**File**: `.github/agents/ecosystem-coordinator-agent/agent.yml`  
**Status**: 🟢 Available

**Capabilities**:
- Multi-agent task decomposition
- Coordinate agent workflows
- Optimize task distribution
- Resolve agent conflicts
- Generate coordination reports

**Use Cases**:
- "Coordinate multiple agents to complete RAG coverage task"
- "Decompose large task into agent-specific subtasks"

---

### 24. ✅ Emergent Intelligence Agent
**Tool Name**: `emergent-intelligence-agent`  
**File**: `.github/agents/emergent-intelligence-agent/agent.yml`  
**Status**: 🟢 Available

**Capabilities**:
- Identify emergent patterns in codebase
- Detect architectural issues
- Suggest refactoring opportunities
- Learn from past decisions
- Generate intelligence reports

**Use Cases**:
- "Identify emergent patterns in the testing code"
- "Suggest architectural improvements"

---

### 25. ✅ Reasoning Advisor Agent
**Tool Name**: `reasoning-advisor-agent`  
**File**: `.github/agents/reasoning-advisor-agent/agent.yml`  
**Status**: 🟢 Available

**Capabilities**:
- Causal analysis of code behavior
- Explainable AI recommendations
- Decision tree generation
- Root cause analysis
- Generate reasoning reports

**Use Cases**:
- "Explain why coverage is failing"
- "Analyze root cause of test failures"

---

### 26. ✅ Performance Monitor Agent
**Tool Name**: `performance-monitor-agent`  
**File**: `.github/agents/performance-monitor-agent/agent.yml`  
**Status**: 🟢 Available

**Capabilities**:
- Real-time performance tracking
- Latency monitoring
- Throughput optimization
- Resource usage analysis
- Generate performance dashboards

**Use Cases**:
- "Monitor performance of RAG queries"
- "Track query latency trends"

---

## Category 7: Release & Deployment

### 27. 📋 Release Gate Agent
**Tool Name**: `release-gate-agent`  
**File**: `.github/agents/release-gate-agent/README.md`  
**Status**: 📋 Planned

**Capabilities**:
- Enforce release readiness gates
- Validate tests, coverage, docs, security
- Collect required approvals
- Generate release notes
- Create release status reports

**Use Cases**:
- "Check release readiness for v1.0.0"
- "Generate release notes from commits"

---

### 28. 📋 Dependency Upgrade Agent
**Tool Name**: `dep-upgrade-agent`  
**File**: Referenced in `AGENT_ECOSYSTEM_MAP.md`  
**Status**: 📋 Planned

**Capabilities**:
- Safe dependency bumps (minor/patch)
- Analyze upgrade impact
- Create draft PRs for upgrades
- Run CI validation
- Generate upgrade reports

**Use Cases**:
- "Propose safe dependency upgrades"
- "Update all patch versions"

---

## Agent Selection Guide

### By Task Type

| Task | Recommended Agent(s) |
|------|---------------------|
| **Generate tests** | ci-testing-agent, test-coverage-monitor |
| **Fix test failures** | test-alignment-fixer, ci-testing-agent |
| **Check security** | dependency-vulnerability-scanner, security-scan-agent |
| **Validate configs** | config-validator, infra-linter-agent |
| **Generate docs** | documentation-agent, semantic-search |
| **Monitor performance** | performance-monitor-agent, performance-regression-detector |
| **Coordinate agents** | ecosystem-coordinator-agent |
| **Analyze code** | emergent-intelligence-agent, reasoning-advisor-agent |

### By Expertise Level

**Beginner-Friendly**:
- documentation-agent
- semantic-search
- test-coverage-monitor

**Intermediate**:
- ci-testing-agent
- config-validator
- dependency-vulnerability-scanner

**Advanced**:
- ecosystem-coordinator-agent
- emergent-intelligence-agent
- reasoning-advisor-agent

---

## Verification: GitHub Copilot Dropdown Access

To verify if an agent appears in the GitHub Copilot agent dropdown:

1. **File Format**:
   - ✅ `.agent.md` files (GitHub Copilot native format)
   - ✅ `agent.yml` files in agent directories
   - ❌ Plain documentation files without agent metadata

2. **Required Frontmatter**:
   ```markdown
   ---
   name: agent-name
   description: Agent description
   ---
   ```

3. **Location**: Must be in `.github/agents/` directory

### Agents Confirmed Available in Dropdown

Based on file format analysis:

**Markdown Format (`.agent.md`)**: 14 agents
- bridge-security-monitor
- config-migration-assistant
- config-validator
- datetime-modernizer
- dependency-vulnerability-scanner
- doc-freshness-checker
- integration-test-runner
- owner-approval-guard
- performance-regression-detector
- pii-scrubber
- rag-index-manager
- semantic-search
- test-alignment-fixer
- test-coverage-monitor

**YAML Format (`agent.yml`)**: 6 agents
- ci-optimizer-agent
- documentation-agent
- ecosystem-coordinator-agent
- emergent-intelligence-agent
- performance-monitor-agent
- reasoning-advisor-agent

**Custom Tool Invocation**: 1 agent
- ci-testing-agent (accessed via `ci-testing-agent` tool)

**Total Available**: **21 agents** confirmed accessible via GitHub Copilot

---

## Integration with Cognitive Brain

All agents integrate with the Cognitive Brain using the PDA (Perception-Decision-Action) loop and AfterMath tagging protocol:

```yaml
perception:
  - Gather context from codebase
  - Parse relevant files and data
  - Query Cognitive Brain for history

decision:
  - Analyze options
  - Prioritize actions
  - Select strategy

action:
  - Execute operations
  - Validate results
  - Generate reports

aftermath:
  - Tag decisions with #AFTERMATH_*
  - Record metrics
  - Update Cognitive Brain
  - Document learnings
```

### AfterMath Tags

- `#AFTERMATH_DECISION` - Major decisions made
- `#AFTERMATH_METRIC` - Quantitative measurements
- `#AFTERMATH_QUALITY_CHECK` - Quality validations
- `#AFTERMATH_PATTERN_IDENTIFIED` - Recurring patterns
- `#AFTERMATH_BLOCKER_RESOLVED` - Issues overcome
- `#AFTERMATH_LESSON_LEARNED` - Insights gained
- `#AFTERMATH_NEXT_STEPS` - Future actions

---

## Best Practices for Agent Usage

1. **Single Responsibility**: Choose the most specialized agent for your task
2. **Coordination**: Use ecosystem-coordinator-agent for multi-step workflows
3. **Verification**: Always validate agent outputs before committing
4. **Documentation**: Document agent usage in PR descriptions
5. **Feedback**: Report agent performance to improve future sessions

---

## Next Steps

### Immediate Actions
- ✅ Catalog all agents (COMPLETE)
- [ ] Verify dropdown accessibility for each agent
- [ ] Test agent invocations from GitHub Copilot UI
- [ ] Document agent usage patterns

### Future Enhancements
- Add agent usage analytics
- Create agent performance dashboard
- Implement agent coordination protocols
- Build agent testing framework

---

## References

- [Agent Ecosystem Map](.github/agents/AGENT_ECOSYSTEM_MAP.md)
- [Custom Copilot Agents Specification](.github/agents/CUSTOM_COPILOT_AGENTS_SPECIFICATION.md)
- [CI Testing Agent Implementation](.github/agents/ci-testing-agent/README.md)
- [Cognitive Brain Architecture](.github/agents/COGNITIVE_BRAIN_ARCHITECTURE_DIAGRAMS.md)

---

**Document Status**: ✅ Complete  
**Last Verified**: 2026-01-10  
**Owner**: Agent Development Team  
**Maintainers**: @mbaetiong, @copilot
