# PLANSET: Phase 23 - Coverage 30% Achievement (Comprehensive Execution Guide)

**Created**: 2026-01-20  
**Owner**: GitHub Copilot Agents  
**Target**: Raise coverage from 17.27% to 30%  
**Timeline**: 3-4 weeks  
**Status**: 🔄 READY FOR EXECUTION  
**Agent**: Coverage Roadmap Agent

---

## 🎯 Mission Statement

Execute Phase 23 of the coverage threshold roadmap to achieve 30% test coverage through systematic test development, validation, and threshold enforcement. This planset provides comprehensive execution guidance with error handling, PDA loops, and AfterMath analysis integration.

---

## 📋 PRE-EXECUTION CHECKLIST

### Prerequisites Validation
```bash
# Run before starting Phase 23
cd /home/runner/work/_codex_/_codex_

# 1. Verify Phase 21 & 22 complete
test -f .codex/cognitive_brain/PHASE_21_STATUS_CICD_HARDENING.md && echo "✅ Phase 21 complete"
test -f .codex/security/secrets_usage_matrix.json && echo "✅ Phase 22 Obj 1 complete"
test -f .codex/plans/COVERAGE_THRESHOLD_ROADMAP.md && echo "✅ Phase 22 Obj 2 complete"

# 2. Verify CI stability (check last 3 runs)
# Manual check required via GitHub Actions UI

# 3. Validate baseline coverage
python -m pytest tests/ --cov=src --cov-report=term-missing:skip-covered -q --co

# 4. Verify test infrastructure
python -c "import pytest_cov, xdist, pytest_timeout; print('✅ Test infrastructure ready')"
```

**Decision Gate**: All checks must pass before proceeding. If any fail, address issues first.

---

## 🔄 EXECUTION WORKFLOW (PDA Process)

### **P**lan → **D**o → **A**nalyze Loop Structure

Each week follows the PDA cycle:
1. **Plan**: Define specific modules/tests for the week
2. **Do**: Implement tests with error handling
3. **Analyze**: Measure coverage, identify gaps, adjust plan

---

## 📅 WEEK 1: High-Priority Module Test Development

### Objective
Add 120-150 tests for highest-priority modules from test_priority_matrix.json

### Plan Phase (Day 1)

**Action**: Identify target modules
```bash
# Extract top 15 high-priority modules
python << 'EOF'
import json
with open('.codex/qa_walkthrough/test_priority_matrix.json') as f:
    matrix = json.load(f)
    high_priority = [m for m in matrix.get('high_priority_modules', [])[:15]]
    print("Target modules for Week 1:")
    for i, mod in enumerate(high_priority, 1):
        print(f"{i}. {mod['path']} (priority: {mod['priority_score']})")
EOF
```

**Output**: Create `.codex/plans/phase23_week1_targets.json`

### Do Phase (Days 2-5)

#### Module Group 1: CLI Commands (Days 2-3)
**Modules**: `src/codex/cli.py`, `src/codex/cli_rag.py`, `src/tokenization/cli.py`

**Test Strategy**:
```python
# tests/cli/test_cli_commands.py
import pytest
from typer.testing import CliRunner
from codex.cli import app

def test_cli_help():
    """Verify CLI help displays without errors"""
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.stdout

def test_cli_invalid_command():
    """Verify graceful handling of invalid commands"""
    runner = CliRunner()
    result = runner.invoke(app, ["nonexistent-command"])
    assert result.exit_code != 0
    # Error handling verification

# Add 30-40 similar tests for each CLI command
```

**Error Handling Pattern**:
```python
@pytest.mark.parametrize("invalid_input", [
    None,
    "",
    "  ",
    "invalid-format",
    {"malformed": "data"}
])
def test_cli_command_error_handling(invalid_input):
    """Verify robust error handling for invalid inputs"""
    runner = CliRunner()
    result = runner.invoke(app, ["command", str(invalid_input)])
    # Should not crash, should provide helpful error message
    assert result.exit_code != 0
    assert "Error:" in result.stdout or "Invalid:" in result.stdout
```

#### Module Group 2: Training Logic (Day 4)
**Modules**: `src/modeling.py`, `src/training.py`

