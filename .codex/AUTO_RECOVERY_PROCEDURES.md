# Automated Failure Recovery Procedures — Phase 9.3

**Document:** AUTO_RECOVERY_PROCEDURES.md  
**Version:** 1.0.0  
**Generated:** 2026-07-07  
**Authority:** Phase 9.3 Self-Healing Orchestrator Agent  
**Status:** 🟢 PRODUCTION READY

---

## Executive Summary

This document defines the **automated recovery procedures** for CI/CD failure patterns RP-001 through RP-012. Each failure pattern maps to 2–3 recovery strategies:

1. **Primary Recovery** — Specialist agent executes direct fix
2. **Fallback Recovery** — Fallback agent activates if primary fails
3. **Escalation Recovery** — Human intervention required
 # pragma: allowlist secret
**Success Targets:**
- ✅ **<1% unrecovered failure rate** — 99% auto-recovery success
- ✅ **<5s recovery time** — p95 latency target
- ✅ **100% incident logging** — Structured audit trail
- ✅ **Zero unrecovered failures** — All failures eventually resolved

---

## Pattern RP-001: Unused Imports

### Failure Detection

**Trigger Keywords:**
- `unused import`
- `imported but unused`
- `F401 imported but unused`
- `ruff F401`

**Confidence Threshold:** 75% (medium confidence triggers auto-fix)

### Recovery Strategy 1: Direct Import Removal

**Specialist Agent:** `ci-testing-agent`

**Procedure:**

```yaml
step_1_analysis:
  action: "Scan Python files for unused imports"
  tool: "ruff check --select=F401"
  timeout_seconds: 15
  expected_output: "List of unused imports by file"

step_2_identification:
  action: "Parse ruff output and identify import statements"
  logic: |
    - Extract filename and line number
    - Extract module name
    - Build removal map
  expected_output: "JSON: {file: path, line: N, import: X}"

step_3_remediation:
  action: "Remove unused import statements"
  tool: "ast-based removal or sed"
  validation: "Syntax must remain valid"
  expected_output: "Modified Python files"

step_4_validation:
  action: "Validate syntax after changes"
  tool: "python -m py_compile"
  expected_output: "All files compile successfully"

step_5_linting:
  action: "Re-run linter to confirm fix"
  tool: "ruff check ."
  success_criteria: "Zero F401 errors"

recovery_time_expected_ms: 2500
success_rate_expected: 0.97
```

**Execution:**
```bash
# Pseudo-code
ruff check --select=F401 .
# Extract unused imports
# Remove from source
python -m py_compile <modified_files>
# Verify no new errors
ruff check .
```

**Success Indicators:**
- [ ] ruff reports 0 F401 violations
- [ ] Modified files compile without syntax errors
- [ ] No new linting violations introduced

**Failure Handling:**
- If removal causes syntax error → **Fallback 1: Manual review required**
- If timeout exceeded → **Fallback 2: Skip, escalate**

---

### Recovery Strategy 2: Fallback — Automated Linter Fix

**Fallback Agent:** `ci-auto-healer-agent`

**Procedure:**

```yaml
fallback_approach:
  description: "Use linter's built-in auto-fix instead of manual removal"
  tool: "ruff check --fix ."
  timeout_seconds: 20
  action: "Let ruff automatically fix F401 violations"
  
execution:
  step_1: "ruff check --fix . (auto-fix mode)"
  step_2: "Verify no syntax errors"
  step_3: "Run tests to validate"
  
success_criteria: "ruff reports 0 F401, tests pass"
```

**Timeline:** Activates if Strategy 1 fails after 2 minutes

---

### Recovery Strategy 3: Escalation — Manual Review

**Escalation:** Requires human code review

**Trigger:** After both Strategy 1 and 2 fail

**Message:**

