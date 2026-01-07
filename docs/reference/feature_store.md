# Feature Store API Reference

## Overview

The Feature Store provides centralized management of feature definitions, versioning, and materialization for machine learning pipelines. It enables:

- **Feature Definition**: Define reusable feature transformations
- **Versioning**: Track feature versions with metadata
- **Materialization**: Cache computed features for performance
- **Health Monitoring**: Monitor feature freshness and quality
- **Caching**: Automatic caching of expensive computations

## Core Classes

### FeatureStore

Main class for managing features and feature groups.

#### Constructor

```python
FeatureStore(store_path: Path | str)
```

**Parameters:**
- `store_path`: Path to feature store directory (created if doesn't exist)

**Example:**
```python
from codex_ml.features import FeatureStore

store = FeatureStore("/path/to/feature/store")
```

#### Methods

##### `register_feature_group(group: FeatureGroup) -> None`

Register a feature group with the store.

**Parameters:**
- `group`: FeatureGroup instance to register

**Example:**
```python
from codex_ml.features import Feature, FeatureGroup

# Define features
def normalize_text(inputs):
    return inputs["text"].lower().strip()

text_feature = Feature(
    name="normalized_text",
    transform_fn=normalize_text,
    dependencies=["text"]
)

# Create group
text_group = FeatureGroup(
    name="text_features",
    features=[text_feature],
    version="1.0.0",
    description="Text preprocessing features"
)

# Register
store.register_feature_group(text_group)
```

##### `get_feature_group(name: str) -> Optional[FeatureGroup]`

Retrieve a registered feature group by name.

**Parameters:**
- `name`: Name of the feature group

**Returns:**
- `FeatureGroup` if found, `None` otherwise

**Example:**
```python
group = store.get_feature_group("text_features")
if group:
    print(f"Group version: {group.version}")
```

##### `materialize_features(group_name: str, inputs: Dict[str, Any]) -> Dict[str, Any]`

Compute and cache features for a group.

**Parameters:**
- `group_name`: Name of the feature group
- `inputs`: Input data dictionary

**Returns:**
- Dictionary mapping feature names to computed values

**Example:**
```python
inputs = {"text": "  Hello World  ", "label": 1}
features = store.materialize_features("text_features", inputs)
# Returns: {"normalized_text": "hello world"}
```

##### `get_cached_features(cache_key: str) -> Optional[Dict[str, Any]]`

Retrieve cached feature values.

**Parameters:**
- `cache_key`: Cache key (typically computed from inputs)

**Returns:**
- Cached features if available, `None` otherwise

**Example:**
```python
cache_key = store.compute_cache_key(inputs)
cached = store.get_cached_features(cache_key)
if cached:
    features = cached
else:
    features = store.materialize_features("text_features", inputs)
```

##### `clear_cache() -> None`

Clear all cached feature values.

**Example:**
```python
store.clear_cache()
```

---

### Feature

Represents a single feature definition.

#### Constructor

```python
Feature(
    name: str,
    transform_fn: Callable,
    dependencies: List[str] = [],
    metadata: Optional[FeatureMetadata] = None
)
```

**Parameters:**
- `name`: Unique feature name
- `transform_fn`: Function that computes the feature value
- `dependencies`: List of input field names required
- `metadata`: Optional metadata (version, description, etc.)

**Example:**
```python
def word_count(inputs):
    return len(inputs["text"].split())

word_count_feature = Feature(
    name="word_count",
    transform_fn=word_count,
    dependencies=["text"]
)
```

#### Methods

##### `compute(inputs: Dict[str, Any]) -> Any`

Compute feature value from inputs.

**Parameters:**
- `inputs`: Dictionary containing all required dependencies

**Returns:**
- Computed feature value

**Example:**
```python
result = word_count_feature.compute({"text": "Hello world"})
# Returns: 2
```

---

### FeatureGroup

Collection of related features.

#### Constructor

```python
FeatureGroup(
    name: str,
    features: List[Feature],
    version: str,
    description: str = ""
)
```

**Parameters:**
- `name`: Group name
- `features`: List of Feature instances
- `version`: Semantic version (e.g., "1.0.0")
- `description`: Human-readable description

**Example:**
```python
text_features = FeatureGroup(
    name="text_processing",
    features=[normalized_text, word_count, char_count],
    version="1.2.0",
    description="Text preprocessing and statistics"
)
```

#### Methods

##### `get_feature(name: str) -> Optional[Feature]`

Get a specific feature from the group.

**Parameters:**
- `name`: Feature name

**Returns:**
- Feature if found, None otherwise

**Example:**
```python
feature = text_features.get_feature("word_count")
```

---

### FeatureMetadata

Metadata for a feature.

#### Constructor

```python
FeatureMetadata(
    name: str,
    version: str,
    dtype: str,
    description: str,
    created_at: str,
    updated_at: str,
    tags: Dict[str, Any] = {}
)
```

**Parameters:**
- `name`: Feature name
- `version`: Feature version
- `dtype`: Data type (e.g., "int", "float", "str")
- `description`: Feature description
- `created_at`: ISO 8601 timestamp
- `updated_at`: ISO 8601 timestamp
- `tags`: Additional metadata

**Example:**
```python
from datetime import datetime

metadata = FeatureMetadata(
    name="word_count",
    version="1.0.0",
    dtype="int",
    description="Number of words in text",
    created_at=datetime.now().isoformat(),
    updated_at=datetime.now().isoformat(),
    tags={"category": "text", "priority": "high"}
)
```

#### Methods

##### `to_dict() -> dict`

Convert metadata to dictionary.

**Returns:**
- Dictionary representation

---

## Complete Example

### Text Feature Pipeline

```python
from codex_ml.features import Feature, FeatureGroup, FeatureStore, FeatureMetadata
from datetime import datetime

# Initialize store
store = FeatureStore("/tmp/features")

# Define feature transformations
def normalize_text(inputs):
    """Lowercase and strip whitespace."""
    return inputs["text"].lower().strip()

def word_count(inputs):
    """Count words in text."""
    return len(inputs["text"].split())

def char_count(inputs):
    """Count characters in text."""
    return len(inputs["text"])

def avg_word_length(inputs):
    """Average word length."""
    words = inputs["text"].split()
    if not words:
        return 0.0
    return sum(len(w) for w in words) / len(words)

# Create features with metadata
text_feature = Feature(
    name="normalized_text",
    transform_fn=normalize_text,
    dependencies=["text"],
    metadata=FeatureMetadata(
        name="normalized_text",
        version="1.0.0",
        dtype="str",
        description="Normalized text (lowercase, trimmed)",
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat(),
        tags={"type": "preprocessing"}
    )
)

word_count_feature = Feature(
    name="word_count",
    transform_fn=word_count,
    dependencies=["text"]
)

char_count_feature = Feature(
    name="char_count",
    transform_fn=char_count,
    dependencies=["text"]
)

avg_word_len_feature = Feature(
    name="avg_word_length",
    transform_fn=avg_word_length,
    dependencies=["text"]
)

# Create feature group
text_group = FeatureGroup(
    name="text_statistics",
    features=[text_feature, word_count_feature, char_count_feature, avg_word_len_feature],
    version="1.0.0",
    description="Text preprocessing and statistical features"
)

# Register with store
store.register_feature_group(text_group)

# Materialize features
inputs = {
    "text": "  Hello World! This is a test.  ",
    "label": 1
}

features = store.materialize_features("text_statistics", inputs)
print(features)
# Output:
# {
#   "normalized_text": "hello world! this is a test.",
#   "word_count": 6,
#   "char_count": 33,
#   "avg_word_length": 4.0
# }
```

### Numerical Feature Pipeline

```python
import numpy as np

# Define numerical features
def log_transform(inputs):
    """Log transform of value."""
    return np.log1p(inputs["value"])

def standardize(inputs):
    """Z-score normalization."""
    mean = inputs.get("mean", 0.0)
    std = inputs.get("std", 1.0)
    return (inputs["value"] - mean) / std

def binned_value(inputs):
    """Bin value into categories."""
    value = inputs["value"]
    if value < 10:
        return "low"
    elif value < 50:
        return "medium"
    else:
        return "high"

# Create features
log_feature = Feature(
    name="log_value",
    transform_fn=log_transform,
    dependencies=["value"]
)

std_feature = Feature(
    name="standardized_value",
    transform_fn=standardize,
    dependencies=["value", "mean", "std"]
)

bin_feature = Feature(
    name="value_bin",
    transform_fn=binned_value,
    dependencies=["value"]
)

# Create group
numerical_group = FeatureGroup(
    name="numerical_features",
    features=[log_feature, std_feature, bin_feature],
    version="1.0.0",
    description="Numerical feature transformations"
)

store.register_feature_group(numerical_group)

# Use
inputs = {"value": 42.0, "mean": 30.0, "std": 15.0}
features = store.materialize_features("numerical_features", inputs)
```

## Best Practices

### 1. Feature Versioning

Always version your features and feature groups:

```python
# Good
group = FeatureGroup(
    name="text_features",
    features=[...],
    version="2.1.0",  # Semantic versioning
    description="Added sentiment score (v2.1.0)"
)

# Bad
group = FeatureGroup(
    name="text_features",
    features=[...],
    version="latest",  # Not reproducible
    description="Text features"
)
```

### 2. Caching Strategy

Use caching for expensive features:

```python
# For expensive computations
cache_key = store.compute_cache_key(inputs)
cached = store.get_cached_features(cache_key)

if cached:
    features = cached
else:
    features = store.materialize_features("expensive_features", inputs)
```

### 3. Dependency Management

Clearly specify dependencies:

```python
# Good - explicit dependencies
feature = Feature(
    name="ratio",
    transform_fn=lambda x: x["numerator"] / x["denominator"],
    dependencies=["numerator", "denominator"]
)

# Bad - hidden dependencies
feature = Feature(
    name="ratio",
    transform_fn=lambda x: x["numerator"] / x["denominator"],
    dependencies=[]  # Missing!
)
```

### 4. Error Handling

Handle missing inputs gracefully:

```python
def safe_divide(inputs):
    """Safely divide with fallback."""
    num = inputs.get("numerator", 0.0)
    denom = inputs.get("denominator", 1.0)
    if denom == 0:
        return 0.0
    return num / denom
```

### 5. Feature Documentation

Document features with metadata:

```python
metadata = FeatureMetadata(
    name="engagement_score",
    version="1.0.0",
    dtype="float",
    description="User engagement score based on clicks, views, and time spent",
    created_at="2025-01-01T00:00:00Z",
    updated_at="2025-01-01T00:00:00Z",
    tags={
        "category": "user_behavior",
        "priority": "high",
        "sla": "daily_refresh"
    }
)
```

## See Also

- [Feature Engineering Guide](./feature_engineering.md) - Best practices and patterns
- [Feature Store Monitoring](../src/codex_ml/features/monitoring.py) - Health checks and alerts
- [Training Pipeline Integration](../training/) - Using features in training
