# Metrics Guide

> Comprehensive guide to evaluation metrics in the Codex ML framework

## Overview

The Codex ML framework provides a registry of deterministic evaluation metrics for assessing model performance. Metrics are categorized into:

1. **Core metrics** - Always available (no extra dependencies)
2. **Optional metrics** - Require additional dependencies (BLEU, ROUGE)

## Core Metrics

Core metrics are included with the base installation and require no additional dependencies:

| Metric | Description | Use Case |
|--------|-------------|----------|
| `token_accuracy` | Token-level accuracy | Token classification |
| `f1_score` | Micro/macro/binary F1 | Classification |
| `recall_score` | Micro/macro/binary recall | Classification |
| `perplexity` | Perplexity | Language modeling |

### Usage

```python
from codex_ml.metrics.api import get_metric

# Get a metric
accuracy = get_metric("token_accuracy")

# Compute score
score = accuracy(predictions, labels)
print(f"Accuracy: {score:.4f}")
```text

### Class-based metrics

The `codex_ml.metrics.metric_implementations` module provides stateful metric
classes used by the unified training loop. They accumulate batches and expose a
`compute()` method returning a dictionary of metric values:

```python
from codex_ml.metrics.metric_implementations import F1Score

metric = F1Score(average="micro")
metric.update([1, 0, 1], [1, 0, 0])
print(metric.compute()["f1_score"])
```text

### NDJSON summariser

Metrics emitted to NDJSON logs can be summarised via
`codex_ml.metrics.api.summarize_ndjson_logs(path)`, which validates every line
and returns the mean for each numeric field. Use the helper to produce quick
report cards or to sanity check offline runs:

```python
from codex_ml.metrics.api import summarize_ndjson_logs

summary = summarize_ndjson_logs("runs/train/metrics.ndjson")
print(summary["loss"])
```text

## Optional Metrics

Optional metrics require additional dependencies specified in `requirements-optional.txt`.

### BLEU (Bilingual Evaluation Understudy)

**Dependency:** `nltk>=3.8`

BLEU measures n-gram overlap between generated and reference text. Commonly used for machine translation and text generation.

**Installation:**
```bash
pip install nltk
# Or install all optional dependencies
pip install -r requirements-optional.txt
```text

**Usage:**
```python
from codex_ml.metrics.registry import get_metric

bleu = get_metric("bleu")

predictions = ["the cat sat on the mat"]
references = ["the cat sat on the mat"]

score = bleu(predictions, references)
# Returns: ~1.0 for perfect match
# Returns: None if nltk not installed
```text

**Characteristics:**
- Range: 0.0 to 1.0
- Higher is better
- Measures precision of n-grams (1-4 grams by default)
- Uses smoothing for short sequences
- Returns `None` if `nltk` is not installed

### ROUGE-L (Recall-Oriented Understudy for Gisting Evaluation)

**Dependency:** `rouge-score>=0.1.2`

ROUGE-L measures longest common subsequence (LCS) between generated and reference text. Commonly used for summarization evaluation.

**Installation:**
```bash
pip install rouge-score
# Or install all optional dependencies
pip install -r requirements-optional.txt
```text

**Usage:**
```python
from codex_ml.metrics.registry import get_metric

rouge = get_metric("rougeL")

predictions = ["the quick brown fox jumps"]
references = ["the quick brown fox jumped"]

score = rouge(predictions, references)
# Returns: F-measure of LCS
# Returns: None if rouge-score not installed
```text

**Characteristics:**
- Range: 0.0 to 1.0
- Higher is better
- Measures recall-oriented longest common subsequence
- F-measure of precision and recall
- Returns `None` if `rouge-score` is not installed

## Graceful Degradation

All optional metrics implement graceful degradation:

1. **Metric registered**: Metrics are registered in the registry regardless of dependency availability
2. **Callable returned**: `get_metric()` always returns a callable
3. **None on missing deps**: Metrics return `None` when dependencies are unavailable
4. **No exceptions**: Missing dependencies do not raise exceptions

Example:

```python
from codex_ml.metrics.registry import get_metric

# Always returns a callable, even if nltk not installed
bleu = get_metric("bleu")

# Returns None if nltk not available, otherwise returns score
score = bleu(["test"], ["test"])

if score is None:
    print("BLEU not available (missing nltk)")
else:
    print(f"BLEU score: {score:.4f}")
```text

## Installing Optional Dependencies

### All Optional Dependencies

Install all optional dependencies at once:

```bash
pip install -r requirements-optional.txt
```text

### Selective Installation

Install only specific metrics:

```bash
# BLEU only
pip install nltk

# ROUGE only
pip install rouge-score

# Both generative metrics
pip install nltk rouge-score
```text

### Extras Group (if configured in pyproject.toml)

```bash
# Install with extras group
pip install -e ".[metrics]"

# Or all optional features
pip install -e ".[all]"
```text

## Testing with Optional Dependencies

