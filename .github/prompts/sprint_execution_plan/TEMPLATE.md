# [Task ID]: [Task Title]

> **🤖 GITHUB COPILOT: This is an actionable task prompt. Begin implementation immediately.**
>
> **Template Version:** 2.0.0 (Autonomous Iteration)  
> **Last Updated:** 2025-12-06  
> **Status:** Ready for Copilot Execution  
> **Autonomy Level:** Self-Healing, Self-Troubleshooting, Self-Iterating

---

## 🎯 COPILOT INSTRUCTION: START HERE

**@workspace Execute this task using the following protocol:**

1. **READ** the entire prompt to understand context and requirements
2. **CHECK** prerequisites and generate sub-prompts if dependencies missing
3. **IMPLEMENT** each step sequentially with validation after each
4. **TEST** implementation continuously using provided commands
5. **SELF-CORRECT** if validation fails (up to 5 attempts)
6. **VERIFY** all acceptance criteria are met before marking complete

**Execution Mode:** Autonomous with human oversight  
**Expected Duration:** [effort_estimate from metadata]  
**Success Criteria:** All acceptance criteria checked ✅

---

## Metadata

```yaml
task_id: "[T1-T10 or GAP-XXX]"
priority: "[P0|P1|P2|P3]"
phase: "[1|2|3|4]"
phase_name: "[Foundation|Reproducibility|Autonomy|Excellence]"
effort_estimate: "[Small: 1-2 days | Medium: 3-5 days | Large: 1-2 weeks]"
sprint_week: "[Week 1-16]"
dependencies: 
  - "[Task IDs that must be completed first]"
  - "[None if no dependencies]"
blocks:
  - "[Task IDs that are blocked by this task]"
  - "[None if nothing blocked]"
capability_impact:
  - "[Capability domain(s) improved by this task]"
related_gaps:
  - "[Gap IDs from gap_backlog_prioritized.md]"
autonomous_features:
  - "Self-validation with automated tests"
  - "Self-diagnosis via error pattern matching"
  - "Self-correction through iterative refinement"
  - "Self-verification against acceptance criteria"
  - "Self-expansion: Generate prerequisite prompts when needed"
  - "Self-adaptation: Adjust approach based on current state"
iteration_protocol:
  max_attempts: 5
  validation_frequency: "After each implementation step"
  fallback_strategy: "Documented in Troubleshooting section"
  expansion_triggers:
    - "Missing prerequisite detected"
    - "Unexpected dependency discovered"
    - "Gap in current implementation requires foundational work"
  prompt_generation: "Automatic sub-prompt creation for blocking issues"
```

---

## Context

### Current State

**Problem Statement:**
[Describe the current state and the specific problem this task addresses. Reference audit findings.]

**Audit Evidence:**
- **Score:** [Current capability score if applicable, e.g., "safety-security: 0.61"]
- **Gap:** [Specific gap description from audit]
- **Impact:** [Why this gap matters for production autonomy]

**Files/Modules Affected:**
```
[List specific files/directories that need changes]
- path/to/file1.py
- path/to/file2.yaml
- path/to/config/
```

### Target State

**Desired Outcome:**
[Describe what success looks like after completing this task]

**Success Metrics:**
- [Quantifiable metric 1, e.g., "Test coverage ≥70%"]
- [Quantifiable metric 2, e.g., "Security score improved to 0.75+"]
- [Quantifiable metric 3, e.g., "Zero P0/P1 vulnerabilities"]

**Capability Improvement:**
[Expected capability score improvement, e.g., "safety-security: 0.61 → 0.75"]

---

## Prerequisites

**Required Before Starting:**
- [ ] [Dependency 1 completed, e.g., "T1 coverage gate implemented"]
- [ ] [Dependency 2 available, e.g., "Development environment configured"]
- [ ] [Access/permission requirements, e.g., "CI/CD pipeline access"]

**Knowledge Requirements:**
- [Required expertise, e.g., "Familiarity with pytest and coverage.py"]
- [Domain knowledge, e.g., "Understanding of ML training loops"]

**Tools Required:**
- [Tool 1, e.g., "pytest-cov installed"]
- [Tool 2, e.g., "Access to GitHub Actions"]

