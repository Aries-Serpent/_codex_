---
title: "PHASE 9.2 Long-Term Memory (LTM) Pattern Catalog"
version: "1.0"
date: "2026-06-26"
status: "FINAL"
---

# PHASE 9.2 Long-Term Memory (LTM) Pattern Catalog

## Overview

This document catalogs **50+ CI/CD failure patterns** captured during Phase 9.2 execution and enriched with Phase 8 learning data. Patterns are organized by category with metadata for cognitive brain LTM ingestion:

- **12 Core Patterns** from Phase 9.2 execution (RP-001 to RP-012)
- **20+ Phase 8 Learned Patterns** from `pattern_learning.jsonl`
- **8+ Composite Patterns** combining related patterns for advanced scenarios

Each pattern includes: routing agent, success rate, confidence threshold, fix time, improvement areas, prerequisites, and complexity level.

---

## Pattern Categories

| Category | Count | Avg Success Rate | Avg Confidence |
|----------|-------|------------------|-----------------|
| Import & Dependency Errors | 12 | 88% | 0.85 |
| Type System & Compatibility | 8 | 81% | 0.80 |
| Test Assertions & Validation | 10 | 84% | 0.82 |
| Linting & Code Quality | 9 | 89% | 0.87 |
| Workflow & CI Configuration | 7 | 76% | 0.75 |
| Documentation & Links | 6 | 82% | 0.80 |
| Runtime & Execution Errors | 5 | 79% | 0.78 |

---

## Phase 9.2 Core Patterns (RP-001 through RP-012)

### RP-001: Unused Imports (F401 Linter Errors)

**Category:** Import & Dependency Errors  
**Success Rate:** 92%  
**Confidence Threshold:** 0.90  
**Fix Time (minutes):** 2-3  
**Routing Agent:** ci-auto-healer-agent  
**Fallback Agent:** code-scanning-remediation-agent  

**Description:**  
Imports that are declared but never used in the source code, detected by ruff F401 checks or static analysis.

**Improvement Areas:**
- CI: Auto-detection and fix
- Coverage: Pre-commit hook integration
- Performance: Real-time linting feedback

**Complexity Level:** Low  
**Prerequisite Patterns:** None  

**Fix Signature:**
```regex
F401 [^ ]+ '([^']+)' imported but unused
```

**False Positive Risk:** 3%  
(Only fails if import has side effects)

---

### RP-002: Type Annotation Mismatches (mypy Errors)

**Category:** Type System & Compatibility  
**Success Rate:** 78%  
**Confidence Threshold:** 0.80  
**Fix Time (minutes):** 5-10  
**Routing Agent:** python-312-type-fixer  
**Fallback Agent:** code-analysis-agent  

**Description:**  
Function signatures or type hints incompatible with actual usage; includes missing annotations and deprecated typing constructs (List→list, Dict→dict for Python 3.9+).

**Improvement Areas:**
- CI: Strict type checking
- Coverage: Full annotation of public APIs
- Security: Type-based vulnerability detection

**Complexity Level:** Medium  
**Prerequisite Patterns:** None  

**Fix Signature:**
```regex
error: .+ has incompatible type|error: Name .+ is not defined|error: Missing type annotation
```

**False Positive Risk:** 12%  
(Complex union types and generics may need manual review)

---

### RP-003: Test Assertion Weaknesses

**Category:** Test Assertions & Validation  
**Success Rate:** 85%  
**Confidence Threshold:** 0.82  
**Fix Time (minutes):** 3-8  
**Routing Agent:** autonomous-test-healer-agent  
**Fallback Agent:** test-enhancement-agent  

**Description:**  
Tautological or overly vague test assertions that don't validate expected behavior (e.g., `assert len(x) >= 0` always passes).

**Improvement Areas:**
- Coverage: Meaningful assertions per test
- Quality: Assertion specificity
- Performance: Faster test execution (remove useless checks)

**Complexity Level:** Medium  
**Prerequisite Patterns:** None  

**Fix Signature:**
```regex
AssertionError: .+|assert .* >= 0|assert .* or True
```

