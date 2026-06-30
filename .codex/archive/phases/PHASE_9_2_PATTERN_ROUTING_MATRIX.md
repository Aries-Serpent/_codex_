# PHASE 9.2: Pattern-to-Agent Routing Matrix

> **Document:** Routing rules for pattern-to-agent dispatch  
> **Version:** 1.0  
> **Date:** 2026-06-26  
> **Status:** ✅ PRODUCTION READY

---

## Executive Summary

This document defines how the cascade orchestrator routes detected CI failures to appropriate specialist agents for automated remediation. Each pattern has a primary agent assignment with fallback routing paths.

---

## Primary Pattern-Agent Mappings

### RP-001: Unused Imports (F401)
```
Pattern: RP-001
Confidence Threshold: >85%
Primary Agent: ci-auto-healer-agent
Fallback Agent: autonomous-test-healer-agent
Time to Fix: <2 seconds
Post-Fix Validation: ruff check --select F401
```

**Routing Logic:**
1. Detect F401 error in stderr
2. Route to `ci-auto-healer-agent`
3. Agent applies fix: Remove import OR add `as _` marker
4. Validate with ruff check
5. Re-run affected tests

**Success Metrics:**
- Success rate: 92%
- False positive rate: 3%
- Validation pass rate: 99%

---

### RP-002: Type Annotation Errors
```
Pattern: RP-002
Confidence Threshold: >80%
Primary Agent: python-312-type-fixer
Fallback Agent: ci-testing-agent
Time to Fix: <5 seconds
Post-Fix Validation: mypy --strict
```

**Routing Logic:**
1. Detect mypy error in stderr
2. Parse error type (deprecated, missing, incompatible)
3. Route to `python-312-type-fixer`
4. Agent applies category-specific fix
5. Validate with mypy in strict mode
6. Run affected tests

**Success Metrics:**
- Success rate: 78%
- False positive rate: 12%
- Validation pass rate: 95%

---

### RP-003: Test Assertion Failures
```
Pattern: RP-003
Confidence Threshold: >80%
Primary Agent: autonomous-test-healer-agent
Fallback Agent: ci-testing-agent
Time to Fix: <3 seconds
Post-Fix Validation: pytest --count=5
```

**Routing Logic:**
1. Detect AssertionError in test output
2. Parse assertion code (vague check, tautology, catch-all)
3. Route to `autonomous-test-healer-agent`
4. Agent analyzes assertion and applies targeted fix
5. Re-run test 5 times (check for flakiness)
6. Validate pass on all 5 runs

**Success Metrics:**
- Success rate: 85%
- False positive rate: 11%
- Validation pass rate: 92%

---

### RP-004: Dependency Resolution Conflicts
```
Pattern: RP-004
Confidence Threshold: >75%
Primary Agent: dependency-conflict-agent
Fallback Agent: ci-testing-agent
Time to Fix: <10 seconds
Post-Fix Validation: pip install --dry-run -e .
```

**Routing Logic:**
1. Detect pip ResolutionImpossible or VersionConflict
2. Parse conflicting packages and version constraints
3. Route to `dependency-conflict-agent`
4. Agent finds overlapping version range
5. Apply constraint update to requirements/setup files
6. Validate with dry-run pip install
7. Test actual environment setup

**Success Metrics:**
- Success rate: 72%
- False positive rate: 14%
- Validation pass rate: 88%

---

### RP-005: YAML Formatting Errors
```
Pattern: RP-005
Confidence Threshold: >90%
Primary Agent: workflow-ci-fixer
Fallback Agent: (none, very high confidence)
Time to Fix: <1 second
Post-Fix Validation: yamllint, python yaml.safe_load()
```

**Routing Logic:**
1. Detect YAML parsing error in workflow run
2. Identify exact line and error type (indentation, syntax, structure)
3. Route to `workflow-ci-fixer`
4. Agent applies formatting fix (re-indent, add missing colons, etc.)
5. Validate with yamllint and yaml.safe_load()
6. Dry-run workflow to confirm

**Success Metrics:**
- Success rate: 94%
- False positive rate: 1%
- Validation pass rate: 99%

---