---

## Implementation Guide

### Step 1: [First Major Step]

**Objective:** [What this step achieves]

**Actions:**
1. [Specific action with file path and line numbers if available]
   ```python
   # Example code snippet or modification
   ```

2. [Next action]
   ```bash
   # Example command
   ```

**Validation:**
```bash
# Command to verify this step worked
```

**Expected Output:**
```
[What success looks like for this step]
```

### Step 2: [Second Major Step]

**Objective:** [What this step achieves]

**Actions:**
1. [Specific action]
2. [Next action]

**Validation:**
```bash
# Verification command
```

### Step 3: [Subsequent Steps...]

[Continue with additional steps as needed]

---

## Testing Requirements

### Unit Tests

**Test Cases Required:**
1. **Test Name:** `test_[feature]_[scenario]`
   - **Purpose:** [What this test validates]
   - **Location:** `tests/[module]/test_[feature].py`
   - **Assertions:**
     ```python
     # Example test structure
     def test_feature_scenario():
         # Arrange
         # Act
         # Assert
     ```

2. [Additional test cases...]

### Integration Tests

**Test Cases Required:**
1. [Integration test description]
2. [Additional integration tests...]

### Validation Commands

```bash
# Run tests for this feature
pytest tests/[module]/ -v -k "[feature]"

# Check coverage for modified files
pytest --cov=src/[module] --cov-report=term-missing

# Run specific validation
[custom validation command]
```

**Expected Coverage:**
- Minimum: 80% line coverage for new/modified code
- Target: 90%+ line coverage

---

## Acceptance Criteria

**Definition of Done:**
- [ ] All implementation steps completed
- [ ] All tests passing (unit + integration)
- [ ] Code coverage meets minimum threshold (≥80%)
- [ ] Documentation updated (docstrings, README, etc.)
- [ ] Pre-commit hooks pass (linting, formatting, type checking)
- [ ] CI pipeline passes all checks
- [ ] Capability score improved (if measurable)
- [ ] No new security vulnerabilities introduced
- [ ] Manual validation completed (see verification section)
- [ ] Code reviewed (if working in team)

**Verification Checklist:**
- [ ] **Functional:** Feature works as intended
- [ ] **Performance:** No significant performance regression
- [ ] **Security:** Security checks pass (bandit, semgrep, etc.)
- [ ] **Documentation:** Changes documented
- [ ] **Tests:** Comprehensive test coverage
- [ ] **Backward Compatibility:** No breaking changes

---

## Validation & Verification

### Automated Validation

```bash
# 1. Run test suite
pytest tests/[module]/ -v --cov=src/[module]

# 2. Run linters
pre-commit run --files [modified files]

# 3. Run security scans
bandit -r src/[module]/

# 4. Validate configuration
[validation script if applicable]
```

### Manual Validation

**Steps:**
1. [Manual verification step 1]
   - **Action:** [What to do]
   - **Expected:** [What should happen]

2. [Manual verification step 2]
3. [Additional manual checks...]

### Regression Testing

```bash
# Ensure existing functionality still works
pytest tests/ -m "not slow" --maxfail=1

# Run smoke tests
[smoke test command]
```

---

## Rollback Plan

**If Implementation Fails:**

1. **Revert Changes:**
   ```bash
   git revert [commit-hash]
   # or
   git checkout [branch] -- [files to revert]
   ```

2. **Restore Previous State:**
   - [Specific restoration steps]
   - [Configuration rollback if needed]

3. **Verify Stability:**
   ```bash
   [commands to verify system is stable]
   ```

**Mitigation Strategies:**
- [Strategy 1 to minimize impact]
- [Strategy 2 for recovery]

---

## 🤖 Autonomous Iteration Protocol

### Prompt Expansion System