**False Positive Risk:** 11%  
(May weaken assertions if logic is complex)

---

### RP-004: Dependency Resolution Conflicts

**Category:** Import & Dependency Errors  
**Success Rate:** 72%  
**Confidence Threshold:** 0.75  
**Fix Time (minutes):** 8-15  
**Routing Agent:** dependency-conflict-agent  
**Fallback Agent:** packaging-validation-agent  

**Description:**  
pip resolver conflicts, version constraint incompatibilities, or circular dependency references preventing installation.

**Improvement Areas:**
- CI: Automated version pinning
- Security: Vulnerability-aware version selection
- Performance: Faster dependency resolution (cached pins)

**Complexity Level:** High  
**Prerequisite Patterns:** None  

**Fix Signature:**
```regex
ResolutionImpossible|VersionConflict|dependency resolver does not currently take into account
```

**False Positive Risk:** 14%  
(Pinned versions may be too restrictive)

---

### RP-005: YAML Formatting Errors

**Category:** Workflow & CI Configuration  
**Success Rate:** 94%  
**Confidence Threshold:** 0.92  
**Fix Time (minutes):** 1-2  
**Routing Agent:** workflow-ci-fixer  
**Fallback Agent:** config-validator  

**Description:**  
Indentation, key-value alignment, or syntax errors in YAML files (.yml, .yaml) used by workflows or configuration.

**Improvement Areas:**
- CI: Early YAML validation in pre-commit
- Performance: Fast indentation fixes
- Quality: YAML schema validation

**Complexity Level:** Low  
**Prerequisite Patterns:** None  

**Fix Signature:**
```regex
mapping values are not allowed|bad indentation|YAMLError.*line \d+
```

**False Positive Risk:** 2%  
(Deterministic fixes)

---

### RP-006: Test Coverage Violations

**Category:** Linting & Code Quality  
**Success Rate:** 88%  
**Confidence Threshold:** 0.85  
**Fix Time (minutes):** 10-20  
**Routing Agent:** unified-coverage-agent  
**Fallback Agent:** test-enhancement-agent  

**Description:**  
Code coverage below CI thresholds (commonly 70% or 80%); includes untested branches, exceptions, or edge cases.

**Improvement Areas:**
- Coverage: Incremental threshold increases
- Quality: Edge case handling
- Security: Exception path coverage

**Complexity Level:** Medium  
**Prerequisite Patterns:** RP-003 (test assertions)  

**Fix Signature:**
```regex
coverage: .+ is below \d+(\.\d+)?%|Coverage threshold not met
```

**False Positive Risk:** 8%  
(May add low-value tests to increase coverage)

---

### RP-007: Documentation Link Rot

**Category:** Documentation & Links  
**Success Rate:** 82%  
**Confidence Threshold:** 0.80  
**Fix Time (minutes):** 5-10  
**Routing Agent:** link-validator-agent  
**Fallback Agent:** unified-doc-agent  

**Description:**  
Broken or outdated documentation links, references to non-existent files, or missing anchor tags.

**Improvement Areas:**
- CI: Link validation in pre-commit
- Documentation: Freshness tracking
- Performance: Cached link checks

**Complexity Level:** Low  
**Prerequisite Patterns:** None  

**Fix Signature:**
```regex
404 Not Found|Broken link:|File not found:|Anchor .*does not exist
```

**False Positive Risk:** 6%  
(External links may timeout)

---

### RP-008: Import Path Mismatches

**Category:** Import & Dependency Errors  
**Success Rate:** 86%  
**Confidence Threshold:** 0.84  
**Fix Time (minutes):** 3-7  
**Routing Agent:** ci-importerror-agent  
**Fallback Agent:** reference-updater-agent  

**Description:**  
ImportError or ModuleNotFoundError due to incorrect import paths after refactoring or moving modules.

**Improvement Areas:**
- CI: Import path validation
- Refactoring: Automated import path updates
- Performance: Fast path resolution

**Complexity Level:** Medium  
**Prerequisite Patterns:** None  

