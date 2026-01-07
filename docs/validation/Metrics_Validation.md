# Validation: Metrics — Generative (BLEU/ROUGE) Optional Behavior

> Generated: 2025-11-05 07:27:25 | Author: mbaetiong

## Objective

Confirm generative metrics behave correctly as optional features and the evaluation runner handles different ROUGE-L return shapes (float vs dict).

## Prerequisites

- Local repository clone with status audit changes
- Python 3.10+ installed
- Optional: `pip install ".[metrics]"` for full metric testing

## Validation Checklist

### 1. Optional Behavior Unit Tests

**Command**:
```bash
nox -s repro_smoke
# Or directly:
pytest -q tests/test_metrics_generative.py
```text

**Expected Outcome**:
- All 8 tests pass
- Tests validate both "with deps" and "without deps" scenarios
- Exit code 0

**What Tests Validate**:
- `test_bleu_optional_behavior` - BLEU returns None or float [0,1]
- `test_rouge_l_optional_behavior` - ROUGE-L returns None or float [0,1]
- `test_registry_lists_generative_names` - Metrics registered in registry
- `test_runner_no_generative_dependency_required` - Eval works without generative extras
- `test_bleu_metric_with_identical_inputs` - BLEU perfect match
- `test_rouge_metric_with_identical_inputs` - ROUGE-L perfect match
- `test_runner_handles_rouge_float_return` - Runner accepts float
- `test_runner_handles_rouge_dict_return` - Runner accepts dict

### 2. BLEU Available With Extras

**Command**:
```bash
# Install metrics extras
pip install ".[metrics]"

# Run specific test
pytest -q tests/test_metrics_generative.py::test_bleu_optional_behavior -v
```text

**Expected Outcome**:
- BLEU metric returns a float in range [0, 1]
- Perfect match inputs return score ≈ 1.0
- Non-matching inputs return score < 1.0

**Verify Installation**:
```bash
python -c "
from codex_ml.metrics.registry import get_metric
bleu = get_metric('bleu')
score = bleu(['hello world'], ['hello world'])
assert score is not None, 'BLEU should return value with nltk installed'
assert 0 <= score <= 1, f'BLEU score {score} out of range'
print(f'✓ BLEU available: score={score:.3f}')
"
```text

### 3. ROUGE-L Available With Extras

**Command**:
```bash
# Install metrics extras
pip install ".[metrics]"

# Run specific test
pytest -q tests/test_metrics_generative.py::test_rouge_l_optional_behavior -v
```text

**Expected Outcome**:
- ROUGE-L metric returns a float in range [0, 1]
- Perfect match inputs return score ≈ 1.0
- Partial match inputs return score between 0 and 1

**Verify Installation**:
```bash
python -c "
from codex_ml.metrics.registry import get_metric
rouge = get_metric('rougeL')
score = rouge(['the quick brown fox'], ['the quick brown fox'])
assert score is not None, 'ROUGE-L should return value with rouge_score installed'
assert 0 <= score <= 1, f'ROUGE-L score {score} out of range'
print(f'✓ ROUGE-L available: score={score:.3f}')
"
```text

### 4. Runner ROUGE-L Compatibility

**Command**:
```bash
# Test runner compatibility
pytest -q tests/test_metrics_generative.py::test_runner_handles_rouge_float_return -v
pytest -q tests/test_metrics_generative.py::test_runner_handles_rouge_dict_return -v
```text

**Expected Outcome**:
- Runner accepts float return from ROUGE metric
- Runner accepts dict return with keys: `rougeL_f`, `rougeL`, `f`, `fmeasure`
- Extraction logic tries keys in order and uses first found
- Clear error if dict returned without expected keys

**What This Validates**:
- Backward compatibility with different ROUGE implementations
- Registry returns float (codex_ml.metrics.registry)
- Some external implementations Phase 5 return dict
- Runner handles both gracefully

**Implementation Details**:
```python
# In src/codex_ml/eval/runner.py
if isinstance(rouge_score, dict):
    for key in ["rougeL_f", "rougeL", "f", "fmeasure"]:
        if key in rouge_score:
            results[metric_name] = rouge_score[key]
            break
else:
    results[metric_name] = rouge_score
```text

## Without Metrics Extras

### Graceful Degradation

**Command**:
```bash
# Uninstall optional deps (if installed)
pip uninstall -y nltk rouge-score sacrebleu

# Run tests
pytest -q tests/test_metrics_generative.py
```text

