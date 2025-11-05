# Plugin System Guide

This guide explains how to extend codex_ml with custom plugins using Python entry points.

## Overview

Codex ML supports lightweight plugin discovery via Python entry points. The plugin system allows you to:

- Add custom metrics without modifying core code
- Register custom models, tokenizers, and datasets
- Extend functionality while maintaining backward compatibility
- Keep plugins optional and isolated

The plugin system integrates with codex_ml's registries, automatically discovering and loading plugins declared in your project's `pyproject.toml`.

## How It Works

1. **Declaration**: Plugins are declared as entry points in `pyproject.toml`
2. **Discovery**: At runtime, `codex_ml.plugins.load_plugins()` discovers entry points
3. **Loading**: Entry points are loaded and resolved to Python objects
4. **Registration**: Loaded objects are registered with the appropriate registry
5. **Usage**: Registered plugins become available via standard registry APIs

The plugin system is:
- **Additive**: Plugins supplement built-in functionality
- **Defensive**: Failing plugins are logged and skipped, not raised
- **Backward compatible**: Direct registration continues to work
- **Offline-first**: No network calls, graceful degradation

## Supported Plugin Types

| Plugin Type | Entry Point Group | Registry | Example Use Case |
|-------------|-------------------|----------|------------------|
| Metrics | `codex_ml.metrics` | `codex_ml.metrics.registry` | Custom evaluation metrics |
| Models | `codex_ml.models` | `codex_ml.plugins.models` | Custom model architectures |
| Tokenizers | `codex_ml.tokenizers` | `codex_ml.plugins.tokenizers` | Custom tokenization |
| Datasets | `codex_ml.datasets` | `codex_ml.plugins.datasets` | Custom data loaders |
| Trainers | `codex_ml.trainers` | `codex_ml.plugins.trainers` | Custom training loops |

## Creating a Metric Plugin

### Step 1: Implement Your Metric

Create a metric function that follows the standard signature:

```python
# my_package/metrics.py

def custom_accuracy(predictions, targets, **kwargs):
    """Custom accuracy metric with special handling.
    
    Parameters
    ----------
    predictions : Sequence
        Model predictions
    targets : Sequence
        Ground truth targets
    **kwargs : dict
        Additional keyword arguments
    
    Returns
    -------
    float
        Accuracy score between 0.0 and 1.0
    """
    correct = sum(p == t for p, t in zip(predictions, targets))
    total = len(predictions)
    return correct / total if total > 0 else 0.0


def weighted_f1(predictions, targets, weights=None):
    """F1 score with optional class weights.
    
    Returns
    -------
    float or dict
        F1 score (float) or dict of per-class scores
    """
    # Implementation here
    return 0.85
```

**Requirements**:
- Deterministic: Same inputs always produce same outputs
- Side-effect free: No global state modification
- Type hints: Helps users understand expected inputs/outputs
- Docstring: Explain parameters and return values

### Step 2: Declare Entry Points

Add entry points to your `pyproject.toml`:

```toml
[project.entry-points."codex_ml.metrics"]
custom_accuracy = "my_package.metrics:custom_accuracy"
weighted_f1 = "my_package.metrics:weighted_f1"
```

**Format**: `entry_name = "module.path:function_name"`

### Step 3: Install Your Package

Install your package in the same environment as codex_ml:

```bash
# Development install
pip install -e /path/to/my_package

# Or from PyPI
pip install my_package
```

### Step 4: Use Your Plugin

```python
from codex_ml.metrics.registry import get_metric, list_metrics, init_metric_plugins

# Initialize plugins (done automatically on first use)
init_metric_plugins()

# List all available metrics (includes your plugins)
print(list_metrics())
# Output: ['exact_match', 'f1', 'bleu', 'custom_accuracy', 'weighted_f1', ...]

# Get and use your custom metric
metric = get_metric("custom_accuracy")
score = metric(predictions=["a", "b", "c"], targets=["a", "b", "d"])
print(f"Score: {score}")  # Output: Score: 0.666...
```

## Advanced Plugin Patterns

### Plugin with Setup Hook

For plugins that need initialization:

```python
# my_package/metrics.py

class CustomMetric:
    """Metric plugin with initialization."""
    
    def __init__(self, config=None):
        self.config = config or {}
    
    def __call__(self, predictions, targets):
        # Use self.config for behavior
        return self.compute(predictions, targets)
    
    def compute(self, predictions, targets):
        # Implementation
        return 0.9
    
    @staticmethod
    def register(register_fn):
        """Plugin hook called by loader."""
        instance = CustomMetric(config={"threshold": 0.5})
        register_fn("custom_metric", instance)

# Entry point:
# custom_metric_plugin = "my_package.metrics:CustomMetric"
```

### Plugin with Optional Dependencies

Handle optional dependencies gracefully:

```python
def rouge_variant(predictions, targets):
    """ROUGE variant that requires optional dependency."""
    try:
        from rouge_score import rouge_scorer
    except ImportError:
        # Return None when dependency is missing
        return None
    
    scorer = rouge_scorer.RougeScorer(["rouge1"], use_stemmer=True)
    scores = [
        scorer.score(t, p)["rouge1"].fmeasure
        for p, t in zip(predictions, targets)
    ]
    return sum(scores) / len(scores) if scores else None
```

### Multi-Metric Plugin

Register multiple metrics from one entry point:

```python
def register_suite(register_fn):
    """Register a suite of related metrics."""
    
    def metric_a(preds, targets):
        return 0.5
    
    def metric_b(preds, targets):
        return 0.7
    
    # Register multiple metrics
    register_fn("suite_metric_a", metric_a)
    register_fn("suite_metric_b", metric_b)

# Entry point:
# metric_suite = "my_package.metrics:register_suite"
```

## Testing Your Plugin

Create tests to verify your plugin works:

```python
# tests/test_my_plugin.py
import pytest
from codex_ml.metrics.registry import get_metric, init_metric_plugins


def test_custom_accuracy_plugin_loads():
    """Verify plugin is discovered and registered."""
    # Force reload to test discovery
    init_metric_plugins(force=True)
    
    # Should be able to retrieve the metric
    metric = get_metric("custom_accuracy")
    assert callable(metric)


def test_custom_accuracy_correctness():
    """Verify metric computes correctly."""
    metric = get_metric("custom_accuracy")
    
    # Perfect match
    score = metric(["a", "b", "c"], ["a", "b", "c"])
    assert score == 1.0
    
    # Partial match
    score = metric(["a", "b", "c"], ["a", "b", "d"])
    assert abs(score - 0.666) < 0.01


def test_plugin_handles_edge_cases():
    """Verify plugin handles edge cases."""
    metric = get_metric("custom_accuracy")
    
    # Empty inputs
    score = metric([], [])
    assert score == 0.0
    
    # Mismatched lengths (if supported)
    # score = metric(["a"], ["a", "b"])
    # assert ...
```

## Best Practices

### 1. Defensive Implementation

```python
def safe_metric(predictions, targets):
    """Metric with defensive checks."""
    # Validate inputs
    if not predictions or not targets:
        return 0.0
    
    if len(predictions) != len(targets):
        raise ValueError(f"Length mismatch: {len(predictions)} vs {len(targets)}")
    
    # Compute with error handling
    try:
        result = compute_score(predictions, targets)
        return float(result)
    except Exception as e:
        # Log error and return safe default
        import logging
        logging.warning(f"Metric computation failed: {e}")
        return 0.0
```

### 2. Clear Documentation

```python
def documented_metric(predictions, targets, threshold=0.5):
    """Compute accuracy with confidence threshold.
    
    Predictions below the threshold are treated as incorrect.
    
    Parameters
    ----------
    predictions : Sequence[str]
        Predicted labels
    targets : Sequence[str]
        Ground truth labels
    threshold : float, default=0.5
        Minimum confidence threshold (if using probabilities)
    
    Returns
    -------
    float
        Accuracy score between 0.0 and 1.0
    
    Examples
    --------
    >>> metric(["a", "b"], ["a", "b"])
    1.0
    >>> metric(["a", "b"], ["a", "c"])
    0.5
    
    Notes
    -----
    This metric is deterministic and suitable for offline evaluation.
    """
    # Implementation
    pass
```

### 3. Deterministic Behavior

```python
# Good: Deterministic
def deterministic_metric(predictions, targets):
    return sum(p == t for p, t in zip(predictions, targets)) / len(predictions)

# Avoid: Non-deterministic
def non_deterministic_metric(predictions, targets):
    import random
    # Don't use random sampling without fixed seed
    sample = random.sample(list(zip(predictions, targets)), k=10)
    return score(sample)
```

### 4. Optional Dependencies

```python
def metric_with_optional_dep(predictions, targets):
    """Metric using optional dependency."""
    try:
        import optional_lib
    except ImportError:
        # Return None to signal dependency is missing
        return None
    
    # Use optional_lib for computation
    return optional_lib.compute(predictions, targets)
```

## Troubleshooting

### Plugin Not Discovered

**Problem**: Your plugin doesn't appear in `list_metrics()`

**Solutions**:
1. Verify entry point declaration in `pyproject.toml`
2. Reinstall package: `pip install -e .`
3. Force plugin reload: `init_metric_plugins(force=True)`
4. Check for import errors in plugin module

```python
# Debug plugin discovery
import logging
logging.basicConfig(level=logging.DEBUG)

from codex_ml.metrics.registry import init_metric_plugins
count = init_metric_plugins(force=True)
print(f"Loaded {count} plugins")
```

### Import Errors

**Problem**: Plugin fails to load with ImportError

**Solution**: Check plugin dependencies are installed

```python
# In your plugin
try:
    from required_dependency import something
except ImportError as e:
    # Provide helpful error message
    raise ImportError(
        f"Plugin 'my_metric' requires 'required_dependency'. "
        f"Install with: pip install required_dependency"
    ) from e
```

### Registration Conflicts

**Problem**: Plugin name conflicts with built-in metric

**Solution**: Use `override=True` or choose unique name

```python
# In your plugin's register hook
def register(register_fn):
    # Override built-in metric (use with caution)
    register_fn("f1", custom_f1, override=True)
    
    # Or use unique name
    register_fn("custom_f1", custom_f1)
```

## See Also

- [Metrics Guide](metrics.md) - Built-in metrics and usage
- [Evaluation Guide](../reference/eval_runner.md) - Running evaluations
- [Plugin Loader API](../reference/plugins.md) - Plugin loader reference
- [Python Packaging Guide](https://packaging.python.org/guides/creating-and-discovering-plugins/)
