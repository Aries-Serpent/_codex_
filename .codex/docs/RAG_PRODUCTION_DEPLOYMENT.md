# RAG Module Production Deployment Guide

**Version:** 1.0.0  
**Last Updated:** 2026-02-10  
**Status:** Production Ready

---

## 📋 Overview

This guide provides comprehensive instructions for deploying the RAG (Retrieval-Augmented Generation) module to production environments. The module includes meta tensor handling, embedding generation, FAISS-based retrieval, and integration with external APIs.

---

## ✅ Prerequisites

### Required Environment Variables

| Variable | Purpose | Required | Default |
|----------|---------|----------|---------|
| `HF_TOKEN` | HuggingFace API token for model downloads | Yes | None |
| `RAG_OPENAI_KEY` | OpenAI API key for OpenAI embeddings provider | Optional | None |
| `PYTHONPATH` | Should include `src` directory | Yes | None |

### Required Dependencies

```txt
# Core RAG dependencies (from requirements.txt)
sentence-transformers>=3.0.0    # Embedding model framework
faiss-cpu>=1.7.4                # Vector similarity search
openai>=1.0.0                   # OpenAI API client
torch==2.10.0+cpu               # PyTorch (CPU-only)

# Additional dependencies
transformers>=4.40.0            # HuggingFace transformers
numpy>=1.26.0                   # Numerical operations
```

### System Requirements

**Minimum:**
- CPU: 2 cores
- RAM: 4GB
- Storage: 5GB (for model cache)
- Python: 3.12+

**Recommended:**
- CPU: 4 cores
- RAM: 8GB
- Storage: 10GB (for multiple model caches)
- Python: 3.12+

---

## 🚀 Deployment Steps

### 1. Install Dependencies

```bash
# Clone repository (if not already done)
git clone https://github.com/Aries-Serpent/_codex_.git
cd _codex_

# Install using pip
pip install -r requirements.txt
pip install -r requirements-test.txt

# Verify installation
python -c "import sentence_transformers; import faiss; import openai; print('✅ All dependencies installed')"
```

### 2. Configure Environment

```bash
# Set required environment variables
export HF_TOKEN="your-huggingface-token-here"
export RAG_OPENAI_KEY="your-openai-key-here"  # Optional
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Verify environment
python -c "import os; assert os.getenv('HF_TOKEN'), 'HF_TOKEN not set'; print('✅ Environment configured')"
```

**Security Note:** Never commit tokens to version control. Use environment files (.env) or secret management systems.

### 3. Pre-download and Cache Models

Pre-caching models significantly improves startup time and reduces production latency:

```python
# Pre-download embedding models
from sentence_transformers import SentenceTransformer
import os

cache_dir = "/app/model_cache"  # Use persistent storage
os.makedirs(cache_dir, exist_ok=True)

# Download commonly used models
models = [
    "sentence-transformers/all-MiniLM-L6-v2",  # Lightweight, fast
    "sentence-transformers/all-mpnet-base-v2",  # Higher quality
]

for model_name in models:
    print(f"Downloading {model_name}...")
    model = SentenceTransformer(
        model_name,
        cache_folder=cache_dir,
        token=os.getenv('HF_TOKEN')
    )
    print(f"✅ {model_name} cached")
```

### 4. Test RAG Functionality

```bash
# Run core meta tensor tests
PYTHONPATH=src pytest tests/test_rag_meta_tensor_regression.py -v

# Run full RAG test suite (optional, takes ~5 minutes)
PYTHONPATH=src pytest tests/test_rag*.py -v --tb=short

# Expected: 213+ tests passing
```

### 5. Verify Production Readiness

```python
# Test meta tensor handling
from codex.rag.utils import safe_model_to_device, has_meta_tensors
import torch

# Create meta tensor model
with torch.device('meta'):
    model = torch.nn.Linear(10, 5)

# Verify meta tensor detection
assert has_meta_tensors(model) == True, "Meta tensor detection failed"

# Verify safe device transfer
model = safe_model_to_device(model, 'cpu')
assert has_meta_tensors(model) == False, "Device transfer failed"
print("✅ Meta tensor handling working correctly")
```

