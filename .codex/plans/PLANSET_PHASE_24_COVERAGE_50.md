# PLANSET: Phase 24 - Coverage 50% Achievement (Comprehensive Execution Guide)

**Created**: 2026-01-20  
**Owner**: GitHub Copilot Agents  
**Target**: Raise coverage from 30% to 50%  
**Timeline**: 2-3 weeks  
**Status**: 🔄 READY FOR EXECUTION (after Phase 23)  
**Agent**: Coverage Roadmap Agent  
**Prerequisites**: Phase 23 complete with 30%+ coverage

---

## 🎯 Mission Statement

Execute Phase 24 of the coverage threshold roadmap to achieve 50% test coverage through integration testing, workflow validation, and comprehensive error handling. Build on Phase 23 foundations with focus on cross-module interactions and end-to-end scenarios.

---

## 📋 PRE-EXECUTION CHECKLIST

### Prerequisites Validation
```bash
# Run before starting Phase 24
cd /home/runner/work/_codex_/_codex_

# 1. Verify Phase 23 complete
grep "fail_under = 30" pyproject.toml && echo "✅ Phase 23 threshold raised"

# 2. Validate current coverage ≥30%
python -m pytest tests/ --cov=src --cov-report=term | grep "^TOTAL" | awk '{if ($NF >= 30) print "✅ Coverage at "$NF; else print "❌ Coverage below 30%: "$NF}'

# 3. Check Phase 23 AfterMath analysis exists
test -f .codex/plans/PHASE_23_AFTERMATH_ANALYSIS.md && echo "✅ Phase 23 AfterMath complete"

# 4. Verify CI stability (last 5 runs)
# Manual check via GitHub Actions

# 5. Verify no flaky tests from Phase 23
python -m pytest tests/ --reruns=3 -v | grep -c "RERUN" | awk '{if ($1 < 5) print "✅ Flaky tests minimal"; else print "⚠️  Flaky tests: "$1}'
```

**Decision Gate**: All checks must pass. If coverage < 30%, complete Phase 23 first.

---

## 🔄 EXECUTION WORKFLOW (PDA Process)

### Phase 24 Focus Areas

1. **Integration Tests** (60% of effort)
   - Module-to-module interactions
   - Pipeline workflows
   - Service integrations

2. **Workflow Tests** (30% of effort)
   - End-to-end scenarios
   - CLI-driven workflows
   - Configuration variations

3. **Gap Filling** (10% of effort)
   - Remaining unit test gaps from Phase 23
   - Edge cases in existing modules

---

## 📅 WEEK 1: Integration Test Development

### Objective
Add 100-120 integration tests for cross-module interactions

### Plan Phase (Day 1)

**Action**: Identify integration points
```bash
# Analyze module dependencies
python << 'EOF'
import ast
import json
from pathlib import Path
from collections import defaultdict

# Parse imports to build dependency graph
src_path = Path("src")
dependencies = defaultdict(list)

for py_file in src_path.rglob("*.py"):
    if py_file.name == "__init__.py":
        continue
    try:
        with open(py_file) as f:
            tree = ast.parse(f.read(), filename=str(py_file))
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module and node.module.startswith("codex"):
                    module_name = str(py_file.relative_to(src_path))
                    dependencies[module_name].append(node.module)
    except Exception as e:
        continue

# Identify high-connectivity modules (good integration test targets)
print("Top integration test targets:")
sorted_deps = sorted(dependencies.items(), key=lambda x: len(x[1]), reverse=True)
for module, deps in sorted_deps[:15]:
    print(f"  {module}: {len(deps)} dependencies")
    
# Save for reference
with open(".codex/plans/phase24_integration_targets.json", "w") as f:
    json.dump(dict(dependencies), f, indent=2)
EOF
```

### Do Phase (Days 2-6)