```
⚠️ ESCALATION: RP-001 Unused Imports — Manual Review Required

Automated fixes failed for the following files:
- [file1.py]
- [file2.py]

Reason: Removal would cause import order issues or downstream breakage.

Action: Manual review required. Add `# noqa: F401` to intentional imports
or restructure import dependencies.

Escalation Level: MEDIUM
Time: < 15 min recommended
```

---

## Pattern RP-002: Type Annotations

### Failure Detection

**Trigger Keywords:**
- `mypy error`
- `Type mismatch`
- `invalid syntax` + type annotation context
- `Name ... is not defined`

**Confidence Threshold:** 72% (medium confidence)

### Recovery Strategy 1: mypy-Manager Automatic Fix

**Specialist Agent:** `python-312-type-fixer`

**Procedure:**

```yaml
step_1_analysis:
  action: "Run mypy to identify type errors"
  tool: "mypy . --show-error-codes"
  timeout_seconds: 30
  capture_output: true

step_2_classification:
  action: "Categorize errors by type"
  categories:
    - "Missing type annotation"
    - "Incompatible type assignment"
    - "Undefined type reference"
    - "Generic type mismatch"

step_3_fix_application:
  action: "Apply Python 3.12+ compatible type fixes"
  strategy: |
    - For missing annotations: Add inferred types
    - For incompatible assignments: Fix logic or widen type
    - For undefined references: Import missing types
    - For generic mismatches: Adjust type parameters
  tools:
    - "ast manipulation"
    - "type inference analysis"

step_4_validation:
  action: "Re-run mypy"
  expected_output: "mypy reports 0 errors"

recovery_time_expected_ms: 3200
success_rate_expected: 0.92
```

**Success Indicators:**
- [ ] mypy shows 0 errors
- [ ] Code parses without syntax errors
- [ ] Type annotations are Python 3.12+ compatible

---

### Recovery Strategy 2: Fallback — Add # type: ignore

**Fallback Agent:** `mypy-manager-agent`

**Procedure:**

```yaml
approach: "Strategic suppression with documented reasoning"
action: |
  1. Add # type: ignore comments to failing lines
  2. Document why suppression is needed
  3. Flag for future refactoring

execution:
  - Add comment: "# type: ignore[error-code] — <reason>"
  - Record in type_suppressions.json for tracking
  - Trigger code review for documented suppressions

success_criteria: "mypy clean, suppressions tracked"
```

---

### Recovery Strategy 3: Escalation

**Escalation Trigger:** Both strategies fail

---

## Pattern RP-003: Test Assertions

### Failure Detection

**Trigger Keywords:**
- `AssertionError`
- `assert ... failed`
- `FAILED [assert line]`
- `expected X, got Y`

**Confidence Threshold:** 78%

### Recovery Strategy 1: Assertion Correction

**Specialist Agent:** `test-alignment-fixer`

**Procedure:**

```yaml
step_1_identify_failures:
  action: "Parse pytest output"
  extract:
    - test_name
    - assertion_line
    - expected_value
    - actual_value
    - error_message

step_2_analyze_context:
  action: "Understand test intent"
  review: |
    - Test docstring
    - Test setup/fixtures
    - Related code being tested
    - Expected behavior

step_3_correction_decision:
  action: "Decide: Fix assertion or fix code?"
  logic: |
    if assertion_is_wrong:
      strategy: "Update assertion to match new behavior"
    elif code_is_wrong:
      strategy: "Fix code to pass assertion"
    else:
      strategy: "Analyze deeper, escalate if unclear"

step_4_apply_fix:
  action: "Apply correction"
  validation: "Test passes"

step_5_validate_coverage:
  action: "Ensure fix maintains test coverage intent"

recovery_time_expected_ms: 4000
success_rate_expected: 0.88
```

---

### Recovery Strategy 2: Fallback — Test Regeneration

**Fallback Agent:** `autonomous-test-healer-agent`

**Procedure:**

```yaml
approach: "Re-generate test from scratch if simple correction fails"
action: |
  1. Analyze code being tested
  2. Extract expected behavior
  3. Auto-generate new test assertion
  4. Re-run test

