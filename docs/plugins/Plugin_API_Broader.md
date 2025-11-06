# Plugin API - Broader Factory System

> Comprehensive guide to the Codex plugin system and factory registries

## Overview

The Codex plugin system provides extensibility through:

1. **Factory Registries** - Runtime registration of models, metrics, data loaders, and more
2. **Entry Points** - Python package entry points for plugin discovery
3. **Adapter Interfaces** - Standard interfaces for plugin implementations

## Stable Registry Names

The Codex plugin system uses frozen, stable registry names defined in `codex_addons/registry_names.py`. These names form part of the public API and follow a strict stability guarantee.

### Canonical Registry Names

| Registry Kind | Stable Names | Description |
|---------------|--------------|-------------|
| `metrics` | `token_accuracy`, `ppl`, `exact_match`, `f1`, `bleu`, `rouge` | Evaluation metrics |
| `models` | `minilm`, `bert_base_uncased`, `gpt2` | Model factories |
| `data_loaders` | `lines`, `jsonl`, `csv`, `parquet` | Data loading functions |
| `tokenizers` | `hf`, `sentencepiece` | Tokenizer factories |
| `trainers` | `functional`, `hf_trainer` | Training loop implementations |

**Stability guarantee:** Names in these registries will not be removed or changed without a deprecation cycle spanning at least two minor releases.

### Querying Stable Names

```python
from codex_addons.registry_names import (
    ALL_REGISTRY_NAMES,
    get_all_stable_names,
    is_stable_name,
    get_description,
)

# Get all stable names across all registries
all_names = get_all_stable_names()

# Check if a name is stable
if is_stable_name("metrics", "token_accuracy"):
    print("✓ Stable metric name")

# Get description for a stable name
desc = get_description("metrics", "f1")
print(f"F1 score: {desc}")
```

### Entry Point Groups

The following entry point groups are **stable** and part of the public API:

| Group Name | Purpose | Example Plugins |
|------------|---------|-----------------|
| `codex_ml.plugins` | General-purpose plugins | hello, custom_callbacks |
| `codex_ml.models` | Model factories | minilm, bert_base_uncased |
| `codex_ml.metrics` | Metric implementations | token_accuracy, ppl, exact_match, f1 |
| `codex_ml.data_loaders` | Data loading functions | lines, jsonl, csv |
| `codex_ml.tokenizers` | Tokenizer factories | hf, sentencepiece |
| `codex_ml.trainers` | Training loop implementations | functional, custom |

### Registry Classes

All registries follow a consistent API pattern with **stable ordering** and **idempotent registration**:

```python
from codex_addons.registry import Registry

# Create a registry
registry = Registry(kind="my_components")

# Register items (idempotent - can call multiple times safely)
@registry.register("my_component")
class MyComponent:
    pass

# List registered names (stable sorted order)
names = registry.list()  # Always returns same order
assert names == sorted(names)  # Always sorted

# Get a registered item
item = registry.get("my_component")

# Check membership
if "my_component" in registry:
    print("✓ Component registered")
```

**Key guarantees:**
- `list()` and `names()` always return names in **sorted order** (deterministic across runs)
- `register()` is **idempotent** - registering the same object twice is a no-op
- Registry names are **case-sensitive**

### Registration Lifecycle

```python
from codex_addons.registry import Registry

registry = Registry(kind="metrics")

# 1. Initial registration
@registry.register("accuracy")
def my_accuracy(preds, labels):
    return sum(p == l for p, l in zip(preds, labels)) / len(labels)

# 2. Idempotent re-registration (no-op)
registry.register("accuracy", my_accuracy)  # Silent no-op

# 3. Re-registration with different object (warns)
@registry.register("accuracy")  # Warns about re-registration
def new_accuracy(preds, labels):
    # New implementation
    return calculate_accuracy_v2(preds, labels)

# 4. Query registration
assert "accuracy" in registry
assert len(registry) == 1
assert registry.list() == ["accuracy"]
```

## Plugin Development

### Creating a Metric Plugin

