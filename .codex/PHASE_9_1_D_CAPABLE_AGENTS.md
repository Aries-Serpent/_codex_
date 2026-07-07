# Phase 9.1: D_CAPABLE Agent Registry

**Document**: `.codex/PHASE_9_1_D_CAPABLE_AGENTS.md`  
**Generated**: 2026-07-07T18:20:47.507485  
**Authority**: @mbaetiong (D-tier autonomous, GO CONTINUE)  
**Track**: Phase 9 Track 9.1 Task 9.1.1  
**Status**: ✅ COMPLETE

---

## Executive Summary

This document provides the authoritative inventory of **9 D_CAPABLE agents** currently operational in the Aries-Serpent/_codex_ codebase. These agents have been validated to meet the D_CAPABLE decision framework criteria and are cleared for autonomous execution with structured handoff protocols.

---

## D_CAPABLE Agent Roster

### CI (1 agents)

#### CI Health Alert Agent
- **ID**: `ci-health-alert-agent`
- **Version**: 1.1.0
- **Maturity**: production
- **Enforcement Tier**: PARTIAL
- **Role**: specialist
- **Description**: Auto-responds to GitHub issues tagged ci-health-alert. Classifies failure patterns and proposes batch fixes.

### CI_CD (3 agents)

#### Copilot Session Chain
- **ID**: `copilot-session-chain`
- **Version**: 1.0.0
- **Maturity**: production
- **Enforcement Tier**: GROUNDED
- **Role**: orchestrator
- **Description**: Automates opening the next Copilot Coding Agent sub-PR targeting staging integration branch.

#### Self-Healing Orchestrator Agent
- **ID**: `self-healing-orchestrator-agent`
- **Version**: 1.0.0
- **Maturity**: production
- **Enforcement Tier**: PARTIAL
- **Role**: orchestrator
- **Description**: Orchestrates autonomous self-healing loops across CI failure patterns (RP-001 through RP-004+).

#### Workflow CI Fixer
- **ID**: `workflow-ci-fixer`
- **Version**: N/A
- **Maturity**: production
- **Enforcement Tier**: GROUNDED
- **Role**: specialist
- **Description**: Fixes GitHub Actions workflow syntax errors, permission issues, and CI failures.

### QUALITY (1 agents)

#### Rust Error Validator
- **ID**: `rust-error-validator`
- **Version**: N/A
- **Maturity**: production
- **Enforcement Tier**: GROUNDED
- **Role**: specialist
- **Description**: Scans Rust code for error handling issues and validates PyResult usage

### SECURITY (1 agents)

#### Packaging Validation Agent
- **ID**: `packaging-validation-agent`
- **Version**: 1.0.0
- **Maturity**: production
- **Enforcement Tier**: PARTIAL
- **Role**: specialist
- **Description**: Validates Python packaging configuration, detects Dependabot vulnerabilities, enforces PEP 621 compliance.

### TESTING (3 agents)

#### Ci Testing Agent
- **ID**: `ci-testing-agent`
- **Version**: N/A
- **Maturity**: production
- **Enforcement Tier**: GROUNDED
- **Role**: specialist
- **Description**: Specialized agent for debugging and fixing CI/CD pipeline issues, test failures, and build problems

#### Test Assertion Updater
- **ID**: `test-assertion-updater`
- **Version**: N/A
- **Maturity**: production
- **Enforcement Tier**: PARTIAL
- **Role**: specialist
- **Description**: Fixes test alignment issues by updating tests to match API changes and ensuring test assertions are correct

#### Test Pattern Guardian
- **ID**: `test-pattern-guardian`
- **Version**: N/A
- **Maturity**: production
- **Enforcement Tier**: GROUNDED
- **Role**: utility
- **Description**: Proactive test quality enforcement through AST-based pattern detection for mock exhaustion and serialization issues.

---

## D_CAPABLE Criteria Met

All 9 listed agents meet the following D_CAPABLE decision framework criteria:

1. ✅ **Production Maturity**: All agents are marked as production-ready
2. ✅ **Autonomy Model**: Explicitly marked with `autonomy_model: D_CAPABLE` in AGENT_REGISTRY.yaml
3. ✅ **Active Status**: All agents are actively maintained and deployed
4. ✅ **Enforcement Coverage**: All agents have defined enforcement tiers (GROUNDED, PARTIAL)
5. ✅ **Role Definition**: All agents have clearly defined roles (specialist, orchestrator, utility)

---

## Autonomy Framework Integration

Each agent is integrated with the autonomy framework as follows:

| ID | Enforcement Tier | Role | Capability |
|----|------------------|------|-----------|
| `ci-health-alert-agent` | PARTIAL | specialist | Structured autonomous (with gates) |
| `copilot-session-chain` | GROUNDED | orchestrator | High-assurance autonomous |
| `self-healing-orchestrator-agent` | PARTIAL | orchestrator | Structured autonomous (with gates) |
| `workflow-ci-fixer` | GROUNDED | specialist | High-assurance autonomous |
| `rust-error-validator` | GROUNDED | specialist | High-assurance autonomous |
| `packaging-validation-agent` | PARTIAL | specialist | Structured autonomous (with gates) |
| `ci-testing-agent` | GROUNDED | specialist | High-assurance autonomous |
| `test-assertion-updater` | PARTIAL | specialist | Structured autonomous (with gates) |
| `test-pattern-guardian` | GROUNDED | utility | High-assurance autonomous |

---

## Decision Logging Framework Requirements

These 9 D_CAPABLE agents will be integrated with the Phase 9.1 decision logging framework:

- **Decision Logger** (Task 9.1.2): Captures all autonomous decisions from these agents
- **Confidence Scorer** (Task 9.1.3): Assigns 0-100 confidence scores to decisions
- **Audit Trail** (Task 9.1.4): Maintains immutable audit records for all decisions
- **Test Suite** (Task 9.1.5): Validates decision accuracy across 100+ scenarios
- **Authorization Summary** (Task 9.1.6): Documents authorization and deployment status

---

## Next Steps

1. **Task 9.1.2**: Build decision logging framework for these 9 agents
2. **Task 9.1.3**: Implement confidence scoring system
3. **Task 9.1.4**: Create audit trail storage and query infrastructure
4. **Task 9.1.5**: Run 100+ decision scenario tests
5. **Task 9.1.6**: Deploy authorization updates to production

---

## Validation Hash

```
D_CAPABLE_COUNT: 9
REGISTRY_VERSION: 2.0.0
LAST_UPDATED: 2026-07-01T15:26:30Z
GENERATED_AT: 2026-07-07T18:20:47.507546
```

---

**Status**: ✅ Deliverable READY for Task 9.1.1  
**Authority Approval**: @mbaetiong (GO CONTINUE)  
**Next Phase**: Task 9.1.2 (unblocked as of 2026-07-07T18:20:47.507547)
