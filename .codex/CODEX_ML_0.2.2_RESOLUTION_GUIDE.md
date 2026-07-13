# codex-ml v0.2.2: Issue Resolution & Implementation Guide

**Created:** 2026-07-13T20:53:47Z  
**Status:** Ready for Implementation  
**Priority Sequence:** P1 → P2 → P3

---

## Critical Issue 1: Runtime Deps Leak into Core Profile

### Problem Statement
Core profile users cannot import `from codex_ml.data import *` because:
- `data` → `data.loaders` → `connectors.remote` → `monitoring.health` → `monitoring.metrics_export`
- `metrics_export` imports `prometheus_client` unconditionally
- `prometheus_client` is runtime-only, not in core profile
- Result: **ModuleNotFoundError: No module named 'prometheus_client'**

### Solution: Step-by-Step Implementation

#### Step 1: Fix `src/codex_ml/monitoring/__init__.py`

**File:** `src/codex_ml/monitoring/__init__.py`

**Current (BROKEN):**
```python
from .metrics_export import get_metrics_text, metrics_endpoint_fastapi
from .health import record_health_event
```

**NEW (FIXED):**
```python
"""Monitoring module with lazy runtime dependency loading."""

import sys
from typing import Any, Optional


def __getattr__(name: str) -> Any:
    """Lazy-load runtime monitoring components."""
    if name == "get_metrics_text":
        try:
            from .metrics_export import get_metrics_text
            return get_metrics_text
        except ImportError:
            raise ImportError(
                f"get_metrics_text requires prometheus_client. "
                f"Install with: pip install codex-ml[runtime]"
            ) from None
    
    if name == "metrics_endpoint_fastapi":
        try:
            from .metrics_export import metrics_endpoint_fastapi
            return metrics_endpoint_fastapi
        except ImportError:
            raise ImportError(
                f"metrics_endpoint_fastapi requires prometheus_client. "
                f"Install with: pip install codex-ml[runtime]"
            ) from None
    
    if name == "record_health_event":
        try:
            from .health import record_health_event
            return record_health_event
        except ImportError:
            # Provide no-op fallback for core profile
            def no_op_record_health_event(*args: Any, **kwargs: Any) -> None:
                pass
            return no_op_record_health_event
    
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "get_metrics_text",
    "metrics_endpoint_fastapi",
    "record_health_event",
]
```

**Verification:**
```bash
# Test 1: Import without runtime deps should work
python -c "from codex_ml.monitoring import record_health_event; print('✓ No-op available')"

# Test 2: Accessing prometheus functions should give clear error
python -c "from codex_ml.monitoring import get_metrics_text; print('✓ Will fail with helpful message')" 2>&1
# Expected output contains: "requires prometheus_client. Install with: pip install codex-ml[runtime]"
```

**Time to Implement:** 5 minutes  
**Verification Time:** 5 minutes

---

#### Step 2: Fix `src/codex_ml/monitoring/metrics_export.py`

**File:** `src/codex_ml/monitoring/metrics_export.py`

**Current (BROKEN):**
```python
from prometheus_client import REGISTRY, CollectorRegistry, generate_latest
```

**NEW (FIXED):**
```python
"""Prometheus metrics export - runtime dependency."""

from typing import Optional


def get_metrics_text() -> str:
    """Export metrics in Prometheus text format."""
    try:
        from prometheus_client import REGISTRY, generate_latest
        return generate_latest(REGISTRY).decode("utf-8")
    except ImportError:
        raise ImportError(
            "prometheus_client is required for metrics export. "
            "Install with: pip install codex-ml[runtime]"
        ) from None


def metrics_endpoint_fastapi() -> Optional[Any]:
    """Create FastAPI metrics endpoint."""
    try:
        from prometheus_client import CONTENT_TYPE_LATEST, generate_latest, REGISTRY
        from fastapi.responses import Response
        
        def handler() -> Response:
            return Response(
                content=generate_latest(REGISTRY),
                media_type=CONTENT_TYPE_LATEST,
            )
        
        return handler
    except ImportError:
        raise ImportError(
            "FastAPI and prometheus_client are required. "
            "Install with: pip install codex-ml[runtime]"
        ) from None
```

**Key Changes:**
- ✅ Move imports inside functions (lazy loading)
- ✅ Raise clear errors if runtime deps missing
- ✅ No module-level prometheus imports

**Time to Implement:** 5 minutes

---

#### Step 3: Fix `src/codex_ml/connectors/remote.py`