```python
# my_metrics.py
def custom_accuracy(predictions, labels):
    """Calculate custom accuracy metric.
    
    Args:
        predictions: Model predictions
        labels: Ground truth labels
        
    Returns:
        float: Accuracy score
    """
    correct = sum(p == l for p, l in zip(predictions, labels))
    return correct / len(labels) if labels else 0.0


# Mark as Codex v1 API
custom_accuracy.__codex_api__ = "v1"
```

**Register via entry point** (in `pyproject.toml`):

```toml
[project.entry-points."codex_ml.metrics"]
custom_accuracy = "my_package.my_metrics:custom_accuracy"
```

### Creating a Model Plugin

```python
# my_models.py
from transformers import AutoModel, AutoTokenizer


def load_custom_model(config):
    """Factory function for custom model.
    
    Args:
        config: Model configuration dict
            - model_name: Hugging Face model name
            - device: Target device (cpu/cuda)
            
    Returns:
        tuple: (model, tokenizer)
    """
    model_name = config.get("model_name", "bert-base-uncased")
    device = config.get("device", "cpu")
    
    model = AutoModel.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    model.to(device)
    
    return model, tokenizer


load_custom_model.__codex_api__ = "v1"
```

**Register via entry point**:

```toml
[project.entry-points."codex_ml.models"]
custom = "my_package.my_models:load_custom_model"
```

### Creating a Data Loader Plugin

```python
# my_loaders.py
import json
from pathlib import Path


def load_custom_format(path, **kwargs):
    """Load data from custom format.
    
    Args:
        path: Path to data file
        **kwargs: Additional loader options
        
    Yields:
        dict: Data records
    """
    path = Path(path)
    
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


load_custom_format.__codex_api__ = "v1"
```

**Register via entry point**:

```toml
[project.entry-points."codex_ml.data_loaders"]
custom_format = "my_package.my_loaders:load_custom_format"
```

## Adapter Interfaces

### Metric Adapter

All metrics should follow this interface:

```python
from typing import Any, List


def metric_adapter(predictions: List[Any], labels: List[Any]) -> float:
    """Standard metric interface.
    
    Args:
        predictions: Model predictions
        labels: Ground truth labels
        
    Returns:
        Metric score (higher is better)
        
    Raises:
        ValueError: If inputs are incompatible
    """
    # Implementation
    pass
```

### Model Factory Adapter

Model factories should follow this interface:

```python
from typing import Any, Dict, Tuple


def model_factory(config: Dict[str, Any]) -> Tuple[Any, Any]:
    """Standard model factory interface.
    
    Args:
        config: Model configuration
            - model_name: str
            - device: str
            - dtype: str
            - Additional model-specific options
            
    Returns:
        tuple: (model, tokenizer) or (model, None)
        
    Raises:
        ValueError: If config is invalid
        ImportError: If required dependencies unavailable
    """
    # Implementation
    pass
```

### Data Loader Adapter

Data loaders should follow this interface:

```python
from pathlib import Path
from typing import Any, Dict, Iterator


def data_loader(path: str | Path, **kwargs: Any) -> Iterator[Dict[str, Any]]:
    """Standard data loader interface.
    
    Args:
        path: Path to data file or directory
        **kwargs: Loader-specific options
            
    Yields:
        Data records as dictionaries
        
    Raises:
        FileNotFoundError: If path doesn't exist
        ValueError: If data format is invalid
    """
    # Implementation
    pass
```

## Usage Examples

### Listing Available Plugins

```python
from codex_ml.plugins.registry import discover

# Discover all plugins
plugins = discover(group="codex_ml.plugins")
print(f"Found {len(plugins)} plugins:")
for name, plugin in plugins.items():
    print(f"  - {name}: {plugin}")

# Discover metrics
metrics = discover(group="codex_ml.metrics")
print(f"Available metrics: {list(metrics.keys())}")
```

### Using Registered Components

```python
from codex_ml.metrics.registry import BUILTIN_METRICS

# Use a built-in metric
if "accuracy" in BUILTIN_METRICS:
    accuracy_fn = BUILTIN_METRICS["accuracy"]
    score = accuracy_fn([1, 2, 3], [1, 2, 0])
    print(f"Accuracy: {score}")
```

### Loading from Entry Points

