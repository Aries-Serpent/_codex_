# Evaluation Metrics Guide

This guide documents the built-in metrics available in the `codex_ml` evaluation framework and how to use them for model assessment.

## Overview

The metrics registry (`codex_ml.metrics.registry`) provides a collection of deterministic, reproducible metrics for evaluating model performance. All metrics are designed to work offline without requiring external API calls.

## Available Metrics

### Token-Level Metrics

#### `accuracy@token` / `token_accuracy`
Computes token-level accuracy for sequence predictions.

**Usage**:
```python
from codex_ml.metrics.registry import get_metric

metric = get_metric("accuracy@token")
score = metric(predictions=[1, 2, 3], targets=[1, 2, 4], ignore_index=-100)
# Returns: 0.666 (2 out of 3 tokens correct)
```

**Parameters**:
- `preds`: Sequence of predicted token IDs
- `targets`: Sequence of target token IDs
- `ignore_index`: Token ID to ignore (default: -100)

### Text-Level Metrics

#### `exact_match`
Computes exact string match after normalization (lowercase, whitespace collapse).

**Usage**:
```python
metric = get_metric("exact_match")
score = metric(
    preds=["hello world", "test"],
    targets=["Hello  World", "test"]
)
# Returns: 1.0 (both match after normalization)
```

**Parameters**:
- `remove_punct`: Whether to remove punctuation before comparison (default: False)

#### `f1`
Computes average per-example F1 score over whitespace-tokenized words (bag-of-words).

**Usage**:
```python
metric = get_metric("f1")
score = metric(
    preds=["the cat sat on mat"],
    targets=["the cat sat on the mat"]
)
# Returns F1 based on token overlap
```

### Generative Metrics

#### `bleu`
Computes corpus-level BLEU score using NLTK's implementation with smoothing.

**Optional dependency**: `nltk`

**Usage**:
```python
metric = get_metric("bleu")
score = metric(
    preds=["the cat sat on the mat", "hello world"],
    targets=["a cat sat on a mat", "hello there"]
)
# Returns: BLEU score (0.0-1.0), or None if nltk unavailable
```

**Notes**:
- Uses NLTK's `SmoothingFunction().method3` for corpus BLEU
- Automatically normalizes and tokenizes text
- Returns `None` if nltk is not installed (graceful degradation)

#### `rougeL`
Computes ROUGE-L F-measure using the `rouge_score` library.

**Optional dependency**: `rouge_score`

**Usage**:
```python
metric = get_metric("rougeL")
score = metric(
    preds=["the quick brown fox jumps"],
    targets=["the quick brown fox jumped"]
)
# Returns: ROUGE-L F-measure (0.0-1.0), or None if rouge_score unavailable
```

**Notes**:
- Uses stemming for better matching
- Measures longest common subsequence
- Returns `None` if rouge_score is not installed

#### `chrf`
Character-level F-score metric.

**Optional dependencies**: `sacrebleu` (preferred) or `nltk`

**Usage**:
```python
metric = get_metric("chrf")
score = metric(preds=["hello"], targets=["helo"])
# Returns: chrF score or None
```

### Diversity Metrics

#### `dist-1` / `dist-2`
Measures lexical diversity as the ratio of unique unigrams (dist-1) or bigrams (dist-2) to total tokens.

**Usage**:
```python
metric = get_metric("dist-1")
score = metric(preds=["the cat the dog", "test test"], targets=None)
# Returns: proportion of unique unigrams
```

**Notes**:
- Higher values indicate more diverse vocabulary
- Useful for assessing generation quality
- `targets` parameter is ignored (not used for diversity)

### Language Model Metrics

#### `ppl` / `perplexity`
Computes perplexity from negative log-likelihood values.

**Usage**:
```python
metric = get_metric("ppl")

# From sequence of NLL values
score = metric([2.3, 1.8, 2.1])  # Returns: exp(mean(nll))

# From sum and count
score = metric(nll_sum=100.0, n_tokens=50)  # Returns: exp(100/50)
```

