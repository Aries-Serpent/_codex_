# Autonomous Self-Review Protocol for AI Assistants

## 🎯 Executive Summary

The Autonomous Self-Review Protocol ensures AI assistants perform comprehensive self-review before concluding any interaction. It implements a deterministic, iterative process that prevents premature completion and ensures all concerns are addressed through autonomous self-healing cycles.

## 🧠 Core Concepts

### The Problem

AI assistants often complete tasks without thorough validation, leading to:
- Incomplete implementations
- Unaddressed edge cases
- Missing tests or documentation
- Undiscovered risks
- Premature convergence

### The Solution

A structured, multi-phase protocol that:
1. Generates initial solutions as **DRAFT**
2. Runs iterative self-review cycles
3. Identifies gaps, risks, and incompleteness
4. Applies fixes autonomously
5. Validates convergence before completion
6. Ensures production readiness

## 📊 Protocol Structure

### Phase 1: Initial Response Generation

```
Stage: DRAFT
Actions:
  - Generate initial solution/response
  - Mark as DRAFT-1
  - Trigger self-review cycle
```

### Phase 2: Iterative Self-Review Cycle

```
Stage: IN_REVIEW → FIXING → VALIDATING
Iterations: Until stable
Actions:
  - Scan for gaps
  - Identify risks
  - Apply fixes
  - Generate status report
  - Check termination criteria
```

### Phase 3: Convergence Validation

```
Stage: STABLE → COMPLETE
Criteria:
  - No high-priority gaps remain
  - All risks mitigated or documented
  - Production readiness achieved
  - Self-healing cycle stable (≥90% convergence)
  - Minimum 2 cycles completed
```

## 🔧 Implementation

### Core Module: `ai_self_review_protocol.py`

Provides the foundational protocol implementation:

```python
from scripts.ai_self_review_protocol import SelfReviewProtocol, Priority, IssueType

# Initialize protocol
protocol = SelfReviewProtocol("Implement feature X")

# Cycle 1: Identify issues
cycle1 = protocol.start_cycle()
protocol.identify_issue(
    IssueType.MISSING_TEST,
    Priority.HIGH,
    "Core functionality lacks unit tests",
    "src/module.py"
)
protocol.complete_cycle(["Identified issues"])

# Cycle 2: Fix and validate
cycle2 = protocol.start_cycle()
protocol.fix_issue(issue_id, "Added comprehensive tests")
protocol.validate_fix(issue_id, "Tests passing")
protocol.complete_cycle(["Fixed high-priority issues"])

# Check convergence
converged, reason = protocol.check_convergence()

# Finalize
protocol.finalize_review("All criteria met")
protocol.save_report()
protocol.print_summary()
```

### Practical Tool: `code_change_reviewer.py`

Applies protocol to code changes:

```bash
# Review changed files
python scripts/code_change_reviewer.py --repo /path/to/repo

# With custom task description
python scripts/code_change_reviewer.py --task "Feature implementation" --save-report

# Output to specific directory
python scripts/code_change_reviewer.py --output /path/to/reports --save-report
```

## 📋 Issue Types

| Type | Description | Example |
|------|-------------|---------|
| **GAP** | Missing functionality | Feature not fully implemented |
| **RISK** | Potential problem | Security vulnerability, race condition |
| **INCOMPLETE** | Partial implementation | TODO comments, stub methods |
| **OPTIMIZATION** | Performance/quality improvement | Inefficient algorithm, code smell |
| **VALIDATION** | Testing/verification needed | No assertions, missing edge cases |
| **INCONSISTENCY** | Contradictory elements | Naming mismatch, style violation |
| **MISSING_TEST** | Test coverage gap | Critical path untested |
| **MISSING_DOC** | Documentation gap | Missing docstrings, README |

## ⚡ Priority Levels

| Priority | Meaning | Action Required |
|----------|---------|-----------------|
| **CRITICAL** | Must fix immediately | Block completion until resolved |
| **HIGH** | Should fix in this session | Address before finalizing |
| **MEDIUM** | Can defer with documentation | Document mitigation strategy |
| **LOW** | Nice to have | Optional improvement |

## 🔄 Review Cycle Flow

```
┌─────────────────┐
│  Start Cycle    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Identify Issues │◄─────┐
└────────┬────────┘      │
         │               │
         ▼               │
┌─────────────────┐      │
│   Apply Fixes   │      │
└────────┬────────┘      │
         │               │
         ▼               │
┌─────────────────┐      │
│    Validate     │      │
└────────┬────────┘      │
         │               │
         ▼               │
┌─────────────────┐      │
│ Check           │      │
│ Convergence     │──No──┘
└────────┬────────┘
         │
         │ Yes
         ▼
┌─────────────────┐
│   Finalize      │
└─────────────────┘
```

