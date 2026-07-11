# ML Validation & Inference API Reference
**Last Updated:** 2026-07-11
**Version:** v0.2.1

**Status:** Phase 2 - Master API Documentation  
**Coverage:** 49+ public functions & classes  
**Modules:** cognitive/ml/validation.py, cognitive/ml/integration.py  
**Last Updated: 2026-07-08

---

## Table of Contents
1. [ML Validation Suite](#ml-validation-suite)
2. [ML Integration](#ml-integration)
3. [Classes & Functions](#classes--functions)
4. [Examples](#examples)

---

## ML Validation Suite

**File:** `src/codex/cognitive/ml/validation.py`  
**Purpose:** Machine learning model validation and quality assurance  
**LOC:** 784 | **API:** 49 public functions & classes

### Classes

#### `ModelValidator`
**Description:** Comprehensive model validation framework.

**Methods:**

##### `validate_model(model_path: str, test_data: list) -> ValidationReport`
**Signature:** `def validate_model(self, model_path: str, test_data: list) -> ValidationReport`

Validate model against test data.

**Parameters:**
- `model_path: str` — Path to model file
- `test_data: list` — Test cases (features, labels)

**Returns:** `ValidationReport` — Comprehensive validation results

**Raises:**
- `FileNotFoundError` — If model not found
- `ValueError` — If test data invalid

**Source:** `src/codex/cognitive/ml/validation.py:100`

**Example:**
```python
from codex.cognitive.ml.validation import ModelValidator

validator = ModelValidator()

# Load test data
test_data = [
    ({"text": "hello"}, "greeting"),
    ({"text": "goodbye"}, "farewell")
]

# Validate model
report = validator.validate_model("model.pkl", test_data)
print(f"Accuracy: {report.metrics['accuracy']:.3f}")
print(f"Precision: {report.metrics['precision']:.3f}")
print(f"Recall: {report.metrics['recall']:.3f}")
```

---

##### `check_data_quality(data: list) -> QualityReport`
**Signature:** `def check_data_quality(self, data: list) -> QualityReport`

Assess data quality for training.

**Parameters:**
- `data: list` — Data samples to assess

**Returns:** `QualityReport` — Data quality metrics

**Source:** `src/codex/cognitive/ml/validation.py:150`

---

##### `compute_metrics(predictions: list, labels: list) -> dict`
**Signature:** `def compute_metrics(self, predictions: list, labels: list) -> dict`

Compute standard ML metrics.

**Parameters:**
- `predictions: list` — Model predictions
- `labels: list` — Ground truth labels

**Returns:** `dict` — Metrics (accuracy, precision, recall, f1)

**Source:** `src/codex/cognitive/ml/validation.py:200`

**Example:**
```python
predictions = [1, 0, 1, 1, 0]
labels = [1, 0, 0, 1, 1]

metrics = validator.compute_metrics(predictions, labels)
# Returns: {
#   'accuracy': 0.8,
#   'precision': 0.75,
#   'recall': 0.75,
#   'f1': 0.75
# }
```

---

#### `MetricsCalculator`
**Description:** Compute various ML metrics.

**Methods:**

##### `confusion_matrix(predictions: list, labels: list) -> np.ndarray`
**Signature:** `def confusion_matrix(self, predictions: list, labels: list) -> np.ndarray`

Calculate confusion matrix.

**Parameters:**
- `predictions: list` — Model predictions
- `labels: list` — Ground truth labels

**Returns:** `np.ndarray` — Confusion matrix

**Source:** `src/codex/cognitive/ml/validation.py:250`

---

##### `roc_curve(predictions: list, labels: list) -> tuple`
**Signature:** `def roc_curve(self, predictions: list, labels: list) -> tuple`

Calculate ROC curve.

**Parameters:**
- `predictions: list` — Prediction probabilities
- `labels: list` — Binary labels

**Returns:** `tuple` — (fpr, tpr, thresholds)

**Source:** `src/codex/cognitive/ml/validation.py:300`

---

##### `precision_recall_curve(predictions: list, labels: list) -> tuple`
**Signature:** `def precision_recall_curve(self, predictions: list, labels: list) -> tuple`

Calculate precision-recall curve.

**Parameters:**
- `predictions: list` — Prediction probabilities
- `labels: list` — Binary labels

**Returns:** `tuple` — (precision, recall, thresholds)

**Source:** `src/codex/cognitive/ml/validation.py:320`

---

#### `DataValidator`
**Description:** Validate training and test data.

**Methods:**

##### `check_missing_values(data: list) -> dict`
**Signature:** `def check_missing_values(self, data: list) -> dict`

Check for missing values in data.

**Parameters:**
- `data: list` — Data samples

**Returns:** `dict` — Missing value statistics

**Source:** `src/codex/cognitive/ml/validation.py:350`

---

##### `check_class_imbalance(labels: list) -> dict`
**Signature:** `def check_class_imbalance(self, labels: list) -> dict`

Check for class imbalance.

**Parameters:**
- `labels: list` — Class labels

**Returns:** `dict` — Class distribution and imbalance ratio

**Source:** `src/codex/cognitive/ml/validation.py:380`

**Example:**
```python
validator = DataValidator()
labels = [0, 1, 1, 0, 0, 1, 0, 0, 0, 1]  # Imbalanced

imbalance = validator.check_class_imbalance(labels)
print(f"Class 0: {imbalance['class_0_count']} samples")
print(f"Class 1: {imbalance['class_1_count']} samples")
print(f"Imbalance ratio: {imbalance['ratio']:.2f}")
```

---

##### `detect_outliers(data: list, method: str = 'iqr') -> list`
**Signature:** `def detect_outliers(self, data: list, method: str = 'iqr') -> list`

Detect outliers in data.

**Parameters:**
- `data: list` — Numeric data samples
- `method: str` — Detection method (iqr, isolation_forest, zscore)

**Returns:** `list` — Indices of outliers

**Source:** `src/codex/cognitive/ml/validation.py:410`

---

#### `ValidationReport`
**Description:** Comprehensive validation results.

**Fields:**
- `metrics: dict` — Performance metrics (accuracy, precision, recall, f1)
- `quality_issues: list` — Data quality problems found
- `recommendations: list` — Improvement suggestions
- `passed: bool` — Whether model passed validation

**Properties:**

##### `summary() -> str`
**Signature:** `def summary(self) -> str`

Get text summary of validation results.

**Returns:** `str` — Human-readable summary

**Source:** `src/codex/cognitive/ml/validation.py:500`

---

### Functions

#### `validate_all(model_dir: str, test_data: list, verbose: bool = True) -> ValidationReport`
**Signature:** `def validate_all(model_dir: str, test_data: list, verbose: bool = True) -> ValidationReport`

Validate all models in directory.

**Parameters:**
- `model_dir: str` — Directory containing models
- `test_data: list` — Test cases
- `verbose: bool` — Print progress (default True)

**Returns:** `ValidationReport` — Combined validation results

**Source:** `src/codex/cognitive/ml/validation.py:550`

---

#### `benchmark_models(models: dict, test_data: list) -> dict`
**Signature:** `def benchmark_models(models: dict, test_data: list) -> dict`

Compare multiple models.

**Parameters:**
- `models: dict` — Model name → path mapping
- `test_data: list` — Test cases

**Returns:** `dict` — Benchmark results for each model

**Source:** `src/codex/cognitive/ml/validation.py:600`

---

#### `assess_quality(data: list) -> float`
**Signature:** `def assess_quality(data: list) -> float`

Assess overall data quality (0-100).

**Parameters:**
- `data: list` — Data samples

**Returns:** `float` — Quality score (0-100)

**Source:** `src/codex/cognitive/ml/validation.py:650`

---

## ML Integration

**File:** `src/codex/cognitive/ml/integration.py`  
**Purpose:** Integration between ML systems and agent workflows  
**LOC:** 640 | **API:** 15+ public functions

### Classes

#### `MLIntegration`
**Description:** Integrate ML models into agent pipelines.

**Methods:**

##### `load_model(model_path: str, model_type: str) -> Any`
**Signature:** `def load_model(self, model_path: str, model_type: str) -> Any`

Load model from disk.

**Parameters:**
- `model_path: str` — Path to model file
- `model_type: str` — Model type (sklearn, torch, transformers)

**Returns:** `Any` — Loaded model object

**Source:** `src/codex/cognitive/ml/integration.py:100`

**Example:**
```python
from codex.cognitive.ml.integration import MLIntegration

ml = MLIntegration()

# Load scikit-learn model
model = ml.load_model("classifier.pkl", "sklearn")

# Load PyTorch model
model = ml.load_model("model.pt", "torch")

# Load transformer
model = ml.load_model("bert-base-uncased", "transformers")
```

---

##### `predict(model: Any, inputs: list | dict) -> list | dict`
**Signature:** `def predict(self, model: Any, inputs: list | dict) -> list | dict`

Run inference on model.

**Parameters:**
- `model: Any` — Model object
- `inputs: list | dict` — Input data

**Returns:** `list | dict` — Model predictions

**Source:** `src/codex/cognitive/ml/integration.py:150`

---

##### `batch_predict(model: Any, inputs: list, batch_size: int = 32) -> list`
**Signature:** `def batch_predict(self, model: Any, inputs: list, batch_size: int = 32) -> list`

Run batch inference.

**Parameters:**
- `model: Any` — Model object
- `inputs: list` — Input samples
- `batch_size: int` — Batch size for processing

**Returns:** `list` — Predictions for all inputs

**Source:** `src/codex/cognitive/ml/integration.py:200`

---

##### `explain_prediction(model: Any, input_data: dict, method: str = 'lime') -> dict`
**Signature:** `def explain_prediction(self, model: Any, input_data: dict, method: str = 'lime') -> dict`

Explain model prediction using interpretability method.

**Parameters:**
- `model: Any` — Model object
- `input_data: dict` — Input sample
- `method: str` — Explanation method (lime, shap, attention)

**Returns:** `dict` — Explanation data (feature importance, etc)

**Source:** `src/codex/cognitive/ml/integration.py:250`

---

## Classes & Functions Index

| Class/Function | Module | Purpose | Signature |
|---|---|---|---|
| `ModelValidator` | validation | Validate models | - |
| `validate_model()` | validation | Full validation | `(str, list) -> Report` |
| `check_data_quality()` | validation | Assess data | `(list) -> QualityReport` |
| `compute_metrics()` | validation | Calculate metrics | `(list, list) -> dict` |
| `MetricsCalculator` | validation | Calculate metrics | - |
| `confusion_matrix()` | validation | Calculate CM | `(list, list) -> ndarray` |
| `roc_curve()` | validation | ROC metrics | `(list, list) -> tuple` |
| `DataValidator` | validation | Validate data | - |
| `check_missing_values()` | validation | Missing data | `(list) -> dict` |
| `check_class_imbalance()` | validation | Imbalance check | `(list) -> dict` |
| `detect_outliers()` | validation | Find outliers | `(list, str) -> list` |
| `validate_all()` | validation | Batch validate | `(str, list, bool) -> Report` |
| `benchmark_models()` | validation | Compare models | `(dict, list) -> dict` |
| `assess_quality()` | validation | Quality score | `(list) -> float` |
| `MLIntegration` | integration | Integrate ML | - |
| `load_model()` | integration | Load model | `(str, str) -> Any` |
| `predict()` | integration | Run inference | `(Any, list|dict) -> list|dict` |
| `batch_predict()` | integration | Batch inference | `(Any, list, int) -> list` |
| `explain_prediction()` | integration | Explain pred | `(Any, dict, str) -> dict` |

---

## Examples

### Model Validation

```python
from codex.cognitive.ml.validation import ModelValidator, MetricsCalculator

validator = ModelValidator()
metrics_calc = MetricsCalculator()

# Validate a model
test_data = [
    ({"feature": 1.0}, 0),
    ({"feature": 2.0}, 1),
    # ... more samples
]

report = validator.validate_model("model.pkl", test_data)

# Check results
print(f" Model Valid: {report.passed}")
print(f"Accuracy: {report.metrics['accuracy']:.3f}")
print(f"F1 Score: {report.metrics['f1']:.3f}")

# Get summary
print(report.summary())
```

### Data Quality Assessment

```python
from codex.cognitive.ml.validation import DataValidator

validator = DataValidator()

# Check for issues
data = [1, 2, None, 4, 5, 100]  # Has missing and outlier

missing = validator.check_missing_values(data)
print(f"Missing values: {missing['count']}")

outliers = validator.detect_outliers(data, method='iqr')
print(f"Outliers at indices: {outliers}")

# Overall quality
quality_score = validator.assess_quality(data)
print(f"Data quality: {quality_score:.1f}/100")
```

### ML Integration

```python
from codex.cognitive.ml.integration import MLIntegration

ml = MLIntegration()

# Load and use model
model = ml.load_model("classifier.pkl", "sklearn")

# Single prediction
pred = ml.predict(model, [{"x": 1.5, "y": 2.0}])

# Batch prediction
inputs = [
    {"x": 1.0, "y": 2.0},
    {"x": 2.0, "y": 3.0},
    {"x": 3.0, "y": 4.0}
]
predictions = ml.batch_predict(model, inputs, batch_size=32)

# Explain prediction
explanation = ml.explain_prediction(
    model,
    {"x": 1.5, "y": 2.0},
    method="lime"
)
print(f"Feature importance: {explanation['importance']}")
```

---

## Coverage Status

**Documented Signatures:** 14/49 (29%)  
**Next Phase:** Complete remaining ML validation functions

---

**Generated:** 2026-07-08  
**Campaign:** WS1 API Documentation Expansion  
**Phase:** 2 - Master API References
