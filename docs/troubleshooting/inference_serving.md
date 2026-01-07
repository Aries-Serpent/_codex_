# Inference Serving Troubleshooting Guide

> **Version**: 2.0.0  
> **Last Updated**: 2025-12-07

---

## Overview

This guide helps diagnose and resolve common issues with the inference serving infrastructure. It covers model loading, authentication, performance, circuit breakers, and deployment problems.

---

## Quick Diagnostic Checklist

Before diving into specific issues, run through this checklist:

- [ ] Check `/health` endpoint status
- [ ] Review Prometheus metrics at `/metrics`
- [ ] Check circuit breaker state
- [ ] Verify model is loaded (`GET /models`)
- [ ] Check logs for errors
- [ ] Verify environment variables
- [ ] Test with simple request

---

## Common Issues

### 1. Model Loading Failures

#### Symptoms
- 500 errors on `/infer` endpoint
- "Model not found" errors
- High `/health` endpoint latency

#### Causes & Solutions

**Cause**: Model file not found
```bash
# Check model path
ls -lh /models/my-model/

# Verify MODEL_PATH environment variable
echo $MODEL_PATH

# Solution: Correct model path
export MODEL_PATH=/correct/path/to/model
```

**Cause**: Insufficient memory
```bash
# Check available memory
free -h

# Check GPU memory (if applicable)
nvidia-smi

# Solution: Reduce batch size or use quantization
export MODEL_QUANTIZATION=int8
```

**Cause**: Invalid model format
```bash
# Verify model format
python3 -c "
from transformers import AutoModel
model = AutoModel.from_pretrained('$MODEL_PATH')
print('Model loaded successfully')
"

# Solution: Re-export model or use correct loader
```

---

### 2. Authentication Failures

#### Symptoms
- 401 Unauthorized responses
- "Invalid API key" errors
- Authentication exhaustion warnings

#### Causes & Solutions

**Cause**: Missing or invalid API keys
```bash
# Check API keys are set
echo $CODEX_API_KEYS

# Solution: Set valid API keys (comma-separated)
export CODEX_API_KEYS="key1,key2,key3"
```

**Cause**: JWT token expired
```python
# Check token expiration
import jwt
token = "your_token"
decoded = jwt.decode(token, options={"verify_signature": False})
print(f"Expires: {decoded['exp']}")

# Solution: Generate new token
```

**Cause**: Timing attack detection
- Constant-time comparison Phase 5 fail on clock skew
- Solution: Ensure NTP sync on all servers

---

### 3. Circuit Breaker Issues

#### Symptoms
- 503 Service Unavailable responses
- "Circuit breaker open" in logs
- `/health` reports unhealthy

#### Diagnostic Commands
```bash
# Check circuit breaker state
curl http://localhost:8000/metrics | grep circuit_breaker_state

# Check failure count
curl http://localhost:8000/metrics | grep circuit_breaker_failure_count

# Check uptime ratio
curl http://localhost:8000/metrics | grep circuit_breaker_uptime_ratio
```

#### Solutions

**If circuit breaker is open:**
1. Check underlying model health:
   ```bash
   # Test model directly
   python3 -c "
   from src.codex_ml.serving.model_loader import ModelLoader
   loader = ModelLoader()
   model = loader.load('model_name')
   print('Model healthy')
   "
   ```

2. Wait for exponential backoff to complete:
   - First retry: 1 second
   - Second retry: 2 seconds
   - Third retry: 4 seconds
   - Max: 300 seconds

3. Manual reset (if needed):
   ```python
   from src.codex_ml.serving.resilience import EnhancedCircuitBreaker
   breaker = EnhancedCircuitBreaker.get_instance("model_name")
   breaker.reset()
   ```

**If circuit breaker is flapping (open/closed rapidly):**
- Increase failure threshold
- Increase backoff duration
- Check for intermittent network issues

---

### 4. High Latency / Slow Responses

#### Diagnostic Workflow

