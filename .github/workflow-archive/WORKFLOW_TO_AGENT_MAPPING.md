# Workflow-to-Agent Mapping

**Purpose**: Map GitHub Actions workflows to relevant custom Copilot agents for automation opportunities  
**Date**: 2026-02-06  
**Total Workflows Analyzed**: 108  
**Workflows with Agent Mapping**: 79  
**Unique Agents Referenced**: 15

---

## 📊 Executive Summary

This document maps GitHub Actions workflows to custom Copilot agents that can:
- **Monitor** workflow execution
- **Analyze** workflow failures
- **Auto-fix** common issues
- **Optimize** workflow performance
- **Validate** workflow changes

### Agent Categories

| Category | Agent Count | Primary Function |
|----------|-------------|------------------|
| **CI/CD & Testing** | 6 | Test monitoring, failure fixing, CI debugging |
| **Security** | 3 | Alert verification, CodeQL resolution, vulnerability patching |
| **Documentation** | 3 | Quality assessment, link validation, freshness checking |
| **Repository Health** | 2 | Hygiene maintenance, artifact monitoring |
| **Specialized** | 1 | Cognitive brain management, owner approval |

---

## 🤖 Custom Agent Reference

### CI/CD & Testing Agents

1. **ci-testing-agent** 
   - Location: `.github/agents/ci-testing-agent.md`
   - Purpose: Debug CI/CD pipelines, test failures, import errors
   - Activation: `@copilot Use the CI Testing Agent to debug...`

2. **workflow-ci-fixer**
   - Location: `.github/agents/workflow-ci-fixer.agent.md`
   - Purpose: Fix GitHub Actions workflow syntax errors and failures
   - Activation: `@copilot Use workflow-ci-fixer to fix...`

3. **ci-emergency-response-agent**
   - Location: `.github/agents/ci-emergency-response-agent.md`
   - Purpose: Emergency CI/CD pipeline fixes
   - Activation: `@copilot Use ci-emergency-response-agent for...`

4. **test-coverage-monitor**
   - Location: `.github/agents/test-coverage-monitor.agent.md`
   - Purpose: Monitor test coverage and enforce thresholds
   - Activation: `@copilot Use test-coverage-monitor to check...`

5. **test-alignment-fixer**
   - Location: `.github/agents/test-alignment-fixer.agent.md`
   - Purpose: Fix test alignment issues after API changes
   - Activation: `@copilot Use test-alignment-fixer to align...`

6. **autonomous-test-healer-agent**
   - Location: `.github/agents/autonomous-test-healer-agent.md`
   - Purpose: Auto-fix test failures
   - Activation: `@copilot Use autonomous-test-healer to heal...`

### Security Agents

7. **security-alert-verification-agent**
   - Location: `.github/agents/security-alert-verification-agent.md`
   - Purpose: Verify GitHub security alerts and propose remediation
   - Activation: `@copilot Use security-alert-verification-agent to verify...`

8. **codeql-alert-resolution-agent**
   - Location: `.github/agents/codeql-alert-resolution-agent.md`
   - Purpose: Resolve CodeQL alerts
   - Activation: `@copilot Use codeql-alert-resolution-agent to resolve...`

9. **code-scanning-remediation-agent**
   - Location: `.github/agents/code-scanning-remediation-agent.md`
   - Purpose: Fix code scanning issues
   - Activation: `@copilot Use code-scanning-remediation-agent to fix...`

### Documentation Agents

10. **documentation-quality-agent**
    - Location: `.github/agents/documentation-quality-agent.md`
    - Purpose: Automated documentation quality assessment
    - Activation: `@copilot Use documentation-quality-agent to assess...`

11. **link-validator-agent**
    - Location: `.github/agents/link-validator-agent.md`
    - Purpose: Cross-reference and link validation
    - Activation: `@copilot Use link-validator-agent to validate...`