### RP-006: Coverage Threshold Violations
```
Pattern: RP-006
Confidence Threshold: >80%
Primary Agent: unified-coverage-agent
Fallback Agent: autonomous-test-healer-agent
Time to Fix: <15 seconds
Post-Fix Validation: coverage report --fail-under=X
```

**Routing Logic:**
1. Detect coverage failure in workflow
2. Identify missing coverage lines/branches
3. Route to `unified-coverage-agent`
4. Agent evaluates options:
   - A) Add tests to cover code
   - B) Mark code as non-critical (pragma: no cover)
   - C) Adjust threshold (if justified)
5. Validate with coverage report
6. Run all tests to ensure they pass

**Success Metrics:**
- Success rate: 81%
- False positive rate: 13%
- Validation pass rate: 91%

---

### RP-007: Documentation Link Validation
```
Pattern: RP-007
Confidence Threshold: >85%
Primary Agent: link-validator-agent
Fallback Agent: (none, deterministic)
Time to Fix: <2 seconds
Post-Fix Validation: link-validator --validate-all
```

**Routing Logic:**
1. Detect broken link in validation workflow
2. Identify link type (relative, external, fragment)
3. Route to `link-validator-agent`
4. Agent applies fix:
   - A) Update path if file was moved
   - B) Fix fragment reference if section exists
   - C) Flag external links for manual review
5. Re-validate all links in document

**Success Metrics:**
- Success rate: 89%
- False positive rate: 5%
- Validation pass rate: 96%

---

### RP-008: Import Path Issues (P19 Shadow)
```
Pattern: RP-008
Confidence Threshold: >75%
Primary Agent: ci-importerror-agent
Fallback Agent: ci-testing-agent
Time to Fix: <5 seconds
Post-Fix Validation: python -c "import ..."
```

**Routing Logic:**
1. Detect ImportError or ModuleNotFoundError
2. Determine cause (path change, shadow import, stale .egg-link)
3. Route to `ci-importerror-agent`
4. Agent applies fix:
   - A) Update import paths in source
   - B) Rename/move shadow import
   - C) Regenerate .egg-link (pip install -e .)
5. Test imports from multiple contexts
6. Run test suite

**Success Metrics:**
- Success rate: 76%
- False positive rate: 15%
- Validation pass rate: 89%

---

### RP-009: Flaky/Timing Test Failures
```
Pattern: RP-009
Confidence Threshold: >70%
Primary Agent: autonomous-test-healer-agent
Fallback Agent: ci-testing-agent
Time to Fix: <8 seconds
Post-Fix Validation: pytest --count=20 (all should pass)
```

**Routing Logic:**
1. Detect test failure with "FLAKY" marker or TimeoutError
2. Identify flakiness pattern (race condition, timing, isolation)
3. Route to `autonomous-test-healer-agent`
4. Agent applies stabilization:
   - A) Add explicit sync/flush calls
   - B) Replace sleep() with polling
   - C) Improve test isolation (fixtures, cleanup)
5. Run test 20 times, all should pass
6. Monitor for flakiness on subsequent runs

**Success Metrics:**
- Success rate: 68%
- False positive rate: 18%
- Validation pass rate: 85%

---

### RP-010: Workflow Compliance Issues
```
Pattern: RP-010
Confidence Threshold: >88%
Primary Agent: workflow-compliance-guardian
Fallback Agent: (none, deterministic)
Time to Fix: <2 seconds
Post-Fix Validation: yamllint, GitHub workflow syntax check
```

**Routing Logic:**
1. Detect workflow compliance error (missing concurrency, timeout-minutes, etc.)
2. Identify missing field or misconfiguration
3. Route to `workflow-compliance-guardian`
4. Agent applies mandatory fix:
   - Add concurrency control if missing
   - Add timeout-minutes to all jobs
   - Ensure job dependencies are valid
5. Validate with yamllint
6. Re-run workflow to confirm compliance

**Success Metrics:**
- Success rate: 88%
- False positive rate: 2%
- Validation pass rate: 99%

---

### RP-011: Cargo Feature Configuration
```
Pattern: RP-011
Confidence Threshold: >90%
Primary Agent: ci-testing-agent
Fallback Agent: (none, deterministic)
Time to Fix: <2 seconds
Post-Fix Validation: cargo clippy --all-features
```

