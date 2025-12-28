# Inference Monitoring Guide

Comprehensive guide for monitoring ML model inference in production.

## Overview

This guide covers monitoring strategies, metrics collection, alerting, and observability for production inference systems.

## Key Metrics

### Performance Metrics

**Latency:**
- P50, P95, P99 response times
- End-to-end latency
- Model inference time
- Pre/post-processing time

**Throughput:**
- Requests per second (RPS)
- Batches processed per second
- Token throughput (for LLMs)

**Resource Utilization:**
- CPU usage
- GPU utilization and memory
- System memory
- Network I/O

### Quality Metrics

**Prediction Quality:**
- Confidence scores
- Prediction distribution
- Output validation failures
- Data drift detection

**Error Rates:**
- HTTP error rates (4xx, 5xx)
- Model inference errors
- Timeout rates
- Validation failures

## Monitoring Stack

### Recommended Tools

**Metrics Collection:**
- Prometheus - Time-series metrics
- StatsD - Application metrics
- OpenTelemetry - Distributed tracing

**Visualization:**
- Grafana - Dashboards and alerts
- Kibana - Log analysis
- Custom dashboards

**Alerting:**
- AlertManager - Prometheus alerts
- PagerDuty - Incident management
- Slack/Discord - Team notifications

## Implementation

### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, Gauge

# Request metrics
inference_requests = Counter(
    'inference_requests_total',
    'Total inference requests',
    ['model_name', 'version', 'status']
)

inference_duration = Histogram(
    'inference_duration_seconds',
    'Inference duration in seconds',
    ['model_name', 'version']
)

# Resource metrics
gpu_utilization = Gauge(
    'gpu_utilization_percent',
    'GPU utilization percentage',
    ['gpu_id']
)

# Quality metrics
prediction_confidence = Histogram(
    'prediction_confidence',
    'Model prediction confidence scores',
    ['model_name']
)
```

### FastAPI Integration

```python
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

# Auto-instrument FastAPI
Instrumentator().instrument(app).expose(app)

@app.post("/predict")
async def predict(data: Dict):
    with inference_duration.labels(
        model_name="model_v1",
        version="1.0"
    ).time():
        result = model.predict(data)
    
    inference_requests.labels(
        model_name="model_v1",
        version="1.0",
        status="success"
    ).inc()
    
    return result
```

## Dashboards

### Key Dashboards

**1. Overview Dashboard**
- Total requests (24h)
- Error rate (%)
- P95 latency trend
- Active models

**2. Performance Dashboard**
- Latency percentiles (P50, P95, P99)
- Throughput graph
- Resource utilization
- Batch size distribution

**3. Quality Dashboard**
- Prediction confidence distribution
- Error type breakdown
- Data drift indicators
- Model comparison

**4. Resource Dashboard**
- CPU/GPU utilization
- Memory usage
- Network I/O
- Queue lengths

## Alerting Rules

### Critical Alerts

```yaml
groups:
  - name: inference_critical
    rules:
      - alert: HighErrorRate
        expr: rate(inference_requests_total{status="error"}[5m]) > 0.05
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }}% over 5 minutes"

      - alert: HighLatency
        expr: histogram_quantile(0.95, inference_duration_seconds) > 1.0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High P95 latency"
          description: "P95 latency is {{ $value }}s"

      - alert: GPUOutOfMemory
        expr: gpu_memory_used_bytes / gpu_memory_total_bytes > 0.95
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "GPU memory almost exhausted"
```

## Logging Strategy

### Structured Logging

```python
import structlog

logger = structlog.get_logger()

@app.post("/predict")
async def predict(request_id: str, data: Dict):
    logger.info(
        "inference_request_received",
        request_id=request_id,
        model_name="model_v1",
        input_size=len(data)
    )
    
    try:
        result = model.predict(data)
        
        logger.info(
            "inference_completed",
            request_id=request_id,
            duration_ms=duration,
            confidence=result.confidence
        )
        
        return result
    except Exception as e:
        logger.error(
            "inference_failed",
            request_id=request_id,
            error=str(e),
            exc_info=True
        )
        raise
```

### Log Levels

- **DEBUG**: Detailed diagnostic information
- **INFO**: General operational events
- **WARNING**: Unusual events that aren't errors
- **ERROR**: Error events that still allow operation
- **CRITICAL**: Severe errors requiring immediate attention

## Tracing

### Distributed Tracing Setup

```python
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

tracer = trace.get_tracer(__name__)

@app.post("/predict")
async def predict(data: Dict):
    with tracer.start_as_current_span("inference_request"):
        # Pre-processing span
        with tracer.start_as_current_span("preprocess"):
            preprocessed = preprocess(data)
        
        # Model inference span
        with tracer.start_as_current_span("model_inference"):
            result = model.predict(preprocessed)
        
        # Post-processing span
        with tracer.start_as_current_span("postprocess"):
            final_result = postprocess(result)
        
        return final_result
```

## Health Checks

### Endpoint Implementation

```python
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    checks = {
        "model_loaded": model is not None,
        "gpu_available": torch.cuda.is_available(),
        "memory_ok": check_memory_usage() < 0.9
    }
    
    if all(checks.values()):
        return {"status": "healthy", "checks": checks}
    else:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "checks": checks}
        )

@app.get("/ready")
async def readiness_check():
    """Readiness check for load balancer."""
    # Check if model is warm and ready
    if model.is_ready():
        return {"status": "ready"}
    return JSONResponse(status_code=503, content={"status": "not_ready"})
```

## Data Drift Detection

### Monitor Input Distribution

```python
from scipy.stats import ks_2samp

class DriftDetector:
    def __init__(self, reference_data):
        self.reference_data = reference_data
    
    def detect_drift(self, current_data, threshold=0.05):
        """Detect distribution drift using KS test."""
        statistic, p_value = ks_2samp(
            self.reference_data,
            current_data
        )
        
        is_drift = p_value < threshold
        
        logger.info(
            "drift_check",
            p_value=p_value,
            is_drift=is_drift
        )
        
        return is_drift
```

## Best Practices

### Monitoring Checklist

- [ ] Metrics collection enabled
- [ ] Dashboards created and accessible
- [ ] Alerts configured with proper thresholds
- [ ] On-call rotation established
- [ ] Runbooks documented
- [ ] Log retention policy defined
- [ ] Monitoring tested in staging

### Performance Tips

- Use sampling for high-volume metrics
- Aggregate metrics before export
- Use async logging
- Set appropriate retention periods
- Monitor the monitoring system

### Security

- Secure metrics endpoints
- Sanitize logs (no PII/secrets)
- Use authentication for dashboards
- Encrypt metrics in transit
- Regular security audits

## Troubleshooting

### Common Issues

**High Latency:**
- Check batch sizes
- Review model optimization
- Inspect resource utilization
- Analyze slow queries

**Memory Leaks:**
- Monitor memory over time
- Check for tensor accumulation
- Review batch processing
- Inspect cache sizes

**Prediction Errors:**
- Validate input data
- Check model compatibility
- Review preprocessing logic
- Inspect error logs

## Resources

- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- [Grafana Documentation](https://grafana.com/docs/)
- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)
- [ML Monitoring Guide](https://ml-ops.org/content/three-levels-of-ml-software)

## Related Guides

- [Inference Performance](inference_performance.md)
- [Inference Deployment](inference_deployment.md)
- [Production ML Best Practices](../docs/ml_ops/production_best_practices.md)
