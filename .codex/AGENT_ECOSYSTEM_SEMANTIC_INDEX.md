# AGENT ECOSYSTEM INDEX
## Phase 1 Semantic Analysis | Aries-Serpent/_codex_

> **Generated**: 2026-01-23 | **Agent Count**: 147 active + 14 archived

---

## AGENT CLASSIFICATION HIERARCHY

### By Autonomy Model

**D_CAPABLE Agents** (Grounded Decision Making)
- ci-testing-agent
- ci-failure-resolution-agent
- Self-healing orchestrator
- ~8 specialized operational agents

**E Model Agents** (Advisory)
- Specialist domain agents (CI, docs, security, testing)
- ~139 agents with enforcement_tier=PARTIAL

### By Domain Specialization

#### 1. CI/CD Automation (18 agents)
- **ci-testing-agent** - Test collection, import errors, P19 detection
- **ci-auto-healer-agent** - Auto-fix CI failures
- **ci-failure-resolution-agent** - Diagnose failure patterns
- **ci-emergency-response-agent** - Blocking failure handling
- **ci-optimization-agent** - Pipeline performance
- **ci-pattern-guardian** - Pattern knowledge tracking
- **workflow-health-monitor** - Workflow reliability
- **workflow-compliance-guardian** - Concurrency + timeout rules
- **workflow-ci-fixer** - Syntax and config fixes
- 9+ additional CI specialist agents

#### 2. Documentation (15 agents)
- **unified-doc-agent** - Unified documentation management
- **documentation-quality-agent** - Quality assessment
- **documentation-consolidator** - Reduce duplication
- **doc-freshness-checker** - Link validation, accuracy
- **link-validator-agent** - Broken reference detection
- **post-merge-doc-alignment-agent** - After-merge alignment
- 9+ additional documentation agents

#### 3. Testing & Quality (20 agents)
- **autonomous-test-healer-agent** - Flaky test detection & fixing
- **test-alignment-fixer-enhanced** - API change alignment
- **mutation-testing-agent** - Test effectiveness
- **test-enhancement-agent** - Edge case coverage
- **test-failure-analyzer-agent** - Root cause analysis
- **test-pattern-guardian** - Anti-pattern detection
- **fragile-test-guardian** - Flakiness stabilization
- 13+ additional testing agents

#### 4. Security & Compliance (16 agents)
- **unified-security-scanner** - Comprehensive SAST + dependency
- **codeql-alert-resolution-agent** - CodeQL fix automation
- **secret-detection-agent** - Credential detection
- **security-alert-verification-agent** - Alert verification
- **code-scanning-remediation-agent** - SAST alert fixes
- **dependency-security-review-agent** - Vulnerability review
- **security-audit-agent** - Full audit coverage
- **unified-governance-gate** - Policy enforcement
- 8+ additional security agents

#### 5. Code Analysis & Refactoring (14 agents)
- **code-analysis-agent** - Static analysis
- **code-review** - Code quality review
- **test-alignment-fixer** - API alignment
- **python-312-type-fixer** - Type compatibility
- **reference-updater-agent** - Symbol name updates
- **datetime-modernizer** - Datetime modernization
- 8+ additional analysis agents

#### 6. Dependency & Infrastructure (18 agents)
- **dependency-conflict-agent** - Pip resolver conflicts
- **dependency-vulnerability-scanner** - CVE tracking
- **packaging-validation-agent** - PEP 621 compliance
- **INFRA_LINTER_AGENT_PROMPT** - IaC validation
- **cache-management-agent** - Cache strategy optimization
- **branch-divergence-resolution-agent** - Branch sync
- 12+ additional infrastructure agents

#### 7. Performance & Optimization (12 agents)
- **performance-monitor-agent** - Real-time metrics
- **performance-regression-detector** - Regression alerts
- **cache-manager-integration** - Cache coordination
- **workflow-optimization-agent** - Workflow efficiency
- 8+ additional performance agents

#### 8. Orchestration & Coordination (8 agents)
- **orchestrator-agent** - Multi-agent orchestration
- **self-healing-orchestrator-agent** - Autonomous healing
- **agent-orchestrator** - Task distribution
- **cognitive-brain-session-injector** - Context injection
- **cognitive-brain-cli-agent** - CLI operations
- **cognitive-ooda-loop-agent** - OODA execution
- 2+ additional orchestration agents

