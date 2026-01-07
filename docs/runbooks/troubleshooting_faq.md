# MLOps Phase 6 - Troubleshooting FAQ

**Version**: 1.0.0  
**Last Updated**: 2025-12-07

---

## General Questions

### Q: How do I know if Phase 6 features are enabled?

**A**: Check your configuration files:

```bash
# Check MLflow
grep -A 2 "mlflow:" configs/production/tracking.yaml

# Check feature store
grep "enabled:" configs/production/features.yaml

# Check data validation
grep "enabled:" configs/production/data_validation.yaml
```

All features are **opt-in** by default (disabled unless explicitly enabled).

---

### Q: Will Phase 6 break my existing training scripts?

**A**: No! All Phase 6 features maintain 100% backward compatibility. Your existing code will continue to work without any modifications.

```python
# This still works without any Phase 6 configs
from codex_ml.training.loop import run_minimal_training

config = {"training": {"base_loss": 10.0, "decay": 0.9}}
results = run_minimal_training(config, max_steps=10, run_dir="./runs")
```

---

### Q: How do I disable a Phase 6 feature temporarily?

**A**: Set `enabled: false` in the relevant configuration file:

```yaml
# Disable MLflow
tracking:
  mlflow:
    enabled: false

# Disable feature store
feature_store:
  enabled: false

# Disable data validation
data_validation:
  enabled: false
```

---

## MLflow Tracking

### Q: MLflow UI shows no experiments

**A**: Check these steps:

1. Verify MLflow is enabled:
```yaml
tracking:
  mlflow:
    enabled: true
```

2. Check tracking URI:
```bash
ls -la mlruns/
# Should show experiment directories
```

3. Start UI with correct path:
```bash
mlflow ui --backend-store-uri file://./mlruns
```

---

### Q: Training is slower with MLflow enabled

**A**: Performance overhead should be <1%. If experiencing issues:

1. Enable async logging:
```yaml
tracking:
  mlflow:
    async_logging: true
```

2. Reduce logging frequency:
```python
if step % 10 == 0:  # Log every 10 steps instead of every step
    tracker.log_metrics(metrics, step=step)
```

3. Batch metrics:
```yaml
tracking:
  mlflow:
    batch_metrics: true
```

---

### Q: Can't connect to MLflow server

**A**: Common issues:

1. **Server not running**: Start MLflow server
```bash
mlflow server --host 0.0.0.0 --port 5000
```

2. **Wrong URI**: Check configuration
```yaml
tracking:
  mlflow:
    uri: "http://localhost:5000"  # Update to correct URI
```

3. **Network issue**: Test connection
```bash
curl http://mlflow-server:5000/health
```

4. **Fallback to local**: Use file-based tracking
```yaml
tracking:
  mlflow:
    uri: "file://./mlruns"
```

---

## Feature Store

### Q: Feature store initialization fails

**A**: Try these steps:

1. Check directory permissions:
```bash
mkdir -p artifacts/features/production
chmod 755 artifacts/features/production
```

2. Re-initialize:
```bash
python scripts/initialize_feature_store.py --config configs/production/features.yaml
```

3. Verify:
```bash
python -m codex_ml.cli.feature_store list
```

---

### Q: Features showing as "stale"

**A**: Features are considered stale if not updated in 48+ hours:

1. Check last update time:
```bash
python -m codex_ml.cli.feature_store health
```

2. Refresh features:
```bash
# Trigger feature pipeline to regenerate
python scripts/refresh_features.py
```

3. If expected (batch features updated weekly), adjust SLA:
```yaml
feature_store:
  sla:
    freshness_sla_minutes: 10080  # 1 week
```

---

### Q: Feature retrieval is slow

**A**: Optimize performance:

1. Enable caching:
```yaml
feature_store:
  point_in_time:
    cache_enabled: true
    cache_ttl_minutes: 60
```

2. Enable partitioning:
```yaml
feature_store:
  storage:
    partition_by_date: true
```

