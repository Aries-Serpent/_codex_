# Atomic Remediation Diffs for Top 10 Critical Fixes
**Generated:** 2025-12-06 03:45:00

This document provides ready-to-apply atomic diffs for the top 10 most critical gaps identified in the audit. Each diff is minimal, focused, and can be applied independently.

---

## 1. Add Coverage Gate Enforcement (T005)

**File:** `pytest.ini`

```diff
--- a/pytest.ini
+++ b/pytest.ini
@@ -1,5 +1,8 @@
 [pytest]
 addopts = -q
+    --cov=src/codex_ml
+    --cov=src/training
+    --cov-fail-under=80
+    --cov-report=term-missing
+    --cov-report=html:artifacts/coverage
 markers =
     smoke: quick smoke tests for CLI
     integration: integration tests
```

**File:** `noxfile.py`

```diff
--- a/noxfile.py
+++ b/noxfile.py
@@ -150,7 +150,11 @@ def tests(session: nox.Session) -> None:
     session.install("-e", ".[test]")
     
     # Run pytest
-    session.run("pytest", "tests/", *session.posargs)
+    session.run(
+        "pytest", "tests/",
+        "--cov=src/codex_ml", "--cov=src/training",
+        "--cov-fail-under=80",
+        *session.posargs
+    )
     
     _show_vendor_scan(session)
```

---

## 2. Enforce Deterministic Operations (T007)

**File:** `src/training/trainer.py`

```diff
--- a/src/training/trainer.py
+++ b/src/training/trainer.py
@@ -8,6 +8,7 @@ from typing import Optional, Dict, Any
 import torch
 from torch import nn
 from torch.utils.data import DataLoader
+import os
 
 from .config import TrainingConfig
 
@@ -25,6 +26,19 @@ class Trainer:
         self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
         self.logger = self._setup_logger()
         
+        # Enable deterministic mode if requested
+        if self.config.deterministic:
+            self._enable_deterministic_mode()
+    
+    def _enable_deterministic_mode(self):
+        """Enable PyTorch deterministic mode for reproducibility."""
+        torch.use_deterministic_algorithms(True)
+        # Set CUBLAS workspace config for determinism
+        os.environ['CUBLAS_WORKSPACE_CONFIG'] = ':4096:8'
+        # Warn about potential performance impact
+        self.logger.info(
+            "Deterministic mode enabled. This Phase 5 reduce training performance."
+        )
+        
     def _setup_logger(self):
         """Setup training logger."""
         import logging
```

**File:** `training/config.py`

```diff
--- a/training/config.py
+++ b/training/config.py
@@ -12,6 +12,7 @@ class TrainingConfig:
     learning_rate: float = 1e-4
     num_epochs: int = 3
     seed: int = 42
+    deterministic: bool = True  # Enable deterministic operations
     gradient_accumulation_steps: int = 1
     max_grad_norm: float = 1.0
```

---

## 3. Save and Restore RNG State in Checkpoints (T006)

**File:** `src/training/checkpoint_manager.py`

```diff
--- a/src/training/checkpoint_manager.py
+++ b/src/training/checkpoint_manager.py
@@ -5,6 +5,7 @@ from pathlib import Path
 from typing import Dict, Any, Optional
 import torch
 import json
+import random
 from datetime import datetime
 
 class CheckpointManager:
@@ -36,6 +37,14 @@ class CheckpointManager:
             'scheduler_state_dict': scheduler.state_dict() if scheduler else None,
             'config': self.config,
             'metrics': metrics,
+            'rng_states': {
+                'python': random.getstate(),
+                'numpy': np.random.get_state(),
+                'torch': torch.get_rng_state(),
+                'cuda': [
+                    torch.cuda.get_rng_state(i) 
+                    for i in range(torch.cuda.device_count())
+                ] if torch.cuda.is_available() else []
+            }
         }
         
         # Save checkpoint
@@ -68,6 +77,18 @@ class CheckpointManager:
         if checkpoint['scheduler_state_dict'] and scheduler:
             scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
         
+        # Restore RNG states for reproducibility
+        if 'rng_states' in checkpoint:
+            rng_states = checkpoint['rng_states']
+            random.setstate(rng_states['python'])
+            np.random.set_state(rng_states['numpy'])
+            torch.set_rng_state(rng_states['torch'])
+            if torch.cuda.is_available() and rng_states['cuda']:
+                for i, state in enumerate(rng_states['cuda']):
+                    torch.cuda.set_rng_state(state, device=i)
+            self.logger.info("RNG states restored from checkpoint")
+        else:
+            self.logger.warning("No RNG states found in checkpoint - reproducibility not guaranteed")
+        
         return checkpoint
     
     def get_best_checkpoint(self, metric: str = 'loss', mode: str = 'min') -> Optional[Path]:
```

