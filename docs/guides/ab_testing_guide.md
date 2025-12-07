# A/B Testing Guide

## Overview

The A/B Testing Framework enables scientific validation of model improvements through controlled experiments with statistical significance testing.

## Quick Start

```python
from codex_ml.training.ab_testing import ABTestManager, ABTestConfig

# Configure experiment
config = ABTestConfig(
    experiment_name="model_v2_evaluation",
    control_variant="v1.0",
    treatment_variants=["v2.0"],
    traffic_split={"v1.0": 0.5, "v2.0": 0.5},
    primary_metric="accuracy",
    min_samples=100
)

# Initialize manager
manager = ABTestManager(config)
```

## Core Concepts

### 1. Experiment Configuration

Define your A/B test parameters:

```python
from codex_ml.training.ab_testing import ABTestConfig

config = ABTestConfig(
    experiment_name="feature_improvement_test",
    control_variant="baseline_v1",        # Current production model
    treatment_variants=["candidate_v2"],  # New model to test
    traffic_split={
        "baseline_v1": 0.5,   # 50% to control
        "candidate_v2": 0.5   # 50% to treatment
    },
    primary_metric="accuracy",     # Metric to optimize
    min_samples=100,               # Minimum samples per variant
    confidence_level=0.95          # 95% confidence for significance
)
```

### 2. Recording Results

Track performance for each variant:

```python
# Run inference and record results
for request in production_requests:
    # Route to variant based on traffic split
    variant = select_variant(config.traffic_split)
    
    # Run inference
    prediction = run_model(variant, request.input)
    
    # Compute metrics
    metrics = {
        "accuracy": compute_accuracy(prediction, request.label),
        "latency": measure_latency(),
        "f1_score": compute_f1(prediction, request.label)
    }
    
    # Record result
    manager.record_result(variant, metrics)
```

### 3. Statistical Significance

Check if results are statistically significant:

```python
# Check significance
if manager.is_significant(alpha=0.05):
    print("✅ Results are statistically significant (p < 0.05)")
    
    # Determine winner
    winner = manager.get_winner()
    print(f"Winner: {winner}")
    
    # Get detailed report
    report = manager.get_comparison_report()
    print(f"Improvement: {report['winner_improvement']:.2%}")
else:
    print("⏳ Not enough data or no significant difference")
```

### 4. Gradual Rollout

Safely deploy the winning variant:

```python
if manager.is_significant():
    winner = manager.get_winner()
    
    # Gradual rollout in 5 steps
    manager.gradual_rollout(
        winner_variant=winner,
        steps=5
    )
    # Step 1: 20% traffic
    # Step 2: 40% traffic
    # Step 3: 60% traffic
    # Step 4: 80% traffic
    # Step 5: 100% traffic
```

## Complete Workflow

### Step 1: Setup Experiment

```python
from codex_ml.training.ab_testing import ABTestManager, ABTestConfig
from codex_ml.training.continuous_learning import ContinuousLearningPipeline

# Load models
control_model = load_model("models/v1.0/model.pt")
treatment_model = load_model("models/v2.0/model.pt")

# Configure A/B test
config = ABTestConfig(
    experiment_name="v2_rollout",
    control_variant="v1.0",
    treatment_variants=["v2.0"],
    traffic_split={"v1.0": 0.8, "v2.0": 0.2},  # Start with 20% to new model
    primary_metric="f1_score",
    min_samples=500
)

manager = ABTestManager(config)
```

### Step 2: Run Experiment