**Test Strategy**:
```python
# tests/training/test_training_logic.py
import pytest
from unittest.mock import Mock, patch
import torch
from modeling import ModelConfig, initialize_model

def test_model_initialization():
    """Verify model initializes with valid config"""
    config = ModelConfig(hidden_size=768, num_layers=12)
    model = initialize_model(config)
    assert model is not None
    assert model.config.hidden_size == 768

def test_model_initialization_invalid_config():
    """Verify graceful failure with invalid config"""
    with pytest.raises(ValueError, match="hidden_size must be positive"):
        config = ModelConfig(hidden_size=-1)

@pytest.mark.parametrize("batch_size,seq_length", [
    (1, 128),
    (8, 512),
    (32, 128),
])
def test_training_step_shapes(batch_size, seq_length):
    """Verify training step handles various batch shapes"""
    # Test implementation with shape validation
    pass
```

#### Module Group 3: Data Loaders (Day 5)
**Modules**: `src/data/datasets.py`, `src/data/preprocessing.py`

**Test Strategy**:
```python
# tests/data/test_data_loaders.py
import pytest
from pathlib import Path
from data.datasets import load_dataset, preprocess_data

def test_dataset_loading_valid_path():
    """Verify dataset loads from valid path"""
    # Use fixture or test data
    dataset = load_dataset("tests/fixtures/sample_dataset.json")
    assert len(dataset) > 0

def test_dataset_loading_missing_file():
    """Verify graceful handling of missing dataset"""
    with pytest.raises(FileNotFoundError):
        load_dataset("nonexistent/path.json")

def test_dataset_loading_corrupted_data():
    """Verify handling of corrupted data"""
    # Test with malformed JSON, invalid formats, etc.
    pass

@pytest.fixture
def sample_dataset():
    """Provide reusable test dataset"""
    return [
        {"text": "Sample text 1", "label": 0},
        {"text": "Sample text 2", "label": 1},
    ]

def test_preprocessing_pipeline(sample_dataset):
    """Verify preprocessing pipeline executes successfully"""
    processed = preprocess_data(sample_dataset)
    assert len(processed) == len(sample_dataset)
    # Add assertions for expected transformations
```

### Analyze Phase (Day 6)

**Action**: Measure coverage progress
```bash
# Run coverage analysis
python -m pytest tests/cli tests/training tests/data \
  --cov=src/codex/cli.py \
  --cov=src/modeling.py \
  --cov=src/data/datasets.py \
  --cov-report=term-missing \
  --cov-report=html:htmlcov/week1 \
  --cov-report=json:.coverage_week1.json

# Analyze results
python << 'EOF'
import json
with open('.coverage_week1.json') as f:
    cov = json.load(f)
    total_statements = sum(file_data['summary']['num_statements'] 
                          for file_data in cov['files'].values())
    covered_statements = sum(file_data['summary']['covered_lines'] 
                            for file_data in cov['files'].values())
    coverage_pct = (covered_statements / total_statements * 100) if total_statements > 0 else 0
    print(f"Week 1 Coverage: {coverage_pct:.2f}%")
    print(f"Covered: {covered_statements}/{total_statements} statements")
    
    # Identify gaps
    gaps = []
    for file_path, file_data in cov['files'].items():
        file_cov = file_data['summary']['percent_covered']
        if file_cov < 50:
            gaps.append((file_path, file_cov))
    
    if gaps:
        print("\nGaps to address:")
        for path, cov_pct in sorted(gaps, key=lambda x: x[1]):
            print(f"  - {path}: {cov_pct:.1f}%")
EOF
```

**AfterMath Analysis**:
```markdown
## Week 1 AfterMath Analysis

### What Worked ✅
- [List successful test patterns]
- [Modules that reached >70% coverage]

### What Didn't Work ❌
- [Tests that were flaky or problematic]
- [Modules still below target]

### Lessons Learned 📚
- [Key insights from test development]
- [Error patterns encountered and solutions]

### Adjustments for Week 2 🔄
- [Specific changes to approach]
- [Additional modules to target]
```

**Decision Gate**: Coverage should be at ~22-25% after Week 1. If below 20%, reassess approach.

---

## 📅 WEEK 2: Integration Tests & Gap Filling

### Objective
Add 100-120 tests focusing on module interactions and filling Week 1 gaps

### Plan Phase (Day 1)