3. Check current performance:
```bash
python scripts/benchmarks/feature_retrieval_benchmark.py
```

Target: <10ms p95 latency

---

## Data Validation

### Q: Validation is failing my training jobs

**A**: Determine if failures are legitimate:

1. Check validation report:
```bash
cat artifacts/validation_reports/latest.json
```

2. Review failed checks:
```python
import json
with open('artifacts/validation_reports/latest.json') as f:
    report = json.load(f)
    print(report['errors'])
```

3. If false positives, adjust thresholds:
```yaml
data_validation:
  null_checks:
    null_threshold: 0.10  # Increase from 0.05
```

4. If legitimate issues, fix data:
```bash
# Investigate data quality issues
python scripts/data_quality_analysis.py
```

---

### Q: Validation is too slow

**A**: Optimize validation performance:

1. Enable sampling (already enabled by default):
```yaml
data_validation:
  performance:
    sampling_enabled: true
    sample_size: 10000  # Validate only 10K rows
```

2. Reduce checks:
```yaml
data_validation:
  statistical_checks:
    enabled: false  # Disable expensive checks
```

3. Parallel validation:
```yaml
data_validation:
  performance:
    parallel_validation: true
    num_workers: 4
```

---

### Q: How do I add custom validation rules?

**A**: Define rules in configuration:

```yaml
data_validation:
  custom_rules:
    enabled: true
    rules:
      - name: "check_date_range"
        column: "date"
        condition: "value >= '2020-01-01' and value <= '2025-12-31'"
      - name: "check_positive_amount"
        column: "amount"
        condition: "value > 0"
```

---

## Evaluation

### Q: EvaluationRunner not found

**A**: Check import path:

```python
# Correct import
from codex_ml.evaluation.runner import EvaluationRunner

# If still not found, check installation
pip install -e .
```

---

### Q: How do I add custom metrics?

**A**: Define custom metric adapter:

```python
from codex_ml.evaluation.runner import MetricAdapter

class MyCustomMetric(MetricAdapter):
    def __init__(self):
        super().__init__(name="my_metric")
    
    def compute(self) -> Dict[str, float]:
        # Custom metric logic
        return {"my_metric": calculated_value}

# Use in evaluation
runner = EvaluationRunner(
    model=model,
    dataset=dataset,
    metrics=[MyCustomMetric()]
)
```

---

### Q: Evaluation reports not generating

**A**: Check configuration:

```yaml
evaluation:
  reporting:
    enabled: true
    output_path: "artifacts/evaluation_reports"
    format: ["json", "html", "markdown"]
```

Verify output directory exists:
```bash
mkdir -p artifacts/evaluation_reports
ls -la artifacts/evaluation_reports/
```

---

## Monitoring & Alerts

### Q: Alerts not triggering

**A**: Check alert configuration:

1. Verify alerting enabled:
```yaml
monitoring:
  alerting:
    enabled: true
```

2. Check channels configured:
```yaml
monitoring:
  alerting:
    channels:
      slack:
        enabled: true
        webhook_url: "${SLACK_WEBHOOK_URL}"
```

3. Test alerts:
```bash
python -m codex_ml.cli.monitoring test-alerts --channel slack
```

4. Set environment variables:
```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

---

### Q: Dashboards not showing data

**A**: Verify monitoring setup:

1. Check monitoring status:
```bash
cat artifacts/monitoring/status.json
```

2. Verify data is being collected:
```bash
ls -la artifacts/monitoring/metrics/
```

3. Restart monitoring:
```bash
python -m codex_ml.cli.monitoring restart
```

---

## Performance Issues

### Q: Overall performance degradation

**A**: Phase 6 features should have <5% overhead. If experiencing issues:

1. **Measure baseline**:
```bash
# Disable all Phase 6 features
python train.py  # Baseline time
```

2. **Enable features one by one**:
```bash
# Enable only MLflow
python train.py  # Compare time
```

3. **Identify bottleneck**:
```bash
python -m cProfile -o profile.stats train.py
python -m pstats profile.stats
```

4. **Optimize**:
- MLflow: Enable async logging
- Validation: Increase sample size threshold
- Feature store: Enable caching

---

### Q: High memory usage

**A**: Check these areas:

1. **MLflow artifact logging**: Don't log large files frequently
```python
# Log only final model, not intermediate checkpoints
if epoch == final_epoch:
    tracker.log_artifact("model.pt")