#### Integration Group 1: CLI → Model Pipeline (Days 2-3)
```python
# tests/integration/test_cli_model_pipeline.py
import pytest
from typer.testing import CliRunner
from pathlib import Path
import tempfile
import torch

def test_cli_train_to_checkpoint():
    """Verify CLI training produces valid checkpoint"""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create minimal config
        config = Path(tmpdir) / "config.yaml"
        config.write_text("""
model:
  type: transformer
  hidden_size: 256
  num_layers: 4
training:
  batch_size: 4
  max_steps: 10
  save_steps: 5
data:
  train_path: tests/fixtures/tiny_train.json
  eval_path: tests/fixtures/tiny_eval.json
""")
        
        # Run training
        result = runner.invoke(app, [
            "train",
            "--config", str(config),
            "--output-dir", tmpdir
        ])
        
        assert result.exit_code == 0, f"Training failed: {result.output}"
        
        # Verify checkpoint created
        checkpoint_dir = Path(tmpdir) / "checkpoint-5"
        assert checkpoint_dir.exists(), "Checkpoint not created"
        assert (checkpoint_dir / "pytorch_model.bin").exists()
        
        # Verify checkpoint loadable
        model = torch.load(checkpoint_dir / "pytorch_model.bin")
        assert model is not None

def test_cli_train_resume_from_checkpoint():
    """Verify training can resume from checkpoint"""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        # First training run (partial)
        config = Path(tmpdir) / "config.yaml"
        config.write_text("""
model:
  type: transformer
  hidden_size: 128
training:
  batch_size: 2
  max_steps: 5
  save_steps: 5
data:
  train_path: tests/fixtures/tiny_train.json
""")
        
        result1 = runner.invoke(app, [
            "train",
            "--config", str(config),
            "--output-dir", tmpdir
        ])
        assert result1.exit_code == 0
        
        # Resume training
        config.write_text("""
model:
  type: transformer
  hidden_size: 128
training:
  batch_size: 2
  max_steps: 10
  save_steps: 5
data:
  train_path: tests/fixtures/tiny_train.json
""")
        
        result2 = runner.invoke(app, [
            "train",
            "--config", str(config),
            "--output-dir", tmpdir,
            "--resume-from-checkpoint", str(Path(tmpdir) / "checkpoint-5")
        ])
        assert result2.exit_code == 0
        
        # Verify continued training
        checkpoint_10 = Path(tmpdir) / "checkpoint-10"
        assert checkpoint_10.exists()

@pytest.mark.parametrize("invalid_config", [
    {"model": {"hidden_size": -1}},  # Invalid hidden size
    {"training": {"batch_size": 0}},  # Zero batch size
    {"data": {"train_path": "nonexistent.json"}},  # Missing data
])
def test_cli_train_invalid_config_handling(invalid_config):
    """Verify graceful handling of invalid configs"""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "invalid_config.yaml"
        import yaml
        config_path.write_text(yaml.dump(invalid_config))
        
        result = runner.invoke(app, [
            "train",
            "--config", str(config_path),
            "--output-dir", tmpdir
        ])
        
        assert result.exit_code != 0
        assert "Error" in result.output or "Invalid" in result.output
```

#### Integration Group 2: Data → Model Pipeline (Day 4)
```python
# tests/integration/test_data_model_pipeline.py
import pytest
from data.datasets import load_dataset, DataCollator
from modeling import AutoModel, AutoConfig
import torch

def test_data_loading_to_model_input():
    """Verify data pipeline produces valid model inputs"""
    # Load dataset
    dataset = load_dataset("tests/fixtures/sample_dataset.json")
    assert len(dataset) > 0
    
    # Create data collator
    collator = DataCollator(max_length=128)
    
    # Prepare batch
    batch = collator([dataset[i] for i in range(min(4, len(dataset)))])
    
    # Verify batch structure
    assert "input_ids" in batch
    assert "attention_mask" in batch
    assert isinstance(batch["input_ids"], torch.Tensor)
    
    # Load model
    config = AutoConfig.from_pretrained("tests/fixtures/test_model_config.json")
    model = AutoModel.from_config(config)
    
    # Forward pass
    with torch.no_grad():
        outputs = model(**batch)
    
    assert outputs is not None
    assert hasattr(outputs, "logits") or hasattr(outputs, "last_hidden_state")

def test_data_preprocessing_pipeline_end_to_end():
    """Verify complete data preprocessing pipeline"""
    from data.preprocessing import (
        load_raw_data,
        clean_text,
        tokenize,
        create_features
    )
    
    # Load raw data
    raw_data = load_raw_data("tests/fixtures/raw_text.txt")
    assert len(raw_data) > 0
    
    # Clean
    cleaned = [clean_text(text) for text in raw_data]
    assert all(isinstance(text, str) for text in cleaned)
    
    # Tokenize
    tokenized = [tokenize(text) for text in cleaned]
    assert all(isinstance(tokens, list) for tokens in tokenized)
    
    # Create features
    features = create_features(tokenized)
    assert isinstance(features, dict)
    assert "input_ids" in features

@pytest.mark.parametrize("corrupted_data", [
    b'\x89PNG\r\n\x1a\n',  # Binary data
    '{"malformed": json}',  # Invalid JSON
    '',  # Empty
])
def test_data_pipeline_corruption_handling(corrupted_data):
    """Verify robustness to data corruption"""
    from data.datasets import load_dataset
    import tempfile
    
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.json', delete=False) as f:
        if isinstance(corrupted_data, bytes):
            f.write(corrupted_data)
        else:
            f.write(corrupted_data.encode())
        temp_path = f.name
    
    try:
        with pytest.raises((ValueError, json.JSONDecodeError, UnicodeDecodeError)):
            load_dataset(temp_path)
    finally:
        Path(temp_path).unlink()
```