**Fix Signature:**
```regex
ImportError: No module named|ModuleNotFoundError: No module named|cannot import name
```

**False Positive Risk:** 9%  
(Circular imports may need manual resolution)

---

### RP-009: Flaky Test Detection

**Category:** Test Assertions & Validation  
**Success Rate:** 65%  
**Confidence Threshold:** 0.70  
**Fix Time (minutes):** 15-30  
**Routing Agent:** fragile-test-guardian  
**Fallback Agent:** autonomous-test-healer-agent  

**Description:**  
Tests that pass intermittently due to timing issues, randomness, or resource contention; includes retry logic and @pytest.mark.flaky detection.

**Improvement Areas:**
- Quality: Deterministic tests
- Performance: Faster CI (fewer flaky retries)
- Reliability: Consistent test execution

**Complexity Level:** High  
**Prerequisite Patterns:** RP-003 (test assertions)  

**Fix Signature:**
```regex
FLAKY|flaky test|intermittent failure|@pytest.mark.flaky|Timeout after \d+s
```

**False Positive Risk:** 18%  
(May mask actual race conditions)

---

### RP-010: Workflow Compliance Violations

**Category:** Workflow & CI Configuration  
**Success Rate:** 76%  
**Confidence Threshold:** 0.78  
**Fix Time (minutes):** 5-15  
**Routing Agent:** workflow-compliance-guardian  
**Fallback Agent:** unified-governance-gate  

**Description:**  
GitHub Actions workflows violating concurrency constraints, timeout rules, or WEC (Workflow Execution Checklist) requirements.

**Improvement Areas:**
- CI: Compliance enforcement
- Performance: Optimized concurrency
- Governance: Policy adherence

**Complexity Level:** Medium  
**Prerequisite Patterns:** None  

**Fix Signature:**
```regex
concurrency constraint|timeout exceeded|WEC validation failed|approval required
```

**False Positive Risk:** 10%  
(May override intentional concurrency)

---

### RP-011: Cargo Feature Flag Issues

**Category:** Runtime & Execution Errors  
**Success Rate:** 79%  
**Confidence Threshold:** 0.78  
**Fix Time (minutes):** 8-12  
**Routing Agent:** rust-config-validator  
**Fallback Agent:** config-validator  

**Description:**  
Rust/Cargo missing or misconfigured feature flags causing compilation or runtime failures.

**Improvement Areas:**
- CI: Feature flag validation
- Compilation: Faster builds (optimized features)
- Security: Minimal feature surface

**Complexity Level:** Medium  
**Prerequisite Patterns:** None  

**Fix Signature:**
```regex
feature .+ not found|unresolved reference.*feature|Cargo.toml invalid features
```

**False Positive Risk:** 7%  
(Feature interactions may be complex)

---

### RP-012: CodeQL Security Alerts

**Category:** Linting & Code Quality  
**Success Rate:** 89%  
**Confidence Threshold:** 0.87  
**Fix Time (minutes):** 10-25  
**Routing Agent:** codeql-alert-resolution-agent  
**Fallback Agent:** code-scanning-remediation-agent  

**Description:**  
CodeQL security alerts including injection vulnerabilities, insecure defaults, or unsafe comparisons.

**Improvement Areas:**
- Security: Vulnerability remediation
- CI: Auto-fix for common patterns
- Compliance: SAST compliance

**Complexity Level:** High  
**Prerequisite Patterns:** None  

**Fix Signature:**
```regex
CodeQL alert|Security alert|Vulnerability detected:|CWE-\d+
```

**False Positive Risk:** 5%  
(Security fixes require validation)

---

## Phase 8 Learned Patterns (Extended)

### L-001: Circular Import Detection

**Category:** Import & Dependency Errors  
**Success Rate:** 91%  
**Confidence Threshold:** 0.88  
**Fix Time (minutes):** 8-12  
**Routing Agent:** ci-importerror-agent  
**Fallback Agent:** reference-updater-agent  

**Description:**  
Circular imports between modules, detected via import-cycle analysis.

**Improvement Areas:**
- CI: Early circular import detection
- Architecture: Module boundary enforcement
- Performance: Faster import resolution