```

2. **Feature caching**: Adjust cache size
```yaml
feature_store:
  point_in_time:
    cache_ttl_minutes: 30  # Reduce from 60
```

3. **Validation sampling**: Ensure sampling is enabled
```yaml
data_validation:
  performance:
    sampling_enabled: true
    sample_size: 5000  # Reduce from 10000
```

---

## Configuration Issues

### Q: YAML syntax errors

**A**: Validate YAML:

```bash
# Check syntax
python -c "import yaml; yaml.safe_load(open('configs/production/tracking.yaml'))"

# Use yamllint
yamllint configs/production/tracking.yaml
```

---

### Q: Environment variables not working

**A**: Check variable substitution:

```yaml
# Correct format
slack:
  webhook_url: "${SLACK_WEBHOOK_URL}"

# Verify environment variable is set
echo $SLACK_WEBHOOK_URL

# Or set in script
export SLACK_WEBHOOK_URL="https://hooks.slack.com/..."
```

---

## Deployment Issues

### Q: Staging deployment failed

**A**: Run deployment with validation:

```bash
# Validate only (no changes)
python scripts/deploy_phase6.py --environment staging --validate-only

# Check validation results
cat artifacts/deployment_reports/latest.json

# Fix issues and re-run
python scripts/deploy_phase6.py --environment staging
```

---

### Q: How do I rollback?

**A**: Quick rollback options:

**Option 1: Disable in configs**
```yaml
tracking.mlflow.enabled: false
feature_store.enabled: false
data_validation.enabled: false
```

**Option 2: Git revert**
```bash
git revert <commit-hash>
git push
```

**Option 3: Remove artifacts**
```bash
rm -rf artifacts/monitoring/
rm -rf artifacts/features/
```

---

## Getting Help

### Q: Where can I get support?

**A**: Support channels:

1. **Slack**: #mlops-support (fastest)
2. **Email**: mlops-team@company.com
3. **Documentation**: 
   - `configs/production/README.md`
   - `PHASE_6_QUICKSTART.md`
   - `docs/runbooks/`
4. **Office Hours**: Check team calendar
5. **GitHub Issues**: For bugs or feature requests

---

### Q: How do I report a bug?

**A**: Include this information:

1. **Configuration**: Which features enabled?
2. **Steps to reproduce**: Exact commands/code
3. **Expected vs actual**: What should happen vs what happened
4. **Environment**: Python version, OS, dependencies
5. **Logs**: Relevant error messages or stack traces

Template:
```markdown
**Feature**: MLflow Tracking
**Config**: tracking.mlflow.enabled=true
**Steps**: 
1. Run `python train.py`
2. Check MLflow UI

**Expected**: Runs appear in UI
**Actual**: No runs visible
**Error**: [paste error message]
**Environment**: Python 3.9, Ubuntu 20.04
```

---

### Q: How do I suggest improvements?

**A**: We welcome feedback!

1. **Quick suggestions**: #mlops-support Slack
2. **Feature requests**: GitHub Issues with label "enhancement"
3. **Documentation updates**: Submit PR to `docs/`
4. **Survey**: Fill out feedback form (link in #mlops-support)

---

## Additional Resources

- **Quickstart Guide**: `PHASE_6_QUICKSTART.md`
- **Full Documentation**: `configs/production/README.md`
- **Runbooks**: `docs/runbooks/`
- **Training Materials**: `docs/training_materials/`
- **Phase 7 Roadmap**: `workbench/PHASE7_NEXT_STEPS_ROADMAP.md`

---

*Last updated: 2025-12-07*  
*Questions not answered here? Ask in #mlops-support!*