---

## 📊 Monitoring & Observability

### Key Metrics

| Metric | Description | Threshold | Action |
|--------|-------------|-----------|--------|
| `rag.meta_tensor_detected` | Rate of meta tensor detections | < 10% | Normal operation |
| `rag.to_empty_duration` | Meta tensor device transfer time | < 5s | Monitor for performance |
| `rag.model_load_time` | Model initialization time | < 30s | Check caching |
| `rag.embedding_latency` | Text embedding generation time | < 100ms | Optimize batch size |
| `rag.retrieval_latency` | FAISS search time | < 50ms | Check index size |

### Logging Configuration

The RAG module uses Python's standard logging. Configure for production:

```python
import logging

# Production logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/rag/rag.log'),
        logging.StreamHandler()
    ]
)

# Set specific loggers
logging.getLogger('codex.rag').setLevel(logging.INFO)
logging.getLogger('sentence_transformers').setLevel(logging.WARNING)
```

### Log Messages to Monitor

**INFO Level:**
- `"Meta tensor device transfer completed in X.XXXs"` - Meta tensor handling
- `"Model device transfer completed in X.XXXs"` - Standard transfers (if > 1s)

**WARNING Level:**
- `"Meta tensor detected in model"` - Meta tensor usage detected
- `"PyTorch not available, attempting fallback"` - Missing PyTorch

**ERROR Level:**
- `"PyTorch version does not support to_empty()"` - Upgrade required
- `"Error moving model to device"` - Device transfer failure

### Recommended Alerts

Configure alerts based on your monitoring system:

```yaml
# Example alert configuration (adjust for your system)
alerts:
  - name: high_meta_tensor_rate
    condition: rag.meta_tensor_detected > 0.10  # More than 10%
    severity: warning
    message: "High meta tensor detection rate - investigate model initialization"
  
  - name: slow_device_transfer
    condition: rag.to_empty_duration > 5.0  # More than 5 seconds
    severity: warning
    message: "Slow meta tensor device transfer - performance issue"
  
  - name: slow_model_load
    condition: rag.model_load_time > 30.0  # More than 30 seconds
    severity: warning
    message: "Slow model loading - check caching and network"
```

---

## 🔧 Troubleshooting

### Issue: Meta Tensor Errors

**Symptom:**
```
NotImplementedError: Cannot copy out of meta tensor; no data!
```

**Root Cause:** Models initialized with meta tensors attempting standard `.to()` device transfer.

**Solution:**
1. Verify `safe_model_to_device()` is being used (not direct `.to()`)
2. Check logs for "Meta tensor detected" warnings
3. Ensure PyTorch >= 2.0 (supports `to_empty()`)

**Prevention:** Always use `safe_model_to_device()` for all model device transfers.

---

### Issue: Model Download Timeouts

**Symptom:**
```
ConnectionError: Unable to download model from HuggingFace
```

**Root Cause:** Missing HF_TOKEN or network connectivity issues.

**Solution:**
1. Verify `HF_TOKEN` is set: `echo $HF_TOKEN`
2. Test connectivity: `curl https://huggingface.co`
3. Pre-download models during deployment (see Step 3)
4. Use model cache in persistent storage

**Prevention:** Pre-cache models in container images or shared volumes.

---

### Issue: FAISS Index Creation Fails

**Symptom:**
```
RuntimeError: Error creating FAISS index
```

**Root Cause:** Missing `get_sentence_embedding_dimension()` method or incorrect dimension.

**Solution:**
1. Verify using real SentenceTransformer (not mock)
2. Check dimension: `model.get_sentence_embedding_dimension()`
3. Ensure dimension matches embeddings (typically 384 or 768)

**Prevention:** Use proper model initialization with dimension validation.

---

### Issue: High Memory Usage

**Symptom:** Container OOM killed or slow performance

**Root Cause:** Multiple model instances or large batch sizes

**Solution:**
1. Reduce batch size in embedding generation
2. Use single model instance (singleton pattern)
3. Monitor memory with: `docker stats` or system tools
4. Consider model quantization for production

**Prevention:** Load models once, reuse across requests.

---

## 🔐 Security Considerations