**Action**: Analyze Week 1 gaps and plan integration tests
```bash
# Identify untested module interactions
python << 'EOF'
import json
with open('.coverage_week1.json') as f:
    cov = json.load(f)
    # Identify modules with low coverage
    low_cov_modules = {
        path: data['summary']['percent_covered']
        for path, data in cov['files'].items()
        if data['summary']['percent_covered'] < 50
    }
    
    print("Integration test targets:")
    print("1. CLI → Training pipeline")
    print("2. Data loading → Preprocessing → Model input")
    print("3. Configuration → Model initialization")
    
    print("\nGap-filling targets:")
    for path, cov_pct in sorted(low_cov_modules.items(), key=lambda x: x[1])[:10]:
        print(f"  - {path}: {cov_pct:.1f}%")
EOF
```

### Do Phase (Days 2-5)

#### Integration Test Group 1: CLI-to-Training Pipeline
```python
# tests/integration/test_cli_training_pipeline.py
import pytest
from typer.testing import CliRunner
from pathlib import Path
import tempfile

def test_train_command_end_to_end():
    """Verify complete training pipeline from CLI"""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.yaml"
        config_path.write_text("""
model:
  hidden_size: 128
  num_layers: 2
training:
  batch_size: 8
  epochs: 1
        """)
        
        result = runner.invoke(app, [
            "train",
            "--config", str(config_path),
            "--data", "tests/fixtures/tiny_dataset.json",
            "--output", tmpdir
        ])
        
        assert result.exit_code == 0
        assert (Path(tmpdir) / "model.pt").exists()
```

#### Integration Test Group 2: Data Pipeline
```python
# tests/integration/test_data_pipeline.py
def test_data_loading_preprocessing_model_input():
    """Verify complete data transformation pipeline"""
    # Load raw data
    raw_data = load_dataset("tests/fixtures/raw_data.json")
    
    # Preprocess
    processed_data = preprocess_data(raw_data)
    
    # Convert to model input format
    model_inputs = prepare_model_inputs(processed_data)
    
    # Verify shapes and types
    assert isinstance(model_inputs, dict)
    assert "input_ids" in model_inputs
    assert model_inputs["input_ids"].shape[0] == len(raw_data)
```

#### Gap-Filling Tests
For each module with <50% coverage, add targeted tests:
```python
# tests/unit/test_gap_filling.py
# Use coverage report to identify uncovered lines
# Add tests specifically for those code paths

def test_uncovered_branch_X():
    """Cover previously untested branch X"""
    # Test implementation targeting specific lines
    pass
```

### Analyze Phase (Day 6)

**Action**: Comprehensive coverage analysis
```bash
# Run full test suite with coverage
python -m pytest tests/ \
  --cov=src \
  --cov-report=term-missing \
  --cov-report=html:htmlcov/week2 \
  --cov-report=json:.coverage_week2.json \
  --cov-report=xml:coverage_week2.xml

# Compare Week 1 vs Week 2
python << 'EOF'
import json

with open('.coverage_week1.json') as f:
    week1 = json.load(f)
with open('.coverage_week2.json') as f:
    week2 = json.load(f)

def calc_coverage(data):
    total = sum(f['summary']['num_statements'] for f in data['files'].values())
    covered = sum(f['summary']['covered_lines'] for f in data['files'].values())
    return (covered / total * 100) if total > 0 else 0

cov1 = calc_coverage(week1)
cov2 = calc_coverage(week2)

print(f"Week 1 Coverage: {cov1:.2f}%")
print(f"Week 2 Coverage: {cov2:.2f}%")
print(f"Improvement: {cov2 - cov1:.2f}%")
print(f"\nTarget: 30%")
print(f"Gap remaining: {max(0, 30 - cov2):.2f}%")
EOF
```

**AfterMath Analysis**:
```markdown
## Week 2 AfterMath Analysis

### Coverage Progress
- Week 1: X%
- Week 2: Y%
- Improvement: Z%
- Target: 30%
- Gap: [remaining percentage]

### Integration Test Insights
- [Which integration patterns worked well]
- [Which required more mocking/fixtures]

### Remaining Gaps
- [Specific modules still below target]
- [Hard-to-test code paths]

### Risk Assessment
- [Flaky tests identified]
- [CI stability concerns]

### Week 3 Strategy
- [Final push tactics]
- [Threshold raise preparation]
```

**Decision Gate**: Coverage should be at ~27-29% after Week 2. If below 25%, add one more week of test development.

---

## 📅 WEEK 3: Final Push & Threshold Raise

### Objective
Achieve 30%+ coverage and raise threshold in pyproject.toml