### Offline Metrics

#### `offline:weighted-accuracy`
Weighted accuracy that loads class weights from a local JSON fixture.

**Configuration**:
Set `CODEX_ML_WEIGHTED_ACCURACY_PATH` or `CODEX_ML_OFFLINE_METRICS_DIR` environment variable to point to a JSON file with class weights:

```json
{
  "class_a": 1.0,
  "class_b": 2.0,
  "class_c": 0.5
}
```

**Usage**:
```python
metric = get_metric("offline:weighted-accuracy")
score = metric(
    preds=["class_a", "class_b"],
    targets=["class_a", "class_c"],
    weights_path="/path/to/weights.json"
)
```

## Using Metrics in Evaluation

### With `run_evaluation`

```python
from codex_ml.config import EvaluationConfig
from codex_ml.eval.runner import run_evaluation

cfg = EvaluationConfig(
    dataset_path="data/eval.jsonl",
    dataset_format="jsonl",
    metrics=["exact_match", "f1", "bleu", "rougeL"],
    output_dir="results/eval_001",
    seed=42,
    prediction_field="prediction",
    target_field="target",
    text_field="text",
)

results = run_evaluation(cfg)
print(results["metrics"])
# Output: {'exact_match': 0.85, 'f1': 0.92, 'bleu': 0.45, 'rougeL': 0.78}
```

### Listing Available Metrics

```python
from codex_ml.metrics.registry import list_metrics

available = list_metrics()
print(available)
# ['accuracy@token', 'token_accuracy', 'ppl', 'exact_match', 'f1', 'bleu', 'rougeL', ...]
```

## Reproducibility

All built-in metrics are deterministic and produce identical results given the same inputs. Key features:

1. **Deterministic text normalization**: Consistent lowercase, whitespace handling
2. **Fixed random seeds**: Not applicable (metrics are deterministic functions)
3. **No external API calls**: All computations are local
4. **Offline-first**: Optional dependencies gracefully degrade to `None` returns

## Custom Metrics

### Registering a Custom Metric

```python
from codex_ml.metrics.registry import register_metric

@register_metric("custom_score")
def my_custom_metric(preds, targets):
    """Compute custom metric."""
    # Your implementation
    return score
```

### Plugin-Based Metrics

For distributable custom metrics, use entry points in your `pyproject.toml`:

```toml
[project.entry-points."codex_ml.metrics"]
my_metric = "my_package.metrics:my_metric_function"
```

The metric will be automatically discovered and registered.

## Testing Metrics

When adding new metrics, include tests that verify:

1. **Correctness**: Known inputs produce expected outputs
2. **Edge cases**: Empty inputs, None values, identical pred/target
3. **Graceful degradation**: Missing optional dependencies return None
4. **Determinism**: Multiple calls with same inputs return same result

Example test:

```python
def test_bleu_metric_correctness():
    from codex_ml.metrics.registry import get_metric
    
    metric = get_metric("bleu")
    
    # Perfect match
    score = metric(preds=["hello"], targets=["hello"])
    assert score == 1.0 or score is None  # None if nltk missing
    
    # No match
    score = metric(preds=["hello"], targets=["goodbye"])
    assert score is not None and score < 0.3 or score is None
```

## Troubleshooting

### Metric returns None
Some metrics require optional dependencies. Install them:

```bash
pip install nltk rouge_score sacrebleu
```

### ImportError for metric dependencies
The registry gracefully handles missing dependencies. Check which dependencies are needed:

- `bleu`: requires `nltk`
- `rougeL`: requires `rouge_score`
- `chrf`: requires `sacrebleu` or `nltk`

### Different results across runs
Ensure all metrics are called with the same:
- Input normalization settings
- Text preprocessing
- Seed values (though built-in metrics are deterministic)

## See Also

- [Evaluation Runner Documentation](../reference/eval_runner.md)
- [Reproducibility Guide](../repro.md)
- [Testing Guide](TESTING_GUIDE.md)