**Automatic Prerequisite Detection:**
```python
def detect_prerequisites(task):
    """
    Scan task requirements and detect missing prerequisites.
    
    Generates new prompts automatically when:
    - Required files/modules don't exist
    - Dependency tasks incomplete
    - Configuration missing
    - Infrastructure not ready
    """
    missing_prerequisites = []
    
    # Check file existence
    for required_file in task.required_files:
        if not os.path.exists(required_file):
            missing_prerequisites.append({
                'type': 'missing_file',
                'file': required_file,
                'action': 'Create prerequisite file',
                'generate_prompt': True
            })
    
    # Check module imports
    for required_module in task.required_modules:
        try:
            __import__(required_module)
        except ImportError:
            missing_prerequisites.append({
                'type': 'missing_module',
                'module': required_module,
                'action': 'Install or implement module',
                'generate_prompt': True
            })
    
    # Check dependency tasks
    for dep_task_id in task.dependencies:
        if not is_task_complete(dep_task_id):
            missing_prerequisites.append({
                'type': 'incomplete_dependency',
                'task_id': dep_task_id,
                'action': 'Complete dependency task first',
                'generate_prompt': True
            })
    
    return missing_prerequisites
```

**Prompt Generation Template:**
```python
def generate_prerequisite_prompt(prerequisite):
    """
    Auto-generate a new prompt for addressing prerequisites.
    
    Creates a focused sub-prompt that:
    - Addresses the specific blocking issue
    - Follows the same template structure
    - Links back to parent task
    - Has clear acceptance criteria
    """
    if prerequisite['type'] == 'missing_file':
        return f"""
# [SUB-TASK]: Create {prerequisite['file']}

> **Parent Task:** [{parent_task_id}]
> **Type:** Prerequisite - Missing File
> **Priority:** Blocking
> **Auto-Generated:** Yes

## Context
This file is required by task {parent_task_id} but does not currently exist.

### Target State
- ✅ File {prerequisite['file']} exists
- ✅ File has valid structure/syntax
- ✅ File is importable (if Python)
- ✅ Parent task can proceed

## Implementation Guide

### Step 1: Create File Structure
```bash
touch {prerequisite['file']}
# or
mkdir -p $(dirname {prerequisite['file']})
touch {prerequisite['file']}
```

### Step 2: Add Minimal Valid Content
[Based on file type and context...]

### Step 3: Validate
```bash
# Syntax check
python -m py_compile {prerequisite['file']}

# Import check (if Python module)
python -c "import {module_name}"
```

## Acceptance Criteria
- [ ] File exists at expected path
- [ ] File has valid syntax
- [ ] Parent task prerequisites now satisfied

## Return to Parent
Once complete, resume: {parent_task_id}
"""
    
    elif prerequisite['type'] == 'missing_module':
        return generate_module_installation_prompt(prerequisite)
    
    elif prerequisite['type'] == 'incomplete_dependency':
        return generate_dependency_completion_prompt(prerequisite)
```

**Expansion Decision Tree:**
```
Start Task Implementation
│
├─> Check Prerequisites
│   ├─> All satisfied? → Proceed with main task
│   └─> Prerequisites missing?
│       │
│       ├─> Generate Sub-Prompts
│       │   ├─> Missing files → Create file prompts
│       │   ├─> Missing modules → Install/implement prompts
│       │   ├─> Incomplete deps → Link to dependency prompts
│       │   └─> Config missing → Configuration prompts
│       │
│       ├─> Execute Sub-Prompts First
│       │   ├─> Complete sub-prompt 1
│       │   ├─> Validate completion
│       │   ├─> Complete sub-prompt 2
│       │   └─> Return to main task
│       │
│       └─> Re-validate Prerequisites → Proceed or Generate More
```

**Adaptive Prompt Expansion Examples:**

1. **Missing Test Infrastructure:**
```yaml
detected: "pytest.ini not found"
generates_prompt:
  title: "Create pytest.ini Configuration"
  priority: "Blocking"
  content: |
    # Sub-Task: Create pytest.ini
    
    ## Context
    Parent task T1 requires pytest configuration but pytest.ini doesn't exist.
    
    ## Implementation
    1. Create pytest.ini in repository root
    2. Add basic configuration:
       ```ini
       [pytest]
       testpaths = tests
       python_files = test_*.py
       python_classes = Test*
       python_functions = test_*
       ```
    3. Validate: `pytest --co -q`
    
    ## Return to Parent
    Resume T1: Coverage Gate Enforcement
```