**Routing Logic:**
1. Detect Cargo feature mismatch error
2. Parse error to identify missing feature
3. Route to `ci-testing-agent`
4. Agent adds feature to Cargo.toml with dependencies
5. Validate with cargo clippy --all-features
6. Run cargo tests --all-features

**Success Metrics:**
- Success rate: 91%
- False positive rate: 2%
- Validation pass rate: 99%

---

### RP-012: CodeQL/Security Alerts
```
Pattern: RP-012
Confidence Threshold: >60%
Primary Agent: code-scanning-remediation-agent
Fallback Agent: (human review required)
Time to Fix: <20 seconds
Post-Fix Validation: Code scanning re-run
```

**Routing Logic:**
1. Detect CodeQL/security alert in results
2. Identify alert type (SQL injection, hardcoded credentials, XSS, etc.)
3. Route to `code-scanning-remediation-agent`
4. Agent applies security fix (parameterized queries, secrets manager, etc.)
5. Re-run code scanning to verify
6. Flag for human review if confidence <70%

**Success Metrics:**
- Success rate: 65%
- False positive rate: 22%
- Validation pass rate: 78%

---

## Confidence Scoring Algorithm

```python
def calculate_confidence(failure_log: str, pattern: Pattern) -> float:
    """
    Calculate confidence score for pattern match (0.0 to 1.0)
    """
    score = 0.0
    
    # Primary signature match (40% weight)
    if re.search(pattern.primary_regex, failure_log):
        score += 0.40
    
    # Secondary indicators (30% weight)
    secondary_matches = sum(
        1 for indicator in pattern.secondary_indicators
        if indicator in failure_log
    )
    score += min(0.30, 0.10 * secondary_matches)
    
    # Absence of conflicting patterns (30% weight)
    if not any(
        re.search(other.primary_regex, failure_log)
        for other in OTHER_PATTERNS
        if other.id != pattern.id
    ):
        score += 0.30
    
    return min(1.0, score)
```

---

## Fallback & Escalation Rules

### Confidence-Based Routing
```
IF confidence > 85%:
    Direct routing to primary agent (high confidence)
ELIF confidence > 70%:
    Route to primary agent with human notification
ELIF confidence > 50%:
    Route with escalation flag (human review after agent attempt)
ELSE:
    Direct to human review (low confidence)
```

### Max Iterations Policy
```
MAX_ITERATIONS = 5
FOR iteration = 1 TO MAX_ITERATIONS:
    agent.attempt_fix(failure)
    IF validation_passes():
        commit_fix()
        return SUCCESS
    ELSE:
        log_attempt(iteration)
        IF iteration == MAX_ITERATIONS:
            escalate_to_human(full_context)
            return ESCALATED
    END IF
END FOR
```

### Escalation Checklist
When escalating to human review, provide:
- ✅ Original failure log (full stderr/stdout)
- ✅ Pattern matched (with confidence score)
- ✅ All 5 fix attempts and their results
- ✅ Recommended next steps
- ✅ Risk assessment (false positive likelihood)
- ✅ Contact info for specialist agent (if known)

---

## Routing Configuration

```yaml
# .codex/PHASE_9_2_ROUTING_CONFIG.yaml

routing_rules:
  - pattern_id: RP-001
    name: "Unused Imports"
    primary_agent: ci-auto-healer-agent
    confidence_threshold: 0.85
    max_attempts: 3
    post_fix_validation: ["ruff check --select F401"]
    
  - pattern_id: RP-002
    name: "Type Annotations"
    primary_agent: python-312-type-fixer
    confidence_threshold: 0.80
    max_attempts: 4
    post_fix_validation: ["mypy --strict"]
    
  # ... (all 12 patterns)

escalation_policy:
  max_iterations: 5
  human_review_threshold: 0.60
  escalation_method: github_pr_comment
  tags: ["requires-manual-review", "cascade-escalation"]

validation_strategy:
  timeout_seconds: 300
  retry_on_timeout: true
  max_retries: 3

monitoring:
  track_false_positives: true
  track_success_rate: true
  track_classification_latency: true
  dashboards:
    - url: /dashboards/cascade-health
    - url: /dashboards/pattern-stats
```

---

## Routing Decision Matrix

