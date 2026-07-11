# Troubleshooting Guide
**Last Updated:** 2026-07-11
**Version:** v0.2.1

**Version:** 0.1.0  
**Last Updated: 2026-07-09
**Audience:** Support, Operators, Developers

---

## Quick Diagnostic

```bash
# Check Python version
python --version  # Must be ≥3.12

# Check installation
pip list | grep codex-ml

# Test import
python -c "import codex; print(codex.__version__)"

# Enable debug logging
export LOG_LEVEL=DEBUG
python -m codex.cli score --verbose
```

---

## Common Issues

### Import Errors

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'codex'` | `pip install codex-ml==0.1.0` |
| `ImportError: cannot import name 'X' from 'codex'` | `pip install --upgrade codex-ml` |
| `ImportError: No module named 'torch'` | `pip install codex-ml[ml]==0.1.0` |

### Installation Issues

| Issue | Solution |
|-------|----------|
| pip install fails | Clear cache: `pip cache purge` then retry |
| Version conflict | Create fresh venv: `python -m venv env` |
| Permission denied | Use `--user` flag: `pip install --user codex-ml` |

### Docker Issues

| Issue | Solution |
|-------|----------|
| `docker pull` fails | `docker login` then retry |
| Port 8000 in use | Use different port: `docker run -p 9000:8000` |
| Container exits immediately | Check logs: `docker logs <id>` |
| Out of memory | Reduce batch size or enable GPU |

### Kubernetes Issues

| Issue | Solution |
|-------|----------|
| `CrashLoopBackOff` | Check logs: `kubectl logs <pod>` |
| Pod pending | Check resources: `kubectl describe node` |
| Service unreachable | Port-forward: `kubectl port-forward svc/codex-api-service 8000:8000` |

### Performance Issues

| Issue | Solution |
|-------|----------|
| High latency (>1s) | Reduce batch size, enable caching |
| Out of memory | Use CPU instead of GPU, reduce model size |
| Cache misses | Increase cache TTL, pre-load data |

---

## Debug Mode

### Enable Detailed Logging

```bash
# Environment variable
export LOG_LEVEL=DEBUG

# Run with verbose flag
python -m codex.cli score --verbose

# Check log files
tail -f .codex/sessions/*.log | grep -i error
```

### Collect Diagnostics

```bash
# System info
python -c "import sys, platform; print(f'{platform.system()} {platform.release()}')"

# Python packages
pip list

# GPU info (if available)
nvidia-smi

# Memory usage
free -h  # Linux
sysctl hw.memsize  # macOS
```

---

## Performance Tuning

### Batch Size Optimization

```python
from codex.ml import InferencePipeline

pipeline = InferencePipeline("bert-base")
texts = ["text1", "text2", ...] * 100

# Test different batch sizes
for bs in [1, 8, 16, 32, 64]:
    result = pipeline(texts, batch_size=bs)
    print(f"Batch {bs}: {result.throughput} samples/sec")
```

### Cache Configuration

```python
from codex.ml import CachedInferencePipeline

pipeline = CachedInferencePipeline(
    model="bert-base",
    cache_layers={
        "http": True,
        "model": True,
        "data": True,
        "compute": True
    },
    ttl_seconds=3600
)
```

### Memory Optimization

```python
# Use smaller model
pipeline = InferencePipeline("distilbert-base")

# Reduce batch size
batch_size = 8

# Enable memory optimization
import torch
torch.cuda.empty_cache()
```

---

## Support Resources

- **Docs:** [docs/](../)
- **Issues:** [GitHub Issues](https://github.com/Aries-Serpent/_codex_/issues)
- **Discussions:** [GitHub Discussions](https://github.com/Aries-Serpent/_codex_/discussions)
- **Email:** support@example.com

---

**Last Updated: 2026-07-09