## 📊 Convergence Criteria

The protocol checks multiple criteria for convergence:

### 1. Minimum Cycles
- At least **2 cycles** must complete
- Ensures thorough review

### 2. Convergence Score
- ≥90% of high-priority issues resolved
- Formula: `fixed_high_priority / total_high_priority`

### 3. Critical Issues
- **Zero** unresolved critical issues
- All critical risks mitigated

### 4. Maximum Cycles
- **10 cycles** maximum
- Prevents infinite loops

### 5. Validation Status
- All fixes validated
- Tests passing
- No regressions

## 🎯 Usage Patterns

### Pattern 1: Code Development

```python
protocol = SelfReviewProtocol("Implement authentication module")

# Cycle 1: Initial implementation review
cycle1 = protocol.start_cycle()
# ... identify security issues, missing tests, etc.
protocol.complete_cycle(["Initial code written"])

# Cycle 2: Fix security issues
cycle2 = protocol.start_cycle()
# ... fix identified security issues
protocol.complete_cycle(["Fixed security issues"])

# Cycle 3: Add tests
cycle3 = protocol.start_cycle()
# ... add comprehensive tests
protocol.complete_cycle(["Added test coverage"])

# Check convergence and finalize
if protocol.check_convergence()[0]:
    protocol.finalize_review("Authentication module production-ready")
```

### Pattern 2: Bug Fix Validation

```python
protocol = SelfReviewProtocol("Fix bug #1234")

# Cycle 1: Verify fix
cycle1 = protocol.start_cycle()
protocol.identify_issue(
    IssueType.VALIDATION,
    Priority.HIGH,
    "Need regression test for bug fix",
    "tests/"
)
protocol.complete_cycle(["Bug fix implemented"])

# Cycle 2: Add regression test
cycle2 = protocol.start_cycle()
protocol.fix_issue(issue_id, "Added regression test")
protocol.complete_cycle(["Added regression test"])

# Finalize
protocol.finalize_review("Bug fix validated with regression test")
```

### Pattern 3: Documentation Update

```python
protocol = SelfReviewProtocol("Update API documentation")

# Cycle 1: Check completeness
cycle1 = protocol.start_cycle()
# ... scan for missing docs
protocol.complete_cycle(["Identified doc gaps"])

# Cycle 2: Fill gaps
cycle2 = protocol.start_cycle()
# ... add missing documentation
protocol.complete_cycle(["Updated documentation"])

# Finalize
protocol.finalize_review("Documentation complete and accurate")
```

## 📈 Metrics & Reporting

### Review Report Structure

```json
{
  "session_id": "a1b2c3d4e5f6g7h8",
  "task_description": "Implement feature X",
  "started_at": "2025-12-21T03:00:00",
  "completed_at": "2025-12-21T03:15:00",
  "status": "complete",
  "cycles": [
    {
      "cycle_number": 1,
      "started_at": "2025-12-21T03:00:00",
      "completed_at": "2025-12-21T03:05:00",
      "issues_identified": [...],
      "issues_fixed": [],
      "convergence_score": 0.0
    },
    {
      "cycle_number": 2,
      "started_at": "2025-12-21T03:05:00",
      "completed_at": "2025-12-21T03:10:00",
      "issues_identified": [],
      "issues_fixed": ["issue1", "issue2"],
      "convergence_score": 0.9
    }
  ],
  "total_issues_identified": 5,
  "total_issues_fixed": 4,
  "total_issues_deferred": 1,
  "remaining_high_priority": 0,
  "production_ready": true
}
```

### Summary Output

```
======================================================================
Self-Review Protocol Summary - Session a1b2c3d4e5f6g7h8
======================================================================
Task: Implement feature X
Status: complete
Cycles Completed: 2

Issues:
  Total Identified: 5
  Fixed: 4
  Deferred: 1
  Remaining High-Priority: 0

Convergence: 100.0%
Production Ready: ✓ Yes
======================================================================
```

## 🔍 Code Review Integration

### Automatic Code Analysis

The `code_change_reviewer.py` tool automatically checks for:

**Python Files:**
- Missing docstrings (classes, functions)
- TODO/FIXME comments
- Bare except clauses
- Excessive print statements
- Syntax errors

**Test Coverage:**
- Corresponding test files exist
- Test file naming conventions

**Documentation:**
- README.md presence
- Documentation updates needed

### Example Output