12. **doc-freshness-checker**
    - Location: `.github/agents/doc-freshness-checker.agent.md`
    - Purpose: Check documentation freshness and validate links
    - Activation: `@copilot Use doc-freshness-checker to check...`

### Repository Health Agents

13. **repository-hygiene-agent**
    - Location: `.github/agents/repository-hygiene-agent.md`
    - Purpose: Autonomous repository cleanup and maintenance
    - Activation: `@copilot Use repository-hygiene-agent to clean...`

14. **artifact-monitor-agent**
    - Location: `.github/agents/artifact-monitor-agent.md`
    - Purpose: Autonomous CI/CD health monitoring with pattern recognition
    - Activation: `@copilot Use artifact-monitor-agent to monitor...`

### Specialized Agents

15. **cognitive-brain-manager**
    - Location: `.github/agents/cognitive-brain-manager.md`
    - Purpose: Manage cognitive brain system
    - Activation: `@copilot Use cognitive-brain-manager to manage...`

16. **owner-approval-guard**
    - Location: `.github/agents/owner-approval-guard.agent.md`
    - Purpose: Enforce owner approval for autonomous operations
    - Activation: `@copilot Use owner-approval-guard to verify...`

---

## 📋 Workflow-to-Agent Mapping

### CI/CD Workflows (16 workflows)

#### auto-fix-common-issues.yml
- **Display**: Auto-fix Common Issues
- **Category**: CI/CD
- **Relevant Agents**: 
  - ci-testing-agent
  - workflow-ci-fixer
  - ci-emergency-response-agent
- **Use Case**: Automated issue fixing, workflow optimization

#### batch-ci-triage.yml
- **Display**: Art_Batch CI Failure Triage
- **Category**: Agent
- **Artifacts**: 2
- **Relevant Agents**:
  - artifact-monitor-agent
  - ci-testing-agent
  - workflow-ci-fixer
- **Use Case**: CI failure analysis, automated triage, artifact monitoring

#### ci-diagnostic-automation.yml
- **Display**: CI Diagnostic Automation
- **Category**: CI/CD
- **Relevant Agents**:
  - ci-testing-agent
  - workflow-ci-fixer
  - ci-emergency-response-agent
- **Use Case**: Automated diagnostics, workflow debugging

#### ci-health-monitor.yml
- **Display**: CI Health Monitor
- **Category**: CI/CD
- **Relevant Agents**:
  - ci-testing-agent
  - workflow-ci-fixer
  - artifact-monitor-agent
- **Use Case**: Health monitoring, trend analysis

#### ci-health-suite.yml
- **Display**: Art_CI Health Suite
- **Category**: CI/CD
- **Artifacts**: 1
- **Relevant Agents**:
  - ci-testing-agent
  - workflow-ci-fixer
  - artifact-monitor-agent
- **Use Case**: Comprehensive health checks, artifact-based reporting

#### optimized-ci.yml
- **Display**: Optimized CI Pipeline
- **Category**: CI/CD
- **Relevant Agents**:
  - ci-testing-agent
  - test-coverage-monitor
  - test-alignment-fixer
  - autonomous-test-healer-agent
- **Use Case**: Test execution, coverage monitoring, test healing

#### post-merge-validation-optimized.yml
- **Display**: Art_Post-Merge Validation (Optimized)
- **Category**: CI/CD
- **Artifacts**: 1
- **Relevant Agents**:
  - ci-testing-agent
  - test-coverage-monitor
  - test-alignment-fixer
  - artifact-monitor-agent
- **Use Case**: Post-merge validation, test verification, artifact analysis

#### rust_swarm_ci.yml
- **Display**: Art_Rust-Python Hybrid Swarm CI/CD
- **Category**: CI/CD
- **Artifacts**: 6 (CRITICAL - most artifacts)
- **Relevant Agents**:
  - ci-testing-agent
  - test-coverage-monitor
  - test-alignment-fixer
  - artifact-monitor-agent
- **Use Case**: Multi-language CI, comprehensive artifact monitoring

