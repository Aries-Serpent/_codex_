# Fairness Evaluation Guide

## Overview

The fairness evaluation system provides tools for detecting and mitigating bias in ML models.

## Supported Metrics

### 1. Demographic Parity
Statistical parity across sensitive attributes.

### 2. Equal Opportunity  
True positive rate equality.

### 3. Calibration
Reliability of confidence scores.

## Usage

```python
from codex_ml.plugins.fairness_checker import FairnessCheckerPlugin

checker = FairnessCheckerPlugin()
metrics = checker.execute(
    predictions=predictions,
    labels=labels,
    sensitive_attributes={"gender": gender, "age": age}
)
```

## Integration with A/B Testing

```python
from codex_ml.training.ab_testing import ABTestManager

manager = ABTestManager()
manager.create_experiment(
    "model_v2",
    model_a="baseline",
    model_b="improved",
    fairness_constraints={
        "min_demographic_parity": 0.90,
        "min_equal_opportunity": 0.90
    }
)
```

## Best Practices

1. Monitor fairness metrics continuously
2. Set fairness constraints in experiments
3. Alert on bias drift
4. Document bias mitigation strategies

See `src/codex_ml/plugins/fairness_checker.py` for implementation.