```bash
$ python scripts/code_change_reviewer.py --repo . --save-report

Reviewing 3 changed file(s)...

=== Cycle 1: Initial Analysis ===
Analyzing: src/module.py
Analyzing: src/utils.py
Analyzing: tests/test_module.py
Issues identified: 8

=== Cycle 2: Convergence Check ===
Convergence status: Need at least 2 cycles (current: 2)

======================================================================
Self-Review Protocol Summary
======================================================================
...
Production Ready: ✗ No

⚠ Remaining High-Priority Issues:
  - [HIGH] Missing docstring for FunctionDef 'process_data'
    Location: src/module.py
  - [HIGH] No test file found for src/utils.py
    Location: test_coverage

✓ Report saved: .codex/self_review/review_a1b2c3d4e5f6g7h8.json
```

## 🔗 Integration Points

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
- id: self-review
  name: Run self-review protocol
  entry: python3 scripts/code_change_reviewer.py
  language: system
  pass_filenames: false
  stages: [manual]
```

### CI/CD Pipeline

```yaml
# .github/workflows/self-review.yml
- name: Self-Review Protocol
  run: |
    python scripts/code_change_reviewer.py --repo . --save-report
    # Fail if not production ready
    exit $?
```

### IDE Integration

Configure as external tool in VS Code, PyCharm, etc.

## 🎓 Best Practices

### 1. Start Every Task with Protocol

Initialize protocol at the beginning of any significant task:
```python
protocol = SelfReviewProtocol("Clear task description")
```

### 2. Be Specific in Issue Descriptions

Bad: "Code needs improvement"
Good: "Function has O(n²) complexity, should be O(n log n)"

### 3. Document Mitigation Strategies

For deferred issues, always document why and how to address later:
```python
protocol.defer_issue(
    issue_id,
    "Will address in separate PR #1234 focused on performance"
)
```

### 4. Validate Every Fix

Never mark as fixed without validation:
```python
protocol.fix_issue(issue_id, "Added input validation")
protocol.validate_fix(issue_id, "Tests passing with edge cases")
```

### 5. Use Minimum 2 Cycles

Always run at least 2 cycles even if first seems complete:
- Cycle 1: Identify issues
- Cycle 2: Validate fixes

## 🐛 Troubleshooting

### Protocol Never Converges

**Symptom:** Reaches max cycles without convergence

**Solutions:**
1. Lower priority of non-critical issues
2. Document mitigation for deferred issues
3. Review convergence threshold (default: 90%)

### Too Many Low-Priority Issues

**Symptom:** Convergence blocked by numerous low-priority items

**Solution:** Focus on HIGH/CRITICAL priorities first, defer LOW issues

### False Positives in Code Review

**Symptom:** Tool identifies non-issues

**Solutions:**
1. Add exceptions to analyzer
2. Use code comments to suppress warnings
3. Customize detection rules

## 📚 API Reference

### SelfReviewProtocol Class

```python
class SelfReviewProtocol:
    def __init__(task_description: str, output_dir: Optional[Path])
    def start_cycle() -> ReviewCycle
    def identify_issue(...) -> Issue
    def fix_issue(issue_id: str, fix_description: str) -> bool
    def defer_issue(issue_id: str, reason: str) -> bool
    def validate_fix(issue_id: str, validation_result: str) -> bool
    def calculate_convergence() -> float
    def check_convergence() -> Tuple[bool, str]
    def complete_cycle(changes_made: List[str]) -> ReviewCycle
    def finalize_review(final_notes: str) -> ReviewReport
    def save_report(filename: Optional[str]) -> Path
    def print_summary()
```

### CodeChangeReviewer Class

```python
class CodeChangeReviewer:
    def __init__(repo_path: Path)
    def get_changed_files() -> List[Path]
    def analyze_python_file(filepath: Path) -> List[Tuple[...]]
    def check_test_coverage(changed_files: List[Path]) -> List[Tuple[...]]
    def check_documentation(changed_files: List[Path]) -> List[Tuple[...]]
    def run_review_cycle(task_description: str) -> SelfReviewProtocol
```

## 🔗 Related Documentation

- [AUTO_CONFIG_README.md](AUTO_CONFIG_README.md) - Automated configuration
- [AI_SEARCH_README.md](AI_SEARCH_README.md) - Repository search
- [DATASET_MANAGEMENT_README.md](DATASET_MANAGEMENT_README.md) - Dataset management

## 📝 Changelog

- **Previous Cycle-12-21**: Initial implementation
  - Core self-review protocol
  - Code change reviewer tool
  - Comprehensive documentation
  - Integration with existing systems

## 🎯 Future Enhancements

- [ ] Machine learning-based issue prediction
- [ ] Integration with static analysis tools (pylint, mypy)
- [ ] Natural language issue descriptions
- [ ] Automatic fix suggestions
- [ ] Cross-repository pattern learning
- [ ] Real-time convergence visualization
- [ ] Team-wide metrics aggregation
- [ ] Custom rule definitions