### Plan Phase (Day 1)

**Action**: Final gap analysis
```bash
# Identify remaining gaps to reach 30%
python << 'EOF'
import json
with open('.coverage_week2.json') as f:
    cov = json.load(f)
    
# Calculate current coverage
total = sum(f['summary']['num_statements'] for f in cov['files'].values())
covered = sum(f['summary']['covered_lines'] for f in cov['files'].values())
current_pct = (covered / total * 100) if total > 0 else 0

print(f"Current: {current_pct:.2f}%")
print(f"Target: 30%")
print(f"Gap: {30 - current_pct:.2f}%")

# Estimate tests needed
statements_needed = int((30 - current_pct) / 100 * total)
tests_estimated = statements_needed // 3  # Assume ~3 statements per test

print(f"\nEstimated tests needed: {tests_estimated}")
print("\nQuick wins (high impact, low effort):")
# Identify easy modules to bump coverage
EOF
```

### Do Phase (Days 2-4)

**Action**: Targeted test additions for remaining gaps
```python
# Focus on:
# 1. Missing error handling tests
# 2. Edge cases in existing modules
# 3. Quick configuration/utility tests

# tests/unit/test_final_coverage_push.py
@pytest.mark.parametrize("edge_case", [
    "empty_input",
    "null_value",
    "oversized_input",
    "special_characters",
])
def test_edge_case_handling(edge_case):
    """Cover remaining edge cases"""
    # Implement edge case tests
    pass
```

### Threshold Raise (Day 5)

**Prerequisites**:
```bash
# 1. Verify coverage ≥30%
python -m pytest tests/ --cov=src --cov-report=term | grep "^TOTAL"

# 2. Verify CI green
# Check GitHub Actions for last 3 runs - all must pass

# 3. Verify no flaky tests
python -m pytest tests/ --reruns=3 --reruns-delay=1 -v | grep -i "rerun"
# Should see minimal or no reruns
```

**Action**: Update threshold
```bash
# Update pyproject.toml
sed -i 's/fail_under = 0/fail_under = 30/' pyproject.toml

# Verify change
grep "fail_under" pyproject.toml

# Commit change
git add pyproject.toml
git commit -m "feat: Raise coverage threshold to 30% (Phase 23 complete)

- Added 250-300 unit tests across high-priority modules
- Added 100-120 integration tests for module interactions
- Verified coverage at 30.X%
- CI passing for 3 consecutive runs

Phase 23 complete. Ready for Phase 24."
```

### Validation (Day 6-7)

**Action**: Monitor CI and validate threshold
```bash
# Run full test suite locally
python -m pytest tests/ -v

# Should pass with new threshold

# Monitor CI for 3 runs
# All must pass to confirm threshold is stable
```

**AfterMath Analysis**:
```markdown
## Phase 23 Complete - AfterMath Analysis

### Final Metrics
- Starting coverage: 17.27%
- Ending coverage: [actual]%
- Tests added: [actual count]
- Duration: [actual weeks]

### Success Factors
- [What worked well in test development]
- [Effective testing patterns]
- [Good fixtures/utilities created]

### Challenges Encountered
- [Difficult-to-test modules]
- [CI stability issues]
- [Flaky test root causes]

### Reusable Patterns
- [Test patterns to reuse in Phase 24]
- [Fixture libraries created]
- [Mocking strategies]

### Recommendations for Phase 24
- [Specific improvements]
- [Areas to focus on]
- [Infrastructure needs]

### Tag: #Phase23Complete #Coverage30 #PDALoop
```

---

## 🚨 ERROR HANDLING & ROLLBACK

### Common Errors and Solutions

#### Error 1: Coverage Calculation Mismatch
**Symptom**: pytest-cov reports different coverage than manual calculation
**Solution**:
```bash
# Clear coverage cache
rm -rf .coverage .coverage.* htmlcov/

# Re-run with explicit source
python -m pytest tests/ --cov=src --cov-config=pyproject.toml
```

#### Error 2: Flaky Tests Causing CI Failures
**Symptom**: Tests pass locally but fail in CI intermittently
**Solution**:
```python
# Add retries for flaky tests
@pytest.mark.flaky(reruns=3, reruns_delay=2)
def test_potentially_flaky():
    pass

# Or use pytest-timeout to catch hanging tests
@pytest.mark.timeout(60)
def test_with_timeout():
    pass
```

