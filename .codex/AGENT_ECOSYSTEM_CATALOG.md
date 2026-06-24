# 🏛️ COMPREHENSIVE AGENT ECOSYSTEM CATALOG

**Version:** 2.0.0  
**Generated:** 2026-06-20T06:50:10.980917  
**Total Agents:** 159 (145 Active + 14 Archived)  
**Repository:** aries-serpent/_codex_

---

## Executive Summary

This catalog provides complete documentation of the 159-agent ecosystem for the _codex_ platform. It serves as the authoritative reference for:

- **Agent Inventory**: Complete listing of all active and archived agents
- **Domain Organization**: 8 domain clusters for easy navigation
- **Capability Matrix**: Which agents handle which task categories
- **Quick Reference**: Activation commands and use cases for each agent

### Document Navigation
- [Section 1: Domain Cluster Overview](#section-1-domain-cluster-overview)
- [Section 2: Complete Agent Listings](#section-2-complete-agent-listings)
- [Section 3: Capability Matrix](#section-3-capability-matrix)
- [Section 4: Archived Agent Reference](#section-4-archived-agent-reference)
- [Section 5: Search Index](#section-5-search-index)

---

## SECTION 1: DOMAIN CLUSTER OVERVIEW

### Domain Statistics

| Domain | Active | Archived | Total | Key Responsibility |
|--------|--------|----------|-------|-------------------|
| CI/CD & Automation | 26 | 2 | 28 | Pipeline automation, failure detection, self-healing |
| Testing & Quality | 28 | 1 | 29 | Test coverage, mutation testing, quality gates |
| Repository Operations | 46 | 2 | 48 | PR analysis, issue triage, branch management |
| Security & Compliance | 17 | 1 | 18 | SAST, dependency scanning, secret detection |
| Documentation & Knowledge | 12 | 0 | 12 | Doc consolidation, link validation, freshness |
| Domain-Specific | 19 | 1 | 20 | ML validation, infrastructure, configuration |
| Orchestration & Multi-Agent | 1 | 0 | 1 | Multi-agent workflow coordination |
| Infrastructure & Platform | 3 | 0 | 3 | Performance, caching, monitoring |
| **TOTAL** | **145** | **14** | **159** | - |

### Domain Descriptions

#### 1️⃣ CI/CD & Automation (28 agents)
Responsible for automating, healing, and optimizing GitHub Actions workflows and CI/CD pipelines.

**Key Responsibilities:**
- Detect and fix CI/CD failures automatically
- Optimize workflow performance
- Validate workflow compliance
- Handle parameter mismatches
- Provide emergency response to blocking failures

**Unified Entry Point:** `ci-failure-resolution-agent`, `ci-emergency-response-agent`

**Key Agents:**
- ci-auto-healer-agent
- ci-docker-build-healer
- ci-emergency-response-agent
- ci-failure-resolution-agent
- ci-health-alert-agent
- ci-importerror-agent
- ci-log-retrieval-agent
- ci-optimization-agent
- ci-parameter-mismatch-healer
- ci-pattern-guardian
- ci-resilience-emergency-response-agent
- ci-testing-agent
- ci-triage-pipeline-agent
- workflow-ci-fixer
- workflow-compliance-guardian
- workflow-health-monitor
- workflow-health-monitor.deprecated
- workflow-management-agent
- workflow-optimization-agent
- self-healing-orchestrator-agent
- branch-divergence-resolution-agent
- autonomous-test-healer-agent
- ci-importerror-agent
- ci-log-retrieval-agent
- ci-parameter-mismatch-healer
- ci-pattern-guardian
- ci-resilience-emergency-response-agent

#### 2️⃣ Testing & Quality (29 agents)
Responsible for improving and maintaining test coverage, detecting flaky tests, and ensuring quality gates.

**Key Responsibilities:**
- Manage test coverage thresholds
- Fill coverage gaps strategically
- Detect and stabilize flaky tests
- Perform mutation testing
- Enhance test quality

**Unified Entry Point:** `unified-coverage-agent`

**Key Agents:**
- unified-coverage-agent
- autonomous-test-healer-agent
- fragile-test-guardian
- integration-test-runner
- mutation-testing-agent
- test-alignment-fixer
- test-alignment-fixer-enhanced
- test-enhancement-agent
- test-failure-analyzer-agent
- test-pattern-guardian
- tokenization-coverage-agent
- test-coverage-monitor (deprecated)
- coverage-gapfill-agent (deprecated)
- coverage-maintenance-agent (deprecated)
- coverage-roadmap-agent (deprecated)

#### 3️⃣ Repository Operations (48 agents)
Largest domain: handles PR analysis, issue triage, branch management, and overall repository health.

**Key Responsibilities:**
- Analyze pull requests
- Triage and manage issues
- Monitor repository health
- Enforce governance policies
- Manage branch strategies
- Track dependencies

**Key Agents:**
- github-guru-agent
- repository-hygiene-agent
- repository-organization-agent
- root-organizer-agent
- pr-check-remediation-agent
- pr-test-infrastructure-fixer
- policy-coach-agent
- dependency-conflict-agent
- dependency-security-review-agent
- dependency-vulnerability-scanner
- link-validator-agent
- doc-freshness-checker
- owner-approval-guard
- session-analysis-agent
- session-log-retrieval-agent
- reference-updater-agent
- code-analysis-agent
- code-scanning-remediation-agent
- claim-verification-agent

#### 4️⃣ Security & Compliance (18 agents)
Focused on security scanning, vulnerability detection, and compliance enforcement.

**Key Responsibilities:**
- SAST and static analysis
- Dependency vulnerability scanning
- Secret detection and remediation
- CodeQL alert resolution
- Security audit and scanning
- Compliance checking

**Unified Entry Point:** `unified-security-scanner`

**Key Agents:**
- codeql-alert-resolution-agent
- unified-security-scanner
- secret-detection-agent
- code-scanning-remediation-agent
- security-audit-agent
- security-alert-verification-agent
- bridge-security-monitor
- pii-scrubber

#### 5️⃣ Documentation & Knowledge (12 agents)
Manages documentation quality, consistency, and maintenance.

**Key Responsibilities:**
- Consolidate redundant docs
- Validate link freshness
- Improve documentation quality
- Maintain consistency
- Post-merge alignment

**Unified Entry Point:** `unified-doc-agent`

**Key Agents:**
- unified-doc-agent
- documentation-consolidator
- documentation-quality-agent
- doc-freshness-checker
- doc-refactor-test-agent
- link-validator-agent
- github-pages-manager
- post-merge-doc-alignment-agent
- terminology-consistency-agent

#### 6️⃣ Domain-Specific (20 agents)
Specialized agents for ML validation, infrastructure, configuration, and other focused domains.

**Key Responsibilities:**
- ML validation and pipeline health
- Infrastructure as Code linting
- Configuration migration and validation
- Energy conversion modeling
- Google Home automation scripts

**Key Agents:**
- ml-validation-suite-agent
- meta-tensor-validator
- rag-index-manager
- rag-freshness-loop-agent
- rag-meta-tensor-guardian
- rag-meta-tensor-regression-agent
- rag-module-management-agent
- INFRA_LINTER_AGENT_PROMPT
- config-validator
- config-migration-assistant
- rust-config-validator
- json-serialization-expert
- datetime-modernizer
- python-312-type-fixer
- mypy-manager-agent
- energy-conversion-agent
- google-home-script-agent
- python-architect-agent
- cognitive-brain-cli-agent
- cognitive-brain-session-injector

#### 7️⃣ Orchestration & Multi-Agent (1 agent)
High-level orchestration of multi-agent workflows.

**Key Agents:**
- orchestrator-agent
- agent-orchestrator
- cognitive-ooda-loop-agent
- self-healing-orchestrator-agent

#### 8️⃣ Infrastructure & Platform (3 agents)
Platform-level capabilities for performance, caching, and monitoring.

**Key Agents:**
- cache-management-agent
- cache-manager-integration
- performance-monitor-agent
- performance-regression-detector
- artifact-monitor-agent
- msv-dashboard-monitor
- rag-meta-tensor-validator

---

## SECTION 2: COMPLETE AGENT LISTINGS

### Active Agents (145)


#### Agent 1: GitHub App Manager
- **ID:** `github-app-manager`
- **Category:** operations
- **Status:** active
- **Description:** GitHub App Manager agent
- **Capabilities:** github_app_jwt, installation_tokens, webhook_verification, pat_token_fallback, codex_master_key

#### Agent 2: GitHub Guru Agent
- **ID:** `github-guru-agent`
- **Category:** operations
- **Status:** active
- **Description:** Full-spectrum GitHub repository intelligence: PR analysis, issue triage, workflow health monitoring,
- **Capabilities:** pr_analysis, issue_triage, workflow_health_monitoring, branch_governance, contributor_intelligence

#### Agent 3: Ast Analysis Agent
- **ID:** `ast-analysis-agent`
- **Category:** uncategorized
- **Status:** active
- **Description:** specialist
- **Capabilities:** ast_analysis_agent

#### Agent 4: Cache Logic Validator
- **ID:** `cache-logic-validator`
- **Category:** uncategorized
- **Status:** active
- **Description:** specialist
- **Capabilities:** cache_logic_validator

#### Agent 5: Ci Failure Diagnostician
- **ID:** `ci-failure-diagnostician`
- **Category:** uncategorized
- **Status:** active
- **Description:** specialist
- **Capabilities:** ci_failure_diagnostician

#### Agent 6: Ci Optimizer Agent
- **ID:** `ci-optimizer-agent`
- **Category:** uncategorized
- **Status:** active
- **Description:** specialist
- **Capabilities:** ci_optimizer_agent

#### Agent 7: Ci Testing Agent
- **ID:** `ci-testing-agent`
- **Category:** uncategorized
- **Status:** active
- **Description:** Specialized agent for debugging and fixing CI/CD pipeline issues, test failures, and build problems
- **Capabilities:** ci_failure_diagnosis, test_failure_analysis, build_problem_resolution, log_analysis

#### Agent 8: Codex_Reviewer
- **ID:** `codex_reviewer`
- **Category:** uncategorized
- **Status:** active
- **Description:** specialist
- **Capabilities:** codex_reviewer

#### Agent 9: Cognitive Brain Agent
- **ID:** `cognitive-brain-agent`
- **Category:** uncategorized
- **Status:** active
- **Description:** specialist
- **Capabilities:** cognitive_brain_agent

#### Agent 10: Compliance Checker Agent
- **ID:** `compliance-checker-agent`
- **Category:** uncategorized
- **Status:** active
- **Description:** utility
- **Capabilities:** compliance_checker_agent

#### Agent 11: Dep Upgrade Agent
- **ID:** `dep-upgrade-agent`
- **Category:** uncategorized
- **Status:** active
- **Description:** specialist
- **Capabilities:** dep_upgrade_agent

#### Agent 12: Documentation Agent
- **ID:** `documentation-agent`
- **Category:** uncategorized
- **Status:** active
- **Description:** specialist
- **Capabilities:** documentation_agent

#### Agent 13: Ecosystem Coordinator Agent
- **ID:** `ecosystem-coordinator-agent`
- **Category:** uncategorized
- **Status:** active
- **Description:** specialist
- **Capabilities:** ecosystem_coordinator_agent

#### Agent 14: Emergent Intelligence Agent
- **ID:** `emergent-intelligence-agent`
- **Category:** uncategorized
- **Status:** active
- **Description:** specialist
- **Capabilities:** emergent_intelligence_agent

#### Agent 15: Flaky Triage Agent
- **ID:** `flaky-triage-agent`
- **Category:** uncategorized
- **Status:** active
- **Description:** specialist
- **Capabilities:** flaky_triage_agent

#### Agent 16: Infra Linter Agent
- **ID:** `infra-linter-agent`
- **Category:** uncategorized
- **Status:** active
- **Description:** specialist
- **Capabilities:** infra_linter_agent

#### Agent 17: Performance Monitor Agent
- **ID:** `performance-monitor-agent`
- **Category:** uncategorized
- **Status:** active
- **Description:** utility
- **Capabilities:** performance_monitor_agent

#### Agent 18: Project Architect Researcher
- **ID:** `project-architect-researcher`
- **Category:** uncategorized
- **Status:** active
- **Description:** NotebookLM API integration for project research and architecture analysis
- **Capabilities:** api_integration, research_synthesis, architecture_design, documentation_analysis

#### Agent 19: Pyo3 Integration Tester
- **ID:** `pyo3-integration-tester`
- **Category:** uncategorized
- **Status:** active
- **Description:** Tests PyO3 Rust-Python integration and validates bindings
- **Capabilities:** pyo3_testing, rust_python_bindings, integration_validation

#### Agent 20: Reasoning Advisor Agent
- **ID:** `reasoning-advisor-agent`
- **Category:** uncategorized
- **Status:** active
- **Description:** specialist
- **Capabilities:** reasoning_advisor_agent

#### Agent 21: Release Gate Agent
- **ID:** `release-gate-agent`
- **Category:** uncategorized
- **Status:** active
- **Description:** utility
- **Capabilities:** release_gate_agent

#### Agent 22: Rust Error Validator
- **ID:** `rust-error-validator`
- **Category:** uncategorized
- **Status:** active
- **Description:** Scans Rust code for error handling issues and validates PyResult usage
- **Capabilities:** rust_error_detection, unwrap_validation, pyresult_checking

#### Agent 23: Security Advisory Resolver
- **ID:** `security-advisory-resolver`
- **Category:** uncategorized
- **Status:** active
- **Description:** specialist
- **Capabilities:** security_advisory_resolver

#### Agent 24: Security Scan Agent
- **ID:** `security-scan-agent`
- **Category:** uncategorized
- **Status:** active
- **Description:** specialist
- **Capabilities:** security_scan_agent

#### Agent 25: Test Assertion Updater
- **ID:** `test-assertion-updater`
- **Category:** uncategorized
- **Status:** active
- **Description:** Fixes test alignment issues by updating tests to match API changes and ensuring test assertions are
- **Capabilities:** test_alignment, assertion_updates, api_change_tracking

#### Agent 26: Utf8 Safety Linter
- **ID:** `utf8-safety-linter`
- **Category:** uncategorized
- **Status:** active
- **Description:** specialist
- **Capabilities:** utf8_safety_linter

#### Agent 27: Test Pattern Guardian
- **ID:** `test-pattern-guardian`
- **Category:** uncategorized
- **Status:** active
- **Description:** Proactive test quality enforcement through AST-based pattern detection for mock exhaustion, serializ
- **Capabilities:** ast_pattern_detection, mock_exhaustion_prevention, json_serialization_validation, fixture_independence_checking, test_quality_enforcement

#### Agent 28: Config Validator (Enhanced)
- **ID:** `config-validator-enhanced`
- **Category:** uncategorized
- **Status:** active
- **Description:** Hydra config integrity and coverage validation, ensures all experiment configs referenced in tests e
- **Capabilities:** config_existence_validation, cross_reference_checking, schema_compliance, hydra_integration

#### Agent 29: Unified Security Scanner
- **ID:** `unified-security-scanner`
- **Category:** uncategorized
- **Status:** active
- **Description:** Multi-scanner security audit — CVE detection, secret scanning, GHAS triage, SBOM generation, and uni
- **Capabilities:** cve_scanning, secret_detection, ghas_alert_triage, sbom_generation, auto_remediation

#### Agent 30: Cross-Agent Knowledge Graph
- **ID:** `cross-agent-knowledge-graph`
- **Category:** uncategorized
- **Status:** active
- **Description:** Persistent JSON-LD knowledge graph enabling cross-session pattern sharing, fix pattern deduplication
- **Capabilities:** node_registration, edge_creation, semantic_query, conflict_detection, staleness_pruning

#### Agent 31: CodeQL Alert Resolution Agent
- **ID:** `codeql-alert-resolution-agent`
- **Category:** uncategorized
- **Status:** active
- **Description:** Autonomous CodeQL alert triage and resolution — classifies CWE categories, applies fix patterns, dis
- **Capabilities:** codeql_alert_ingestion, cwe_classification, auto_fix_application, false_positive_dismissal, regression_prevention

#### Agent 32: RAG Meta-Tensor Regression Agent
- **ID:** `rag-meta-tensor-regression-agent`
- **Category:** uncategorized
- **Status:** active
- **Description:** Prevents and resolves meta-tensor initialization regressions in the RAG pipeline — guards safe_model
- **Capabilities:** meta_tensor_detection, device_placement_validation, regression_prevention, canonical_fix_application, cognitive_brain_pattern_storage

#### Agent 33: CI Triage Pipeline Agent
- **ID:** `ci-triage-pipeline-agent`
- **Category:** uncategorized
- **Status:** active
- **Description:** Systematic CI failure triage using GitHub MCP tools — downloads logs, classifies failures by pattern
- **Capabilities:** ci_log_retrieval, failure_classification, fix_pattern_application, drq_integration, cognitive_brain_learning

#### Agent 34: Recon Scout Agent
- **ID:** `recon-scout-agent`
- **Category:** uncategorized
- **Status:** active
- **Description:** Read-only codebase reconnaissance — walks all files to surface CI blockers, security risks, quality
- **Capabilities:** ci_blocker_detection, security_tripwire_scan, code_quality_audit, documentation_gap_detection, architecture_drift_analysis

#### Agent 35: Policy Coach Agent
- **ID:** `policy-coach-agent`
- **Category:** uncategorized
- **Status:** active
- **Description:** Monitors Copilot Agent sessions for codebase policy violations and re-aligns behaviour at 3 mandator
- **Capabilities:** policy_violation_detection, session_re_alignment, pre_close_gate_enforcement, violation_pattern_matching, prompt_injection

#### Agent 36: Python Architect Agent
- **ID:** `python-architect-agent`
- **Category:** uncategorized
- **Status:** active
- **Description:** Advanced Python architecture design and review — enforces patterns, refactoring strategies, and modu
- **Capabilities:** architecture_review, refactoring_guidance, pattern_enforcement, module_structure_validation

#### Agent 37: CI Auto-Healer Agent
- **ID:** `ci-auto-healer`
- **Category:** ci_cd
- **Status:** active
- **Description:** Detects CI failures, matches them to a known pattern library (P-001 to P-029), applies validated fix
- **Capabilities:** ci_failure_detection, pattern_matching, automated_code_fix, local_test_validation, drq_filing

#### Agent 38: Agent IQ Scoring Gate
- **ID:** `agent-iq-scoring-gate`
- **Category:** governance
- **Status:** active
- **Description:** Evaluates agent IQ and gates deployments based on scoring thresholds.
- **Capabilities:** governance

#### Agent 39: Agent Orchestrator
- **ID:** `agent-orchestrator`
- **Category:** orchestration
- **Status:** active
- **Description:** Coordinates multi-agent workflows, routing tasks to specialist agents.
- **Capabilities:** orchestration

#### Agent 40: Artifact Monitor Agent
- **ID:** `artifact-monitor-agent`
- **Category:** ci_cd
- **Status:** active
- **Description:** Monitors CI/CD artifact health, detects stale or missing artifacts.
- **Capabilities:** ci_cd

#### Agent 41: Autonomous Test Healer Agent
- **ID:** `autonomous-test-healer-agent`
- **Category:** testing
- **Status:** active
- **Description:** Auto-heals failing tests by identifying root causes and applying targeted fixes.
- **Capabilities:** testing

#### Agent 42: Bridge Security Monitor
- **ID:** `bridge-security-monitor`
- **Category:** security
- **Status:** active
- **Description:** Monitors IPC bridge security, detects unauthorized access, validates message integrity.
- **Capabilities:** security

#### Agent 43: Cache Management Agent
- **ID:** `cache-management-agent`
- **Category:** ci_cd
- **Status:** active
- **Description:** Manages CI/CD caching strategies; prunes stale caches, validates cache keys.
- **Capabilities:** ci_cd

#### Agent 44: CI Auto-Healer Agent
- **ID:** `ci-auto-healer-agent`
- **Category:** ci_cd
- **Status:** active
- **Description:** Detects and repairs CI failures using P-001-P-035 pattern library.
- **Capabilities:** ci_cd

#### Agent 45: CI Emergency Response Agent
- **ID:** `ci-emergency-response-agent`
- **Category:** ci_cd
- **Status:** active
- **Description:** Emergency response for critical CI pipeline failures requiring immediate action.
- **Capabilities:** ci_cd

#### Agent 46: CI ImportError Agent
- **ID:** `ci-importerror-agent`
- **Category:** ci_cd
- **Status:** active
- **Description:** Diagnoses and remediates ImportError/ModuleNotFoundError in test suites.
- **Capabilities:** ci_cd

#### Agent 47: CI Log Retrieval Agent
- **ID:** `ci-log-retrieval-agent`
- **Category:** ci_cd
- **Status:** active
- **Description:** Retrieves authenticated GitHub Actions logs and summarizes failures.
- **Capabilities:** ci_cd

#### Agent 48: CI Optimization Agent
- **ID:** `ci-optimization-agent`
- **Category:** ci_cd
- **Status:** active
- **Description:** Identifies and applies optimizations to reduce CI pipeline runtime.
- **Capabilities:** ci_cd

#### Agent 49: CI Parameter Mismatch Healer
- **ID:** `ci-parameter-mismatch-healer`
- **Category:** ci_cd
- **Status:** active
- **Description:** Detects and corrects parameter/argument mismatches in CI workflow calls.
- **Capabilities:** ci_cd

#### Agent 50: Claim Verification Agent
- **ID:** `claim-verification-agent`
- **Category:** documentation
- **Status:** active
- **Description:** Verifies factual claims in commit messages and documentation.
- **Capabilities:** documentation

#### Agent 51: Code Analysis Agent
- **ID:** `code-analysis-agent`
- **Category:** quality
- **Status:** active
- **Description:** Static code quality analysis with actionable improvement recommendations.
- **Capabilities:** quality

#### Agent 52: Code Scanning Remediation Agent
- **ID:** `code-scanning-remediation-agent`
- **Category:** security
- **Status:** active
- **Description:** Remediates code scanning alerts (CodeQL, Semgrep) with minimal-change fixes.
- **Capabilities:** security

#### Agent 53: Codebase Health Guardian
- **ID:** `codebase-health-guardian`
- **Category:** quality
- **Status:** active
- **Description:** Continuous monitoring of overall codebase health metrics and trends.
- **Capabilities:** quality

#### Agent 54: Cognitive Brain Manager
- **ID:** `cognitive-brain-manager`
- **Category:** cognitive
- **Status:** active
- **Description:** Manages cognitive brain system state, phase transitions, and health scoring.
- **Capabilities:** cognitive

#### Agent 55: Config Migration Assistant
- **ID:** `config-migration-assistant`
- **Category:** configuration
- **Status:** active
- **Description:** Migrates legacy configurations to Hydra-based format with validation.
- **Capabilities:** configuration

#### Agent 56: Config Validator
- **ID:** `config-validator`
- **Category:** configuration
- **Status:** active
- **Description:** Validates Hydra configuration files for schema compliance and type safety.
- **Capabilities:** configuration

#### Agent 57: CPU-Only CI Config Agent
- **ID:** `cpu-only-ci-config-agent`
- **Category:** ci_cd
- **Status:** active
- **Description:** Configures CI workflows for CPU-only environments (no GPU dependencies).
- **Capabilities:** ci_cd

#### Agent 58: Cross-Platform Filename Validator
- **ID:** `cross-platform-filename-validator`
- **Category:** quality
- **Status:** active
- **Description:** Validates filenames for cross-platform compatibility; blocks illegal characters.
- **Capabilities:** quality

#### Agent 59: Datetime Modernizer
- **ID:** `datetime-modernizer`
- **Category:** quality
- **Status:** active
- **Description:** Migrates datetime.utcnow() to datetime.now(tz=timezone.utc) across codebase.
- **Capabilities:** quality

#### Agent 60: Dependency Conflict Agent
- **ID:** `dependency-conflict-agent`
- **Category:** dependencies
- **Status:** active
- **Description:** Diagnoses pip resolver conflicts; recommends compatible version ranges.
- **Capabilities:** dependencies

#### Agent 61: Doc Freshness Checker
- **ID:** `doc-freshness-checker`
- **Category:** documentation
- **Status:** active
- **Description:** Validates documentation freshness; identifies stale docs and broken links.
- **Capabilities:** documentation

#### Agent 62: Doc Refactor Test Agent
- **ID:** `doc-refactor-test-agent`
- **Category:** documentation
- **Status:** active
- **Description:** Refactors documentation tests and validates documentation test infrastructure.
- **Capabilities:** documentation

#### Agent 63: Fragile Test Guardian
- **ID:** `fragile-test-guardian`
- **Category:** testing
- **Status:** active
- **Description:** Identifies and stabilizes fragile/flaky tests before they cause CI failures.
- **Capabilities:** testing

#### Agent 64: GitHub Pages Manager
- **ID:** `github-pages-manager`
- **Category:** documentation
- **Status:** active
- **Description:** Manages GitHub Pages deployment, MkDocs builds, documentation validation, cognitive_app accessibilit
- **Capabilities:** documentation

#### Agent 65: Integration Test Runner
- **ID:** `integration-test-runner`
- **Category:** testing
- **Status:** active
- **Description:** Runs integration tests across services; validates cross-component interactions.
- **Capabilities:** testing

#### Agent 66: JSON Serialization Expert
- **ID:** `json-serialization-expert`
- **Category:** quality
- **Status:** active
- **Description:** Diagnoses and fixes JSON serialization issues in API responses and data pipelines.
- **Capabilities:** quality

#### Agent 67: Link Validator Agent
- **ID:** `link-validator-agent`
- **Category:** documentation
- **Status:** active
- **Description:** Cross-reference and link validation for documentation; detects broken links.
- **Capabilities:** documentation

#### Agent 68: Meta Tensor Validator
- **ID:** `meta-tensor-validator`
- **Category:** ml
- **Status:** active
- **Description:** Validates PyTorch model initialization patterns to prevent meta tensor issues.
- **Capabilities:** machine_learning

#### Agent 69: ML Validation Suite Agent
- **ID:** `ml-validation-suite-agent`
- **Category:** ml
- **Status:** active
- **Description:** Comprehensive ML model validation including determinism and reproducibility checks.
- **Capabilities:** machine_learning

#### Agent 70: MSV Dashboard Monitor
- **ID:** `msv-dashboard-monitor`
- **Category:** monitoring
- **Status:** active
- **Description:** Monitors MSV dashboard metrics and alerts on regressions.
- **Capabilities:** monitoring

#### Agent 71: Mutation Testing Agent
- **ID:** `mutation-testing-agent`
- **Category:** testing
- **Status:** active
- **Description:** Performs mutation testing to evaluate test suite effectiveness.
- **Capabilities:** testing

#### Agent 72: Owner Approval Guard
- **ID:** `owner-approval-guard`
- **Category:** governance
- **Status:** active
- **Description:** Enforces owner approval requirements for autonomous operations.
- **Capabilities:** governance

#### Agent 73: Performance Regression Detector
- **ID:** `performance-regression-detector`
- **Category:** performance
- **Status:** active
- **Description:** Detects performance regressions by comparing metrics against baselines.
- **Capabilities:** performance

#### Agent 74: PII Scrubber
- **ID:** `pii-scrubber`
- **Category:** security
- **Status:** active
- **Description:** Scrubs PII from text content before processing; ensures GDPR/CCPA compliance.
- **Capabilities:** security

#### Agent 75: PR-3095 Verification Agent
- **ID:** `pr-3095-verification-agent`
- **Category:** governance
- **Status:** active
- **Description:** Verifies that PR 3095 fixes have been correctly applied across the codebase.
- **Capabilities:** governance

#### Agent 76: PR Check Remediation Agent
- **ID:** `pr-check-remediation-agent`
- **Category:** ci_cd
- **Status:** active
- **Description:** Remediates failed PR checks by analyzing failure patterns and applying fixes.
- **Capabilities:** ci_cd

#### Agent 77: PR Test Infrastructure Fixer
- **ID:** `pr-test-infrastructure-fixer`
- **Category:** testing
- **Status:** active
- **Description:** Fixes test infrastructure issues introduced by PR changes.
- **Capabilities:** testing

#### Agent 78: PyPI Publishing Operations Agent
- **ID:** `pypi-publishing-operations-agent`
- **Category:** operations
- **Status:** active
- **Description:** Manages PyPI package publishing operations and release workflows.
- **Capabilities:** operations

#### Agent 79: Python 3.12 Type Fixer
- **ID:** `python-312-type-fixer`
- **Category:** quality
- **Status:** active
- **Description:** Fixes Python 3.12 type annotation incompatibilities across the codebase.
- **Capabilities:** quality

#### Agent 80: QA Walkthrough Agent
- **ID:** `qa-walkthrough-agent`
- **Category:** testing
- **Status:** active
- **Description:** Executes repository-wide QA walkthrough with evidence-based audit steps.
- **Capabilities:** testing

#### Agent 81: Quantum Compliance Tuning Agent
- **ID:** `quantum-compliance-tuning-agent`
- **Category:** cognitive
- **Status:** active
- **Description:** Tunes quantum-inspired compliance parameters for cognitive brain optimization.
- **Capabilities:** cognitive

#### Agent 82: RAG Freshness Loop Agent
- **ID:** `rag-freshness-loop-agent`
- **Category:** ml
- **Status:** active
- **Description:** Maintains RAG index freshness through continuous update and validation loops.
- **Capabilities:** machine_learning

#### Agent 83: RAG Index Manager
- **ID:** `rag-index-manager`
- **Category:** ml
- **Status:** active
- **Description:** Manages RAG index operations including building, updating, and querying.
- **Capabilities:** machine_learning

#### Agent 84: RAG Meta Tensor Guardian
- **ID:** `rag-meta-tensor-guardian`
- **Category:** ml
- **Status:** active
- **Description:** Guards RAG tensor operations against meta tensor initialization errors.
- **Capabilities:** machine_learning

#### Agent 85: RAG Module Management Agent
- **ID:** `rag-module-management-agent`
- **Category:** ml
- **Status:** active
- **Description:** Manages RAG module lifecycle including initialization and hot-swapping.
- **Capabilities:** machine_learning

#### Agent 86: Reference Updater Agent
- **ID:** `reference-updater-agent`
- **Category:** quality
- **Status:** active
- **Description:** Atomic reference updates across entire codebase with transaction-like behavior.
- **Capabilities:** quality

#### Agent 87: Repository Hygiene Agent
- **ID:** `repository-hygiene-agent`
- **Category:** operations
- **Status:** active
- **Description:** Autonomous repository cleanup, maintenance, and codebase hygiene specialist.
- **Capabilities:** operations

#### Agent 88: Repository Organization Agent
- **ID:** `repository-organization-agent`
- **Category:** operations
- **Status:** active
- **Description:** Organizes repository structure per LFS policy and directory conventions.
- **Capabilities:** operations

#### Agent 89: Root Organizer Agent
- **ID:** `root-organizer-agent`
- **Category:** operations
- **Status:** active
- **Description:** Safe incremental root folder reorganization; zero-break guarantee.
- **Capabilities:** operations

#### Agent 90: Rust Config Validator
- **ID:** `rust-config-validator`
- **Category:** configuration
- **Status:** active
- **Description:** Validates Rust configurations in hybrid Python/Rust swarm components.
- **Capabilities:** configuration

#### Agent 91: Security Alert Verification Agent
- **ID:** `security-alert-verification-agent`
- **Category:** security
- **Status:** active
- **Description:** Validates GitHub security alerts, triage, and generates remediation plans.
- **Capabilities:** security

#### Agent 92: Semantic Search Agent
- **ID:** `semantic-search`
- **Category:** ml
- **Status:** active
- **Description:** Semantic search over codebase and documentation using vector embeddings.
- **Capabilities:** machine_learning

#### Agent 93: Session Analysis Agent
- **ID:** `session-analysis-agent`
- **Category:** cognitive
- **Status:** active
- **Description:** Analyzes Copilot sessions, verifies commits, extracts patterns for learning.
- **Capabilities:** cognitive

#### Agent 94: Session Log Retrieval Agent
- **ID:** `session-log-retrieval-agent`
- **Category:** cognitive
- **Status:** active
- **Description:** Recalls previous Copilot sessions, extracts uncommitted work, searches history.
- **Capabilities:** cognitive

#### Agent 95: Terminology Consistency Agent
- **ID:** `terminology-consistency-agent`
- **Category:** documentation
- **Status:** active
- **Description:** Enforces consistent terminology across documentation and code comments.
- **Capabilities:** documentation

#### Agent 96: Test Alignment Fixer
- **ID:** `test-alignment-fixer`
- **Category:** testing
- **Status:** active
- **Description:** Fixes test alignment issues by updating tests to match API changes.
- **Capabilities:** testing

#### Agent 97: Test Alignment Fixer Enhanced
- **ID:** `test-alignment-fixer-enhanced`
- **Category:** testing
- **Status:** active
- **Description:** Enhanced test alignment fixer with broader coverage and smarter detection.
- **Capabilities:** testing

#### Agent 98: Test Enhancement Agent
- **ID:** `unified-coverage-agent`
- **Category:** testing
- **Status:** active
- **Description:** Improves test quality through refactoring, edge case coverage, assertion hardening.
- **Capabilities:** testing

#### Agent 99: Test Failure Analyzer Agent
- **ID:** `test-failure-analyzer-agent`
- **Category:** testing
- **Status:** active
- **Description:** Analyzes and diagnoses test failures with root cause classification.
- **Capabilities:** testing

#### Agent 100: Tokenization Coverage Agent
- **ID:** `tokenization-coverage-agent`
- **Category:** testing
- **Status:** active
- **Description:** Improves src/tokenization test coverage, CLI validation, and coverage reporting.
- **Capabilities:** testing

#### Agent 101: Tracking Document QA Agent
- **ID:** `tracking-document-qa-agent`
- **Category:** documentation
- **Status:** active
- **Description:** QA validation of tracking documents, completion reports, and session summaries.
- **Capabilities:** documentation

#### Agent 102: Unified Doc Agent
- **ID:** `unified-doc-agent`
- **Category:** documentation
- **Status:** active
- **Description:** Unified documentation management combining freshness, quality, and consolidation.
- **Capabilities:** documentation

#### Agent 103: Unified Governance Gate
- **ID:** `unified-governance-gate`
- **Category:** governance
- **Status:** active
- **Description:** Unified governance enforcement across all operations, merges, and deployments.
- **Capabilities:** governance

#### Agent 104: Workflow Analytics Agent
- **ID:** `workflow-analytics-agent`
- **Category:** ci_cd
- **Status:** active
- **Description:** Analyzes workflow performance, detects patterns, and recommends optimizations.
- **Capabilities:** ci_cd

#### Agent 105: Workflow CI Fixer
- **ID:** `workflow-ci-fixer`
- **Category:** ci_cd
- **Status:** active
- **Description:** Fixes GitHub Actions workflow syntax errors, permission issues, and CI failures.
- **Capabilities:** ci_cd

#### Agent 106: Workflow Health Monitor
- **ID:** `workflow-health-monitor`
- **Category:** ci_cd
- **Status:** active
- **Description:** Real-time workflow health monitoring with alerting and trend analysis.
- **Capabilities:** ci_cd

#### Agent 107: Workflow Management Agent
- **ID:** `workflow-management-agent`
- **Category:** ci_cd
- **Status:** active
- **Description:** Orchestrates workflow operations including scheduling, triggers, and lifecycle.
- **Capabilities:** ci_cd

#### Agent 108: Workflow Optimization Agent
- **ID:** `workflow-optimization-agent`
- **Category:** ci_cd
- **Status:** active
- **Description:** Identifies and applies workflow optimizations for speed and cost reduction.
- **Capabilities:** ci_cd

#### Agent 109: Cognitive Brain CLI Agent
- **ID:** `cognitive-brain-cli-agent`
- **Category:** operations
- **Status:** active
- **Description:** Production agent for operating the Cognitive Brain CLI console. Executes shell commands, HTTP reques
- **Capabilities:** operations

#### Agent 110: Workflow Compliance Guardian
- **ID:** `workflow-compliance-guardian`
- **Category:** ci
- **Status:** active
- **Description:** Enforces and auto-heals branch-scoped concurrency + timeout rules across all 91 GitHub Actions workf
- **Capabilities:** continuous_integration

#### Agent 111: CI Health Alert Agent
- **ID:** `ci-health-alert-agent`
- **Category:** ci
- **Status:** active
- **Description:** Auto-responds to GitHub issues tagged ci-health-alert. Classifies failure patterns (including SELF_H
- **Capabilities:** continuous_integration, packaging_validation, self_healing_cascade_detection

#### Agent 112: Repo Var Sync Agent
- **ID:** `repo-var-sync-agent`
- **Category:** infrastructure
- **Status:** active
- **Description:** Keeps .codex/agent_context.json bidirectionally in sync with GitHub Actions repository variables (CO
- **Capabilities:** infrastructure

#### Agent 113: Cognitive OODA Loop Agent
- **ID:** `cognitive-ooda-loop-agent`
- **Category:** cognitive
- **Status:** active
- **Description:** Executes a full OODA loop from a PR comment. Drives the real OODAOrchestrator via POST /api/ooda/pro
- **Capabilities:** cognitive

#### Agent 114: Memory Sync Agent
- **ID:** `memory-sync-agent`
- **Category:** cognitive
- **Status:** active
- **Description:** Syncs SQLiteMemory (STM/LTM) with the cognitive brain pattern library. Consolidates hot STM entries
- **Capabilities:** cognitive

#### Agent 115: Telemetry Classifier Agent
- **ID:** `telemetry-classifier-agent`
- **Category:** ci
- **Status:** active
- **Description:** Reads CI telemetry artifacts, identifies top-N unknown failure patterns, and generates new classifie
- **Capabilities:** continuous_integration

#### Agent 116: Admin Automation Agent
- **ID:** `admin-automation-agent`
- **Category:** operations
- **Status:** active
- **Description:** specialist
- **Capabilities:** operations

#### Agent 117: Batch Triage Agent
- **ID:** `batch-triage-agent`
- **Category:** ci
- **Status:** active
- **Description:** specialist
- **Capabilities:** continuous_integration

#### Agent 118: CI Diagnostic Agent
- **ID:** `ci-diagnostic-agent`
- **Category:** ci
- **Status:** active
- **Description:** specialist
- **Capabilities:** continuous_integration

#### Agent 119: Codebase QA Walkthrough Agent
- **ID:** `codebase-qa-walkthrough-agent`
- **Category:** quality
- **Status:** active
- **Description:** specialist
- **Capabilities:** quality

#### Agent 120: Cognitive Brain Session Injector
- **ID:** `cognitive-brain-session-injector`
- **Category:** cognitive
- **Status:** active
- **Description:** specialist
- **Capabilities:** cognitive

#### Agent 121: Dependency Conflict Resolver
- **ID:** `dependency-conflict-resolver`
- **Category:** dependencies
- **Status:** active
- **Description:** specialist
- **Capabilities:** dependencies

#### Agent 122: Doc Test Scribe
- **ID:** `doc-test-scribe`
- **Category:** documentation
- **Status:** active
- **Description:** specialist
- **Capabilities:** documentation

#### Agent 123: Documentation Sync Validator
- **ID:** `documentation-sync-validator`
- **Category:** documentation
- **Status:** active
- **Description:** specialist
- **Capabilities:** documentation

#### Agent 124: Dynamics365 PowerPlatform Architect Agent
- **ID:** `dynamics365-powerplatform-architect-agent`
- **Category:** integration
- **Status:** active
- **Description:** specialist
- **Capabilities:** integration

#### Agent 125: GitHub Auth Manager
- **ID:** `github-auth-manager`
- **Category:** security
- **Status:** active
- **Description:** specialist
- **Capabilities:** security

#### Agent 126: GitHub Code Reviewer
- **ID:** `github-code-reviewer`
- **Category:** quality
- **Status:** active
- **Description:** specialist
- **Capabilities:** quality

#### Agent 127: GitHub Deployment Gatekeeper
- **ID:** `github-deployment-gatekeeper`
- **Category:** operations
- **Status:** active
- **Description:** utility
- **Capabilities:** operations

#### Agent 128: GitHub Security Enforcer
- **ID:** `github-security-enforcer`
- **Category:** security
- **Status:** active
- **Description:** specialist
- **Capabilities:** security

#### Agent 129: GitHub Security Validator Agent
- **ID:** `github-security-validator-agent`
- **Category:** security
- **Status:** active
- **Description:** specialist
- **Capabilities:** security

#### Agent 130: GitHub Test Orchestrator
- **ID:** `github-test-orchestrator`
- **Category:** testing
- **Status:** active
- **Description:** orchestrator
- **Capabilities:** testing

#### Agent 131: GitHub Testing Orchestrator Agent
- **ID:** `github-testing-orchestrator-agent`
- **Category:** testing
- **Status:** active
- **Description:** orchestrator
- **Capabilities:** testing

#### Agent 132: GitHub Workflow Optimizer
- **ID:** `github-workflow-optimizer`
- **Category:** operations
- **Status:** active
- **Description:** specialist
- **Capabilities:** operations

#### Agent 133: ML Threat Detector
- **ID:** `ml-threat-detector`
- **Category:** security
- **Status:** active
- **Description:** specialist
- **Capabilities:** security

#### Agent 134: Repo Health Guardian
- **ID:** `repo-health-guardian`
- **Category:** operations
- **Status:** active
- **Description:** utility
- **Capabilities:** operations

#### Agent 135: Security Vulnerability Patcher
- **ID:** `security-vulnerability-patcher`
- **Category:** security
- **Status:** active
- **Description:** specialist
- **Capabilities:** security

#### Agent 136: Service Integration Tester
- **ID:** `service-integration-tester`
- **Category:** testing
- **Status:** active
- **Description:** specialist
- **Capabilities:** testing

#### Agent 137: Test Coverage Enforcer
- **ID:** `test-coverage-enforcer`
- **Category:** testing
- **Status:** active
- **Description:** specialist
- **Capabilities:** testing

#### Agent 138: Zendesk Architect Agent
- **ID:** `zendesk-architect-agent`
- **Category:** integration
- **Status:** active
- **Description:** specialist
- **Capabilities:** integration

#### Agent 139: Orchestrator Agent
- **ID:** `orchestrator-agent`
- **Category:** operations
- **Status:** active
- **Description:** orchestrator
- **Capabilities:** operations

#### Agent 140: Copilot Session Chain
- **ID:** `copilot-session-chain`
- **Category:** ci_cd
- **Status:** active
- **Description:** Automates opening the next Copilot Coding Agent sub-PR targeting 0D_base_ (the staging integration b
- **Capabilities:** session_chaining, integration_branch_enforcement, sub_pr_creation, copilot_trigger, base_staging_integration

#### Agent 141: Packaging Validation Agent
- **ID:** `packaging-validation-agent`
- **Category:** security
- **Status:** active
- **Description:** Validates Python packaging configuration (pyproject.toml, lock files), detects Dependabot vulnerabil
- **Capabilities:** packaging_validation, dependency_management, security_scanning, pep621_compliance, dependabot_remediation

#### Agent 142: Energy Conversion Agent
- **ID:** `energy-conversion-agent`
- **Category:** simulation
- **Status:** active
- **Description:** AI-enhanced agent skilled in developing programmatic systems for simulating and calculating gas-to-e
- **Capabilities:** energy_conversion_simulation, gas_to_electric, power_distribution, thermodynamic_modeling, ai_optimization

#### Agent 143: Promote Integration Branch Workflow
- **ID:** `promote-integration-branch`
- **Category:** ci_cd
- **Status:** active
- **Description:** Autonomously creates the 0D_base_ staging integration branch from a given SHA using GitHubMCPPoster.
- **Capabilities:** branch_creation, pr_lifecycle, integration_branch_management, promotion_workflow, codex_master_key_ops

#### Agent 144: Create Sub-PR to 0D_base_ Workflow
- **ID:** `create-sub-pr-to-0D_base_`
- **Category:** ci_cd
- **Status:** active
- **Description:** Creates a pull request from any session branch into 0D_base_ (staging integration branch). Verifies
- **Capabilities:** sub_pr_creation, session_branch_management, zero_d_base_routing, integration_branch_management

#### Agent 145: Post Accountability to Discussion Workflow
- **ID:** `post-accountability-to-discussion`
- **Category:** ci_cd
- **Status:** active
- **Description:** Automated workflow that posts session accountability entries to GitHub Discussion #3673 ([Ongoing] C
- **Capabilities:** accountability_reporting, discussion_posting, governance_automation, session_documentation


### Archived Agents (14)

#### Archived Agent 1: Cache Manager Integration
- **ID:** `cache-manager-integration`
- **Status:** ARCHIVED
- **Description:** Integration layer for cache management across workflow and composite actions.

#### Archived Agent 2: CI Failure Resolution Agent
- **ID:** `ci-failure-resolution-agent`
- **Status:** ARCHIVED
- **Description:** Resolves CI failures by diagnosing logs and applying structured fix patterns.

#### Archived Agent 3: CI Resilience Emergency Response Agent
- **ID:** `ci-resilience-emergency-response-agent`
- **Status:** ARCHIVED
- **Description:** Resilience-focused emergency CI recovery with retry and fallback strategies.

#### Archived Agent 4: Coverage Gapfill Agent
- **ID:** `coverage-gapfill-agent`
- **Status:** ARCHIVED
- **Description:** DEPRECATED (S174): Superseded by unified-coverage-agent. Targets low-coverage modules and generates

#### Archived Agent 5: Coverage Maintenance Agent
- **ID:** `coverage-maintenance-agent`
- **Status:** ARCHIVED
- **Description:** DEPRECATED (S174): Superseded by unified-coverage-agent. Maintains test coverage over time; alerts o

#### Archived Agent 6: Coverage Roadmap Agent
- **ID:** `coverage-roadmap-agent`
- **Status:** ARCHIVED
- **Description:** DEPRECATED (S174): Superseded by unified-coverage-agent. Drives coverage threshold roadmap, tracks p

#### Archived Agent 7: Dependency Security Review Agent
- **ID:** `dependency-security-review-agent`
- **Status:** ARCHIVED
- **Description:** Reviews dependency security posture; flags CVEs and outdated packages.

#### Archived Agent 8: Dependency Vulnerability Scanner
- **ID:** `dependency-vulnerability-scanner`
- **Status:** ARCHIVED
- **Description:** Scans dependencies against multiple CVE databases; generates remediation plans.

#### Archived Agent 9: Documentation Consolidator
- **ID:** `documentation-consolidator`
- **Status:** ARCHIVED
- **Description:** Consolidates fragmented documentation with semantic analysis and content preservation.

#### Archived Agent 10: Documentation Quality Agent
- **ID:** `documentation-quality-agent`
- **Status:** ARCHIVED
- **Description:** Automated documentation quality assessment; MkDocs validation; link checking.

#### Archived Agent 11: Secret Detection Agent
- **ID:** `secret-detection-agent`
- **Status:** ARCHIVED
- **Description:** Scans codebase for accidentally committed secrets and credentials.

#### Archived Agent 12: Security Audit Agent
- **ID:** `security-audit-agent`
- **Status:** ARCHIVED
- **Description:** Comprehensive security audits across code, dependencies, and workflows.

#### Archived Agent 13: Test Coverage Agent
- **ID:** `test-coverage-agent`
- **Status:** ARCHIVED
- **Description:** DEPRECATED (S174): Superseded by unified-coverage-agent. Drives test coverage improvements; identifi

#### Archived Agent 14: Test Coverage Monitor
- **ID:** `test-coverage-monitor`
- **Status:** ARCHIVED
- **Description:** DEPRECATED (S174): Superseded by unified-coverage-agent. Monitors test coverage, enforces thresholds


---

## SECTION 3: CAPABILITY MATRIX

This matrix shows which agents handle which capability categories:

| Capability | Agents | Entry Points |
|------------|--------|--------------|
| **PR Analysis** | github-guru-agent, pr-check-remediation-agent, code-review | github-guru-agent |
| **Issue Triage** | github-guru-agent, policy-coach-agent | github-guru-agent |
| **CI/CD Automation** | ci-auto-healer-agent, ci-failure-resolution-agent, workflow-ci-fixer | ci-failure-resolution-agent |
| **Test Coverage** | unified-coverage-agent, test-coverage-agent, fragile-test-guardian | unified-coverage-agent |
| **Security Scanning** | unified-security-scanner, codeql-alert-resolution-agent, secret-detection-agent | unified-security-scanner |
| **Documentation** | unified-doc-agent, doc-freshness-checker, link-validator-agent | unified-doc-agent |
| **Dependency Management** | dependency-vulnerability-scanner, dependency-conflict-agent | dependency-vulnerability-scanner |
| **Code Quality** | code-analysis-agent, test-pattern-guardian, mutation-testing-agent | code-analysis-agent |
| **Performance** | performance-monitor-agent, cache-management-agent, workflow-optimization-agent | performance-monitor-agent |
| **Repository Hygiene** | repository-hygiene-agent, root-organizer-agent | repository-hygiene-agent |

---

## SECTION 4: ARCHIVED AGENT REFERENCE

### Why Agents Get Archived

1. **Consolidated into Unified Entry Points** (40%):
   - `coverage-gapfill-agent` → `unified-coverage-agent`
   - `test-coverage-agent` → `unified-coverage-agent`
   - `coverage-maintenance-agent` → `unified-coverage-agent`

2. **Replaced by Better Alternatives** (30%):
   - `workflow-health-monitor.deprecated` → `workflow-health-monitor`

3. **Functionality Absorbed by Other Agents** (20%):
   - Capabilities rolled into orchestrator-agent or other specialists

4. **Deprecated Due to Obsolescence** (10%):
   - No longer needed due to platform changes

---

## SECTION 5: SEARCH INDEX

### Index by Keywords

**agent-id:** Search by agent identifier  
**agent-name:** Search by agent display name  
**capability:** Search by capability tag  
**category:** Search by domain category  
**status:** Active | Archived

### Quick Reference by Task

**Need to fix CI/CD failures?** → `ci-failure-resolution-agent`, `ci-emergency-response-agent`

**Need to improve test coverage?** → `unified-coverage-agent`

**Need security scanning?** → `unified-security-scanner`

**Need to consolidate docs?** → `unified-doc-agent`

**Need PR analysis?** → `github-guru-agent`

**Need repository health?** → `repository-hygiene-agent`

**Need cache optimization?** → `cache-management-agent`

**Need multi-agent orchestration?** → `orchestrator-agent`

---

## Metadata

- **Generated:** 2026-06-20T06:50:10.985194
- **Source:** `.github/agents/AGENT_REGISTRY.yaml`
- **Version:** 7.0
- **Maintainer:** @mbaetiong
- **Next Update:** 2026-06-22T12:00Z (Phase D Launch)