1. **Check P95/P99 latency:**
   ```bash
   curl http://localhost:8000/metrics | grep inference_latency_seconds
   ```

2. **Identify bottleneck:**
   ```bash
   # Check model inference time
   curl http://localhost:8000/metrics | grep model_prediction_latency_seconds
   
   # Check queueing time
   # latency_total - prediction_latency = queue_time
   ```

3. **Check resource utilization:**
   ```bash
   # CPU
   top -bn1 | grep python
   
   # GPU (if applicable)
   nvidia-smi
   
   # Memory
   free -h
   ```

#### Solutions

**High model inference time:**
- Enable quantization: `export MODEL_QUANTIZATION=int8`
- Reduce batch size
- Use GPU acceleration
- Optimize model architecture

**High queueing time:**
- Increase number of workers
- Enable request batching
- Scale horizontally (add replicas)

**Memory pressure:**
- Enable memory pooling
- Reduce cache size
- Use model quantization

**Example performance tuning:**
```python
# In inference server config
from src.codex_ml.serving.optimizations import (
    RequestBatcher, 
    DynamicBatchSizer
)

# Enable batching
batcher = RequestBatcher(
    max_batch_size=32,
    max_wait_ms=10
)

# Enable dynamic sizing
sizer = DynamicBatchSizer(
    target_latency_ms=100
)
```

---

### 5. Rate Limiting Issues

#### Symptoms
- 429 Too Many Requests responses
- Requests rejected during load spikes
- Uneven load distribution

#### Diagnostic Commands
```bash
# Check rate limit metrics
curl http://localhost:8000/metrics | grep rate_limit

# Check request rate
curl http://localhost:8000/metrics | grep request_count
```

#### Solutions

**Increase rate limits:**
```bash
# Set higher limits (requests per minute)
export RATE_LIMIT_RPM=5000
```

**Implement client-side retry:**
```python
import time
import requests

def predict_with_retry(data, max_retries=3):
    for attempt in range(max_retries):
        response = requests.post(
            "http://localhost:8000/infer",
            json=data
        )
        if response.status_code == 429:
            # Exponential backoff
            time.sleep(2 ** attempt)
            continue
        return response.json()
    raise Exception("Rate limit exceeded")
```

**Use token bucket algorithm:**
- Current implementation: Sliding window
- For bursty traffic, consider token bucket

---

### 6. Connection/Network Issues

#### Symptoms
- Connection refused errors
- Timeout errors
- Intermittent failures

#### Diagnostic Steps

1. **Verify service is running:**
   ```bash
   # Check process
   ps aux | grep inference_server
   
   # Check port binding
   netstat -tlnp | grep 8000
   ```

2. **Test connectivity:**
   ```bash
   # Local
   curl http://localhost:8000/health
   
   # Remote
   curl http://<server-ip>:8000/health
   ```

3. **Check firewall rules:**
   ```bash
   # Linux
   sudo iptables -L -n | grep 8000
   
   # Check if port is blocked
   telnet <server-ip> 8000
   ```

#### Solutions

**Connection refused:**
- Ensure server is started: `python -m src.codex_ml.serving.inference_server`
- Check bind address: Should be `0.0.0.0` for remote access

**Timeout errors:**
- Increase client timeout
- Check network latency: `ping <server-ip>`
- Check for packet loss: `mtr <server-ip>`

**DNS issues:**
- Use IP address instead of hostname
- Check DNS resolution: `nslookup <hostname>`

---

### 7. Deployment Issues

#### Symptoms
- Rollback triggered during blue-green deployment
- High error rate in new version
- Traffic not shifting to green

#### Diagnostic Commands
```bash
# Check deployment status
curl http://localhost:8000/deployment/status

# Check traffic weights
curl http://localhost:8000/metrics | grep traffic_weight
```

#### Solutions

**Rollback triggered:**
1. Check error rate threshold:
   ```python
   # Default: 5% error rate
   # Adjust if needed
   deployment.config.error_threshold_percent = 10.0
   ```