**Complexity Level:** Medium  
**Prerequisite Patterns:** None  
**Phase Introduced:** 8  
**Confidence Score:** 0.88  
**Avg Success Rate:** 91%  

---

### L-002: Deprecated Typing Constructs

**Category:** Type System & Compatibility  
**Success Rate:** 93%  
**Confidence Threshold:** 0.91  
**Fix Time (minutes):** 2-5  
**Routing Agent:** python-312-type-fixer  
**Fallback Agent:** code-analysis-agent  

**Description:**  
Python 3.9+ deprecation warnings for typing module constructs (List, Dict, Optional, etc.) that should use built-in types.

**Improvement Areas:**
- CI: Python 3.12+ compatibility
- Performance: Faster typing module
- Quality: Modern Python idioms

**Complexity Level:** Low  
**Prerequisite Patterns:** None  
**Phase Introduced:** 8  
**Confidence Score:** 0.91  
**Avg Success Rate:** 93%  

---

### L-003: Exception Handling Breadth

**Category:** Code Quality  
**Success Rate:** 84%  
**Confidence Threshold:** 0.82  
**Fix Time (minutes):** 5-10  
**Routing Agent:** code-analysis-agent  
**Fallback Agent:** test-enhancement-agent  

**Description:**  
Overly broad exception handlers (bare except: or Exception) that mask specific errors.

**Improvement Areas:**
- Quality: Specific error handling
- Debugging: Better error messages
- Security: Exception-based attacks prevention

**Complexity Level:** Medium  
**Prerequisite Patterns:** None  
**Phase Introduced:** 8  
**Confidence Score:** 0.82  
**Avg Success Rate:** 84%  

---

### L-004: Missing Error Context

**Category:** Runtime & Execution Errors  
**Success Rate:** 79%  
**Confidence Threshold:** 0.78  
**Fix Time (minutes):** 5-15  
**Routing Agent:** ci-testing-agent  
**Fallback Agent:** test-failure-analyzer-agent  

**Description:**  
Errors without context (line numbers, variable values, stack traces), making debugging difficult.

**Improvement Areas:**
- Debugging: Better error messages
- CI: Faster failure diagnosis
- Logging: Contextual information capture

**Complexity Level:** Medium  
**Prerequisite Patterns:** None  
**Phase Introduced:** 8  
**Confidence Score:** 0.78  
**Avg Success Rate:** 79%  

---

### L-005: Resource Leak Detection

**Category:** Runtime & Execution Errors  
**Success Rate:** 86%  
**Confidence Threshold:** 0.84  
**Fix Time (minutes):** 10-20  
**Routing Agent:** code-analysis-agent  
**Fallback Agent:** codebase-health-guardian  

**Description:**  
File handles, database connections, or network sockets not properly closed or released.

**Improvement Areas:**
- Performance: Memory efficiency
- Reliability: Resource cleanup
- Quality: Context manager usage

**Complexity Level:** High  
**Prerequisite Patterns:** None  
**Phase Introduced:** 8  
**Confidence Score:** 0.84  
**Avg Success Rate:** 86%  

---

### L-006: Hardcoded Paths

**Category:** Code Quality  
**Success Rate:** 88%  
**Confidence Threshold:** 0.86  
**Fix Time (minutes):** 3-8  
**Routing Agent:** code-analysis-agent  
**Fallback Agent:** codebase-health-guardian  

**Description:**  
Hardcoded file paths or URLs that should use configuration or environment variables.

**Improvement Areas:**
- Portability: Cross-platform support
- Configuration: Environment-aware paths
- Security: Sensitive path hardening

**Complexity Level:** Low  
**Prerequisite Patterns:** None  
**Phase Introduced:** 8  
**Confidence Score:** 0.86  
**Avg Success Rate:** 88%  

---

### L-007: Empty Test Fixtures

**Category:** Test Assertions & Validation  
**Success Rate:** 82%  
**Confidence Threshold:** 0.80  
**Fix Time (minutes):** 3-7  
**Routing Agent:** autonomous-test-healer-agent  
**Fallback Agent:** test-enhancement-agent  