#### self-healing-ci.yml
- **Display**: Self-Healing CI
- **Category**: CI/CD
- **Relevant Agents**:
  - ci-testing-agent
  - workflow-ci-fixer
  - ci-emergency-response-agent
  - autonomous-test-healer-agent
- **Use Case**: Automatic failure recovery, self-healing pipelines

---

### Security Workflows (15 workflows)

#### codeql-analysis.yml
- **Display**: CodeQL Security Analysis
- **Category**: Security
- **Relevant Agents**:
  - security-alert-verification-agent
  - codeql-alert-resolution-agent
  - code-scanning-remediation-agent
- **Use Case**: Security scanning, alert verification, automated remediation

#### codeql-chunked.yml
- **Display**: Art_CodeQL Chunked Analysis
- **Category**: Security
- **Artifacts**: 3
- **Relevant Agents**:
  - security-alert-verification-agent
  - codeql-alert-resolution-agent
  - artifact-monitor-agent
- **Use Case**: Large-scale security scanning, artifact-based analysis

#### dependency-scan.yml
- **Display**: Art_Dependency Security Scan
- **Category**: Security
- **Artifacts**: 1
- **Relevant Agents**:
  - security-alert-verification-agent
  - artifact-monitor-agent
- **Use Case**: Dependency vulnerability scanning, alert management

#### security-scan.yml
- **Display**: Art_Security Scan
- **Category**: Security
- **Artifacts**: 1
- **Relevant Agents**:
  - security-alert-verification-agent
  - code-scanning-remediation-agent
  - artifact-monitor-agent
- **Use Case**: General security scanning, remediation automation

#### security-scanning-suite.yml
- **Display**: Art_Security Scanning Suite
- **Category**: Security
- **Artifacts**: 3
- **Relevant Agents**:
  - security-alert-verification-agent
  - codeql-alert-resolution-agent
  - code-scanning-remediation-agent
  - artifact-monitor-agent
- **Use Case**: Comprehensive security suite, multi-artifact analysis

#### security-suite.yml
- **Display**: Art_Unified Security Suite
- **Category**: Security
- **Artifacts**: 1
- **Relevant Agents**:
  - security-alert-verification-agent
  - codeql-alert-resolution-agent
  - artifact-monitor-agent
- **Use Case**: Unified security operations, centralized artifact management

#### semgrep_sarif.yml
- **Display**: Art_Semgrep SAST (SARIF Upload)
- **Category**: Security
- **Artifacts**: 1
- **Relevant Agents**:
  - security-alert-verification-agent
  - code-scanning-remediation-agent
  - artifact-monitor-agent
- **Use Case**: SAST scanning, SARIF analysis, automated fixes

---

### Testing Workflows (8 workflows)

#### coverage_report.yml
- **Display**: Art_Coverage Report Generator
- **Category**: Other
- **Artifacts**: 1
- **Relevant Agents**:
  - test-coverage-monitor
  - test-alignment-fixer
  - artifact-monitor-agent
- **Use Case**: Coverage tracking, threshold enforcement, trend analysis

#### test-comprehensive.yml
- **Display**: Art_Comprehensive Tests with Caching
- **Category**: Testing
- **Artifacts**: 4
- **Relevant Agents**:
  - test-coverage-monitor
  - test-alignment-fixer
  - autonomous-test-healer-agent
  - artifact-monitor-agent
- **Use Case**: Comprehensive testing, coverage monitoring, test healing

#### test-rag.yml
- **Display**: Art_RAG Module Tests
- **Category**: Testing
- **Artifacts**: 2
- **Relevant Agents**:
  - test-coverage-monitor
  - test-alignment-fixer
  - autonomous-test-healer-agent
  - artifact-monitor-agent
- **Use Case**: Specialized RAG testing, module-specific coverage