```python
import random

def run_ab_test_experiment(manager, duration_hours=24):
    """Run A/B test for specified duration."""
    
    start_time = time.time()
    end_time = start_time + (duration_hours * 3600)
    
    request_count = 0
    
    while time.time() < end_time:
        # Get production request
        request = get_next_request()
        
        # Select variant based on traffic split
        rand = random.random()
        cumulative = 0
        variant = None
        
        for var, percentage in config.traffic_split.items():
            cumulative += percentage
            if rand <= cumulative:
                variant = var
                break
        
        # Run inference
        model = control_model if variant == "v1.0" else treatment_model
        prediction = model.predict(request.input)
        
        # Compute metrics
        metrics = {
            "f1_score": compute_f1(prediction, request.label),
            "accuracy": compute_accuracy(prediction, request.label),
            "latency_ms": measure_latency(model, request.input),
            "throughput": 1.0  # requests per second
        }
        
        # Record result
        manager.record_result(variant, metrics)
        
        request_count += 1
        
        # Log progress every 100 requests
        if request_count % 100 == 0:
            print(f"Processed {request_count} requests")
            print_interim_results(manager)
    
    print(f"✅ Experiment complete: {request_count} requests processed")
    return manager
```

### Step 3: Analyze Results

```python
def analyze_ab_test_results(manager):
    """Analyze A/B test results."""
    
    # Get comparison report
    report = manager.get_comparison_report()
    
    print("\n" + "="*50)
    print("A/B Test Results")
    print("="*50)
    
    print(f"\nExperiment: {report['experiment_name']}")
    print(f"Start Time: {report['start_time']}")
    
    # Variant statistics
    print("\nVariant Statistics:")
    for variant_name, stats in report['variants'].items():
        print(f"\n  {variant_name}:")
        print(f"    Traffic: {stats['traffic_percentage']:.1%}")
        print(f"    Samples: {stats['sample_count']}")
        print(f"    Metrics:")
        for metric, value in stats['metrics'].items():
            print(f"      {metric}: {value:.4f}")
    
    # Statistical significance
    print(f"\nStatistically Significant: {report['is_significant']}")
    
    if report['is_significant']:
        print(f"Winner: {report['winner']}")
        
        # Calculate improvement
        control_metrics = report['variants'][config.control_variant]['metrics']
        winner_metrics = report['variants'][report['winner']]['metrics']
        
        improvement = {}
        for metric in control_metrics:
            baseline = control_metrics[metric]
            new_value = winner_metrics[metric]
            pct_change = ((new_value - baseline) / baseline) * 100
            improvement[metric] = pct_change
            print(f"  {metric}: {pct_change:+.2f}%")
    else:
        print("\n⚠️ No statistically significant difference detected")
        print("Recommendation: Continue experiment or try different approach")
    
    # Save report
    manager.save_results("reports/ab_test_results.json")
    
    return report
```

### Step 4: Deploy Winner

```python
def deploy_if_successful(manager, min_improvement=0.02):
    """Deploy if test shows significant improvement."""
    
    if not manager.is_significant():
        print("❌ Not deploying: results not significant")
        return False
    
    winner = manager.get_winner()
    
    # Check if winner is treatment (not control)
    if winner == config.control_variant:
        print("❌ Not deploying: control variant won")
        return False
    
    # Check improvement threshold
    report = manager.get_comparison_report()
    control_metric = report['variants'][config.control_variant]['metrics'][config.primary_metric]
    winner_metric = report['variants'][winner]['metrics'][config.primary_metric]
    improvement = (winner_metric - control_metric) / control_metric
    
    if improvement < min_improvement:
        print(f"❌ Not deploying: improvement ({improvement:.2%}) below threshold ({min_improvement:.2%})")
        return False
    
    # All checks passed - deploy!
    print(f"✅ Deploying {winner} (improvement: {improvement:.2%})")
    
    # Gradual rollout
    manager.gradual_rollout(winner, steps=5)
    
    return True
```

## Advanced Patterns

### Multi-Variant Testing

Test multiple candidates simultaneously:

```python
config = ABTestConfig(
    experiment_name="multi_variant_test",
    control_variant="v1.0",
    treatment_variants=["v2.0", "v2.1", "v3.0"],  # Multiple treatments
    traffic_split={
        "v1.0": 0.4,   # 40% control
        "v2.0": 0.2,   # 20% each treatment
        "v2.1": 0.2,
        "v3.0": 0.2
    },
    primary_metric="f1_score"
)
```