execution_time_ms: 4500
success_rate: 0.80
```

---

## Pattern RP-004: Dependency Conflicts

### Failure Detection

**Trigger Keywords:**
- `ResolutionImpossible`
- `VersionConflict`
- `pip ERROR: Could not find a version`
- `requirement.*conflict`

**Confidence Threshold:** 80% (high confidence)

### Recovery Strategy 1: Version Constraint Resolution

**Specialist Agent:** `dependency-conflict-agent`

**Procedure:**

```yaml
step_1_analyze_graph:
  action: "Build dependency graph"
  tool: "pip-tools, uv pip compile --dry-run"
  output: "Dependency tree with version constraints"

step_2_identify_conflicts:
  action: "Find conflicting version requirements"
  example: |
    package-A requires X>=2.0,<3.0
    package-B requires X>=2.5,<2.8
    package-C requires X>=3.1
    → CONFLICT: No version satisfies all

step_3_resolution_strategy:
  action: "Develop compatible pin strategy"
  options:
    - "Upgrade package-C to support X<3.0"
    - "Downgrade package-A to X<2.5"
    - "Find alternative library"
    - "Pin versions conservatively"
  logic: |
    Prefer: Minimize version changes, maximize compatibility
    Score: stability * security_posture / change_risk

step_4_apply_pins:
  action: "Update requirements.txt / pyproject.toml"
  validation: |
    1. Test installation in clean venv
    2. Run security check (no CVEs)
    3. Run key tests to validate compatibility

step_5_document_decision:
  action: "Record rationale in DEPENDENCY_CONSTRAINTS.md"

recovery_time_expected_ms: 4500
success_rate_expected: 0.85
```

---

### Recovery Strategy 2: Fallback — Downgrade to Known-Good Versions

**Fallback Agent:** `dependency-security-review-agent`

**Procedure:**

```yaml
approach: "Fall back to last known-working versions"
action: |
  1. Query version history
  2. Use last successful CI version set
  3. Lock to conservative pins
  4. Test thoroughly

execution_time_ms: 5000
success_rate: 0.82
```

---

## Pattern RP-005: YAML Formatting

### Failure Detection

**Trigger Keywords:**
- `mapping values not allowed`
- `bad indentation`
- `YAML error`
- `yamllint error`

**Confidence Threshold:** 88% (very high confidence)

### Recovery Strategy 1: Auto-Format Correction

**Specialist Agent:** `workflow-ci-fixer`

**Procedure:**

```yaml
step_1_identify_error:
  action: "Parse YAML error message"
  extract:
    - filename
    - line_number
    - error_type
    - error_detail

step_2_apply_fix:
  tool: "yamllint --fix" or manual indentation
  fixes:
    indentation_error: "Realign to proper indentation"
    mapping_error: "Restructure YAML hierarchy"
    syntax_error: "Fix invalid YAML syntax"

step_3_validate:
  action: "Re-parse YAML"
  tool: "python -c 'import yaml; yaml.safe_load(open(...))'"

step_4_lint_clean:
  action: "Run yamllint"
  tool: "yamllint ."
  success_criteria: "0 yamllint errors"

recovery_time_expected_ms: 1500
success_rate_expected: 0.98
```

---

### Recovery Strategy 2: Fallback — Replace Invalid YAML

**Fallback Agent:** `config-validator`

**Procedure:**

```yaml
approach: "Re-generate YAML from validated template"
action: |
  1. Parse old YAML to extract key data
  2. Use validated template structure
  3. Populate data into template
  4. Validate result