#### test-suite.yml
- **Display**: Art_Testing Suite
- **Category**: Testing
- **Artifacts**: 5 (CRITICAL - comprehensive test artifacts)
- **Relevant Agents**:
  - test-coverage-monitor
  - test-alignment-fixer
  - autonomous-test-healer-agent
  - artifact-monitor-agent
- **Use Case**: Full test suite execution, comprehensive artifact analysis

---

### Documentation Workflows (7 workflows)

#### documentation-link-checker.yml
- **Display**: Art_Documentation Link Checker
- **Category**: Documentation
- **Artifacts**: 1
- **Relevant Agents**:
  - documentation-quality-agent
  - link-validator-agent
  - doc-freshness-checker
  - artifact-monitor-agent
- **Use Case**: Link validation, broken link detection, documentation health

#### documentation-suite.yml
- **Display**: Art_Documentation Suite
- **Category**: Documentation
- **Artifacts**: 1
- **Relevant Agents**:
  - documentation-quality-agent
  - link-validator-agent
  - doc-freshness-checker
  - artifact-monitor-agent
- **Use Case**: Comprehensive documentation validation, quality assessment

#### pages-mkdocs.yml
- **Display**: MkDocs Pages Deployment
- **Category**: CI/CD
- **Relevant Agents**:
  - documentation-quality-agent
  - link-validator-agent
  - ci-testing-agent
- **Use Case**: Documentation deployment, build validation, link checking

---

### Cognitive Workflows (4 workflows)

#### cognitive-action.yml
- **Display**: Art_Cognitive Action System
- **Category**: Cognitive
- **Artifacts**: 1
- **Relevant Agents**:
  - cognitive-brain-manager
  - artifact-monitor-agent
- **Use Case**: Cognitive system management, action execution monitoring

#### cognitive-aftermath.yml
- **Display**: Art_Cognitive Aftermath Analysis
- **Category**: Cognitive
- **Artifacts**: 1
- **Relevant Agents**:
  - cognitive-brain-manager
  - artifact-monitor-agent
- **Use Case**: Post-execution analysis, cognitive pattern learning

#### cognitive-brain-feed.yml
- **Display**: Art_Cognitive Brain Feed
- **Category**: Cognitive
- **Artifacts**: 1
- **Relevant Agents**:
  - cognitive-brain-manager
  - artifact-monitor-agent
- **Use Case**: Cognitive system data ingestion, brain state monitoring

#### cognitive-decision.yml
- **Display**: Art_Cognitive Decision Engine
- **Category**: Cognitive
- **Artifacts**: 1
- **Relevant Agents**:
  - cognitive-brain-manager
  - artifact-monitor-agent
- **Use Case**: Decision-making processes, cognitive pattern application

---

### Agent Workflows (7 workflows)

#### agent-chain-orchestrator.yml
- **Display**: Art_Agent Chain Orchestrator (Quantum-Inspired)
- **Category**: Agent
- **Artifacts**: 1
- **Relevant Agents**:
  - artifact-monitor-agent
  - owner-approval-guard
- **Use Case**: Agent orchestration, chain planning, approval verification

#### autonomous-agent.yml
- **Display**: Autonomous Agent Runtime
- **Category**: Agent
- **Relevant Agents**:
  - artifact-monitor-agent
  - owner-approval-guard
- **Use Case**: Agent execution, autonomous operations, approval enforcement

#### copilot-self-evolution.yml
- **Display**: Art_Copilot Self-Evolution
- **Category**: Agent
- **Artifacts**: 1
- **Relevant Agents**:
  - test-coverage-monitor
  - test-alignment-fixer
  - artifact-monitor-agent
- **Use Case**: Agent evolution tracking, test integration, pattern learning

---

### Cache Workflows (5 workflows)

#### cache-cleanup.yml
- **Display**: Cache Cleanup
- **Category**: Cache
- **Relevant Agents**:
  - repository-hygiene-agent
  - ci-testing-agent
- **Use Case**: Cache maintenance, repository cleanup, CI optimization