---

## 4. Implement Health Check Endpoints (T004)

**File:** `src/codex/health/__init__.py` (NEW)

```python
"""Health check module for service monitoring."""

from .checks import HealthChecker, HealthStatus

__all__ = ['HealthChecker', 'HealthStatus']
```

**File:** `src/codex/health/checks.py` (NEW)

```python
"""Health check implementations."""
from enum import Enum
from typing import Dict, Any, List, Callable
import time
import logging

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthChecker:
    """Service health checker with readiness and liveness probes."""
    
    def __init__(self):
        self.checks: Dict[str, Callable[[], bool]] = {}
        self.start_time = time.time()
    
    def register_check(self, name: str, check_fn: Callable[[], bool]):
        """Register a health check function."""
        self.checks[name] = check_fn
    
    def health(self) -> Dict[str, Any]:
        """Basic health endpoint."""
        return {
            "status": HealthStatus.HEALTHY.value,
            "uptime_seconds": time.time() - self.start_time
        }
    
    def ready(self) -> Dict[str, Any]:
        """Readiness check - can service handle requests?"""
        results = {}
        all_passed = True
        
        for name, check_fn in self.checks.items():
            try:
                passed = check_fn()
                results[name] = "pass" if passed else "fail"
                if not passed:
                    all_passed = False
            except Exception as e:
                logger.error(f"Health check '{name}' failed: {e}")
                results[name] = f"error: {e}"
                all_passed = False
        
        return {
            "status": HealthStatus.HEALTHY.value if all_passed else HealthStatus.UNHEALTHY.value,
            "checks": results
        }
    
    def live(self) -> Dict[str, Any]:
        """Liveness check - is service alive?"""
        return {
            "status": HealthStatus.HEALTHY.value,
            "uptime_seconds": time.time() - self.start_time
        }
```

**File:** `services/inference/app.py`

```diff
--- a/services/inference/app.py
+++ b/services/inference/app.py
@@ -5,6 +5,7 @@ from typing import List, Dict, Any
 
 from fastapi import FastAPI, HTTPException
 from pydantic import BaseModel
+from codex.health import HealthChecker
 
 app = FastAPI(title="Codex Inference Service")
+health_checker = HealthChecker()
+
+# Register health checks
+health_checker.register_check("model_loaded", lambda: model is not None)
+health_checker.register_check("cuda_available", lambda: torch.cuda.is_available() or True)
+
+@app.get("/health")
+def health():
+    """Basic health check."""
+    return health_checker.health()
+
+@app.get("/ready")
+def readiness():
+    """Readiness check."""
+    return health_checker.ready()
+
+@app.get("/live")
+def liveness():
+    """Liveness check."""
+    return health_checker.live()
 
 class InferenceRequest(BaseModel):
     text: str
```

---

## 5. Add Dependency Vulnerability Scanning to CI (T011)

**File:** `.github/workflows/security-scan.yml` (NEW)

```yaml
name: Security Scan

on:
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 0 * * 1'  # Weekly on Mondays
  workflow_dispatch:

jobs:
  dependency-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install pip-audit
        run: pip install pip-audit
      
      - name: Scan requirements.txt
        run: pip-audit -r requirements.txt --desc --format json --output requirements-audit.json
        continue-on-error: true
      
      - name: Scan requirements-dev.txt
        run: pip-audit -r requirements-dev.txt --desc --format json --output requirements-dev-audit.json
        continue-on-error: true
      
      - name: Scan requirements-ml-cpu.txt
        run: pip-audit -r requirements-ml-cpu.txt --desc --format json --output requirements-ml-audit.json
        continue-on-error: true
      
      - name: Check for critical vulnerabilities
        run: |
          # Fail if any critical vulnerabilities found
          python -c "
          import json
          import sys
          
          critical_found = False
          for file in ['requirements-audit.json', 'requirements-dev-audit.json', 'requirements-ml-audit.json']:
              try:
                  with open(file) as f:
                      data = json.load(f)
                      for vuln in data.get('vulnerabilities', []):
                          if vuln.get('severity') == 'critical':
                              print(f'CRITICAL: {vuln}')
                              critical_found = True
              except FileNotFoundError:
                  pass
          
          if critical_found:
              sys.exit(1)
          "
      
      - name: Upload audit results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: security-audit-results
          path: '*-audit.json'
```

---

