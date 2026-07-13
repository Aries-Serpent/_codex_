# Profile-Specific Imports Guide

**Version:** v0.2.3  
**Last Updated:** 2026-07-13  
**Status:** Active

## Overview

Codex ML v0.2.3 introduces **profile-scoped import guards** to ensure that optional runtime dependencies (like `prometheus_client`, `torch`, `transformers`) do not leak into the core profile.

This document describes:
1. The three installation profiles
2. How import guards work
3. The circular dependency mitigation strategy
4. Testing and validation

---

## Installation Profiles

### 1. Core Profile (8-15 MB)

**Installation:**
```bash
pip install codex-ml[core]
# or
pip install 'codex-ml[core]==0.2.3'
```

**Dependencies:**
- Hydra (configuration management)
- Pydantic (data validation)
- Marshmallow (serialization)
- SQLite3 (standard library)
- No external metrics collection

**What Works:**
- ✅ Data loading: `from codex_ml.data import load_jsonl, load_csv`
- ✅ Local connectors: `from codex_ml.connectors import LocalConnector`
- ✅ Safety filters: `from codex_ml.safety.filters import SafetyFilters`
- ✅ No-op metrics: `from codex_ml.monitoring import CodexMetricsRegistry`
- ✅ Offline-first workflows

**What Requires Runtime Profile:**
- ❌ `from codex_ml.monitoring import get_metrics_text` (requires prometheus_client)
- ❌ `from codex_ml.telemetry.metrics import REQUEST_LATENCY` (requires prometheus_client)
- ❌ ML training/inference (requires torch, transformers)

**Example:**
```python
# Core profile - works without prometheus_client
from codex_ml.data import load_jsonl
from codex_ml.monitoring import CodexMetricsRegistry

# Use noop metrics that work without prometheus_client
registry = CodexMetricsRegistry()
registry.record_training_step(0.5)  # No-op operation

# Try to export metrics - returns "prometheus_client not installed"
from codex_ml.monitoring import get_metrics_text
text = get_metrics_text()
assert "prometheus_client not installed" in text
```

---

### 2. Runtime Profile (20-35 MB)

**Installation:**
```bash
pip install codex-ml[runtime]
# or
pip install 'codex-ml[runtime]==0.2.3'
```

**Dependencies (on top of core):**
- PyTorch
- Hugging Face transformers
- Prometheus client
- Ray (distributed computing)
- FastAPI (API serving)

**What Works:**
- ✅ All core profile features
- ✅ ML inference: `from codex_ml.models import ModelRunner`
- ✅ Pattern learning: `from codex_ml.continuous_learning import PatternLearner`
- ✅ Metrics export: `from codex_ml.monitoring import get_metrics_text`
- ✅ Telemetry: `from codex_ml.telemetry.metrics import REQUEST_LATENCY`
- ✅ Remote connectors: `from codex_ml.connectors import RemoteConnector`

**Example:**
```python
# Runtime profile - prometheus_client available
from codex_ml.data import load_jsonl
from codex_ml.monitoring import CodexMetricsRegistry, get_metrics_text

# Use real Prometheus metrics
registry = CodexMetricsRegistry()
registry.record_training_step(0.5)  # Real metric recording

# Export metrics with actual data
text = get_metrics_text()
assert "codex_ml_" in text  # Real metrics present
```

---

### 3. Full Profile (100+ MB)

**Installation:**
```bash
pip install codex-ml[full]
# or
pip install 'codex-ml[full]==0.2.3'
```

**Dependencies (on top of runtime):**
- All development tools
- Test utilities (pytest, coverage)
- Documentation generators
- Analysis tools
- Jupyter/IPython

**What Works:**
- ✅ All runtime profile features
- ✅ Development and testing
- ✅ Experimentation notebooks
- ✅ Documentation building

---

## Import Guards

### Pattern: Try-Except with Fallback

All optional runtime dependencies use this pattern:

```python
try:
    from prometheus_client import Counter, Gauge
    _HAS_PROMETHEUS = True
except ImportError:  # pragma: no cover - optional dependency
    Counter = Gauge = None
    _HAS_PROMETHEUS = False

# Later in code
if _HAS_PROMETHEUS:
    counter = Counter("requests_total", "Total requests")
else:
    counter = None  # Noop
```

### Key Points

1. **Exception Type**: Must catch `ImportError`, not `IOError` or `OSError`
   - ❌ `except (IOError, OSError)` — wrong, won't catch import failures
   - ✅ `except ImportError` — correct

2. **Noop Fallbacks**: Provide no-op implementations
   ```python
   class _NoopMetric:
       def inc(self, amount=1.0): pass
       def observe(self, value): pass
       def labels(self, **kwargs): return self
   ```

3. **Module-Level Guards**: Apply at import time, not usage time
   - ✅ Guard at: `from prometheus_client import Counter`
   - ❌ Do NOT guard at: `counter.inc()` — too late!

---

## Circular Dependency Mitigation

### Problem (v0.2.2)

```
data.loaders → connectors.base → connectors.remote
    → monitoring.health → monitoring.__init__
    → monitoring.metrics_export
    → (tries to import prometheus_client without guard)
    → ModuleNotFoundError in core profile
```