#### 9. Monitoring & Observability (10 agents)
- **workflow-health-monitor** - Workflow tracking
- **workflow-analytics-agent** - Performance trends
- **artifact-monitor-agent** - CI/CD artifact health
- **telemetry-classifier-agent** - Failure pattern classification
- **ci-log-retrieval-agent** - Log analysis
- **ci-health-alert-agent** - Auto-response to alerts
- 4+ additional monitoring agents

#### 10. Specialized Domain Agents (36 agents)
- **ml-validation-suite-agent** - ML pipeline validation
- **meta-tensor-validator** - PyTorch tensor validation
- **json-serialization-expert** - JSON handling
- **datetime-modernizer** - Python datetime updates
- **python-architect-agent** - PySide6/PyQt6 GUI design
- **energy-conversion-agent** - G2E energy systems
- **google-home-script-agent** - Smart home automation
- **quantum-compliance-tuning-agent** - Quantum compliance
- 28+ additional specialized agents

### By Physics Model

**Bayesian Networks** (Probabilistic)
- github-app-manager
- Risk assessment agents
- 12+ related agents

**Balance Model** (Resource Optimization)
- github-guru-agent
- cache-management-agent
- performance agents
- 25+ related agents

**Path Model** (Flow Optimization)
- workflow agents
- ci-pattern-guardian
- routing agents
- 15+ related agents

**Redundancy Model** (Failure Recovery)
- self-healing-orchestrator-agent
- ci-emergency-response-agent
- recovery agents
- 12+ related agents

---

## AGENT CAPABILITY MATRIX

### By Capability Tag

| Capability | Agents | Use Case |
|------------|--------|----------|
| test_collection | 5+ | Test discovery & execution |
| import_error_resolution | 4+ | Python import fixing |
| p19_shadow_import_detection | 3+ | P19 import patterns |
| code_quality_scanning | 8+ | Linting & analysis |
| security_vulnerability_detection | 12+ | CVE tracking |
| documentation_management | 15+ | Docs generation & maintenance |
| ci_workflow_optimization | 8+ | Pipeline efficiency |
| pattern_recognition | 20+ | Historical pattern matching |
| machine_learning_validation | 6+ | ML model validation |
| autonomous_healing | 10+ | Self-remediation |

---

## INTEGRATION PATTERNS

### Agent-to-Agent Communication
- Via MCP Core + Bridge Protocol v2
- Asynchronous message passing
- Type-safe serialization
- Pattern sharing via Rhizome Connector

### Agent-to-System Integration
- GitHub API integration
- Git operations (commit, push, branch)
- Workflow triggering
- Artifact management

### Agent-to-Cognitive-Brain Integration
- Decision request API
- Pattern learning feedback
- Autonomous level assignment
- Adaptive scoring updates

---

## AGENT MATURITY LEVELS

**Production Maturity**: 140+ agents
- Fully tested and validated
- Active enforcement in CI/CD
- Real-world usage patterns

**Beta Maturity**: 5+ agents
- Limited deployment
- Active monitoring
- User feedback incorporation

**Alpha/Experimental**: 2+ agents
- Research and development
- Limited real-world use

---

## AGENT SELECTION HEURISTICS

### Task-to-Agent Mapping

| Task | Recommended Agent | Fallback | 
|------|-------------------|----------|
| Fix failing test | autonomous-test-healer-agent | test-failure-analyzer-agent |
| Analyze CI failure | ci-testing-agent | ci-failure-resolution-agent |
| Document code | unified-doc-agent | documentation-quality-agent |
| Security scan | unified-security-scanner | security-audit-agent |
| Refactor code | code-analysis-agent | test-alignment-fixer |
| Optimize performance | performance-monitor-agent | workflow-optimization-agent |

---

## FUTURE SCALING ROADMAP

**Phase 2 (Q2 2026)**: 170+ agents
- Enhanced specialization
- Cross-domain coordination
- Distributed orchestration

**Phase 3 (Q3 2026)**: 200+ agents
- Emergent agent behaviors
- Collective intelligence
- Full autonomy (D→C transitions)

---

**Last Updated**: 2026-01-23 | **Status**: Complete | **Version**: 1.0