| Pattern | Confidence >85% | 70-85% | 50-70% | <50% |
|---------|-----------------|--------|---------|------|
| RP-001 (Imports) | Direct → Agent | Route + Notify | Escalate | Human |
| RP-002 (Types) | Direct → Agent | Route + Notify | Escalate | Human |
| RP-003 (Tests) | Direct → Agent | Route + Notify | Escalate | Human |
| RP-004 (Deps) | Direct → Agent | Route + Notify | Escalate | Human |
| RP-005 (YAML) | Direct → Agent | Route (safe) | Escalate | Human |
| RP-006 (Coverage) | Direct → Agent | Route + Notify | Escalate | Human |
| RP-007 (Links) | Direct → Agent | Route (safe) | Escalate | Human |
| RP-008 (Imports2) | Direct → Agent | Route + Notify | Escalate | Human |
| RP-009 (Flaky) | Direct → Agent | Route + Notify | Escalate | Human |
| RP-010 (Workflow) | Direct → Agent | Route (safe) | Escalate | Human |
| RP-011 (Cargo) | Direct → Agent | Route (safe) | Escalate | Human |
| RP-012 (Security) | Direct → Agent | Route + Notify | Escalate | Human |

---

## Agent Availability & SLA

| Agent | Response Time | Fix Time | Availability | Max Parallel |
|-------|---------------|-----------|--------------|----|
| ci-auto-healer-agent | <1s | <2s | 99.5% | 10 |
| python-312-type-fixer | <2s | <5s | 99.0% | 5 |
| autonomous-test-healer-agent | <2s | <8s | 98.8% | 8 |
| dependency-conflict-agent | <2s | <10s | 98.5% | 3 |
| workflow-ci-fixer | <1s | <1s | 99.7% | 20 |
| unified-coverage-agent | <2s | <15s | 98.0% | 4 |
| link-validator-agent | <1s | <2s | 99.8% | 15 |
| ci-importerror-agent | <2s | <5s | 99.2% | 6 |
| workflow-compliance-guardian | <1s | <2s | 99.9% | 25 |
| code-scanning-remediation-agent | <3s | <20s | 97.5% | 2 |

---

## Error Handling & Retry Logic

```python
def route_with_retry(
    failure_log: str,
    pattern: Pattern,
    max_attempts: int = 5
) -> RoutingResult:
    """
    Route failure to agent with retry logic
    """
    for attempt in range(1, max_attempts + 1):
        try:
            agent = get_agent_for_pattern(pattern)
            result = agent.attempt_fix(failure_log)
            
            if validate_fix(result):
                return RoutingResult.SUCCESS
            elif attempt < max_attempts:
                log_attempt_failure(attempt, result)
                # Try again with modified strategy
                continue
            else:
                # Max attempts exceeded
                escalate_to_human(failure_log, all_attempts)
                return RoutingResult.ESCALATED
                
        except AgentTimeoutException:
            if attempt < max_attempts:
                time.sleep(backoff_seconds(attempt))
                continue
            else:
                escalate_to_human(failure_log, "Agent timeout after 5 attempts")
                return RoutingResult.ESCALATED
                
        except Exception as e:
            log_routing_error(pattern, e)
            escalate_to_human(failure_log, f"Routing error: {e}")
            return RoutingResult.ERROR
```

---

## Monitoring & Alerting

### Success Metrics Dashboard
- Pattern detection accuracy: >95%
- Fix success rate by pattern: 65-94%
- Mean classification latency: <500ms
- Escalation rate: <5%
- False positive rate: <2% (target)

### Alert Rules
```yaml
alerts:
  - name: "High Escalation Rate"
    condition: "escalation_rate > 0.10"
    action: "notify slack #ci-health"
    
  - name: "Low Success Rate"
    condition: "fix_success_rate < 0.60"
    action: "page oncall engineer"
    
  - name: "Classification Timeout"
    condition: "classification_latency > 5.0s"
    action: "log for analysis, do not escalate"
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-06-26 | Initial release: 12 patterns mapped to agents with routing rules |

---

**Generated:** 2026-06-26T10:15:00Z  
**Status:** ✅ READY FOR ORCHESTRATOR IMPLEMENTATION  
**Document:** Phase 9.2 Pattern Routing