#### cache-management.yml
- **Display**: Cache Management
- **Category**: Cache
- **Relevant Agents**:
  - repository-hygiene-agent
  - ci-testing-agent
- **Use Case**: Comprehensive cache management, workflow optimization

---

### Authentication Workflows (5 workflows)

#### auth-compliance-report.yml
- **Display**: Art_Auth Compliance Report Generator
- **Category**: Authentication
- **Artifacts**: 1
- **Relevant Agents**:
  - owner-approval-guard
  - artifact-monitor-agent
- **Use Case**: Compliance monitoring, approval verification, report analysis

---

## 🎯 Automation Opportunities

### High-Priority Automation (Top 10 Workflows)

1. **rust_swarm_ci.yml** (6 artifacts)
   - **Agents**: ci-testing-agent, test-coverage-monitor, artifact-monitor-agent
   - **Opportunity**: Automated failure analysis, artifact correlation, test healing
   - **Impact**: High (critical CI pipeline)

2. **test-suite.yml** (5 artifacts)
   - **Agents**: test-coverage-monitor, autonomous-test-healer-agent, artifact-monitor-agent
   - **Opportunity**: Automated test fixing, coverage enforcement, artifact analysis
   - **Impact**: High (primary test workflow)

3. **security-scanning-suite.yml** (3 artifacts)
   - **Agents**: security-alert-verification-agent, codeql-alert-resolution-agent, artifact-monitor-agent
   - **Opportunity**: Automated security remediation, alert triage, artifact tracking
   - **Impact**: Critical (security)

4. **codeql-chunked.yml** (3 artifacts)
   - **Agents**: codeql-alert-resolution-agent, artifact-monitor-agent
   - **Opportunity**: Chunked analysis coordination, artifact aggregation, automated fixes
   - **Impact**: Critical (security)

5. **test-comprehensive.yml** (4 artifacts)
   - **Agents**: test-coverage-monitor, autonomous-test-healer-agent, artifact-monitor-agent
   - **Opportunity**: Comprehensive test automation, multi-artifact analysis
   - **Impact**: High (testing)

6. **self-healing-ci.yml**
   - **Agents**: ci-emergency-response-agent, autonomous-test-healer-agent
   - **Opportunity**: Enhanced self-healing with agent intelligence
   - **Impact**: High (CI reliability)

7. **batch-ci-triage.yml** (2 artifacts)
   - **Agents**: ci-testing-agent, artifact-monitor-agent
   - **Opportunity**: Intelligent triage, pattern recognition, automated remediation
   - **Impact**: High (CI operations)

8. **documentation-suite.yml** (1 artifact)
   - **Agents**: documentation-quality-agent, link-validator-agent, doc-freshness-checker
   - **Opportunity**: Automated documentation quality, link fixing, freshness enforcement
   - **Impact**: Medium (documentation)

9. **cognitive-brain-feed.yml** (1 artifact)
   - **Agents**: cognitive-brain-manager, artifact-monitor-agent
   - **Opportunity**: Cognitive system optimization, pattern learning enhancement
   - **Impact**: Medium (cognitive system)

10. **workflow-analytics-scheduled.yml** (1 artifact)
    - **Agents**: artifact-monitor-agent, ci-testing-agent
    - **Opportunity**: Enhanced analytics, intelligent pattern detection
    - **Impact**: Medium (monitoring)

---

## 📊 Usage Patterns

### Pattern 1: Failure Response Chain
**Workflow**: Any CI/CD workflow fails  
**Agent Chain**:
1. `artifact-monitor-agent` detects failure via artifact analysis
2. `ci-testing-agent` diagnoses failure cause
3. `workflow-ci-fixer` OR `autonomous-test-healer-agent` applies fix
4. `ci-emergency-response-agent` escalates if unfixable

**Example Activation**:
```
@copilot The rust_swarm_ci workflow failed. Use the CI Testing Agent to diagnose, 
then use workflow-ci-fixer to fix any workflow syntax issues, and use 
autonomous-test-healer-agent to fix test failures.
```

