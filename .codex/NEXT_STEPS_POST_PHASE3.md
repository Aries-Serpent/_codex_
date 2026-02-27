# 🚀 Next Steps: RAG Module Post-Phase 3 Actions

**Previous Work:** All 3 phases complete (Core fix, Testing, CI/Production)  
**Current Status:** Production Ready  
**Next:** Staging deployment and performance validation

---

## 📋 Immediate Actions (Week 1)

### Action 1: Deploy to Staging Environment

**Objective:** Validate RAG module in staging before production rollout

**Steps:**

1. **Prepare Staging Environment**
   ```bash
   # Set environment variables
   export HF_TOKEN="your-staging-token"
   export RAG_OPENAI_KEY="your-staging-key"
   export PYTHONPATH="/app/src"

   # Install dependencies
   pip install -r requirements.txt
   pip install -r requirements-test.txt
   ```

2. **Pre-cache Models**
   ```bash
   # Run model caching script
   python -c "
   from sentence_transformers import SentenceTransformer
   import os

   cache_dir = '/app/model_cache'
   os.makedirs(cache_dir, exist_ok=True)

   # Cache primary model
   model = SentenceTransformer(
       'sentence-transformers/all-MiniLM-L6-v2',
       cache_folder=cache_dir,
       token=os.getenv('HF_TOKEN')
   )
   print('✅ Models cached')
   "
   ```

3. **Run Verification Tests**
   ```bash
   # Full RAG test suite
   PYTHONPATH=src pytest tests/test_rag*.py -v
   # Expected: 213+ passing

   # Meta tensor specific validation
   PYTHONPATH=src pytest tests/test_rag_meta_tensor_regression.py -v
   # Expected: 9/9 passing
   ```

4. **Monitor Performance**
   - Watch logs for: `"Meta tensor device transfer completed in X.XXXs"`
   - Track embedding latency
   - Monitor memory usage
   - Check FAISS retrieval speed

**Success Criteria:**
- [ ] All tests passing in staging (213+)
- [ ] Meta tensor handling working correctly
- [ ] Performance metrics within acceptable ranges
- [ ] No errors in logs for 24 hours

---

### Action 2: Performance Benchmarking

**Objective:** Establish baseline performance metrics

**Benchmarks to Run:**

```python
# benchmark_rag_performance.py
import time
import numpy as np
from sentence_transformers import SentenceTransformer
from codex.rag.utils import safe_model_to_device

def benchmark_embedding_generation():
    """Measure embedding generation performance."""
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

    texts = ["Sample text"] * 100

    start = time.time()
    embeddings = model.encode(texts, batch_size=32)
    duration = time.time() - start

    print(f"Embedding 100 texts: {duration:.3f}s")
    print(f"Per-text latency: {duration/100*1000:.1f}ms")

    return duration

def benchmark_meta_tensor_transfer():
    """Measure meta tensor device transfer performance."""
    import torch

    # Create meta tensor model
    with torch.device('meta'):
        model = torch.nn.Linear(1000, 1000)

    start = time.time()
    model = safe_model_to_device(model, 'cpu')
    duration = time.time() - start

    print(f"Meta tensor transfer: {duration:.3f}s")
    return duration

if __name__ == '__main__':
    print("=== RAG Performance Benchmarks ===\n")

    embedding_time = benchmark_embedding_generation()
    transfer_time = benchmark_meta_tensor_transfer()

    print("\n=== Baseline Metrics ===")
    print(f"Embedding generation: {embedding_time:.3f}s (target: <1.0s)")
    print(f"Meta tensor transfer: {transfer_time:.3f}s (target: <0.5s)")
```

**Run Benchmarks:**
```bash
PYTHONPATH=src python benchmark_rag_performance.py
```

**Target Metrics:**
- Embedding generation: < 1.0s for 100 texts
- Meta tensor transfer: < 0.5s
- Memory usage: < 2GB per process
- FAISS retrieval: < 50ms per query