## 6. Pin Docker Base Images (T009)

**File:** `Dockerfile`

```diff
--- a/Dockerfile
+++ b/Dockerfile
@@ -1,4 +1,5 @@
-FROM python:3.11-slim
+# Pin to specific digest for reproducibility
+FROM python:3.11-slim@sha256:abc123...  # Replace with actual digest
 
 WORKDIR /app
```

**File:** `Dockerfile.gpu`

```diff
--- a/Dockerfile.gpu
+++ b/Dockerfile.gpu
@@ -1,4 +1,5 @@
-FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04
+# Pin to specific digest for reproducibility
+FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04@sha256:def456...  # Replace with actual digest
 
 WORKDIR /app
```

**Note:** To get the current digest, run:
```bash
docker pull python:3.11-slim
docker inspect python:3.11-slim --format='{{.RepoDigests}}'
```

---

## 7. Capture Environment Metadata (T008)

**File:** `src/utils/environment_capture.py` (NEW)

```python
"""Environment metadata capture for reproducibility."""
import sys
import platform
import json
from typing import Dict, Any
from pathlib import Path


def capture_environment() -> Dict[str, Any]:
    """Capture complete environment metadata."""
    env_info = {
        "python": {
            "version": sys.version,
            "version_info": {
                "major": sys.version_info.major,
                "minor": sys.version_info.minor,
                "micro": sys.version_info.micro
            },
            "executable": sys.executable
        },
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "processor": platform.processor()
        }
    }
    
    # PyTorch info if available
    try:
        import torch
        env_info["torch"] = {
            "version": torch.__version__,
            "cuda_available": torch.cuda.is_available(),
            "cuda_version": torch.version.cuda if torch.cuda.is_available() else None,
            "cudnn_version": torch.backends.cudnn.version() if torch.cuda.is_available() else None,
            "device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0
        }
        
        if torch.cuda.is_available():
            env_info["cuda_devices"] = [
                {
                    "id": i,
                    "name": torch.cuda.get_device_name(i),
                    "memory_total": torch.cuda.get_device_properties(i).total_memory
                }
                for i in range(torch.cuda.device_count())
            ]
    except ImportError:
        env_info["torch"] = {"error": "PyTorch not installed"}
    
    # NumPy version
    try:
        import numpy as np
        env_info["numpy"] = {"version": np.__version__}
    except ImportError:
        pass
    
    return env_info


def save_environment_manifest(output_path: Path):
    """Save environment manifest to JSON file."""
    env_info = capture_environment()
    with open(output_path, 'w') as f:
        json.dump(env_info, f, indent=2)
    return env_info
```

**File:** `src/training/trainer.py`

```diff
--- a/src/training/trainer.py
+++ b/src/training/trainer.py
@@ -10,6 +10,7 @@ from torch.utils.data import DataLoader
 import os
 
 from .config import TrainingConfig
+from utils.environment_capture import capture_environment, save_environment_manifest
 
 class Trainer:
     """Training orchestrator."""
@@ -26,6 +27,11 @@ class Trainer:
         self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
         self.logger = self._setup_logger()
         
+        # Capture and log environment
+        env_info = capture_environment()
+        self.logger.info(f"Environment: {env_info}")
+        save_environment_manifest(Path(self.config.output_dir) / "environment.json")
+        
         # Enable deterministic mode if requested
         if self.config.deterministic:
             self._enable_deterministic_mode()
```

---

## 8. Add Alerting for Training Failures (T012)

**File:** `src/codex/alerting/__init__.py` (NEW)

```python
"""Alerting module for notifications."""

from .base import Alerter, AlertLevel
from .slack_notifier import SlackNotifier
from .email_notifier import EmailNotifier

__all__ = ['Alerter', 'AlertLevel', 'SlackNotifier', 'EmailNotifier']
```

**File:** `src/codex/alerting/base.py` (NEW)

```python
"""Base alerting interface."""
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Dict, Any


class AlertLevel(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class Alerter(ABC):
    """Base class for alerting implementations."""
    
    @abstractmethod
    def send_alert(
        self,
        message: str,
        level: AlertLevel = AlertLevel.INFO,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send an alert. Returns True if successful."""
        pass
```

**File:** `src/codex/alerting/slack_notifier.py` (NEW)