2. **Missing Dependency:**
```yaml
detected: "ModuleNotFoundError: No module named 'pytest_cov'"
generates_prompt:
  title: "Install pytest-cov Plugin"
  priority: "Blocking"
  content: |
    # Sub-Task: Install pytest-cov
    
    ## Context
    Coverage enforcement requires pytest-cov plugin.
    
    ## Implementation
    1. Add to requirements: `pip install pytest-cov>=4.0`
    2. Or add to pyproject.toml:
       ```toml
       [project.optional-dependencies]
       test = ["pytest-cov>=4.0"]
       ```
    3. Validate: `python -c "import pytest_cov"`
    
    ## Return to Parent
    Resume T1: Coverage Gate Enforcement
```

3. **Infrastructure Not Ready:**
```yaml
detected: "noxfile.py exists but no 'tests' session defined"
generates_prompt:
  title: "Create Nox Tests Session"
  priority: "Blocking"
  content: |
    # Sub-Task: Create Nox Tests Session
    
    ## Context
    T1 needs to modify nox tests session, but it doesn't exist yet.
    
    ## Implementation
    1. Add basic tests session to noxfile.py:
       ```python
       @nox.session
       def tests(session):
           session.install("-e", ".[dev]")
           session.run("pytest", *session.posargs)
       ```
    2. Validate: `nox -s tests --list`
    
    ## Return to Parent
    Resume T1: Coverage Gate Enforcement - Step 3
```

### Expansion Guidelines

**When to Generate Sub-Prompts:**
- ✅ **Missing file/directory** that's not trivial to create inline
- ✅ **Complex prerequisite** requiring multiple steps
- ✅ **Dependency task** not yet completed (link to existing prompt)
- ✅ **Configuration setup** needed before proceeding
- ✅ **Infrastructure component** missing (CI/CD, tools)

**When NOT to Generate Sub-Prompts:**
- ❌ **Trivial file creation** (empty file, simple template)
- ❌ **Single-line changes** (add import, update variable)
- ❌ **Standard library imports** (no installation needed)
- ❌ **Simple configuration** (one or two settings)

**Expansion Workflow:**
```bash
# Autonomous execution with expansion
execute_task_with_expansion() {
    task_id=$1
    
    echo "📋 Starting task: $task_id"
    
    # Check prerequisites
    prereqs=$(detect_prerequisites "$task_id")
    
    if [ -n "$prereqs" ]; then
        echo "⚠️ Prerequisites missing: $prereqs"
        echo "🔄 Generating sub-prompts..."
        
        # Generate and execute sub-prompts
        for prereq in $prereqs; do
            sub_prompt=$(generate_prerequisite_prompt "$prereq")
            echo "$sub_prompt" > ".codex/sub_prompts/${task_id}_prereq_${prereq}.md"
            
            echo "🎯 Executing sub-prompt: ${prereq}"
            execute_prompt "${task_id}_prereq_${prereq}"
            
            # Validate sub-prompt completion
            if ! validate_prerequisite "$prereq"; then
                echo "❌ Sub-prompt failed: ${prereq}"
                return 1
            fi
        done
        
        echo "✅ All prerequisites satisfied"
    fi
    
    # Execute main task
    echo "🚀 Proceeding with main task"
    execute_main_task "$task_id"
}
```

### Self-Adaptation Mechanisms

**Context-Aware Adjustments:**
```python
def adapt_implementation_strategy(task, current_state):
    """
    Adjust implementation approach based on discovered context.
    
    Adaptations:
    - Different file exists → Modify instead of create
    - Alternative tool available → Use instead of installing
    - Existing pattern found → Follow instead of introducing new
    - Tests already exist → Extend instead of creating
    """
    adaptations = []
    
    # Check if alternative files exist
    if task.requires_file("pytest.ini"):
        if os.path.exists("pyproject.toml"):
            adaptations.append({
                'type': 'alternative_config',
                'action': 'Use pyproject.toml instead of creating pytest.ini',
                'rationale': 'pyproject.toml already exists, prefer single config'
            })
    
    # Check for existing patterns
    if task.requires_pattern("coverage_config"):
        existing_patterns = scan_for_patterns(["pytest.ini", "setup.cfg", "pyproject.toml"])
        if existing_patterns:
            adaptations.append({
                'type': 'follow_existing_pattern',
                'action': f'Use {existing_patterns[0]} format',
                'rationale': 'Match existing repository conventions'
            })
    
    # Check for alternative tools
    if task.requires_tool("pytest-cov"):
        if is_tool_available("coverage.py"):
            adaptations.append({
                'type': 'use_alternative_tool',
                'action': 'Use coverage.py directly instead of pytest-cov',
                'rationale': 'coverage.py already installed'
            })
    
    return adaptations
```