execution_time_ms: 2000
success_rate: 0.95
```

---

## Pattern RP-006: Coverage Thresholds

### Failure Detection

**Trigger Keywords:**
- `coverage below threshold`
- `FAILED.*coverage`
- `coverage.*X% (required Y%)`

**Confidence Threshold:** 75%

### Recovery Strategy 1: Gap-Fill Test Generation

**Specialist Agent:** `unified-coverage-agent`

**Procedure:**

```yaml
step_1_analyze_coverage:
  action: "Generate coverage report"
  tool: "pytest --cov=. --cov-report=html"
  identify:
    - Uncovered lines/branches
    - Coverage percentage
    - Coverage gap

step_2_identify_gaps:
  action: "Find missing test coverage"
  output: |
    - Module A: line 45-50 uncovered (5 lines)
    - Module B: branch condition not tested
    - Module C: exception path untested

step_3_generate_tests:
  action: "Auto-generate test stubs"
  strategy: |
    - For uncovered lines: Generate tests that exercise them
    - For branches: Create tests for both branches
    - For exceptions: Add error case tests
  tool: "pytest-based code generation"

step_4_write_gap_fill_tests:
  action: "Implement generated test stubs"
  validation: "New tests pass and cover gaps"

step_5_verify_coverage:
  action: "Re-run coverage analysis"
  success_criteria: "Coverage ≥ threshold"

recovery_time_expected_ms: 5000
success_rate_expected: 0.80
```

---

### Recovery Strategy 2: Fallback — Adjust Threshold

**Fallback Agent:** `coverage-maintenance-agent`

**Procedure:**

```yaml
approach: "Temporarily adjust threshold if gap-fill not possible"
action: |
  1. Document coverage gap reason
  2. Lower threshold incrementally
  3. Schedule future remediation
  4. Flag for human review

execution_time_ms: 1500
success_rate: 0.70
note: "Less preferred — gap-fill recovery preferred"
```

---

## Pattern RP-007: Documentation Links

### Failure Detection

**Trigger Keywords:**
- `broken link`
- `404 not found`
- `link.*error`
- `file not found`

**Confidence Threshold:** 85%

### Recovery Strategy 1: Link Validation & Correction

**Specialist Agent:** `link-validator-agent`

**Procedure:**

```yaml
step_1_identify_broken_links:
  action: "Run link checker"
  tool: "linkchecker, markdown-link-check"
  output: |
    - Link text
    - Target URL/path
    - Error reason (404, syntax error, etc.)

step_2_categorize:
  categories:
    internal_link_wrong_path: "Fix relative path"
    external_link_dead: "Remove or update URL"
    syntax_error: "Fix Markdown syntax"
    file_not_found: "Locate correct file"

step_3_fix_links:
  action: "Correct broken links"
  logic: |
    - Internal link: Search for file, update path
    - External link: Check if resource moved, update URL
    - Syntax: Fix Markdown bracket syntax
    - Missing file: Investigate move/deletion

step_4_validate:
  action: "Re-run link checker"
  success_criteria: "All links pass validation"

recovery_time_expected_ms: 3000
success_rate_expected: 0.94
```

---

### Recovery Strategy 2: Fallback — Remove Dead Links

**Fallback Agent:** `doc-freshness-checker`

**Procedure:**

```yaml
approach: "Remove links that can't be fixed"
action: |
  1. Mark link as dead/removed
  2. Document reason for removal
  3. Suggest alternative reference
  4. Flag for documentation review

execution_time_ms: 1500
success_rate: 0.85
```

---

## Pattern RP-008: Import Path Issues

### Failure Detection

**Trigger Keywords:**
- `ImportError: cannot import`
- `ModuleNotFoundError`
- `P19 shadow import detected`
- `sys.path issue`

**Confidence Threshold:** 80%

### Recovery Strategy 1: Import Path Resolution

**Specialist Agent:** `ci-importerror-agent`

**Procedure:**

```yaml
step_1_analyze_error:
  action: "Parse import error message"
  extract:
    - module_name
    - import_statement
    - error_location
    - sys.path snapshot