**Document Results:**
Create `.codex/RAG_PERFORMANCE_BASELINE.md` with results

---

### Action 3: Security Audit

**Objective:** Verify production security readiness

**Security Checklist:**

```bash
# 1. Secret management audit
echo "Checking environment variables..."
[ -z "$HF_TOKEN" ] && echo "❌ HF_TOKEN not set" || echo "✅ HF_TOKEN set"
[ -z "$RAG_OPENAI_KEY" ] && echo "⚠️ RAG_OPENAI_KEY not set (optional)" || echo "✅ RAG_OPENAI_KEY set"

# 2. Run Bandit security scan
pip install bandit
bandit -r src/codex/rag/ -f txt -o security-audit.txt
cat security-audit.txt

# 3. Check for hardcoded secrets
grep -r "hf_[A-Za-z0-9]" src/codex/rag/ && echo "❌ Found potential HF tokens" || echo "✅ No hardcoded tokens"
grep -r "sk-[A-Za-z0-9]" src/codex/rag/ && echo "❌ Found potential OpenAI keys" || echo "✅ No hardcoded keys"

# 4. Validate input sanitization
PYTHONPATH=src python -c "
from codex.rag.utils import safe_model_to_device

# Test with malicious inputs
try:
    safe_model_to_device(None, 'cpu')
except Exception as e:
    print(f'✅ Handles None: {type(e).__name__}')
"
```

**Review:**
- [ ] No HIGH severity Bandit issues
- [ ] No hardcoded secrets in code
- [ ] Input validation working
- [ ] Rate limiting configured (if applicable)

---

## 📊 Short-term Actions (Month 1)

### Action 4: Extended Device Testing

**Objective:** Validate across different hardware configurations

**Test Matrix:**

| Device | Test Command | Expected Result |
|--------|--------------|-----------------|
| CPU | `DEVICE=cpu pytest tests/test_rag*.py` | 213+ passing |
| CUDA (if available) | `DEVICE=cuda pytest tests/test_rag*.py` | 213+ passing |
| MPS (Apple Silicon) | `DEVICE=mps pytest tests/test_rag*.py` | 213+ passing |

**Create Test Script:**
```bash
#!/bin/bash
# test_all_devices.sh

devices=("cpu")
[ -x "$(command -v nvidia-smi)" ] && devices+=("cuda")
[ "$(uname)" == "Darwin" ] && devices+=("mps")

for device in "${devices[@]}"; do
    echo "Testing on $device..."
    DEVICE=$device PYTHONPATH=src pytest tests/test_rag*.py -v --tb=short
done
```

**Document Results:**
Update `.codex/docs/RAG_PRODUCTION_DEPLOYMENT.md` with device-specific guidance

---

### Action 5: Advanced Monitoring Setup

**Objective:** Production-grade observability

**Monitoring Implementation:**

```python
# monitoring_integration.py
"""
Example integration with monitoring systems.
Adapt for your specific monitoring platform (Datadog, Prometheus, etc.)
"""

class RAGMetrics:
    """Production metrics for RAG operations."""

    @staticmethod
    def record_meta_tensor_detection(device: str):
        """Record meta tensor detection event."""
        # Example: Datadog
        # statsd.increment('rag.meta_tensor_detected', tags=[f'device:{device}'])
        pass

    @staticmethod
    def record_device_transfer_duration(duration: float, device: str):
        """Record device transfer timing."""
        # Example: Prometheus
        # device_transfer_histogram.labels(device=device).observe(duration)
        pass

    @staticmethod
    def record_embedding_latency(duration: float, batch_size: int):
        """Record embedding generation latency."""
        # Example: CloudWatch
        # cloudwatch.put_metric_data(
        #     Namespace='RAG',
        #     MetricData=[{
        #         'MetricName': 'EmbeddingLatency',
        #         'Value': duration,
        #         'Unit': 'Seconds',
        #         'Dimensions': [{'Name': 'BatchSize', 'Value': str(batch_size)}]
        #     }]
        # )
        pass
```