### Solution (v0.2.3)

**1. Lazy-load in monitoring.__init__.py:**
```python
# BEFORE (v0.2.2) - immediate import fails
from .metrics_export import get_metrics_text, metrics_endpoint_fastapi

# AFTER (v0.2.3) - lazy load only when used
def __getattr__(name: str) -> object:
    """Lazy-load metrics_export to avoid prometheus_client import in core profile."""
    if name in ("get_metrics_text", "metrics_endpoint_fastapi"):
        from .metrics_export import get_metrics_text, metrics_endpoint_fastapi
        globals()[name] = locals()[name]
        return locals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
```

**2. Optional import in connectors/remote.py:**
```python
try:
    from codex_ml.monitoring.health import record_health_event
except ImportError:  # pragma: no cover - optional monitoring
    def record_health_event(*_args, **_kwargs) -> None:
        return None
```

**3. Exception guard in connectors/__init__.py:**
```python
# BEFORE (v0.2.2) - unconditional import
from .remote import RemoteConnector  # This could trigger monitoring import

# AFTER (v0.2.3) - safe because remote.py guards monitoring import
from .remote import RemoteConnector  # Safe!
```

### Impact Chain

✅ **Core Profile Success:**
```
data.loaders → connectors.base → connectors.remote
    → monitoring.health (safe, no prometheus import)
    → monitoring.__init__ (safe, metrics_export lazy-loaded)
    ✅ No ImportError
```

✅ **Runtime Profile Success:**
```
Same chain, but when get_metrics_text is called:
    → metrics_export imported on-demand
    → prometheus_client available
    ✅ Metrics exported successfully
```

---

## Testing & Validation

### Test 1: Core Profile Without prometheus_client

```bash
# Uninstall prometheus_client
pip uninstall prometheus-client -y

# Test core imports
python3 -c "from codex_ml.data import load_jsonl; print('OK')"
python3 -c "from codex_ml.connectors import LocalConnector; print('OK')"
python3 -c "from codex_ml.monitoring import CodexMetricsRegistry; print('OK')"
```

### Test 2: Runtime Profile With prometheus_client

```bash
# Install prometheus_client
pip install prometheus-client

# Test all imports
python3 -c "from codex_ml.data import load_jsonl; print('OK')"
python3 -c "from codex_ml.monitoring import get_metrics_text; print('OK')"
python3 -c "from codex_ml.telemetry.metrics import REQUEST_LATENCY; print('OK')"
```

### Test 3: Circular Dependency Resolution

```python
# Should not raise ImportError in core profile
from codex_ml.data.loaders import load_jsonl
from codex_ml.connectors.remote import RemoteConnector
from codex_ml.monitoring.health import record_health_event

# All imports succeeded - circular dependency resolved
```

---

## Migration Guide (v0.2.2 → v0.2.3)

### For End Users

**No action required** if you use `pip install codex-ml[core]` or `pip install codex-ml[runtime]`.

If you see `ModuleNotFoundError: No module named 'prometheus_client'`:
```bash
# Option 1: Install runtime profile (includes prometheus_client)
pip install 'codex-ml[runtime]'

# Option 2: Install prometheus_client separately
pip install prometheus-client
```

### For Contributors

1. **Import guards**: All optional dependencies must use try-except guards
2. **Exception type**: Use `ImportError`, not `IOError` or `OSError`
3. **Lazy loading**: Use `__getattr__` in `__init__.py` for expensive modules
4. **Testing**: Validate both with and without optional dependencies

---

## Files Modified (v0.2.3)

1. **src/codex_ml/monitoring/__init__.py**
   - Added `__getattr__` for lazy-loading metrics_export

2. **src/codex_ml/monitoring/metrics_export.py**
   - Changed exception from `(IOError, OSError)` to `ImportError`

3. **src/codex_ml/monitoring/prometheus_metrics.py**
   - Changed exception from `(IOError, OSError)` to `ImportError`

4. **src/codex_ml/safety/moderation.py**
   - Changed exception from `(IOError, OSError)` to `ImportError`

5. **src/codex_ml/connectors/remote.py**
   - Changed exception from `(IOError, OSError)` to `ImportError`

6. **src/codex_ml/telemetry/server.py**
   - Changed exception from `(ConnectionError, TimeoutError)` to `ImportError`

7. **src/codex_ml/telemetry/metrics.py**
   - Changed exception from `(ConnectionError, TimeoutError)` to `ImportError`

---

## Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| `ModuleNotFoundError: No module named 'prometheus_client'` | Core profile, optional dependency missing | Install runtime: `pip install codex-ml[runtime]` |
| `ImportError: No module named 'codex_ml.data'` | Circular import not resolved | Update to v0.2.3 or later |
| Metrics not exported | Using core profile | Switch to runtime profile or install prometheus-client |
| Noop metrics always used | prometheus_client not imported correctly | Check `_HAS_PROMETHEUS` flag in module |

---

## See Also

- [pyproject.toml](../../pyproject.toml) — Profile definitions
- [Packaging Documentation](../packaging.md) — Dependency management
- [CHANGELOG.md](../../CHANGELOG.md) — v0.2.3 release notes