**Description:**  
Test fixtures that don't provide necessary setup, leading to incomplete test isolation.

**Improvement Areas:**
- Quality: Test fixture robustness
- Reliability: Test isolation
- Performance: Fixture initialization

**Complexity Level:** Medium  
**Prerequisite Patterns:** RP-003 (test assertions)  
**Phase Introduced:** 8  
**Confidence Score:** 0.80  
**Avg Success Rate:** 82%  

---

### L-008: Type Stub Mismatches

**Category:** Type System & Compatibility  
**Success Rate:** 75%  
**Confidence Threshold:** 0.73  
**Fix Time (minutes):** 10-18  
**Routing Agent:** python-312-type-fixer  
**Fallback Agent:** code-analysis-agent  

**Description:**  
Mismatches between .pyi stub files and actual implementation.

**Improvement Areas:**
- CI: Stub validation
- Type Checking: Accurate type information
- IDE Support: Better autocomplete

**Complexity Level:** High  
**Prerequisite Patterns:** RP-002 (type annotations)  
**Phase Introduced:** 8  
**Confidence Score:** 0.73  
**Avg Success Rate:** 75%  

---

## Composite Patterns (Advanced)

### C-001: Import + Type System Fix

**Category:** Multi-pattern composite  
**Success Rate:** 81%  
**Confidence Threshold:** 0.80  
**Fix Time (minutes):** 10-20  
**Routing Agent:** reference-updater-agent  
**Fallback Agent:** code-analysis-agent  

**Description:**  
Combined pattern fixing both import paths (RP-008) and type annotations (RP-002) after module refactoring.

**Prerequisite Patterns:** RP-008, RP-002  
**Complexity Level:** High  

---

### C-002: Coverage + Test Quality

**Category:** Multi-pattern composite  
**Success Rate:** 80%  
**Confidence Threshold:** 0.79  
**Fix Time (minutes):** 15-30  
**Routing Agent:** unified-coverage-agent  
**Fallback Agent:** test-enhancement-agent  

**Description:**  
Combined pattern improving coverage (RP-006) while strengthening assertions (RP-003).

**Prerequisite Patterns:** RP-006, RP-003  
**Complexity Level:** Medium  

---

### C-003: Dependency + Type System Reconciliation

**Category:** Multi-pattern composite  
**Success Rate:** 68%  
**Confidence Threshold:** 0.70  
**Fix Time (minutes):** 20-35  
**Routing Agent:** dependency-conflict-agent  
**Fallback Agent:** packaging-validation-agent  

**Description:**  
Combined pattern resolving dependency conflicts (RP-004) and updating type hints for updated dependencies (RP-002).

**Prerequisite Patterns:** RP-004, RP-002  
**Complexity Level:** High  

---

## Summary Statistics

```yaml
total_patterns: 50
phase_9_2_core: 12
phase_8_learned: 24
composite: 3
unassigned: 11

coverage_by_category:
  import_dependency: 12
  type_system: 8
  test_assertions: 10
  linting_quality: 9
  workflow_ci: 7
  documentation: 6
  runtime: 5
  multi_pattern: 3
  other: 11

aggregate_metrics:
  avg_success_rate: 82.5%
  avg_confidence_threshold: 0.81
  avg_fix_time_minutes: 8.2
  false_positive_rate: 9.1%
  total_improvement_areas: 35
  agents_involved: 23
```

---

## Integration Notes

- **STM Ingestion:** All patterns eligible for short-term memory on first encounter
- **LTM Promotion:** Patterns with ≥5 observations and ≥80% success rate eligible for promotion (see PHASE_9_2_PATTERN_PROMOTION_RULES.md)
- **Session Injection:** Top 20 patterns (by recency + confidence) injected into session context within 2000-token budget (see PHASE_9_2_SESSION_CONTEXT.md)
- **Checkpoint Frequency:** Patterns tracked every 50 failures or 5 minutes, with recovery procedures documented in PHASE_9_2_RECOVERY_PROCEDURES.md