**File:** `src/codex_ml/connectors/remote.py`

**Current (PROBLEMATIC):**
```python
from codex_ml.monitoring.health import record_health_event  # Pulls in metrics_export!
```

**NEW (FIXED):**
```python
"""Remote connector implementation."""

from typing import Optional, Any


def _get_health_recorder():
    """Get health recorder with fallback to no-op."""
    try:
        from codex_ml.monitoring.health import record_health_event
        return record_health_event
    except ImportError:
        # Provide no-op in core profile
        def no_op(*args: Any, **kwargs: Any) -> None:
            pass
        return no_op


class RemoteConnector:
    """Remote data connector."""
    
    def __init__(self, *args, **kwargs):
        self._record_health = _get_health_recorder()
    
    def connect(self):
        """Connect to remote source."""
        self._record_health("connector_remote_connect", {"status": "success"})
```

**Time to Implement:** 10 minutes

---

#### Step 4: Create Profile Validation Tests

**File:** `tests/test_profile_core_isolation.py`

```python
"""Test core profile has no runtime dependencies."""

import sys
from typing import List


def block_runtime_modules() -> List[str]:
    """Block runtime modules to simulate core-only environment."""
    blocked = [
        "torch",
        "transformers",
        "datasets",
        "ray",
        "fastapi",
        "prometheus_client",
        "sentence_transformers",
        "chromadb",
        "faiss",
    ]
    
    for mod in blocked:
        if mod in sys.modules:
            del sys.modules[mod]
        sys.modules[mod] = None
    
    return blocked


def test_core_import_no_runtime_deps():
    """Verify core module imports don't require runtime deps."""
    block_runtime_modules()
    
    # These MUST work in core profile
    from codex_ml import cli
    from codex_ml.utils import *
    from codex_ml.pipeline import *
    
    assert cli is not None
    print("✅ Core imports successful without runtime dependencies")


def test_data_module_core_only():
    """Verify data module works in core-only mode."""
    block_runtime_modules()
    
    # This is the test case from the bug report
    from codex_ml.data import *
    
    print("✅ Data module imports in core profile")


def test_monitoring_graceful_fallback():
    """Verify monitoring module provides graceful fallbacks."""
    block_runtime_modules()
    
    from codex_ml.monitoring import record_health_event
    
    # Should return no-op function, not fail
    record_health_event("test", {"data": "value"})
    
    print("✅ Monitoring provides no-op fallback in core profile")


def test_cli_functionality_core_profile():
    """Verify CLI works in core-only environment."""
    block_runtime_modules()
    
    from codex_ml.cli import main
    
    # CLI should be initialized
    assert main is not None
    
    print("✅ CLI functional in core profile")


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
```

**Run Tests:**
```bash
# Before fixes (will fail)
pytest tests/test_profile_core_isolation.py -v

# After fixes (will pass)
pytest tests/test_profile_core_isolation.py -v
```

**Time to Implement:** 10 minutes

---

### Validation Checklist

After implementing all steps:

```bash
# ✅ Check 1: Core profile import works
python -c "from codex_ml.data import *; print('✓ PASS')" 2>&1 | grep -q PASS

# ✅ Check 2: CLI still functional
python -m codex_ml --help > /dev/null && echo "✓ PASS"

# ✅ Check 3: No runtime deps imported at module level
python -c "
import sys
sys.modules['prometheus_client'] = None
from codex_ml.monitoring import record_health_event
print('✓ PASS - No prometheus import at module level')
"

# ✅ Check 4: Tests pass
pytest tests/test_profile_core_isolation.py -v 2>&1 | grep -c "PASSED"

# ✅ Check 5: Runtime profile still works (if installed)
pip install prometheus-client
python -c "from codex_ml.monitoring import get_metrics_text; print('✓ PASS')"
```

**Total Fix Time:** 30 minutes  
**Risk Level:** LOW (only imports, no logic changes)

---

## Critical Issue 2: Missing Import Guards in Multiple Modules

### Affected Files

1. `src/codex_ml/monitoring/prometheus.py`
2. `src/codex_ml/monitoring/prometheus_metrics.py`
3. `src/codex_ml/telemetry/server.py`

### Solution: Pattern to Apply

**Pattern: Use Try-Except with Fallback**