2. Review logs for errors in green deployment
3. Test green deployment directly before rollout

**Traffic not shifting:**
- Check health checks pass for green
- Verify minimum healthy duration met
- Check gradual rollout progress

**Manual traffic control:**
```python
from src.codex_ml.serving.deployment import TrafficSplitter

splitter = TrafficSplitter()
splitter.set_weights(blue=70, green=30)  # 70% blue, 30% green
```

---

### 8. Cache Performance Issues

#### Symptoms
- Low cache hit rate (<50%)
- High memory usage
- Stale predictions

#### Diagnostic Commands
```bash
# Check cache metrics
curl http://localhost:8000/metrics | grep cache_hit_rate
curl http://localhost:8000/metrics | grep cache_size_bytes
```

#### Solutions

**Low hit rate:**
- Increase cache size (default: 3 models)
- Analyze request patterns
- Implement request normalization

**High memory usage:**
- Reduce cache size
- Enable cache eviction
- Use quantized models

**Stale predictions:**
- Implement cache invalidation
- Set TTL for cached models
- Manual cache clear: `loader.clear_cache()`

---

## Error Code Reference

| Code | Meaning | Solution |
|------|---------|----------|
| 400 | Bad Request | Check request payload format |
| 401 | Unauthorized | Verify API key/JWT token |
| 429 | Too Many Requests | Implement retry with backoff |
| 500 | Internal Server Error | Check logs, circuit breaker state |
| 503 | Service Unavailable | Circuit breaker open, wait for recovery |
| 504 | Gateway Timeout | Increase timeout, optimize model |

---

## Performance Debugging

### Latency Breakdown

```python
# Example latency breakdown
total_latency = 500ms
├── Queue wait: 10ms (2%)
├── Authentication: 5ms (1%)
├── Preprocessing: 50ms (10%)
├── Model inference: 400ms (80%)
└── Postprocessing: 35ms (7%)
```

### Optimization Priority

1. **Model inference (80%)**: Use quantization, GPU, smaller model
2. **Preprocessing (10%)**: Vectorize operations, use compiled libraries
3. **Postprocessing (7%)**: Optimize format conversion
4. **Queue wait (2%)**: Enable batching
5. **Authentication (1%)**: Use token caching

---

## Monitoring Best Practices

### Key Metrics to Watch

1. **Request rate**: Sudden spikes Phase 5 indicate attack or legitimate traffic surge
2. **Error rate**: Should be <1% in production
3. **P95 latency**: Should be <500ms for interactive use cases
4. **Circuit breaker state**: Should be "closed" >99% of time
5. **Cache hit rate**: Target >60% for cost efficiency

### Alert Thresholds

```yaml
# Recommended Prometheus alert thresholds
- error_rate > 5% for 5 minutes
- p95_latency > 1s for 10 minutes  
- circuit_breaker_open > 0 for 2 minutes
- cache_hit_rate < 40% for 30 minutes
- cpu_usage > 90% for 5 minutes
- memory_usage > 90% for 5 minutes
```

---

## Getting Help

### Information to Provide

When requesting support, include:

1. **Symptoms**: What's not working?
2. **Logs**: Last 100 lines from inference server
3. **Metrics**: Current Prometheus metrics (`/metrics`)
4. **Configuration**: Environment variables
5. **Request example**: Sample failing request
6. **Timeline**: When did issue start?

### Useful Commands

```bash
# Collect diagnostic bundle
./scripts/collect_diagnostics.sh

# Generate report
python -m src.codex_ml.serving.diagnostics --report

# Test model loading
python -m src.codex_ml.serving.model_loader --test

# Benchmark performance
python -m tests.serving.test_inference_performance --benchmark
```

---

## Related Documentation

- [Architecture Overview](../architecture/inference_serving.md)
- [Performance Optimization Guide](../guides/inference_performance.md)
- [Deployment Guide](../guides/inference_deployment.md)
- [Monitoring Setup](../guides/inference_monitoring.md)

---

*Last reviewed: 2025-12-07*