### Secret Management

**DO:**
- ✅ Use environment variables or secret management systems
- ✅ Rotate tokens regularly (quarterly minimum)
- ✅ Use read-only tokens when possible
- ✅ Implement rate limiting on API calls

**DON'T:**
- ❌ Never log HF_TOKEN or RAG_OPENAI_KEY
- ❌ Never commit tokens to version control
- ❌ Never share tokens between environments
- ❌ Never use root tokens in production

### Model Cache Security

```bash
# Set proper permissions on model cache
chmod 755 /app/model_cache
chown app:app /app/model_cache

# Use read-only cache in production containers
docker run -v model_cache:/app/model_cache:ro ...
```

### Input Validation

Always validate and sanitize user inputs before embedding:

```python
def validate_input(text: str) -> str:
    """Validate and sanitize text input."""
    if not text or not isinstance(text, str):
        raise ValueError("Invalid input: must be non-empty string")
    
    # Limit length to prevent abuse
    max_length = 10000
    if len(text) > max_length:
        raise ValueError(f"Input too long: max {max_length} characters")
    
    # Remove control characters
    text = ''.join(c for c in text if c.isprintable() or c.isspace())
    
    return text.strip()
```

---

## ⚡ Performance Optimization

### Model Caching Strategy

```python
# Singleton pattern for model reuse
class ModelCache:
    _instance = None
    _models = {}
    
    @classmethod
    def get_model(cls, model_name: str):
        if cls._instance is None:
            cls._instance = cls()
        
        if model_name not in cls._models:
            cls._models[model_name] = SentenceTransformer(
                model_name,
                cache_folder="/app/model_cache"
            )
        
        return cls._models[model_name]

# Usage
model = ModelCache.get_model("sentence-transformers/all-MiniLM-L6-v2")
```

### Batch Processing

```python
# Efficient batch embedding
def embed_texts_batch(texts: list[str], batch_size: int = 32):
    """Process texts in batches for efficiency."""
    embeddings = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        batch_embeddings = model.encode(
            batch,
            batch_size=batch_size,
            show_progress_bar=False,
            convert_to_numpy=True
        )
        embeddings.append(batch_embeddings)
    
    return np.vstack(embeddings)
```

### Resource Allocation

**Container Configuration:**
```yaml
# Docker Compose example
services:
  rag-service:
    image: codex-rag:latest
    resources:
      limits:
        cpus: '4'
        memory: 8G
      reservations:
        cpus: '2'
        memory: 4G
    volumes:
      - model_cache:/app/model_cache:ro
    environment:
      - HF_TOKEN=${HF_TOKEN}
      - RAG_OPENAI_KEY=${RAG_OPENAI_KEY}
```

---

## 📈 Production Checklist

Before deploying to production:

- [ ] All dependencies installed and verified
- [ ] Environment variables configured (HF_TOKEN, RAG_OPENAI_KEY)
- [ ] Models pre-cached in persistent storage
- [ ] Test suite passing (213+ tests)
- [ ] Logging configured and tested
- [ ] Monitoring and alerts configured
- [ ] Security scan completed (no HIGH severity issues)
- [ ] Performance benchmarks met
- [ ] Documentation reviewed and updated
- [ ] Rollback plan prepared
- [ ] On-call team notified

---

## 🔗 Related Documentation

- **Technical Fix:** `.codex/docs/RAG_META_TENSOR_FIX.md`
- **Phase 2 Verification:** `.codex/RAG_PHASE2_VERIFICATION_COMPLETE.md`
- **Test Results:** `.codex/RAG_INTEGRATION_COMPLETE_SESSION_SUMMARY.md`
- **CI Workflow:** `.github/workflows/test-rag.yml`

---

## 📞 Support

**For Issues:**
- GitHub Issues: https://github.com/Aries-Serpent/_codex_/issues
- Documentation: `.codex/docs/`

**For Questions:**
- Review troubleshooting section above
- Check test suite for usage examples
- Review source code documentation

---

**Prepared by:** GitHub Copilot  
**Date:** 2026-02-10  
**Phase:** 3 of 3 - CI & Production  
**Status:** Production Ready