**Adaptive Prompt Updates:**
```python
def update_prompt_with_adaptations(prompt, adaptations):
    """
    Dynamically update prompt based on discovered context.
    
    Inserts adaptation notes before each affected step.
    """
    updated_prompt = prompt
    
    for adaptation in adaptations:
        section = find_affected_section(prompt, adaptation['type'])
        
        adaptation_note = f"""
### 🔄 ADAPTATION DETECTED

**Context:** {adaptation['rationale']}

**Adjusted Approach:**
{adaptation['action']}

**Original Plan:**
{section['original_content']}

**Proceed with adapted approach below:**
"""
        
        updated_prompt = insert_before_section(
            updated_prompt, 
            section['id'], 
            adaptation_note
        )
    
    return updated_prompt
```

**Example Adaptation Flow:**
```
Task: Create pytest.ini
│
├─> Scan repository
│   └─> pyproject.toml exists ✓
│
├─> Adapt strategy
│   ├─> Original: Create new pytest.ini
│   └─> Adapted: Add [tool.pytest.ini_options] to pyproject.toml
│
├─> Update prompt
│   └─> Insert adaptation note with rationale
│
└─> Execute adapted approach
    └─> Success: Follows repository conventions
```

### Self-Validation Loop

**Automatic Validation After Each Step:**
```python
# Pseudo-code for autonomous validation
def validate_implementation(step_number):
    """Auto-validate implementation progress."""
    results = {
        'tests_pass': run_tests(),
        'lints_clean': run_linters(),
        'coverage_met': check_coverage_threshold(),
        'security_clear': run_security_scans(),
        'acceptance_criteria': check_acceptance_criteria(step_number)
    }
    
    if all(results.values()):
        return "✅ PASS: Proceed to next step"
    else:
        failed_checks = [k for k, v in results.items() if not v]
        return f"❌ FAIL: {failed_checks} - Enter self-correction loop"
```

**Validation Commands per Step:**
```bash
# Run automatically after each implementation step
validate_step() {
    echo "🔍 Validating implementation..."
    
    # 1. Syntax check
    python -m py_compile [modified_files] || return 1
    
    # 2. Import check
    python -c "import [module]" || return 1
    
    # 3. Test check
    pytest tests/[relevant]/ -v --tb=short || return 1
    
    # 4. Lint check
    ruff check [modified_files] || return 1
    
    # 5. Coverage check (if applicable)
    pytest --cov=[module] --cov-fail-under=[threshold] || return 1
    
    echo "✅ Step validation PASSED"
    return 0
}
```

### Self-Diagnosis System

**Error Pattern Matching:**
```yaml
common_errors:
  - pattern: "ModuleNotFoundError: No module named '(.*)'"
    diagnosis: "Missing dependency"
    auto_fix: "pip install {module} or add to requirements.txt"
    
  - pattern: "SyntaxError: invalid syntax"
    diagnosis: "Python syntax error"
    auto_fix: "Review code for syntax issues, check indentation and brackets"
    
  - pattern: "ImportError: cannot import name '(.*)' from '(.*)'"
    diagnosis: "Import path incorrect or circular import"
    auto_fix: "Check import statement and module structure"
    
  - pattern: "AssertionError in test_(.*)"
    diagnosis: "Test expectation not met"
    auto_fix: "Review test assertion and implementation logic"
    
  - pattern: "FAILED.*coverage.*below"
    diagnosis: "Coverage threshold not met"
    auto_fix: "Add tests for uncovered code paths"
    
  - pattern: "NameError: name '(.*)' is not defined"
    diagnosis: "Variable or function not defined"
    auto_fix: "Define {name} or import it from appropriate module"
    
  - pattern: "TypeError: (.*) takes (.*) positional argument"
    diagnosis: "Function signature mismatch"
    auto_fix: "Check function arguments and calling code"
```

