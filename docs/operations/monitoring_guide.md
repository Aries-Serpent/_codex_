# Monitoring Guide

## Grafana Dashboards

### Setup

```bash
# Start Grafana
docker run -d -p 3000:3000 grafana/grafana

# Import dashboard
curl -X POST http://localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @configs/grafana/dashboards/ml_operations.json
```

### Available Dashboards

1. **ML Operations** - Model performance, requests, errors
2. **Drift Detection** - Data/config/model drift trends
3. **Resource Utilization** - GPU, CPU, memory
4. **Deployment History** - Version timeline, rollbacks

## AlertManager

### Configuration

Alert routing is defined in `configs/alertmanager/alertmanager.yml`.

### Severity Routing

- **Critical** → PagerDuty (immediate page)
- **High** → Slack #ml-ops-critical
- **Medium** → Slack #ml-ops-warnings
- **Low** → Email

### Custom Alerts

Add to `prometheus_rules.yml`:

```yaml
groups:
  - name: ml_alerts
    rules:
      - alert: ModelAccuracyDrop
        expr: model_accuracy < 0.90
        for: 5m
        labels:
          severity: high
        annotations:
          description: "Model accuracy below 90%"
```

## Prometheus Metrics

Exposed at `/metrics` endpoint:

- `model_accuracy` - Current model accuracy
- `http_requests_total` - Request counter
- `http_errors_total` - Error counter
- `active_models` - Number of active models

See `src/codex_ml/monitoring/metrics.py` for full list.