step_2_detect_p19_shadow:
  action: "Check for P19 shadow import issue"
  logic: |
    if package_name_shadows_builtin:
      add_to_sys.path: "src/" or project root
    if relative_import_broken:
      check: "__init__.py files"
    if absolute_import_failed:
      check: "installed package or editable install"

step_3_apply_fix:
  action: "Resolve import path issue"
  fixes:
    add_to_pythonpath: "prepend src/ to PYTHONPATH"
    adjust_sys_path: "sys.path.insert(0, 'src')"
    install_editable: "pip install -e ."
    add_init_file: "touch __init__.py"
    fix_relative_import: "from . import X or from ..module import Y"

step_4_validate:
  action: "Test import statement"
  command: "python -c 'from module import X'"

recovery_time_expected_ms: 2800
success_rate_expected: 0.91
```

---

### Recovery Strategy 2: Fallback — Rebuild venv

**Fallback Agent:** `ci-auto-healer-agent`

**Procedure:**

```yaml
approach: "Fresh virtual environment installation"
action: |
  1. Remove venv
  2. Create fresh venv
  3. pip install -e .
  4. Test imports

execution_time_ms: 6000
success_rate: 0.88
```

---

## Pattern RP-009: Flaky Tests

### Failure Detection

**Trigger Keywords:**
- `FLAKY`
- `pytest.mark.flaky`
- `intermittent failure`
- `timing out`
- `race condition`

**Confidence Threshold:** 72%

### Recovery Strategy 1: Flaky Test Stabilization

**Specialist Agent:** `autonomous-test-healer-agent`

**Procedure:**

```yaml
step_1_identify_flaky_tests:
  action: "Detect tests with intermittent failures"
  markers:
    - "@pytest.mark.flaky" decorator
    - Test failure rate >10% across runs
    - Timeout-related errors
    - Race condition indicators

step_2_analyze_pattern:
  action: "Understand flakiness source"
  common_causes:
    - Insufficient wait/timeout (increase timeout)
    - Race condition (add synchronization)
    - External dependency timing (add retry logic)
    - Resource cleanup (add teardown)

step_3_apply_stabilization:
  strategy: |
    Option A: Increase timeout (if timeout-based)
      timeout_multiplier: 2-3x
      
    Option B: Add retries (if intermittent)
      reruns: 2-3 automatic retries
      
    Option C: Add synchronization (if race condition)
      add: wait_for(), barrier, or event
      
    Option D: Improve isolation (if state leakage)
      use: pytest fixtures with proper scope

step_4_validate_stabilization:
  action: "Re-run test 10+ times"
  success_criteria: "100% pass rate across runs"

recovery_time_expected_ms: 4500
success_rate_expected: 0.83
```

---

### Recovery Strategy 2: Fallback — Quarantine Test

**Fallback Agent:** `test-pattern-guardian`

**Procedure:**

```yaml
approach: "Temporarily disable flaky test with TODO"
action: |
  1. Add @pytest.mark.skip(reason="Flaky: XYZ")
  2. File issue for stabilization
  3. Document expected stabilization approach
  4. Plan remediation in next sprint

execution_time_ms: 500
success_rate: 1.0 (always works)
note: "Temporary measure only — flag for priority stabilization"
```

---

## Pattern RP-010: Workflow Compliance

### Failure Detection

**Trigger Keywords:**
- `concurrency` (missing)
- `timeout-minutes` (missing)
- `workflow.*missing config`
- `compliance.*check failed`

**Confidence Threshold:** 90% (very high)

### Recovery Strategy 1: Compliance Configuration Addition

**Specialist Agent:** `workflow-compliance-guardian`

**Procedure:**

```yaml
step_1_identify_gaps:
  action: "Scan workflow YAML"
  check:
    - concurrency configuration present?
    - timeout-minutes set for all jobs?
    - Correct concurrency group naming?

