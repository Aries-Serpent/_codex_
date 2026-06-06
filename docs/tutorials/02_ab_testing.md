# Tutorial 02 — Running A/B Tests on Model Outputs

**Estimated time:** 20 minutes  
**Prerequisites:** Python 3.10+, `_codex_` on `PYTHONPATH`  
**Optional:** `scipy` (auto-detected; improves t-distribution accuracy)

---

## When should you use A/B testing?

Use an A/B test when you want a **statistically rigorous answer** to:

> "Is Model B meaningfully better than Model A on metric X?"

Typical scenarios:

- You retrained a model (e.g. with fresh data) and want to confirm it is
  better before promoting it to production.
- You changed a pre-processing step and need to quantify the effect.
- You are comparing two prompt templates for an LLM and want to see which one
  improves task accuracy.

A/B testing guards against **cherry-picking**: a model can look better by
chance, especially on small evaluation sets.  The Welch's t-test framework
in `codex_ml.experiments.ab_testing` gives you a p-value and effect size so
you can make a principled decision.

---

## Quick Start — `run_ab_test`

The simplest entry point is the `run_ab_test` function.  Give it two lists of
per-sample metric values (one for each model variant) and get a structured
result back.

```python
from codex_ml.experiments.ab_testing import run_ab_test

# Per-sample accuracy scores for 200 evaluation examples
control_scores   = [0.82, 0.79, 0.85, 0.81, 0.78, ...]  # Model A (baseline)
treatment_scores = [0.86, 0.83, 0.89, 0.87, 0.84, ...]  # Model B (candidate)

result = run_ab_test(
    control_metrics=control_scores,
    treatment_metrics=treatment_scores,
    metric_name="accuracy",
    alpha=0.05,           # 5 % significance level (default)
)

print(f"Winner:              {result.winner}")
print(f"Significant:         {result.significant}")
print(f"p-value:             {result.p_value:.4f}")
print(f"Effect size (d):     {result.effect_size:.3f}")
print(f"95 % CI (diff):      [{result.confidence_interval[0]:.4f}, {result.confidence_interval[1]:.4f}]")
```

Example output:
```
Winner:              treatment
Significant:         True
p-value:             0.0031
Effect size (d):     0.48
95 % CI (diff):      [0.0181, 0.0619]
```

---

## Interpreting the Result

### `winner`

| Value | Meaning |
|-------|---------|
| `"treatment"` | Model B is statistically better |
| `"control"` | Model A is statistically better |
| `"inconclusive"` | No significant difference detected at the chosen `alpha` |

### `p_value`

The probability of observing a difference at least this large if the two
models were actually identical.  A small p-value (< `alpha`) means the
difference is unlikely to be random noise.

**Rule of thumb:** p < 0.05 → significant; p ≥ 0.05 → inconclusive.

### `effect_size` (Cohen's d)

Measures the *magnitude* of the difference, independent of sample size:

| Cohen's d | Interpretation |
|-----------|----------------|
| 0.2 | Small effect |
| 0.5 | Medium effect |
| 0.8 | Large effect |

A result can be statistically significant but practically negligible (tiny d
with a huge sample).  Always look at both.

### `confidence_interval`

The 95 % confidence interval of the **mean difference** (treatment − control).
If the interval does not contain 0 it corroborates significance.

---

## Full Example — `ABTestSuite` with Multiple Metrics

When you want to evaluate several metrics at once, use `ABTestSuite`:

```python
from codex_ml.experiments.ab_testing import ABTest, ABTestSuite

# ── Build the suite ──────────────────────────────────────────────────────────
suite = ABTestSuite()

# Each ABTest groups a metric name with paired observation lists
suite.add_test(ABTest(
    name="accuracy",
    control_metrics=[0.81, 0.79, 0.84, 0.80, 0.83, 0.78, 0.82],
    treatment_metrics=[0.86, 0.85, 0.88, 0.87, 0.84, 0.83, 0.89],
))

suite.add_test(ABTest(
    name="f1_score",
    control_metrics=[0.76, 0.74, 0.78, 0.75, 0.77],
    treatment_metrics=[0.79, 0.81, 0.80, 0.78, 0.82],
))

suite.add_test(ABTest(
    name="latency_ms",        # lower is better — flip interpretation
    control_metrics=[120, 115, 122, 118, 117],
    treatment_metrics=[130, 128, 135, 127, 132],  # new model is slower
    alpha=0.05,
))

# ── Run all tests ────────────────────────────────────────────────────────────
results = suite.run_all()

for name, r in results.items():
    status = "✅" if r.significant else "➖"
    print(f"{status} {name:15s}  winner={r.winner:12s}  p={r.p_value:.4f}  d={r.effect_size:.3f}")
```

Example output:
```
✅ accuracy         winner=treatment    p=0.0041  d=0.95
✅ f1_score         winner=treatment    p=0.0218  d=0.84
✅ latency_ms       winner=control      p=0.0003  d=-1.42
```

Reading this: Model B is significantly better on accuracy and F1, but
**slower**.  Whether to promote it depends on your latency budget.

### Structured report

```python
report = suite.report()
# {
#   "summary": {"total": 3, "significant": 3, "inconclusive": 0},
#   "tests": {
#     "accuracy":   {"winner": "treatment", "p_value": 0.0041, ...},
#     "f1_score":   {"winner": "treatment", ...},
#     "latency_ms": {"winner": "control",   ...},
#   }
# }
```

---

## Best Practices

### Minimum sample size

Welch's t-test requires **at least 2 observations per group** (enforced by
`run_ab_test`), but in practice you need at least 30 samples per group to get
reliable p-values.  Use a power analysis to determine the required sample size
before running the experiment.

A rough guideline for 80 % power at α = 0.05:

| Expected effect size (d) | Minimum samples per group |
|--------------------------|--------------------------|
| Large (d ≥ 0.8) | ~26 |
| Medium (d ≈ 0.5) | ~64 |
| Small (d ≈ 0.2) | ~394 |

### Choosing `alpha`

- `alpha=0.05` is the standard for most ML experiments.
- Lower `alpha` (e.g. `0.01`) for high-stakes decisions (e.g. medical models).
- Higher `alpha` (e.g. `0.10`) is acceptable for early-stage exploration where
  false negatives (missing a real improvement) are more costly.

### Multiple comparisons

When running an `ABTestSuite` with many metrics, the chance of a false
positive increases.  Apply a **Bonferroni correction**: divide `alpha` by the
number of tests.  For 5 tests at α = 0.05, use `alpha=0.01` per test.

### Keep groups independent

Ensure your control and treatment samples are independent (e.g. different
evaluation examples, not the same examples scored twice).  Paired samples
require a different test (paired t-test).

---

## What happens next?

Once you confirm Model B is better, you can promote it automatically.
**[Tutorial 03 — Setting Up Continuous Learning](03_continuous_learning.md)**
shows how to use `EvalGate` and `ContinuousLearningPipeline` to gate
promotion on statistically verified quality thresholds.

---

> **See also:**  
> `src/codex_ml/experiments/ab_testing.py`