**Expected Outcome**:
- All tests still pass
- BLEU/ROUGE metrics return `None` instead of raising
- Runner validates `None` is acceptable return
- Tests verify registry includes metric names even without deps

**Verify Graceful Behavior**:
```bash
python -c "
from codex_ml.metrics.registry import get_metric, list_metrics

# Metrics should be registered
assert 'bleu' in list_metrics()
assert 'rougel' in [m.lower() for m in list_metrics()]

# But return None without deps
bleu = get_metric('bleu')
score = bleu(['test'], ['test'])
print(f'BLEU without deps: {score}')  # Should be None

rouge = get_metric('rougeL')  
score = rouge(['test'], ['test'])
print(f'ROUGE-L without deps: {score}')  # Should be None
"
```text

## Acceptance Criteria

| Check | Command | With Extras | Without Extras | Status |
|-------|---------|-------------|----------------|--------|
| Optional behavior tests | `pytest tests/test_metrics_generative.py` | All pass | All pass | ✓ |
| BLEU returns value | `get_metric('bleu')(...)` | Float [0,1] | None | ✓ |
| ROUGE-L returns value | `get_metric('rougeL')(...)` | Float [0,1] | None | ✓ |
| Runner float compat | Test mock | Accepts float | N/A | ✓ |
| Runner dict compat | Test mock | Accepts dict | N/A | ✓ |
| Metrics registered | `list_metrics()` | Includes bleu/rouge | Includes bleu/rouge | ✓ |

## Testing Scenarios

### Scenario 1: Development Environment (With Extras)

```bash
# Setup
pip install -e ".[metrics]"

# Validate
pytest tests/test_metrics_generative.py -v

# Expected: All 8 tests pass, BLEU/ROUGE return actual scores
```text

### Scenario 2: Production Environment (Without Extras)

```bash
# Setup (minimal install)
pip install -e .

# Validate
pytest tests/test_metrics_generative.py -v

# Expected: All 8 tests pass, BLEU/ROUGE return None
```text

### Scenario 3: Evaluation With Optional Metrics

```bash
# With extras installed
python -c "
from codex_ml.config import EvaluationConfig
from codex_ml.eval.runner import run_evaluation
from pathlib import Path
import json

# Create test dataset
dataset = Path('test_eval.jsonl')
dataset.write_text(json.dumps({'prediction': 'hello', 'target': 'hello', 'text': 'test'}) + '\n')

# Run with generative metrics
cfg = EvaluationConfig(
    dataset_path=str(dataset),
    dataset_format='jsonl',
    metrics=['exact_match', 'bleu', 'rougeL'],
    output_dir='eval_output',
    seed=42,
    prediction_field='prediction',
    target_field='target',
    text_field='text',
)

result = run_evaluation(cfg)
print('Metrics:', result['metrics'])
# Expected: exact_match=1.0, bleu≈1.0, rougeL≈1.0

dataset.unlink()
"
```text

## Troubleshooting

### BLEU Returns None Despite Installation

**Check Installation**:
```bash
python -c "import nltk; print(nltk.__version__)"
```text

**Solution**:
```bash
pip install --force-reinstall nltk>=3.8
```text

### ROUGE-L Returns None Despite Installation

**Check Installation**:
```bash
python -c "import rouge_score; print(rouge_score.__version__)"
```text

**Solution**:
```bash
pip install --force-reinstall rouge-score>=0.1.2
```text

### Runner Raises Error on ROUGE Dict

**Issue**: Old external ROUGE implementation returns dict

**Solution**: Already handled! Runner checks for multiple dict keys:
- `rougeL_f` - Primary key
- `rougeL` - Alternate key  
- `f` - Generic f-measure
- `fmeasure` - Alternate spelling

If your implementation uses different keys, the test will fail with clear message showing available keys.

### Tests Fail With Import Errors

**Issue**: Missing test dependencies

**Solution**:
```bash
pip install pytest pytest-mock -q
# Or full dev install
pip install -r requirements-dev.txt
```text

## Performance Notes

- Tests complete in < 5 seconds
- BLEU/ROUGE computation is lightweight for test inputs
- No network calls required
- Safe for CI/CD pipelines

## See Also

- [Metrics Guide](../guides/metrics.md) - Complete metrics documentation
- [Repro Validation](Repro_Validation.md) - Reproducibility validation
- [Plugin Guide](../guides/plugins.md) - Custom metrics via plugins