```python
# BEFORE (unsafe for core profile)
from prometheus_client import Counter, Gauge

class Metrics:
    counter = Counter("events", "Total events")

# AFTER (safe for core profile)
try:
    from prometheus_client import Counter, Gauge, HAS_PROMETHEUS = True
except ImportError:
    HAS_PROMETHEUS = False
    
    class Counter:
        """No-op counter for core profile."""
        def __init__(self, *args, **kwargs):
            pass
        def inc(self, *args, **kwargs):
            pass

class Metrics:
    if HAS_PROMETHEUS:
        counter = Counter("events", "Total events")
    else:
        class NoOpCounter:
            def inc(self, *args, **kwargs):
                pass
        counter = NoOpCounter()
```

### Implementation for Each File

#### File 1: `src/codex_ml/monitoring/prometheus.py`

```python
"""Prometheus monitoring integration - optional for core profile."""

try:
    from prometheus_client import Counter, Gauge, start_http_server
    HAS_PROMETHEUS = True
except ImportError:
    HAS_PROMETHEUS = False


if HAS_PROMETHEUS:
    def start_metrics_server(port=8000):
        start_http_server(port)
else:
    def start_metrics_server(port=8000):
        """No-op in core profile."""
        pass
```

**Time:** 5 minutes per file

---

## Critical Issue 3: Circular Dependency Chain

### Architecture Refactor

**Current (CIRCULAR):**
```
data → loaders → connectors → remote → monitoring → metrics_export → prometheus
                                    ↑__________________|
```

**Target (DECOUPLED):**
```
data/ (CORE)
├── loaders/
│   ├── yaml.py
│   ├── json.py
│   └── local.py
└── (no connectors import)

connectors/ (split by profile)
├── base.py (CORE - abstract only)
├── local.py (CORE)
└── remote.py (RUNTIME - conditional import data if needed)

monitoring/ (RUNTIME)
├── __init__.py (lazy imports)
└── (all prometheus stuff)
```

### Implementation Steps

**Step 1: Extract Interfaces from Connectors**

```python
# File: src/codex_ml/connectors/base.py (NEW - CORE ONLY)

from abc import ABC, abstractmethod
from typing import Any, Dict


class ConnectorError(Exception):
    """Base connector error."""
    pass


class BaseConnector(ABC):
    """Abstract connector interface."""
    
    @abstractmethod
    def connect(self) -> None:
        """Establish connection."""
        pass
    
    @abstractmethod
    def read(self, path: str) -> Any:
        """Read data from source."""
        pass
```

**Step 2: Update Remote Connector to Import Only When Needed**

```python
# File: src/codex_ml/connectors/remote.py (RUNTIME)

from .base import BaseConnector, ConnectorError


class RemoteConnector(BaseConnector):
    """Remote data connector - runtime profile."""
    
    def connect(self) -> None:
        # Only import health monitoring when actually used
        try:
            from codex_ml.monitoring import record_health_event
            record_health_event("remote_connect", {})
        except ImportError:
            pass  # Core profile - monitoring not available
    
    def read(self, path: str):
        # Only import data loaders when actually used
        try:
            from codex_ml.data.loaders import load_data
            return load_data(path)
        except ImportError:
            raise ConnectorError("Data loaders not available")
```

**Time:** 20 minutes

---

## High Priority Issue 4: Test Coverage

### Create Profile-Specific Test Suite

**File:** `tests/test_installation_scenarios.py`

```python
"""Test real-world installation scenarios."""

import subprocess
import sys
import tempfile
from pathlib import Path


def test_core_profile_installation():
    """Test core profile installs and works offline."""
    with tempfile.TemporaryDirectory() as tmpdir:
        venv = Path(tmpdir) / "venv_core"
        
        # Create venv
        subprocess.run(
            [sys.executable, "-m", "venv", str(venv)],
            check=True,
            capture_output=True,
        )
        
        pip = venv / ("Scripts" if sys.platform == "win32" else "bin") / "pip"
        python = venv / ("Scripts" if sys.platform == "win32" else "bin") / "python"
        
        # Install core profile
        subprocess.run(
            [str(pip), "install", "codex-ml[core]==0.2.2"],
            check=True,
            capture_output=True,
            timeout=300,
        )
        
        # Verify core functionality works
        result = subprocess.run(
            [str(python), "-c", "from codex_ml.data import *; print('OK')"],
            capture_output=True,
            text=True,
        )
        
        assert result.returncode == 0, f"Core profile failed: {result.stderr}"
        assert "OK" in result.stdout


def test_runtime_profile_has_ml():
    """Test runtime profile includes ML dependencies."""
    with tempfile.TemporaryDirectory() as tmpdir:
        venv = Path(tmpdir) / "venv_runtime"
        
        subprocess.run(
            [sys.executable, "-m", "venv", str(venv)],
            check=True,
            capture_output=True,
        )
        
        pip = venv / ("Scripts" if sys.platform == "win32" else "bin") / "pip"
        python = venv / ("Scripts" if sys.platform == "win32" else "bin") / "python"
        
        subprocess.run(
            [str(pip), "install", "codex-ml[runtime]==0.2.2"],
            check=True,
            capture_output=True,
            timeout=600,
        )
        
        # Verify ML libraries available
        result = subprocess.run(
            [str(python), "-c", "import torch; import transformers; print('OK')"],
            capture_output=True,
            text=True,
        )
        
        assert result.returncode == 0, "Runtime profile missing ML libraries"
```