```python
from codex_ml.plugins.registry import Registry

# Create registry and load from entry points
registry = Registry(kind="custom_components")
count, errors = registry.load_from_entry_points(
    group="my_app.components",
    require_api="v1"
)

print(f"Loaded {count} components")
if errors:
    print("Errors:", errors)

# List loaded components
print("Available:", registry.names())

# Use a component
component = registry.resolve_and_instantiate("my_component", option="value")
```

## API Versioning

Plugins can declare their API version:

```python
def my_plugin():
    pass

# Declare v1 API
my_plugin.__codex_api__ = "v1"

# Legacy attribute also supported
my_plugin.__codex_ext_api__ = "v1"
```

When loading plugins, specify the required API version:

```python
registry.load_from_entry_points(
    group="codex_ml.plugins",
    require_api="v1"  # Only load v1 plugins
)
```

## Best Practices

### 1. Use Descriptive Names

```python
# Good
@registry.register("bert_large_sentiment")

# Avoid
@registry.register("model1")
```

### 2. Provide Metadata

```python
@registry.register(
    "custom_metric",
    category="classification",
    requires=["numpy", "scipy"]
)
```

### 3. Handle Missing Dependencies

```python
def load_optional_component(config):
    try:
        import optional_library
    except ImportError:
        raise ImportError(
            "optional_library required for this component. "
            "Install with: pip install optional_library"
        )
    # Implementation
```

### 4. Validate Configuration

```python
def model_factory(config):
    required = ["model_name", "device"]
    for key in required:
        if key not in config:
            raise ValueError(f"Missing required config key: {key}")
    # Implementation
```

### 5. Document Return Types

```python
def data_loader(path: str) -> Iterator[Dict[str, Any]]:
    """
    Yields:
        dict: Record with keys:
            - text: str
            - label: int
            - metadata: dict
    """
    # Implementation
```

## Troubleshooting

### Plugin Not Found

```python
from codex_ml.plugins.registry import discover

# Check if plugin is registered
plugins = discover(group="codex_ml.plugins")
if "my_plugin" not in plugins:
    print("Plugin not found. Check entry point configuration.")
```

### Import Errors

```python
registry = Registry(kind="test")
count, errors = registry.load_from_entry_points(group="my_group")

# Check for import errors
for name, error in errors.items():
    print(f"Failed to load {name}: {error}")
```

### Duplicate Registrations

The registry will warn about duplicates but keep the first registration:

```python
import warnings

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    
    @registry.register("duplicate")
    def func1():
        pass
    
    @registry.register("duplicate")
    def func2():
        pass
    
    if w:
        print(f"Warning: {w[0].message}")
```

## Migration Guide

### From Manual Registration to Entry Points

**Before:**

```python
# In main code
from my_metrics import accuracy, f1
METRICS = {"accuracy": accuracy, "f1": f1}
```

**After:**

```python
# In plugin module
accuracy.__codex_api__ = "v1"
f1.__codex_api__ = "v1"
```

```toml
# In pyproject.toml
[project.entry-points."codex_ml.metrics"]
accuracy = "my_package.my_metrics:accuracy"
f1 = "my_package.my_metrics:f1"
```

```python
# In main code - auto-discovered
from codex_ml.plugins.registry import discover
metrics = discover(group="codex_ml.metrics")
```

## Testing Plugins

### Unit Tests

```python
def test_my_metric():
    from my_package.my_metrics import custom_accuracy
    
    preds = [1, 2, 3, 1]
    labels = [1, 2, 0, 1]
    
    score = custom_accuracy(preds, labels)
    assert score == 0.75  # 3 out of 4 correct
```

### Integration Tests

```python
def test_plugin_discovery():
    from codex_ml.plugins.registry import get
    
    plugin = get("my_plugin", group="codex_ml.plugins")
    assert plugin is not None
    assert callable(plugin)
```

## Related Documentation

- [API Documentation](../api/README.md) - Auto-generated API reference
- [Metrics Guide](../guides/metrics.md) - Implementing custom metrics
- [Examples](../../examples/plugins/) - Example plugin implementations

## Support

- GitHub Issues: Tag with `[plugins]`
- Example Plugins: See `examples/plugins/` directory
- Tests: See `tests/plugins/` for usage examples