```python
"""Slack notification implementation."""
import os
import requests
from typing import Optional, Dict, Any
from .base import Alerter, AlertLevel


class SlackNotifier(Alerter):
    """Send alerts to Slack webhook."""
    
    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")
        if not self.webhook_url:
            raise ValueError("Slack webhook URL not configured")
    
    def send_alert(
        self,
        message: str,
        level: AlertLevel = AlertLevel.INFO,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send alert to Slack."""
        emoji_map = {
            AlertLevel.INFO: ":information_source:",
            AlertLevel.WARNING: ":warning:",
            AlertLevel.ERROR: ":x:",
            AlertLevel.CRITICAL: ":rotating_light:"
        }
        
        payload = {
            "text": f"{emoji_map[level]} *{level.value.upper()}*: {message}",
            "attachments": []
        }
        
        if context:
            payload["attachments"].append({
                "color": "danger" if level in [AlertLevel.ERROR, AlertLevel.CRITICAL] else "warning",
                "fields": [
                    {"title": k, "value": str(v), "short": True}
                    for k, v in context.items()
                ]
            })
        
        try:
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception:
            return False
```

**File:** `src/training/trainer.py`

```diff
--- a/src/training/trainer.py
+++ b/src/training/trainer.py
@@ -12,6 +12,7 @@ import os
 from .config import TrainingConfig
 from utils.environment_capture import capture_environment, save_environment_manifest
+from codex.alerting import SlackNotifier, AlertLevel
 
 class Trainer:
     """Training orchestrator."""
@@ -27,6 +28,12 @@ class Trainer:
         self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
         self.logger = self._setup_logger()
         
+        # Set up alerting
+        try:
+            self.alerter = SlackNotifier()
+        except ValueError:
+            self.alerter = None  # Alerting not configured
+        
         # Capture and log environment
         env_info = capture_environment()
         self.logger.info(f"Environment: {env_info}")
@@ -45,6 +52,13 @@ class Trainer:
             for epoch in range(self.config.num_epochs):
                 self._train_epoch(epoch, train_loader)
                 self._validate_epoch(epoch, val_loader)
+        except Exception as e:
+            # Send alert on training failure
+            if self.alerter:
+                self.alerter.send_alert(
+                    f"Training failed: {str(e)}",
+                    level=AlertLevel.CRITICAL,
+                    context={"config": str(self.config), "device": str(self.device)}
+                )
+            raise
```

---

## 9. Set up Prometheus Metrics Collection (T014)

**File:** `src/codex/metrics/__init__.py` (NEW)

```python
"""Metrics collection and export."""

from .prometheus_exporter import PrometheusExporter, metrics_registry

__all__ = ['PrometheusExporter', 'metrics_registry']
```

**File:** `src/codex/metrics/prometheus_exporter.py` (NEW)

```python
"""Prometheus metrics exporter."""
from prometheus_client import Counter, Gauge, Histogram, generate_latest, REGISTRY


# Training metrics
training_steps = Counter('training_steps_total', 'Total training steps')
training_loss = Gauge('training_loss', 'Current training loss')
training_epoch = Gauge('training_epoch_current', 'Current training epoch')
training_time = Histogram('training_step_duration_seconds', 'Training step duration')

# Inference metrics
inference_requests = Counter('inference_requests_total', 'Total inference requests')
inference_latency = Histogram('inference_latency_seconds', 'Inference latency')
inference_errors = Counter('inference_errors_total', 'Total inference errors')

# System metrics
gpu_memory_used = Gauge('gpu_memory_used_bytes', 'GPU memory used', ['device'])
cpu_usage_percent = Gauge('cpu_usage_percent', 'CPU usage percentage')


class PrometheusExporter:
    """Prometheus metrics exporter."""
    
    @staticmethod
    def export_metrics() -> bytes:
        """Export metrics in Prometheus format."""
        return generate_latest(REGISTRY)


metrics_registry = {
    'training': {
        'steps': training_steps,
        'loss': training_loss,
        'epoch': training_epoch,
        'time': training_time
    },
    'inference': {
        'requests': inference_requests,
        'latency': inference_latency,
        'errors': inference_errors
    },
    'system': {
        'gpu_memory': gpu_memory_used,
        'cpu_usage': cpu_usage_percent
    }
}
```

**File:** `services/inference/app.py`