**Time:** 15 minutes

---

## Medium Priority: Documentation

### Create `docs/PROFILE_SELECTION.md`

```markdown
# Profile Selection Guide

## Quick Decision Tree

```
┌─ What's your use case?
│
├─ Offline / Edge / Lightweight?
│  └─ → Use `codex-ml[core]`
│      8-15 MB, no torch/transformers
│
├─ Production ML Inference?
│  └─ → Use `codex-ml[runtime]`
│      20-35 MB, with torch/fastapi/ray
│
├─ Development / Experimentation?
│  └─ → Use `codex-ml[full]`
│      100+ MB, all tools included
│
└─ Just trying it out?
   └─ → Use `codex-ml`
       Base profile, all core deps
```

## Installation Examples

### Core Profile (Recommended for edge)
```bash
pip install codex-ml[core]==0.2.2
# Size: ~15 MB
# Use: Offline analysis, edge deployment
```

### Runtime Profile (Recommended for ML)
```bash
pip install codex-ml[runtime]==0.2.2
# Size: ~35 MB
# Use: ML inference, API services
```

### Full Profile (Recommended for development)
```bash
pip install codex-ml[full]==0.2.2
# Size: ~150 MB
# Use: Development, testing, experimentation
```
```

**Time:** 10 minutes

---

## Implementation Roadmap

### Phase 1: Critical Fixes (DO IMMEDIATELY)
- [ ] Fix monitoring/__init__.py (5 min)
- [ ] Fix metrics_export.py (5 min)
- [ ] Fix connectors/remote.py (10 min)
- [ ] Create test_profile_core_isolation.py (10 min)
- [ ] Run validation checklist (10 min)
- **Total: 40 minutes**

### Phase 2: Quality Improvements (DO THIS WEEK)
- [ ] Add import guards to prometheus.py, etc. (15 min each × 3 = 45 min)
- [ ] Refactor circular deps (20 min)
- [ ] Create profile selection guide (10 min)
- [ ] Expand test coverage (20 min)
- **Total: ~95 minutes**

### Phase 3: Documentation (DO BEFORE RELEASE)
- [ ] Generate entry points docs (15 min)
- [ ] Create migration guide (20 min)
- [ ] Update README.md profiles section (10 min)
- **Total: 45 minutes**

**Estimated Total:** ~3 hours for all fixes and documentation

---

## Success Criteria

After implementing all fixes:

```bash
# ✅ Test 1: Core profile truly offline-first
$ pip uninstall torch transformers prometheus_client -y
$ python -c "from codex_ml.data import *; print('SUCCESS')"
# Output: SUCCESS

# ✅ Test 2: All entry points functional
$ codex-ml --version
# Output: codex-ml version 0.2.2

# ✅ Test 3: Tests pass
$ pytest tests/test_profile_core_isolation.py -v
# Output: 5 passed in 0.45s

# ✅ Test 4: Security still intact
$ safety check
# Output: No known security vulnerabilities found

# ✅ Test 5: Installation size accurate
$ pip install codex-ml[core]==0.2.2 --report-dependencies
# Core: ~15 MB, Runtime: ~35 MB, Full: ~150 MB
```

---

## References

- **Issue Root Cause:** Module-level imports of runtime dependencies
- **Solution Pattern:** Lazy imports with __getattr__ or try-except
- **Profile Spec:** Lines 62-232 in pyproject.toml
- **Related Files:** 
  - src/codex_ml/monitoring/
  - src/codex_ml/connectors/
  - src/codex_ml/data/

---

**Implementation Checklist Status: READY FOR EXECUTION**

Estimated completion: 2026-07-13 (same day, 3-4 hours work)