**Diagnostic Decision Tree:**
```
Error Detected
├─> Run diagnostic analysis
│   ├─> Match against known error patterns
│   ├─> Extract error context (file, line, traceback)
│   └─> Generate fix suggestions
│
├─> Attempt auto-fix (if safe)
│   ├─> Apply fix
│   ├─> Re-run validation
│   └─> If pass → Continue | If fail → Escalate
│
└─> Document issue for manual review (if unsafe)
    ├─> Create detailed error report
    ├─> Suggest alternative approaches
    └─> Mark for human intervention
```

### Self-Correction Mechanism

**Iterative Refinement Loop:**
```python
def autonomous_implementation(task):
    """
    Autonomous task implementation with self-correction.
    
    Max iterations: 5
    Validation frequency: After each step
    Fallback: Documented troubleshooting guide
    """
    max_iterations = 5
    current_iteration = 0
    
    while current_iteration < max_iterations:
        current_iteration += 1
        print(f"🔄 Iteration {current_iteration}/{max_iterations}")
        
        # Step 1: Implement current step
        implementation_result = implement_step(task.current_step)
        
        # Step 2: Validate implementation
        validation_result = validate_implementation(task.current_step)
        
        if validation_result.passed:
            print(f"✅ Step {task.current_step} passed")
            task.advance_to_next_step()
            current_iteration = 0  # Reset for next step
            
            if task.is_complete():
                return SUCCESS
        else:
            # Self-correction attempt
            print(f"⚠️ Validation failed: {validation_result.errors}")
            
            # Diagnose issues
            diagnosis = diagnose_errors(validation_result.errors)
            
            # Attempt auto-fix
            if diagnosis.auto_fixable:
                print(f"🔧 Applying auto-fix: {diagnosis.fix_strategy}")
                apply_fix(diagnosis.fix_strategy)
            else:
                print(f"❌ Manual intervention required")
                return NEEDS_HUMAN_REVIEW
    
    # Max iterations reached
    return NEEDS_ESCALATION
```

**Auto-Fix Strategies:**

1. **Missing Dependencies:**
   ```bash
   # Detect and install missing packages
   python -c "import [module]" 2>&1 | grep "No module named" | \
   sed "s/.*'\(.*\)'.*/\1/" | xargs pip install
   ```

2. **Test Failures:**
   ```bash
   # Re-run failed tests with verbose output
   pytest --lf -vv --tb=long  # --lf = last failed
   
   # Generate coverage report to identify gaps
   pytest --cov=[module] --cov-report=html
   open htmlcov/index.html  # Review uncovered lines
   ```

3. **Linting Issues:**
   ```bash
   # Auto-fix safe linting issues
   ruff check --fix [files]
   black [files]
   isort [files]
   ```

4. **Import Errors:**
   ```python
   # Auto-detect circular imports
   python -X importtime [script] 2>&1 | grep "import time"
   
   # Suggest restructuring
   # Move shared code to separate module
   ```

### Troubleshooting Decision Matrix

| Issue Type | Auto-Fix Available? | Action | Escalation Threshold |
|------------|---------------------|--------|---------------------|
| Syntax Error | ❌ | Show error location | Immediate |
| Import Error | ⚠️ Partial | Try install, check paths | After 2 attempts |
| Test Failure | ⚠️ Partial | Re-run, check assertions | After 3 attempts |
| Coverage < Threshold | ✅ | Generate coverage report | After 2 attempts |
| Linting Error | ✅ | Auto-format | After auto-fix fails |
| Type Error | ❌ | Show type hints | After 1 attempt |
| Dependency Conflict | ⚠️ Partial | Show conflict tree | Immediate |
| Configuration Error | ⚠️ Partial | Validate schema | After 1 attempt |

### Continuous Improvement Logging