### Metric-Specific Testing

Compare models on multiple metrics:

```python
def compare_all_metrics(manager):
    """Compare all metrics, not just primary."""
    
    report = manager.get_comparison_report()
    
    all_metrics = set()
    for variant_stats in report['variants'].values():
        all_metrics.update(variant_stats['metrics'].keys())
    
    winners = {}
    for metric in all_metrics:
        # Find best variant for each metric
        best_variant = None
        best_value = float('-inf')
        
        for variant_name, stats in report['variants'].items():
            value = stats['metrics'].get(metric, float('-inf'))
            if value > best_value:
                best_value = value
                best_variant = variant_name
        
        winners[metric] = best_variant
    
    print("Winners by metric:")
    for metric, winner in winners.items():
        print(f"  {metric}: {winner}")
    
    return winners
```

### Sequential Testing

Stop test early if clear winner emerges:

```python
def run_sequential_test(manager, check_interval=100, early_stop_threshold=0.001):
    """Run test with early stopping."""
    
    request_count = 0
    
    while True:
        # Process batch of requests
        for _ in range(check_interval):
            # ... process request and record result ...
            request_count += 1
        
        # Check for early stopping
        if manager.is_significant(alpha=early_stop_threshold):
            winner = manager.get_winner()
            
            if winner != config.control_variant:
                print(f"✅ Early stop: {winner} is clear winner")
                print(f"Stopped after {request_count} requests")
                return True
        
        # Check if enough samples collected
        if request_count >= config.min_samples * len(config.treatment_variants) * 2:
            print("Max samples reached")
            break
    
    return False
```

### Stratified Testing

Test across different user segments:

```python
def stratified_ab_test(manager, user_segments):
    """Run A/B test stratified by user segments."""
    
    segment_managers = {}
    
    for segment_name in user_segments:
        # Create separate manager for each segment
        segment_config = ABTestConfig(
            experiment_name=f"{config.experiment_name}_{segment_name}",
            control_variant=config.control_variant,
            treatment_variants=config.treatment_variants,
            traffic_split=config.traffic_split,
            primary_metric=config.primary_metric
        )
        segment_managers[segment_name] = ABTestManager(segment_config)
    
    # Process requests
    for request in get_requests():
        segment = identify_user_segment(request.user_id)
        
        if segment in segment_managers:
            variant = select_variant(config.traffic_split)
            metrics = run_inference(variant, request)
            segment_managers[segment].record_result(variant, metrics)
    
    # Analyze per segment
    results = {}
    for segment, mgr in segment_managers.items():
        if mgr.is_significant():
            results[segment] = mgr.get_winner()
            print(f"{segment}: Winner is {results[segment]}")
        else:
            results[segment] = None
            print(f"{segment}: No significant difference")
    
    return results
```

## Best Practices

### 1. Sample Size Calculation

Calculate required sample size before starting:

```python
def calculate_required_sample_size(
    baseline_metric=0.90,
    min_detectable_effect=0.02,
    alpha=0.05,
    power=0.80
):
    """Calculate required sample size per variant."""
    
    from scipy import stats
    import math
    
    # Z-scores for alpha and power
    z_alpha = stats.norm.ppf(1 - alpha/2)
    z_beta = stats.norm.ppf(power)
    
    # Effect size
    effect_size = min_detectable_effect / baseline_metric
    
    # Sample size per variant
    n = 2 * ((z_alpha + z_beta) ** 2) / (effect_size ** 2)
    
    return math.ceil(n)

# Example
n_required = calculate_required_sample_size(
    baseline_metric=0.90,
    min_detectable_effect=0.02,  # 2% improvement
    alpha=0.05,
    power=0.80
)
print(f"Required samples per variant: {n_required}")
```

### 2. Multiple Testing Correction

Adjust significance level for multiple comparisons:

```python
def bonferroni_correction(alpha, num_comparisons):
    """Apply Bonferroni correction for multiple testing."""
    return alpha / num_comparisons

# Example with 3 treatment variants
num_comparisons = len(config.treatment_variants)
adjusted_alpha = bonferroni_correction(0.05, num_comparisons)

print(f"Adjusted significance level: {adjusted_alpha}")

# Use adjusted alpha
if manager.is_significant(alpha=adjusted_alpha):
    print("Significant after multiple testing correction")
```

### 3. Confidence Intervals

Calculate confidence intervals for metrics:

```python
from scipy import stats

def calculate_confidence_interval(values, confidence=0.95):
    """Calculate confidence interval for metric values."""
    
    mean = np.mean(values)
    std_err = stats.sem(values)
    margin = std_err * stats.t.ppf((1 + confidence) / 2, len(values) - 1)
    
    return (mean - margin, mean + margin)

# Example
control_accuracy = [0.89, 0.91, 0.90, 0.92, 0.88]
ci = calculate_confidence_interval(control_accuracy)
print(f"95% CI: [{ci[0]:.3f}, {ci[1]:.3f}]")
```

### 4. Power Analysis

Check if test has sufficient power:

```python
def check_statistical_power(manager, min_detectable_effect=0.02):
    """Check if test has sufficient statistical power."""
    
    report = manager.get_comparison_report()
    
    for variant_name, stats in report['variants'].items():
        n = stats['sample_count']
        
        # Calculate achieved power
        # (Simplified - use proper power analysis library in production)
        if n >= 1000:
            power = 0.80
        elif n >= 500:
            power = 0.60
        else:
            power = 0.40
        
        print(f"{variant_name}: n={n}, power≈{power:.2f}")
        
        if power < 0.80:
            print(f"  ⚠️ Low power - need more samples")
```

## Integration with Continuous Learning

Combine A/B testing with continuous learning:

```python
from codex_ml.training.continuous_learning import ContinuousLearningPipeline

def continuous_learning_with_ab_test():
    """Continuous learning with A/B validation."""
    
    pipeline = ContinuousLearningPipeline(model_name="prod_model")
    
    # Monitor for drift
    if monitor.has_critical_drift():
        # Retrain
        new_version = pipeline.retrain(train_fn, new_data)
        
        # A/B test new model
        config = ABTestConfig(
            experiment_name=f"continuous_{new_version.version}",
            control_variant=pipeline.registry.get_latest().version,
            treatment_variants=[new_version.version],
            traffic_split={
                pipeline.registry.get_latest().version: 0.9,
                new_version.version: 0.1
            },
            primary_metric="f1_score"
        )
        
        manager = ABTestManager(config)
        
        # Run test
        run_ab_test_experiment(manager, duration_hours=24)
        
        # Deploy if successful
        if deploy_if_successful(manager):
            pipeline.deploy_model(new_version)
        else:
            pipeline.rollback()
```

## Troubleshooting

### Issue: No Significant Difference

**Problem:** Test runs but shows no significant difference

**Solutions:**
1. Increase sample size
2. Increase effect size (make bigger changes)
3. Use more sensitive metrics
4. Stratify by user segments

```python
# Increase samples
config.min_samples = 2000

# Try different metric
config.primary_metric = "f1_score"  # More sensitive than accuracy
```

### Issue: High Variance

**Problem:** Metrics have high variance, making it hard to detect differences

**Solutions:**
1. Use ratio metrics
2. Apply variance reduction techniques
3. Longer test duration

```python
# Use ratio metrics
metrics = {
    "success_rate": successes / total_requests,
    "error_rate": errors / total_requests
}
```

## Summary

**Key Points:**
- ✅ Configure experiments with traffic splits
- ✅ Record results for all variants
- ✅ Check statistical significance
- ✅ Use gradual rollout for safety
- ✅ Calculate required sample sizes
- ✅ Apply multiple testing corrections
- ✅ Integrate with continuous learning

**Next Steps:**
- See [Continuous Learning Guide](continuous_learning_guide.md)
- See [Plugin Development Guide](plugin_development.md)
- See [Production Deployment Guide](production_deployment.md)