### Pattern 2: Security Alert Response
**Workflow**: Security scan produces alerts  
**Agent Chain**:
1. `security-alert-verification-agent` verifies alert validity
2. `codeql-alert-resolution-agent` OR `code-scanning-remediation-agent` remediates
3. `artifact-monitor-agent` tracks remediation progress

**Example Activation**:
```
@copilot Security alerts detected in codeql-analysis. Use security-alert-verification-agent 
to verify these are real issues, then use codeql-alert-resolution-agent to fix them.
```

### Pattern 3: Documentation Health
**Workflow**: Documentation build or link check  
**Agent Chain**:
1. `doc-freshness-checker` validates documentation age
2. `link-validator-agent` checks all links
3. `documentation-quality-agent` assesses overall quality
4. `artifact-monitor-agent` tracks quality trends

**Example Activation**:
```
@copilot Check documentation health using doc-freshness-checker, then use 
link-validator-agent to fix broken links, and documentation-quality-agent 
to assess overall quality.
```

### Pattern 4: Test Coverage Enforcement
**Workflow**: Test execution with coverage  
**Agent Chain**:
1. `test-coverage-monitor` checks coverage thresholds
2. `test-alignment-fixer` aligns tests with API changes
3. `autonomous-test-healer-agent` fixes failing tests
4. `artifact-monitor-agent` tracks coverage trends

**Example Activation**:
```
@copilot Coverage dropped below threshold in test-suite. Use test-coverage-monitor 
to identify gaps, test-alignment-fixer to update outdated tests, and 
autonomous-test-healer-agent to fix failures.
```

---

## 🔄 Integration Recommendations

### Workflow → Agent Integration Points

1. **Failure Notifications**
   - Add webhook to invoke `artifact-monitor-agent` on workflow failure
   - Trigger `ci-testing-agent` automatically for CI/CD failures
   - Escalate to `ci-emergency-response-agent` after 3 consecutive failures

2. **Security Scan Integration**
   - Auto-invoke `security-alert-verification-agent` when SARIF uploaded
   - Chain to `codeql-alert-resolution-agent` for verified alerts
   - Track via `artifact-monitor-agent` for trending

3. **Documentation Deployment**
   - Pre-deployment: `link-validator-agent` + `doc-freshness-checker`
   - Post-deployment: `documentation-quality-agent` assessment
   - Continuous: `artifact-monitor-agent` for quality trends

4. **Test Execution**
   - Pre-test: `test-alignment-fixer` for API changes
   - During test: `autonomous-test-healer-agent` for failures
   - Post-test: `test-coverage-monitor` for threshold enforcement
   - Continuous: `artifact-monitor-agent` for coverage trends

---

## 📚 Related Documentation

- **Agent Registry**: `.github/agents/AGENT_REGISTRY.md`
- **Agent Selection Guide**: `.github/agents/AGENT_SELECTION_GUIDE.md`
- **Workflow Analysis**: `.github/workflow-archive/WORKFLOW_ANALYSIS_COMPLETE.md`
- **Consolidation Planset**: `.github/workflow-archive/WORKFLOW_CONSOLIDATION_PLANSET_V2.md`
- **Artifact Catalog**: `.github/workflow-archive/ARTIFACT_CATALOG.md`

---

## 🎯 Next Steps

1. **Review Mapping** - Validate agent recommendations for each workflow
2. **Test Integration** - Pilot agent automation on 3-5 high-priority workflows
3. **Measure Impact** - Track MTTR (Mean Time To Resolution) improvements
4. **Expand Coverage** - Extend agent automation to remaining workflows
5. **Document Patterns** - Capture successful patterns for reuse

---

**Document Status**: ✅ Complete  
**Review Required**: Yes (Agent developers + Workflow maintainers)  
**Next Update**: After Phase 1 consolidation complete  

---

*Generated by GitHub Copilot Agent*  
*Date: 2026-02-06*  
*Version: 1.0*