**Track iteration metrics:**
```yaml
iteration_log:
  task_id: "[Task ID]"
  start_time: "2025-12-06T05:00:00Z"
  iterations:
    - iteration: 1
      step: "Step 1: Update pytest config"
      action: "Added coverage flags"
      validation: "✅ PASS"
      duration: "5 minutes"
      
    - iteration: 2
      step: "Step 2: Create fixture"
      action: "Added deterministic seed fixture"
      validation: "❌ FAIL: Import error"
      diagnosis: "torch not imported"
      auto_fix: "Added import torch"
      retry_validation: "✅ PASS"
      duration: "8 minutes"
      
  total_iterations: 2
  success_rate: "100%"
  total_time: "13 minutes"
  human_interventions: 0
```

**Improvement feedback loop:**
```python
def log_iteration_result(task_id, iteration_data):
    """
    Log iteration results for continuous improvement.
    
    Metrics tracked:
    - Success rate per step
    - Common error patterns
    - Auto-fix effectiveness
    - Time per iteration
    - Escalation frequency
    """
    append_to_log(f".codex/iterations/{task_id}.jsonl", iteration_data)
    
    # Analyze patterns
    if iteration_data.errors:
        update_error_patterns(iteration_data.errors)
    
    if iteration_data.auto_fix_applied:
        track_fix_effectiveness(iteration_data.auto_fix, iteration_data.success)
```

---

## Related Audit Artifacts

**Primary References:**
- **Task Definition:** `reports/_codex_task_sequences-20251206.md` (lines X-Y)
- **Gap Analysis:** `workbench/exhaustive_audit/gap_backlog_prioritized.md` (Gap ID: [ID])
- **Current State:** `workbench/exhaustive_audit/detailed_gaps_by_capability.md` ([Capability] section)
- **Capability Score:** `audit_artifacts/capabilities_scored.json` ([capability].score)

**Supporting References:**
- **Remediation Guidance:** `workbench/exhaustive_audit/remediation_diffs.md` (Task [ID])
- **Checklist:** `workbench/exhaustive_audit/[relevant]_checklist.md`
- **Executive Summary:** `reports/_codex_status_update-(2025-12-06).md`
- **Phase Overview:** `.github/prompts/sprint_execution_plan/phase_[N]_[name]/_PHASE_OVERVIEW.md`

**Audit Context:**
- **Repository Size:** 7,152 files analyzed
- **Python LOC:** 262,544 lines
- **Total Gaps:** 45 prioritized tasks
- **Current Maturity:** Level 2-3 → Target: Level 4

---

## GitHub Copilot Usage Tips

### For Copilot Chat

```
@workspace I need to implement task [ID]: [Title]

Context:
- Review the implementation guide in this file
- Focus on files: [list key files]
- Ensure tests meet 80% coverage threshold

Please help me:
1. [Specific request 1]
2. [Specific request 2]
```

### For Copilot Workspace

1. Open this prompt file as reference
2. Use multi-file edit mode for changes across multiple files
3. Run validation commands in integrated terminal
4. Check acceptance criteria before marking complete

### For Copilot CLI

```bash
# Ask Copilot to generate implementation
gh copilot suggest "Implement [task description from this file]"

# Ask for test generation
gh copilot suggest "Generate pytest tests for [feature]"

# Ask for validation
gh copilot suggest "How to validate [acceptance criteria]"
```

---

## Progress Tracking

**Status:** `[ ] Not Started | [ ] In Progress | [ ] Testing | [ ] Complete`

**Time Tracking:**
- **Estimated:** [X days]
- **Actual:** [Y days]
- **Started:** [YYYY-MM-DD]
- **Completed:** [YYYY-MM-DD]

**Notes:**
- [Implementation notes]
- [Blockers encountered]
- [Lessons learned]

---

## Additional Resources

**Documentation:**
- [Link to relevant docs]
- [Link to examples]

**Examples:**
- [Link to similar implementations]
- [Reference code]

**Community:**
- [Relevant issue/PR links]
- [Discussion threads]

---

*Template based on audit findings from comprehensive codebase analysis (2025-12-06)*
*For questions or issues, consult: `reports/_operations_runbook-20251206.md`*