#### Integration Group 3: Configuration → All Systems (Day 5-6)
```python
# tests/integration/test_config_integration.py
import pytest
from hydra import compose, initialize_config_dir
from pathlib import Path
import tempfile

def test_hydra_config_to_model_initialization():
    """Verify Hydra config properly initializes model"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create Hydra config
        config_dir = Path(tmpdir) / "conf"
        config_dir.mkdir()
        (config_dir / "config.yaml").write_text("""
model:
  _target_: modeling.TransformerModel
  hidden_size: 512
  num_layers: 6
  num_heads: 8
""")
        
        # Initialize Hydra
        with initialize_config_dir(config_dir=str(config_dir), version_base="1.1"):
            cfg = compose(config_name="config")
            
            # Instantiate model from config
            from hydra.utils import instantiate
            model = instantiate(cfg.model)
            
            assert model is not None
            assert model.config.hidden_size == 512

def test_config_override_chain():
    """Verify config override hierarchy works correctly"""
    # Test: CLI > Config File > Defaults
    # Implementation depends on your config system
    pass

@pytest.fixture
def config_variations():
    """Provide various config combinations for testing"""
    return [
        {"model": {"type": "gpt2"}, "training": {"optimizer": "adam"}},
        {"model": {"type": "bert"}, "training": {"optimizer": "sgd"}},
        {"model": {"type": "t5"}, "training": {"optimizer": "adafactor"}},
    ]

@pytest.mark.parametrize("config_variant", config_variations())
def test_config_variations(config_variant):
    """Verify system handles different config combinations"""
    # Test each config variant
    pass
```

### Analyze Phase (Day 7)

**Action**: Measure integration test coverage impact
```bash
# Run integration tests with coverage
python -m pytest tests/integration/ \
  --cov=src \
  --cov-append \
  --cov-report=term-missing \
  --cov-report=html:htmlcov/phase24_week1 \
  --cov-report=json:.coverage_phase24_week1.json

# Analyze improvement
python << 'EOF'
import json

# Load Phase 23 final coverage
with open('.coverage_week2.json') as f:  # From Phase 23
    phase23 = json.load(f)

# Load current coverage
with open('.coverage_phase24_week1.json') as f:
    phase24_w1 = json.load(f)

def calc_coverage(data):
    total = sum(f['summary']['num_statements'] for f in data['files'].values())
    covered = sum(f['summary']['covered_lines'] for f in data['files'].values())
    return (covered / total * 100) if total > 0 else 0

cov_p23 = calc_coverage(phase23)
cov_p24_w1 = calc_coverage(phase24_w1)

print(f"Phase 23 End: {cov_p23:.2f}%")
print(f"Phase 24 Week 1: {cov_p24_w1:.2f}%")
print(f"Improvement: {cov_p24_w1 - cov_p23:.2f}%")
print(f"\nTarget: 50%")
print(f"Gap remaining: {max(0, 50 - cov_p24_w1):.2f}%")

# Identify which modules benefited most from integration tests
print("\nTop coverage improvements:")
for file_path in phase24_w1['files']:
    if file_path in phase23['files']:
        old_cov = phase23['files'][file_path]['summary']['percent_covered']
        new_cov = phase24_w1['files'][file_path]['summary']['percent_covered']
        improvement = new_cov - old_cov
        if improvement > 10:
            print(f"  {file_path}: +{improvement:.1f}% ({old_cov:.1f}% → {new_cov:.1f}%)")
EOF
```