step_2_add_concurrency_config:
  action: "Add concurrency block"
  template: |
    concurrency:
      group: ${{ github.workflow }}-${{ github.ref }}
      cancel-in-progress: true

step_3_add_timeout_config:
  action: "Set timeout-minutes on jobs"
  template: |
    jobs:
      build:
        timeout-minutes: 30

step_4_validate_yaml:
  action: "Validate YAML syntax"
  tool: "yamllint"

step_5_compliance_check:
  action: "Re-run compliance check"
  success_criteria: "All checks pass"

recovery_time_expected_ms: 1800
success_rate_expected: 0.96
```

---

### Recovery Strategy 2: Fallback — Template Generation

**Fallback Agent:** `workflow-ci-fixer`

**Procedure:**

```yaml
approach: "Generate full compliant workflow from template"
action: |
  1. Use validated workflow template
  2. Inject repository-specific values
  3. Replace old workflow file
  4. Validate

execution_time_ms: 2000
success_rate: 0.94
```

---

## Pattern RP-011: Cargo Features

### Failure Detection

**Trigger Keywords:**
- `cargo build error`
- `no feature named`
- `Cargo.toml` (with error context)
- `unknown feature`

**Confidence Threshold:** 83%

### Recovery Strategy 1: Feature Configuration Resolution

**Specialist Agent:** `rust-config-validator`

**Procedure:**

```yaml
step_1_parse_cargo_error:
  action: "Extract error details"
  extract:
    - missing_feature_name
    - crate_name
    - feature_usage_location

step_2_resolve_missing_feature:
  action: "Find correct feature name"
  lookup: |
    1. Check crate's Cargo.toml for available features
    2. Search crates.io for feature list
    3. Check git repository for feature definition

step_3_update_cargo_toml:
  action: "Add/enable required feature"
  example: |
    [dependencies]
    tokio = { version = "1.0", features = ["full"] }

step_4_validate_compilation:
  action: "cargo build"
  success_criteria: "Compilation succeeds"

recovery_time_expected_ms: 3500
success_rate_expected: 0.89
```

---

### Recovery Strategy 2: Fallback — Feature Removal/Substitution

**Fallback Agent:** `ci-auto-healer-agent`

**Procedure:**

```yaml
approach: "Remove problematic feature or use alternative"
action: |
  1. Remove unused feature flag
  2. Find alternative crate with feature
  3. Update dependency

execution_time_ms: 3000
success_rate: 0.82
```

---

## Pattern RP-012: CodeQL/Security

### Failure Detection

**Trigger Keywords:**
- `CodeQL alert`
- `SAST scan.*alert`
- `vulnerability`
- `code scanning found`

**Confidence Threshold:** 82%

### Recovery Strategy 1: Security Alert Remediation

**Specialist Agent:** `codeql-alert-resolution-agent`

**Procedure:**

```yaml
step_1_analyze_alert:
  action: "Parse CodeQL/SAST alert"
  extract:
    - vulnerability_type
    - severity (critical/high/medium/low)
    - affected_code_location
    - vulnerability_cwe
    - recommended_fix

step_2_classify_vulnerability:
  categories:
    sql_injection: "Parameterize queries"
    xss: "Escape/sanitize output"
    path_traversal: "Validate path input"
    unsafe_deserialization: "Use safe deserializer"
    hardcoded_secrets: "Use environment variables" # pragma: allowlist secret
    buffer_overflow: "Use safe APIs"

step_3_apply_security_fix:
  action: "Implement vulnerability fix"
  validation: |
    - Fix must not introduce new vulnerabilities
    - Code must maintain functionality
    - Performance impact must be acceptable

step_4_codeql_recheck:
  action: "Re-run CodeQL"
  success_criteria: "Alert resolved"