Tests automatically skip when dependencies are unavailable:

```bash
# Run all tests (skips tests requiring optional deps)
pytest tests/metrics/

# Run only if dependencies are installed
pytest tests/metrics/test_bleu_rouge.py

# Specific test
pytest tests/metrics/test_bleu_rouge.py::TestBLEUMetric::test_bleu_perfect_match
```text

## Adding Custom Metrics

### Register a Custom Metric

```python
from codex_ml.metrics.registry import register_metric

@register_metric("custom_accuracy")
def custom_accuracy(preds, targets):
    """Custom accuracy implementation."""
    correct = sum(p == t for p, t in zip(preds, targets))
    return correct / len(preds) if preds else 0.0
```text

### With Optional Dependencies

```python
from codex_ml.metrics.registry import register_metric

@register_metric("custom_bleu")
def custom_bleu(preds, targets):
    """Custom BLEU with optional dependency."""
    try:
        from some_package import compute_bleu
        return compute_bleu(preds, targets)
    except ImportError:
        # Return None if dependency not available
        return None
```text

### Using patch_registry for Optional Metrics

The `_optional_bleu_rouge` module provides a `patch_registry()` function to add BLEU/ROUGE metrics to a custom registry only if dependencies are available:

```python
from codex_ml.metrics._optional_bleu_rouge import patch_registry

# Create your custom registry
CUSTOM_METRICS = {}

# Patch it with optional metrics (only if nltk/rouge-score installed)
patch_registry(CUSTOM_METRICS)

# Use the metrics
if "bleu" in CUSTOM_METRICS:
    bleu_fn = CUSTOM_METRICS["bleu"]
    score = bleu_fn(["prediction"], ["reference"])
    print(f"BLEU: {score}")
else:
    print("BLEU not available (missing nltk)")
```text

**Benefits:**
- Graceful degradation: No errors if dependencies missing
- Idempotent: Safe to call multiple times
- Returns the same registry object (modified in place)

## Metric Registry API

### get_metric(name)

Retrieve a registered metric by name.

```python
from codex_ml.metrics.registry import get_metric

metric = get_metric("bleu")
score = metric(predictions, references)
```text

### list_metrics()

List all registered metric names:

```python
from codex_ml.metrics.registry import metric_registry

metrics = metric_registry.list()
print(f"Available metrics: {metrics}")
```text

### Metric Signature

All metrics follow this signature:

```python
def metric(
    preds: Sequence[str],
    targets: Sequence[str],
    **kwargs
) -> Optional[float]:
    """
    Compute metric score.
    
    Args:
        preds: Predicted sequences
        targets: Target/reference sequences
        **kwargs: Metric-specific parameters
        
    Returns:
        Float score or None if unavailable
    """
    ...
```text

## Common Patterns

### Check if Metric Available

```python
from codex_ml.metrics.registry import get_metric

bleu = get_metric("bleu")
test_score = bleu(["test"], ["test"])

if test_score is None:
    print("BLEU unavailable - install nltk")
else:
    print(f"BLEU available: {test_score}")
```text

### Compute Multiple Metrics

```python
from codex_ml.metrics.registry import get_metric

predictions = ["the cat sat on the mat"]
references = ["the cat sat on the mat"]

metrics = ["exact_match", "bleu", "rougeL"]
scores = {}

for metric_name in metrics:
    metric = get_metric(metric_name)
    score = metric(predictions, references)
    scores[metric_name] = score

# Filter out None values (unavailable metrics)
available_scores = {k: v for k, v in scores.items() if v is not None}
print(f"Scores: {available_scores}")
```text

## Troubleshooting

### BLEU Returns None

**Symptom:** BLEU metric returns `None` instead of a score

**Solution:** Install nltk:
```bash
pip install nltk
```text

### ROUGE Returns None

**Symptom:** ROUGE metric returns `None` instead of a score

**Solution:** Install rouge-score:
```bash
pip install rouge-score
```text

### ImportError During Metric Computation

**Symptom:** Metrics raise `ImportError` when called

**Solution:** This should not happen - metrics are designed to catch ImportError and return None. If you see this, it may be a bug. Please report it with:
- Python version
- Installed packages (`pip list`)
- Minimal reproduction code

## Related Documentation

- [Evaluation Guide](evaluation/README.md) - End-to-end evaluation workflows
- [Plugin API](plugins/Plugin_API_Broader.md) - Custom metric registration
- [Testing Guide](../tests/README.md) - Testing metrics with optional dependencies

## References

- [BLEU Paper](https://www.aclweb.org/anthology/P02-1040.pdf) - Original BLEU metric
- [ROUGE Paper](https://aclanthology.org/W04-1013/) - ROUGE metrics for summarization
- [nltk Documentation](https://www.nltk.org/) - NLTK library
- [rouge-score Documentation](https://github.com/google-research/google-research/tree/master/rouge) - Google's ROUGE implementation
