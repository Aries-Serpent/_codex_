# Phase 3-6 Agent Delegation Briefs

## Phase 3: Validation Campaign

### Agent: ci-testing-agent
Run the existing validation stack required by touched areas.

```
Task: Complete validation testing on PR #5231 changes
Focus: Tests for Rust FFI, core orchestration, package validation
Produce: .codex/PHASE_3_CI_TESTING_REPORT.md
```

### Agent: test-failure-analyzer-agent  
Analyze and fix any test failures discovered in Phase 3.

```
Task: Diagnose root causes of test failures
Focus: P19 shadow imports, flaky tests, import errors
Produce: .codex/PHASE_3_TEST_FAILURE_ANALYSIS.md
```

### Agent: unified-coverage-agent
Validate test coverage for packaging-critical areas.

```
Task: Check coverage on safety/, config/, packaging-related code
Focus: Maintain >80% coverage threshold
Produce: .codex/PHASE_3_COVERAGE_REPORT.md
```

### Agent: mypy-manager-agent
Type checking for external API surfaces.

```
Task: Verify all public APIs have correct type hints
Focus: External-facing modules and entry points
Produce: .codex/PHASE_3_TYPE_CHECK_REPORT.md
```

## Phase 4: Security/Governance Hardening

### Agent: unified-security-scanner
Full security validation.

```
Task: Dependency vulnerabilities, secrets, SAST
Focus: No new vulnerabilities in PR #5231 changes
Produce: .codex/PHASE_4_SECURITY_SCAN_REPORT.md
```

### Agent: security-audit-agent
Comprehensive security audit.

```
Task: Network policy, auth, permission model
Focus: PolicyViolationError enforcement, offline-first
Produce: .codex/PHASE_4_AUDIT_REPORT.md
```

### Agent: workflow-compliance-guardian
Workflow governance and WEC validation.

```
Task: Verify workflows comply with branch-scoped concurrency/timeouts
Focus: No regressions in CI/CD governance
Produce: .codex/PHASE_4_WORKFLOW_COMPLIANCE.md
```

### Agent: policy-coach-agent
Policy compliance coaching.

```
Task: Repository policy compliance check
Focus: All required policies followed
Produce: .codex/PHASE_4_POLICY_COMPLIANCE.md
```

## Phase 5: Documentation for External/Local Users

### Agent: unified-doc-agent
Update documentation for packaging and deployment.

```
Task: Update INSTALL.md, profiles, offline usage, local usage docs
Focus: Ensure docs match packaged/public experience
Produce: .codex/PHASE_5_DOC_UPDATES.md (summary of changes)
```

### Agent: doc-freshness-checker
Validate documentation freshness and accuracy.

```
Task: Check for stale docs, broken examples, outdated info
Focus: All examples work with current code
Produce: .codex/PHASE_5_DOC_FRESHNESS_REPORT.md
```

### Agent: link-validator-agent
Validate all documentation links.

```
Task: Check internal and external links in docs
Focus: No broken references
Produce: .codex/PHASE_5_LINK_VALIDATION_REPORT.md
```

### Agent: terminology-consistency-agent
Ensure consistent terminology across docs.

```
Task: Validate terminology consistency
Focus: Consistent use of profile names, API terms
Produce: .codex/PHASE_5_TERMINOLOGY_REPORT.md
```

## Phase 6: Consolidation (Non-delegated - handled by main agent)

1. Consolidate all phase reports
2. Identify any blockers preventing release
3. Apply remediation where needed
4. Run final secret scanning and parallel_validation
5. Produce FINAL_PACKAGING_READINESS_ASSESSMENT.md