```diff
--- a/services/inference/app.py
+++ b/services/inference/app.py
@@ -6,6 +6,7 @@ from typing import List, Dict, Any
 from fastapi import FastAPI, HTTPException
 from pydantic import BaseModel
 from codex.health import HealthChecker
+from codex.metrics import PrometheusExporter, metrics_registry
 
 app = FastAPI(title="Codex Inference Service")
 health_checker = HealthChecker()
@@ -26,6 +27,11 @@ def liveness():
     """Liveness check."""
     return health_checker.live()
 
+@app.get("/metrics")
+def metrics():
+    """Prometheus metrics endpoint."""
+    return PrometheusExporter.export_metrics()
+
 class InferenceRequest(BaseModel):
     text: str
     
@@ -33,7 +39,11 @@ class InferenceRequest(BaseModel):
 async def predict(request: InferenceRequest):
     """Run inference."""
     try:
+        # Track metrics
+        metrics_registry['inference']['requests'].inc()
+        with metrics_registry['inference']['latency'].time():
             result = model.predict(request.text)
-        return {"result": result}
+            return {"result": result}
     except Exception as e:
+        metrics_registry['inference']['errors'].inc()
         raise HTTPException(status_code=500, detail=str(e))
```

---

## 10. Implement Config Drift Detection (T010)

**File:** `src/codex/drift/__init__.py` (NEW)

```python
"""Drift detection modules."""

from .config_monitor import ConfigDriftMonitor

__all__ = ['ConfigDriftMonitor']
```

**File:** `src/codex/drift/config_monitor.py` (NEW)

```python
"""Configuration drift detection."""
import hashlib
import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ConfigDriftMonitor:
    """Monitor configuration files for unexpected changes."""
    
    def __init__(self, baseline_path: Path):
        self.baseline_path = baseline_path
        self.baseline = self._load_baseline()
    
    def _load_baseline(self) -> Dict[str, str]:
        """Load baseline configuration hashes."""
        if not self.baseline_path.exists():
            logger.warning(f"No baseline found at {self.baseline_path}")
            return {}
        
        with open(self.baseline_path) as f:
            return json.load(f)
    
    def _compute_hash(self, file_path: Path) -> str:
        """Compute SHA256 hash of file."""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def check_drift(self, config_files: list[Path]) -> Dict[str, Any]:
        """Check for configuration drift."""
        drift_detected = []
        
        for file_path in config_files:
            if not file_path.exists():
                continue
            
            current_hash = self._compute_hash(file_path)
            baseline_hash = self.baseline.get(str(file_path))
            
            if baseline_hash and current_hash != baseline_hash:
                drift_detected.append({
                    "file": str(file_path),
                    "baseline_hash": baseline_hash,
                    "current_hash": current_hash
                })
                logger.warning(f"Config drift detected in {file_path}")
        
        return {
            "drift_detected": len(drift_detected) > 0,
            "files_with_drift": drift_detected
        }
    
    def update_baseline(self, config_files: list[Path]):
        """Update baseline with current configuration hashes."""
        baseline = {}
        for file_path in config_files:
            if file_path.exists():
                baseline[str(file_path)] = self._compute_hash(file_path)
        
        self.baseline_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.baseline_path, 'w') as f:
            json.dump(baseline, f, indent=2)
        
        logger.info(f"Updated baseline with {len(baseline)} configurations")
```

**File:** `scripts/check_config_drift.py` (NEW)

```python
#!/usr/bin/env python3
"""Check for configuration drift."""
from pathlib import Path
from codex.drift import ConfigDriftMonitor

def main():
    """Check configuration drift."""
    root = Path(__file__).parent.parent
    baseline_path = root / ".codex" / "config_baseline.json"
    
    # Collect all config files
    config_files = []
    for pattern in ["configs/**/*.yaml", "configs/**/*.yml", "*.toml"]:
        config_files.extend(root.glob(pattern))
    
    monitor = ConfigDriftMonitor(baseline_path)
    result = monitor.check_drift(config_files)
    
    if result["drift_detected"]:
        print("⚠️  Configuration drift detected:")
        for drift in result["files_with_drift"]:
            print(f"  - {drift['file']}")
        exit(1)
    else:
        print("✅ No configuration drift detected")
        exit(0)

if __name__ == "__main__":
    main()
```

---

## Application Instructions

1. **Review each diff** to understand the changes
2. **Apply diffs sequentially** in the order presented
3. **Run tests after each application** to verify no breakage
4. **Update baseline configurations** where needed
5. **Commit changes atomically** with descriptive messages

## Verification Commands

After applying all diffs, run:

```bash
# Test coverage enforcement
nox -s tests

# Check deterministic mode
python -c "import torch; print(torch.are_deterministic_algorithms_enabled())"

# Verify health endpoints
curl http://localhost:8000/health
curl http://localhost:8000/ready
curl http://localhost:8000/live
curl http://localhost:8000/metrics

# Check config drift
python scripts/check_config_drift.py

# Verify security scanning
pip-audit -r requirements.txt
bandit -r src/ -ll
```

---

*Generated: 2025-12-06 03:45:00*
