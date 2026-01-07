# Feature Engineering Guide

## Introduction

This guide provides best practices and patterns for feature engineering in the Codex ML platform. Feature engineering is the process of transforming raw data into features that better represent the underlying problem to predictive models.

## Table of Contents

- [Feature Definition Patterns](#feature-definition-patterns)
- [Text Features](#text-features)
- [Numerical Features](#numerical-features)
- [Feature Composition](#feature-composition)
- [Caching Strategies](#caching-strategies)
- [Common Pitfalls](#common-pitfalls)

## Feature Definition Patterns

### Basic Feature Pattern

```python
from codex_ml.features import Feature

def feature_function(inputs):
    """Compute feature from inputs."""
    # Your transformation logic
    return transformed_value

feature = Feature(
    name="feature_name",
    transform_fn=feature_function,
    dependencies=["input_field"]
)
```

### Parameterized Features

Use closures to create parameterized features:

```python
def create_threshold_feature(threshold, field_name):
    """Create a threshold-based feature."""
    def threshold_fn(inputs):
        return 1 if inputs[field_name] > threshold else 0
    
    return Feature(
        name=f"{field_name}_above_{threshold}",
        transform_fn=threshold_fn,
        dependencies=[field_name]
    )

# Create multiple threshold features
low_threshold = create_threshold_feature(10, "score")
high_threshold = create_threshold_feature(50, "score")
```

### Conditional Features

Handle missing or invalid data:

```python
def safe_feature(inputs):
    """Handle missing inputs gracefully."""
    value = inputs.get("value")
    
    if value is None:
        return 0.0  # Default value
    
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0

feature = Feature(
    name="safe_numeric_value",
    transform_fn=safe_feature,
    dependencies=["value"]
)
```

## Text Features

### Text Preprocessing

#### Normalization

```python
def normalize_text(inputs):
    """Normalize text (lowercase, strip, remove extra spaces)."""
    text = inputs["text"]
    text = text.lower()
    text = text.strip()
    text = " ".join(text.split())  # Remove extra spaces
    return text

normalized = Feature(
    name="normalized_text",
    transform_fn=normalize_text,
    dependencies=["text"]
)
```

#### Remove Special Characters

```python
import re

def remove_special_chars(inputs):
    """Remove special characters, keep alphanumeric and spaces."""
    text = inputs["text"]
    return re.sub(r'[^a-zA-Z0-9\s]', '', text)

clean_text = Feature(
    name="clean_text",
    transform_fn=remove_special_chars,
    dependencies=["text"]
)
```

#### Tokenization

```python
def tokenize(inputs):
    """Simple whitespace tokenization."""
    return inputs["text"].split()

tokens = Feature(
    name="tokens",
    transform_fn=tokenize,
    dependencies=["text"]
)
```

### Text Statistics

#### Word Count

```python
def word_count(inputs):
    """Count words in text."""
    return len(inputs["text"].split())

wc = Feature(
    name="word_count",
    transform_fn=word_count,
    dependencies=["text"]
)
```

#### Character Count

```python
def char_count(inputs):
    """Count characters (excluding spaces)."""
    return len(inputs["text"].replace(" ", ""))

cc = Feature(
    name="char_count",
    transform_fn=char_count,
    dependencies=["text"]
)
```

#### Average Word Length

```python
def avg_word_length(inputs):
    """Calculate average word length."""
    words = inputs["text"].split()
    if not words:
        return 0.0
    return sum(len(w) for w in words) / len(words)

avg_wl = Feature(
    name="avg_word_length",
    transform_fn=avg_word_length,
    dependencies=["text"]
)
```

#### Sentence Count

```python
import re

def sentence_count(inputs):
    """Count sentences (simple heuristic)."""
    text = inputs["text"]
    sentences = re.split(r'[.!?]+', text)
    return len([s for s in sentences if s.strip()])

sc = Feature(
    name="sentence_count",
    transform_fn=sentence_count,
    dependencies=["text"]
)
```

### Text Complexity Features

#### Lexical Diversity

```python
def lexical_diversity(inputs):
    """Calculate type-token ratio."""
    words = inputs["text"].lower().split()
    if not words:
        return 0.0
    unique_words = len(set(words))
    total_words = len(words)
    return unique_words / total_words

lex_div = Feature(
    name="lexical_diversity",
    transform_fn=lexical_diversity,
    dependencies=["text"]
)
```

#### Uppercase Ratio

```python
def uppercase_ratio(inputs):
    """Ratio of uppercase letters."""
    text = inputs["text"]
    if not text:
        return 0.0
    uppercase = sum(1 for c in text if c.isupper())
    letters = sum(1 for c in text if c.isalpha())
    return uppercase / letters if letters > 0 else 0.0

upper_ratio = Feature(
    name="uppercase_ratio",
    transform_fn=uppercase_ratio,
    dependencies=["text"]
)
```

## Numerical Features

### Basic Transformations

#### Log Transform

```python
import numpy as np

def log_transform(inputs):
    """Log(1+x) transformation."""
    value = inputs["value"]
    return np.log1p(value)

log_feature = Feature(
    name="log_value",
    transform_fn=log_transform,
    dependencies=["value"]
)
```

#### Square Root Transform

```python
def sqrt_transform(inputs):
    """Square root transformation."""
    value = inputs["value"]
    return np.sqrt(max(0, value))  # Handle negative values

sqrt_feature = Feature(
    name="sqrt_value",
    transform_fn=sqrt_transform,
    dependencies=["value"]
)
```

#### Power Transform

```python
def power_transform(power):
    """Create power transformation feature."""
    def transform(inputs):
        return inputs["value"] ** power
    return transform

square = Feature(
    name="value_squared",
    transform_fn=power_transform(2),
    dependencies=["value"]
)
```

### Normalization & Scaling

#### Z-Score Normalization

```python
def z_score_normalize(inputs):
    """Standardize using z-score."""
    value = inputs["value"]
    mean = inputs.get("mean", 0.0)
    std = inputs.get("std", 1.0)
    
    if std == 0:
        return 0.0
    return (value - mean) / std

z_score = Feature(
    name="standardized_value",
    transform_fn=z_score_normalize,
    dependencies=["value", "mean", "std"]
)
```

#### Min-Max Scaling

```python
def min_max_scale(inputs):
    """Scale to [0, 1] range."""
    value = inputs["value"]
    min_val = inputs.get("min", 0.0)
    max_val = inputs.get("max", 1.0)
    
    if max_val == min_val:
        return 0.5
    return (value - min_val) / (max_val - min_val)

scaled = Feature(
    name="scaled_value",
    transform_fn=min_max_scale,
    dependencies=["value", "min", "max"]
)
```

#### Robust Scaling

```python
def robust_scale(inputs):
    """Scale using median and IQR (robust to outliers)."""
    value = inputs["value"]
    median = inputs.get("median", 0.0)
    iqr = inputs.get("iqr", 1.0)
    
    if iqr == 0:
        return 0.0
    return (value - median) / iqr

robust = Feature(
    name="robust_scaled_value",
    transform_fn=robust_scale,
    dependencies=["value", "median", "iqr"]
)
```

### Binning & Discretization

#### Equal-Width Binning

```python
def bin_value(inputs):
    """Bin into equal-width categories."""
    value = inputs["value"]
    
    if value < 10:
        return "very_low"
    elif value < 25:
        return "low"
    elif value < 50:
        return "medium"
    elif value < 75:
        return "high"
    else:
        return "very_high"

binned = Feature(
    name="value_bin",
    transform_fn=bin_value,
    dependencies=["value"]
)
```

#### Quantile-Based Binning

```python
def quantile_bin(inputs):
    """Bin based on quantiles."""
    value = inputs["value"]
    q25 = inputs.get("q25", 25)
    q50 = inputs.get("q50", 50)
    q75 = inputs.get("q75", 75)
    
    if value < q25:
        return "Cycle 1"
    elif value < q50:
        return "Cycle 2"
    elif value < q75:
        return "Cycle 3"
    else:
        return "Cycle 4"

quantile_binned = Feature(
    name="value_quantile",
    transform_fn=quantile_bin,
    dependencies=["value", "q25", "q50", "q75"]
)
```

### Ratio Features

#### Ratio of Two Values

```python
def ratio_feature(inputs):
    """Calculate ratio of two values."""
    numerator = inputs.get("numerator", 0.0)
    denominator = inputs.get("denominator", 1.0)
    
    if denominator == 0:
        return 0.0
    return numerator / denominator

ratio = Feature(
    name="ratio",
    transform_fn=ratio_feature,
    dependencies=["numerator", "denominator"]
)
```

#### Percentage

```python
def percentage_feature(inputs):
    """Calculate percentage."""
    part = inputs.get("part", 0.0)
    total = inputs.get("total", 1.0)
    
    if total == 0:
        return 0.0
    return (part / total) * 100

percentage = Feature(
    name="percentage",
    transform_fn=percentage_feature,
    dependencies=["part", "total"]
)
```

## Feature Composition

### Combining Multiple Features

```python
def create_composite_feature(features):
    """Combine multiple features."""
    def composite(inputs):
        results = {}
        for feature in features:
            results[feature.name] = feature.compute(inputs)
        return results
    
    return Feature(
        name="composite",
        transform_fn=composite,
        dependencies=list(set(sum([f.dependencies for f in features], [])))
    )
```

### Feature Interactions

```python
def interaction_feature(inputs):
    """Create interaction between two features."""
    f1 = inputs["feature1"]
    f2 = inputs["feature2"]
    return f1 * f2

interaction = Feature(
    name="feature1_x_feature2",
    transform_fn=interaction_feature,
    dependencies=["feature1", "feature2"]
)
```

### Polynomial Features

```python
def polynomial_features(degree):
    """Generate polynomial features up to specified degree."""
    def poly(inputs):
        value = inputs["value"]
        return {f"value_pow_{d}": value ** d for d in range(1, degree + 1)}
    
    return Feature(
        name=f"polynomial_{degree}",
        transform_fn=poly,
        dependencies=["value"]
    )
```

## Caching Strategies

### When to Cache

Cache features when:
- Computation is expensive (> 100ms)
- Same inputs appear frequently
- Features are reused across multiple models

### Cache Key Generation

```python
import hashlib
import json

def compute_cache_key(inputs):
    """Generate deterministic cache key from inputs."""
    # Sort keys for deterministic hashing
    sorted_inputs = json.dumps(inputs, sort_keys=True)
    return hashlib.md5(sorted_inputs.encode()).hexdigest()
```

### Time-Based Caching

```python
import time

class TimedCache:
    """Cache with TTL (Time To Live)."""
    
    def __init__(self, ttl_seconds=3600):
        self.cache = {}
        self.ttl = ttl_seconds
    
    def get(self, key):
        """Get cached value if not expired."""
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            else:
                del self.cache[key]
        return None
    
    def set(self, key, value):
        """Cache value with timestamp."""
        self.cache[key] = (value, time.time())
```

### Selective Caching

```python
def should_cache(inputs, result):
    """Decide whether to cache based on inputs/result."""
    # Don't cache small/fast computations
    if isinstance(result, (int, float, str)):
        return False
    
    # Don't cache if inputs are too large
    input_size = len(str(inputs))
    if input_size > 10000:
        return False
    
    return True
```

## Common Pitfalls

### 1. Data Leakage

**Bad:** Using future information

```python
# DON'T: Using target in features
def leaky_feature(inputs):
    return inputs["target"] * 2  # Future information!
```

**Good:** Only use past/present information

```python
# DO: Use only available information
def valid_feature(inputs):
    return inputs["historical_mean"]
```

### 2. Missing Value Handling

**Bad:** Ignoring missing values

```python
# DON'T: Crash on None
def bad_feature(inputs):
    return inputs["value"] * 2  # Crashes if None
```

**Good:** Handle missing values explicitly

```python
# DO: Handle None gracefully
def good_feature(inputs):
    value = inputs.get("value")
    if value is None:
        return 0.0  # Or use median, mean, etc.
    return value * 2
```

### 3. Feature Versioning

**Bad:** Changing features without versioning

```python
# DON'T: Modify existing features
text_features_v1 = FeatureGroup(
    name="text_features",
    version="1.0.0",
    features=[normalize]  # Original
)

# Later, modified without version change:
text_features_v1.features = [normalize, new_feature]  # Bad!
```

**Good:** Create new versions

```python
# DO: Create new version
text_features_v2 = FeatureGroup(
    name="text_features",
    version="2.0.0",  # New version
    features=[normalize, new_feature]
)
```

### 4. Expensive Computations

**Bad:** Recomputing expensive features

```python
# DON'T: Recompute in loop
for item in dataset:
    expensive_feature.compute(item)  # Recomputes every time
```

**Good:** Use materialization and caching

```python
# DO: Materialize once
features = store.materialize_features("expensive_group", inputs)
```

## See Also

- [Feature Store API Reference](./feature_store.md)
- [Feature Monitoring](../src/codex_ml/features/monitoring.py)
- [Training Pipeline](../training/)