**AfterMath Analysis**:
```markdown
## Phase 24 Week 1 AfterMath Analysis

### Integration Test Insights
- [Which integration patterns were most effective]
- [Modules that saw biggest coverage gains]
- [Integration points that were difficult to test]

### Coverage Progress
- Phase 23 End: X%
- Phase 24 Week 1: Y%
- Improvement: Z%
- Target: 50%
- Gap: [remaining]%

### Testing Patterns Discovered
- [Effective fixture patterns]
- [Mocking strategies for external services]
- [Config management in tests]

### Challenges
- [Hard-to-integrate components]
- [Performance issues in integration tests]
- [Flakiness introduced]

### Week 2 Adjustments
- [Focus areas for remaining gap]
- [Additional integration scenarios needed]
```

**Decision Gate**: Coverage should be at ~40-45% after Week 1. If below 38%, reassess approach.

---

## 📅 WEEK 2: Workflow & E2E Tests + Final Push

### Objective
Add 80-100 workflow/E2E tests and reach 50%+ coverage

### Plan Phase (Day 1)

**Action**: Identify end-to-end workflows
```bash
# Map user workflows from CLI entrypoints
python << 'EOF'
import ast
from pathlib import Path

cli_file = Path("src/codex/cli.py")
with open(cli_file) as f:
    tree = ast.parse(f.read())

workflows = []
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        # Look for CLI command decorators
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                if hasattr(decorator.func, 'attr') and 'command' in decorator.func.attr:
                    workflows.append(node.name)

print("E2E Workflow Test Targets:")
for workflow in workflows:
    print(f"  - {workflow}")

# Save for tracking
import json
with open(".codex/plans/phase24_workflow_targets.json", "w") as f:
    json.dump(workflows, f, indent=2)
EOF
```

### Do Phase (Days 2-5)

#### Workflow Tests: Complete User Scenarios
```python
# tests/e2e/test_complete_workflows.py
import pytest
from typer.testing import CliRunner
from pathlib import Path
import tempfile

def test_workflow_train_evaluate_export():
    """Complete workflow: train → evaluate → export model"""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Step 1: Train model
        train_config = tmpdir / "train_config.yaml"
        train_config.write_text("""
model:
  hidden_size: 128
training:
  max_steps: 10
data:
  train_path: tests/fixtures/tiny_train.json
""")
        
        train_result = runner.invoke(app, [
            "train",
            "--config", str(train_config),
            "--output-dir", str(tmpdir / "model")
        ])
        assert train_result.exit_code == 0
        
        # Step 2: Evaluate model
        eval_result = runner.invoke(app, [
            "evaluate",
            "--model-path", str(tmpdir / "model"),
            "--data-path", "tests/fixtures/tiny_eval.json",
            "--output", str(tmpdir / "metrics.json")
        ])
        assert eval_result.exit_code == 0
        assert (tmpdir / "metrics.json").exists()
        
        # Step 3: Export model
        export_result = runner.invoke(app, [
            "export",
            "--model-path", str(tmpdir / "model"),
            "--format", "onnx",
            "--output", str(tmpdir / "model.onnx")
        ])
        assert export_result.exit_code == 0
        assert (tmpdir / "model.onnx").exists()

def test_workflow_data_preparation_to_training():
    """Workflow: prepare data → train model"""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Prepare data
        prep_result = runner.invoke(app, [
            "prepare-data",
            "--input", "tests/fixtures/raw_data.txt",
            "--output", str(tmpdir / "prepared_data.json"),
            "--split-ratio", "0.8"
        ])
        assert prep_result.exit_code == 0
        assert (tmpdir / "prepared_data.json").exists()
        
        # Train on prepared data
        train_result = runner.invoke(app, [
            "train",
            "--data", str(tmpdir / "prepared_data.json"),
            "--output-dir", str(tmpdir / "model"),
            "--max-steps", "5"
        ])
        assert train_result.exit_code == 0

@pytest.mark.slow
def test_workflow_full_pipeline_with_errors():
    """Test workflow with intentional errors to verify error handling"""
    runner = CliRunner()
    
    # Test 1: Missing required data
    result1 = runner.invoke(app, ["train", "--config", "nonexistent.yaml"])
    assert result1.exit_code != 0
    assert "not found" in result1.output.lower() or "error" in result1.output.lower()
    
    # Test 2: Invalid model checkpoint
    with tempfile.TemporaryDirectory() as tmpdir:
        (Path(tmpdir) / "fake_checkpoint").mkdir()
        result2 = runner.invoke(app, [
            "evaluate",
            "--model-path", str(Path(tmpdir) / "fake_checkpoint"),
            "--data-path", "tests/fixtures/tiny_eval.json"
        ])
        assert result2.exit_code != 0
```