#### Error 3: Import Errors After New Tests
**Symptom**: New tests cause import errors in other test files
**Solution**:
```bash
# Verify module structure
python -c "import sys; print('\n'.join(sys.path))"

# Add __init__.py files if missing
find tests/ -type d -exec touch {}/__init__.py \;

# Clear pytest cache
rm -rf .pytest_cache
```

#### Error 4: Threshold Raise Causes CI Failure
**Symptom**: After raising threshold, CI fails on other branches
**Solution**:
```bash
# Rollback threshold immediately
git revert HEAD  # Revert the threshold raise commit

# Analyze which tests are failing
# Add missing tests
# Re-attempt threshold raise
```

### Rollback Procedure

If Phase 23 encounters critical issues:

1. **Immediate Rollback**:
```bash
# Revert threshold change
sed -i 's/fail_under = 30/fail_under = 0/' pyproject.toml
git add pyproject.toml
git commit -m "revert: Rollback coverage threshold to 0% (Phase 23 issues)"
git push
```

2. **Document Failure**:
```markdown
# .codex/plans/PHASE_23_ROLLBACK_ANALYSIS.md
## Rollback Reason
[Describe what went wrong]

## Root Cause
[Technical analysis]

## Remediation Plan
[Steps to fix and retry]

## Timeline
[When to re-attempt Phase 23]
```

3. **Schedule Retry**:
After addressing root cause, restart Phase 23 with adjusted plan.

---

## 📊 SUCCESS CRITERIA

### Must-Have (Blocking)
- [ ] Coverage ≥30% measured by pytest-cov
- [ ] CI passes for 3 consecutive runs after threshold raise
- [ ] Zero critical/high priority test failures
- [ ] All new tests have docstrings
- [ ] pyproject.toml updated with fail_under=30

### Should-Have (Non-Blocking)
- [ ] Integration tests added (100+)
- [ ] Edge case coverage >80% for targeted modules
- [ ] Test execution time <5 minutes for unit tests
- [ ] Coverage artifacts updated in .codex/qa_walkthrough/

### Nice-to-Have (Future)
- [ ] Mutation testing score >70% for core modules
- [ ] Test documentation in docs/testing/
- [ ] Automated coverage regression detection

---

## 🔗 INTEGRATION POINTS

### PDA Loop Integration
- **Plan**: Documented at start of each week
- **Do**: Test development with error handling
- **Analyze**: AfterMath analysis at end of each week
- **Iterate**: Adjust strategy based on analysis

### AfterMath Tags
Use these tags in AfterMath analyses:
- `#Phase23Week1` / `#Phase23Week2` / `#Phase23Week3`
- `#CoverageGain` / `#TestDevelopment`
- `#LessonsLearned` / `#PatternDiscovered`
- `#ErrorHandled` / `#RiskMitigated`

### Cognitive Brain Updates
Update these files at end of Phase 23:
- `.codex/plans/COVERAGE_THRESHOLD_ROADMAP.md` (mark Phase 23 complete)
- `.codex/results.md` (add Phase 23 results)
- `.codex/action_log.ndjson` (append Phase 23 actions)
- `.codex/cognitive_brain/PHASE_23_STATUS.md` (create completion summary)

---

## 📝 CONTINUATION PROMPTSET

**For GitHub Copilot Agent** (post as comment after Phase 23):

```markdown
@copilot Execute Phase 24 of the coverage roadmap documented in `.codex/plans/PLANSET_PHASE_24_COVERAGE_50.md`.

**Context**: Phase 23 complete with 30% coverage threshold raised. Starting point: 30.X% coverage.

**Target**: Raise coverage to 50% through integration and workflow tests.

**Prerequisites**:
- Review Phase 23 AfterMath analysis (`.codex/plans/PHASE_23_AFTERMATH_ANALYSIS.md`)
- Validate baseline at 30%+
- Verify CI stability (check last 5 runs)

**Execution**: Follow PDA process with weekly cycles. Use Coverage Roadmap Agent for execution. Report progress after each week with AfterMath analysis.

**Reference**: `.codex/cognitive_brain/COGNITIVE_BRAIN_CONTINUATION_PHASE_22.md` (master plan)
```

---

**Status**: ✅ READY FOR EXECUTION  
**Next Review**: After Week 1 completion  
**Owner**: @mbaetiong  
**Agent**: Coverage Roadmap Agent