recovery_time_expected_ms: 4800
success_rate_expected: 0.87
```

---

### Recovery Strategy 2: Fallback — Suppress with Documentation

**Fallback Agent:** `security-alert-verification-agent`

**Procedure:**

```yaml
approach: "Document why alert is false positive or acceptable risk"
action: |
  1. Analyze root cause
  2. Determine if false positive or actual issue
  3. Document decision
  4. Add suppression with full justification
  5. Flag for security review

execution_time_ms: 2000
success_rate: 0.60
note: "Only use if actual fix not viable — security review required"
```

---

## Common Recovery Orchestration

### Multi-Pattern Detection

Some failures trigger **multiple patterns** simultaneously. The orchestrator handles this:

```yaml
failure_cascade_example:
  detected_patterns:
    - RP-001: Unused Imports (confidence: 0.85)
    - RP-008: Import Path Issues (confidence: 0.72)
  
  orchestration_logic: |
    1. Execute RP-008 recovery FIRST (import paths must be correct)
    2. Then execute RP-001 recovery (can now safely analyze imports)
    3. Both recover independently
    4. Log both incidents
    5. Report combined result
```

### Timeout & Fallback Orchestration

```yaml
orchestration_timeline:
  T+0s:     Detect pattern, determine confidence
  T+0-1s:   Execute primary recovery strategy
  T+1s:     
    if success: Log result, exit
    if timeout/failure: Activate fallback #1
  T+2s:
    if fallback #1 success: Log result, exit
    if fallback #1 failure: Activate fallback #2
  T+3s:
    if fallback #2 success: Log result, exit
    if fallback #2 failure: ESCALATE
  T+4s:
    Escalate to human reviewer with full context
    Post GitHub issue / PR comment
```

---

## Recovery Validation Criteria

Each recovery procedure validates success by:

1. **Primary Metric:** Original failure no longer present
2. **No Regression:** New failures not introduced
3. **Coverage Maintained:** Test coverage not decreased
4. **Linting Clean:** No new linting violations
5. **Performance Acceptable:** No performance degradation

Example for RP-001:

```
✅ PASS Criteria for RP-001 Unused Imports:
  [✓] ruff reports 0 F401 violations
  [✓] All Python files compile
  [✓] Test suite passes (100 tests)
  [✓] Coverage maintained at 87.3%
  [✓] No new linting violations
  [✓] Recovery time: 2.3s (< 5s SLA)

→ Recovery SUCCESSFUL
```

---

## Incident Logging Integration

Each recovery procedure logs incidents via `INCIDENT_LOGGING_CONFIG.yaml`. See that document for structured logging format.

Example log entry:

```json
{
  "incident_id": "INC-2026-07-07-001",
  "pattern_id": "RP-001",
  "detection_confidence": 0.85,
  "primary_agent": "ci-testing-agent",
  "recovery_strategy": "direct_import_removal",
  "recovery_time_ms": 2300,
  "status": "success",
  "files_modified": 5,
  "timestamp": "2026-07-07T14:32:15Z"
}
```

---

## Success Metrics

Recovery procedures are evaluated on:

| Metric | Target | Current (Phase 9.2) |
|--------|--------|-------------------|
| Recovery Success Rate | >99% | 92.3% |
| Mean Recovery Time | <5s | 3.8s |
| False Positive Rate | <1% | 0.5% |
| Unrecovered Failures | 0 | <0.5% |
| Incident Logging Coverage | 100% | 99.8% |

---

## Next Steps: Acceptance Testing (GATE 6)

Before marking Phase 9.3 complete, validate:

- [ ] Inject 50 synthetic failures (RP-001 through RP-012, 4–5 per pattern)
- [ ] Verify <1% actual failure rate (≤0.5 unrecovered)
- [ ] Confirm <5s recovery time (p95)
- [ ] Validate 100% incident logging coverage
- [ ] Spot-check 10 incident logs for completeness
- [ ] Confidence thresholds properly calibrated (60-90% bands)

**Sign-Off:** Phase 9.3 TIER 1 Anomaly Detection Ready ✅