**Integrate into `src/codex/rag/utils.py`:**
```python
# In safe_model_to_device()
if meta_status:
    RAGMetrics.record_meta_tensor_detection(device)
    # ... existing code ...
    RAGMetrics.record_device_transfer_duration(duration, device)
```

**Configure Alerts:**
```yaml
# Example alert configuration
alerts:
  - name: high_meta_tensor_rate
    query: rate(rag.meta_tensor_detected[5m]) > 0.10
    severity: warning
    message: "High meta tensor detection rate"

  - name: slow_device_transfer
    query: histogram_quantile(0.95, rag.device_transfer_duration) > 5.0
    severity: warning
    message: "95th percentile device transfer > 5s"
```

---

### Action 6: Model Optimization

**Objective:** Improve performance and reduce resource usage

**Optimization Strategies:**

1. **Model Quantization**
   ```python
   # Test quantized models
   from sentence_transformers import SentenceTransformer
   import torch

   model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

   # Quantize to int8
   model = torch.quantization.quantize_dynamic(
       model, {torch.nn.Linear}, dtype=torch.qint8
   )

   # Benchmark: Compare speed and quality
   ```

2. **Batch Size Optimization**
   ```python
   # Find optimal batch size
   batch_sizes = [8, 16, 32, 64, 128]
   for batch_size in batch_sizes:
       # Benchmark and measure throughput
       pass
   ```

3. **Model Caching Strategy**
   ```python
   # Singleton pattern for model reuse
   class ModelCache:
       _models = {}

       @classmethod
       def get_model(cls, name):
           if name not in cls._models:
               cls._models[name] = SentenceTransformer(name)
           return cls._models[name]
   ```

---

## 🎯 Long-term Actions (Quarter 1)

### Action 7: Scalability Planning

**Horizontal Scaling:**
- Load balancer configuration
- Shared model cache strategy
- Distributed FAISS index

**Multi-region Deployment:**
- Latency optimization
- Data residency compliance
- Regional model caches

### Action 8: Advanced Features

**Feature Roadmap:**
- Hybrid search (dense + sparse embeddings)
- Multi-language support
- Custom model fine-tuning
- A/B testing framework

### Action 9: Operational Excellence

**SRE Practices:**
- Automated rollback procedures
- Chaos engineering tests
- Disaster recovery drills
- SLA/SLO tracking

---

## 📞 Copilot Continuation Prompt

```markdown
@copilot Continue RAG Module - Post-Phase 3 Actions

**Context:** Phase 3 complete, production ready

**Current Tasks:**
1. Deploy to staging environment
2. Run performance benchmarks
3. Security audit
4. Extended device testing

**Priority:** Week 1 actions (Deploy, Benchmark, Security)

**Reference:** See `.codex/NEXT_STEPS_POST_PHASE3.md` for complete plan

**Success Criteria:**
- Staging deployment successful
- Performance metrics baseline established
- Security audit complete with no HIGH issues
- Ready for production rollout

**AI Agency Policy Active:** Complete all tasks, iterate until done.
```

---

## 📚 Reference Documentation

- **Deployment Guide:** `.codex/docs/RAG_PRODUCTION_DEPLOYMENT.md`
- **Phase 3 Summary:** `.codex/RAG_PHASE3_COMPLETE_FINAL_SUMMARY.md`
- **Cognitive Brain:** `.codex/cognitive_brain/RAG_INTEGRATION_PHASE3_STATUS.md`
- **CI Workflow:** `.github/workflows/test-rag.yml`

---

**Prepared by:** GitHub Copilot  
**Date:** 2026-02-10  
**Status:** Ready for Execution  
**Priority:** Week 1 actions are HIGH priority