#### Gap-Filling & Edge Cases (Day 6)
```python
# tests/unit/test_phase24_gaps.py
# Target specific uncovered lines from coverage report

def test_error_recovery_in_training_loop():
    """Cover error recovery code paths"""
    pass

def test_edge_case_empty_dataset():
    """Handle empty dataset gracefully"""
    pass

def test_edge_case_single_sample():
    """Handle single sample dataset"""
    pass
```

### Threshold Raise (Day 7)

**Prerequisites Check**:
```bash
# 1. Verify coverage ≥50%
python -m pytest tests/ --cov=src --cov-report=term | grep "^TOTAL"

# 2. Run full test suite
python -m pytest tests/ -v --tb=short

# 3. Check for flaky tests
python -m pytest tests/ --reruns=3 -v | grep "RERUN" | wc -l

# 4. Verify CI green (last 3 runs)
```

**Action**: Raise threshold
```bash
# Update pyproject.toml
sed -i 's/fail_under = 30/fail_under = 50/' pyproject.toml

# Commit
git add pyproject.toml
git commit -m "feat: Raise coverage threshold to 50% (Phase 24 complete)

- Added 100-120 integration tests
- Added 80-100 workflow/E2E tests
- Verified coverage at 50.X%
- CI passing for 3 consecutive runs

Phase 24 complete. Ready for Phase 25."
```

---

## 🚨 ERROR HANDLING & ROLLBACK

### Common Errors

#### Error 1: Integration Test Timeout
**Solution**:
```python
# Add timeouts to slow integration tests
@pytest.mark.timeout(300)  # 5 minutes
def test_slow_integration():
    pass
```

#### Error 2: External Service Dependencies
**Solution**:
```python
# Mock external services
from unittest.mock import patch, Mock

@patch('requests.get')
def test_api_integration(mock_get):
    mock_get.return_value = Mock(status_code=200, json=lambda: {"result": "ok"})
    # Test implementation
```

#### Error 3: Flaky Integration Tests
**Solution**:
```python
# Use retries and fixtures for stability
@pytest.mark.flaky(reruns=3, reruns_delay=2)
@pytest.fixture(scope="session")
def stable_test_environment():
    # Setup once per session
    yield
    # Teardown
```

### Rollback Procedure
Same as Phase 23 - revert threshold, document, fix, retry.

---

## 📊 SUCCESS CRITERIA

### Must-Have
- [ ] Coverage ≥50%
- [ ] 100+ integration tests added
- [ ] 80+ workflow/E2E tests added
- [ ] CI green for 3 runs
- [ ] pyproject.toml updated

### Should-Have
- [ ] Test execution time <10 minutes total
- [ ] Zero critical flaky tests
- [ ] All workflows tested end-to-end

---

## 📝 CONTINUATION PROMPTSET

**For GitHub Copilot Agent** (post as comment after Phase 24):

```markdown
@copilot Execute Phase 25 of the coverage roadmap documented in `.codex/plans/PLANSET_PHASE_25_COVERAGE_70.md`.

**Context**: Phase 24 complete with 50% coverage threshold raised. Starting point: 50.X% coverage.

**Target**: Raise coverage to 70% (production-ready threshold) through comprehensive E2E testing and edge case coverage.

**Prerequisites**:
- Review Phase 24 AfterMath analysis (`.codex/plans/PHASE_24_AFTERMATH_ANALYSIS.md`)
- Validate baseline at 50%+
- Verify integration test stability

**Execution**: Follow PDA process. Use Coverage Roadmap Agent. This is the final push to production-ready coverage.

**Reference**: `.codex/plans/COVERAGE_THRESHOLD_ROADMAP.md` (Phase 25 section)
```

---

**Status**: ✅ READY FOR EXECUTION (after Phase 23)  
**Next Review**: After Week 1 completion  
**Owner**: @mbaetiong  
**Agent**: Coverage Roadmap Agent
