# API Reference Documentation

## Overview

This document provides comprehensive API reference for all Codex ML modules across Phases 1-4.

---

## Phase 1: Foundation

### Security & Safety

#### `codex_ml.safety.prompt_sanitizer`

**PromptSanitizer**

Sanitizes user prompts to prevent injection attacks.

```python
class PromptSanitizer:
    """Sanitizes prompts against injection patterns."""
    
    def __init__(self, strict_mode: bool = True):
        """Initialize sanitizer.
        
        Args:
            strict_mode: If True, raises ValueError on unsafe prompts.
                        If False, redacts unsafe patterns.
        """
        
    def sanitize(self, prompt: str) -> str:
        """Sanitize a prompt string.
        
        Args:
            prompt: Input prompt to sanitize
            
        Returns:
            Sanitized prompt (or raises ValueError in strict mode)
            
        Raises:
            ValueError: If prompt is unsafe and strict_mode=True
        """
        
    def is_safe(self, prompt: str) -> bool:
        """Check if prompt is safe.
        
        Args:
            prompt: Prompt to check
            
        Returns:
            True if prompt passes all safety checks
        """
        
    def get_violations(self, prompt: str) -> List[str]:
        """Get list of violations in prompt.
        
        Args:
            prompt: Prompt to check
            
        Returns:
            List of violation pattern names
        """
```

**Detected Patterns:**
- XSS (Cross-Site Scripting)
- SQL Injection
- Command Injection
- Path Traversal
- LDAP Injection
- XML Injection
- Code Execution
- Server-Side Template Injection (SSTI)
- NoSQL Injection
- Email Header Injection

**Example:**

```python
from codex_ml.safety.prompt_sanitizer import PromptSanitizer

# Strict mode (raises on unsafe input)
sanitizer = PromptSanitizer(strict_mode=True)
try:
    result = sanitizer.sanitize("<script>alert('xss')</script>")
except ValueError as e:
    print(f"Unsafe prompt detected: {e}")

# Non-strict mode (redacts patterns)
sanitizer = PromptSanitizer(strict_mode=False)
safe_prompt = sanitizer.sanitize("<script>alert('xss')</script>")
# Result: "[REDACTED]alert('xss')[REDACTED]"
```

### Observability

#### `codex_ml.serving.health`

Health and readiness check endpoints for Kubernetes/production deployments.

```python
def health_check() -> Dict[str, Any]:
    """Basic health check (liveness probe).
    
    Returns:
        {"status": "healthy", "timestamp": "..."}
    """

def readiness_check(
    required_dirs: Optional[List[Path]] = None,
    required_env_vars: Optional[List[str]] = None,
    min_disk_space_gb: float = 1.0
) -> Dict[str, Any]:
    """Readiness check with system validation.
    
    Args:
        required_dirs: Directories that must exist
        required_env_vars: Environment variables that must be set
        min_disk_space_gb: Minimum free disk space in GB
        
    Returns:
        {
            "status": "ready" | "not_ready",
            "checks": {...},
            "timestamp": "..."
        }
    """

def get_health_router():
    """Get FastAPI router with health endpoints.
    
    Returns:
        FastAPI APIRouter with /health, /ready, /healthz, /readyz
    """
```

**Example:**

```python
from fastapi import FastAPI
from codex_ml.serving.health import get_health_router

app = FastAPI()
app.include_router(get_health_router())

# Endpoints available:
# GET /health - Liveness probe
# GET /ready - Readiness probe  
# GET /healthz - Kubernetes liveness
# GET /readyz - Kubernetes readiness
```

#### `codex_ml.monitoring.metrics`

Prometheus metrics collection and export.

```python
class MetricsCollector:
    """Collects and exports Prometheus metrics."""
    
    def record_request(
        self,
        method: str,
        endpoint: str,
        status_code: int
    ):
        """Record an HTTP request.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: Request endpoint
            status_code: HTTP status code
        """
        
    def record_latency(
        self,
        duration_seconds: float,
        method: str,
        endpoint: str
    ):
        """Record request latency.
        
        Args:
            duration_seconds: Request duration in seconds
            method: HTTP method
            endpoint: Request endpoint
        """
        
    def record_error(
        self,
        error_type: str,
        endpoint: str
    ):
        """Record an error.
        
        Args:
            error_type: Type/class of error
            endpoint: Endpoint where error occurred
        """

def get_metrics_router():
    """Get FastAPI router with /metrics endpoint.
    
    Returns:
        FastAPI APIRouter with Prometheus metrics endpoint
    """
```

**Metrics Exported:**
- `codex_requests_total` - Counter by method/endpoint/status
- `codex_request_latency_seconds` - Histogram by method/endpoint
- `codex_errors_total` - Counter by type/endpoint
- `codex_active_requests` - Gauge of concurrent requests

**Example:**

```python
from codex_ml.monitoring.metrics import record_request, record_latency

# Record request
record_request("GET", "/api/v1/predict", 200)

# Record latency
record_latency(0.123, "GET", "/api/v1/predict")
```

---

## Phase 2: Reproducibility

### Deterministic Training

#### `codex_ml.training.rng_checkpoint`

RNG state management for deterministic training resume.

```python
class RNGState:
    """Captures and restores RNG state across training sessions."""
    
    def __init__(self):
        """Initialize RNG state manager."""
        
    def capture(self):
        """Capture current RNG state from all sources.
        
        Captures state from:
        - Python random module
        - NumPy random
        - PyTorch (CPU and CUDA)
        """
        
    def restore(self):
        """Restore previously captured RNG state."""
        
    def save_to_file(self, path: Path):
        """Save RNG state to JSON file.
        
        Args:
            path: Path to .rng.json file
        """
        
    @classmethod
    def load_from_file(cls, path: Path) -> "RNGState":
        """Load RNG state from JSON file.
        
        Args:
            path: Path to .rng.json file
            
        Returns:
            RNGState instance with loaded state
        """
```

**Example:**

```python
from pathlib import Path
from codex_ml.training.rng_checkpoint import RNGState

# On checkpoint save
rng_state = RNGState()
rng_state.capture()
rng_state.save_to_file(Path("checkpoint.pt.rng.json"))

# On checkpoint resume (deterministic)
rng_state = RNGState.load_from_file(Path("checkpoint.pt.rng.json"))
rng_state.restore()
# Training continues from exact RNG state
```

#### `codex_ml.utils.repro`

Dataset integrity validation with SHA256 hashing.

```python
class DatasetManifest:
    """Manages dataset integrity manifests."""
    
    def __init__(
        self,
        dataset_path: Path | str,
        extensions: Optional[List[str]] = None,
        recursive: bool = True
    ):
        """Initialize dataset manifest.
        
        Args:
            dataset_path: Path to dataset directory
            extensions: File extensions to include (e.g., [".txt", ".json"])
            recursive: Whether to scan recursively
        """
        
    def generate(self) -> "DatasetManifest":
        """Generate manifest by hashing all dataset files.
        
        Returns:
            Self for method chaining
        """
        
    def save(self, manifest_path: Path | str):
        """Save manifest to JSON file.
        
        Args:
            manifest_path: Path to save manifest
        """
        
    def verify(self, manifest_path: Path | str) -> Dict[str, List[str]]:
        """Verify dataset against saved manifest.
        
        Args:
            manifest_path: Path to manifest file
            
        Returns:
            {
                "missing": [...],  # Files in manifest but not in dataset
                "modified": [...], # Files with changed hashes
                "added": [...]     # Files in dataset but not in manifest
            }
        """
        
    def has_drift(self, manifest_path: Optional[Path | str] = None) -> bool:
        """Check if dataset has drifted from manifest.
        
        Args:
            manifest_path: Path to manifest (uses self.manifest_path if None)
            
        Returns:
            True if any files are missing, modified, or added
        """
```

**Example:**

```python
from codex_ml.utils.repro import DatasetManifest

# Generate manifest before training
manifest = DatasetManifest("data/train", extensions=[".txt"])
manifest.generate()
manifest.save("data/train_manifest.json")

# Verify integrity on resume
if manifest.has_drift("data/train_manifest.json"):
    print("⚠️ Dataset drift detected!")
    diff = manifest.verify("data/train_manifest.json")
    print(f"Modified: {len(diff['modified'])}")
    print(f"Missing: {len(diff['missing'])}")
    print(f"Added: {len(diff['added'])}")
```

#### `codex_ml.utils.deterministic`

Enforce deterministic algorithms for reproducibility.

```python
def enable_deterministic_mode():
    """Enable deterministic mode for all frameworks.
    
    Sets:
    - PyTorch: torch.use_deterministic_algorithms(True)
    - TensorFlow: tf.config.experimental.enable_op_determinism()
    - CuDNN: deterministic=True, benchmark=False
    - Environment: PYTHONHASHSEED=0, CUBLAS_WORKSPACE_CONFIG=:4096:8
    """

class DeterministicContext:
    """Context manager for temporary deterministic execution."""
    
    def __enter__(self):
        """Enable deterministic mode."""
        
    def __exit__(self, *args):
        """Restore previous settings."""
```

**Example:**

```python
from codex_ml.utils.deterministic import enable_deterministic_mode, DeterministicContext

# Global deterministic mode
enable_deterministic_mode()

# Or use context manager
with DeterministicContext():
    # Bit-exact reproducibility within this block
    train_model()
```

#### `codex_ml.utils.checkpoint_integrity_validation`

Checkpoint corruption detection with SHA256 validation.

```python
class CheckpointIntegrity:
    """Validates checkpoint file integrity."""
    
    def __init__(self, checkpoint_path: Path | str):
        """Initialize integrity validator.
        
        Args:
            checkpoint_path: Path to checkpoint file
        """
        
    def compute_hash(self) -> str:
        """Compute SHA256 hash of checkpoint.
        
        Returns:
            Hex string of SHA256 hash
        """
        
    def save_integrity(self, metadata: Optional[Dict] = None):
        """Save integrity metadata to .integrity.json file.
        
        Args:
            metadata: Optional metadata to include (e.g., epoch, metrics)
        """
        
    def validate(self, strict: bool = True) -> bool:
        """Validate checkpoint against saved integrity file.
        
        Args:
            strict: If True, raises exception on validation failure
            
        Returns:
            True if validation passes
            
        Raises:
            ValueError: If validation fails and strict=True
        """
```

**Example:**

```python
from codex_ml.utils.checkpoint_integrity_validation import CheckpointIntegrity

# On checkpoint save
integrity = CheckpointIntegrity("checkpoint.pt")
integrity.save_integrity(metadata={"epoch": 10, "loss": 0.5})

# On checkpoint load (validate before loading)
integrity = CheckpointIntegrity("checkpoint.pt")
if not integrity.validate(strict=True):
    raise RuntimeError("Checkpoint corrupted!")
```

#### `codex_ml.utils.config_drift`

Configuration drift detection for reproducibility.

```python
class ConfigDrift:
    """Detects configuration drift between runs."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize config drift detector.
        
        Args:
            config: Configuration dictionary
        """
        
    def compute_hash(self) -> str:
        """Compute SHA256 hash of configuration.
        
        Returns:
            Hex string of config hash
        """
        
    def save_baseline(self, baseline_path: Path | str):
        """Save configuration as baseline.
        
        Args:
            baseline_path: Path to save baseline JSON
        """
        
    def validate_against_baseline(
        self,
        baseline_path: Path | str,
        strict: bool = True
    ) -> Dict[str, Any]:
        """Validate config against baseline.
        
        Args:
            baseline_path: Path to baseline file
            strict: If True, raises exception on drift
            
        Returns:
            {
                "has_drift": bool,
                "added": [...],
                "removed": [...],
                "modified": [...]
            }
            
        Raises:
            ValueError: If drift detected and strict=True
        """
```

**Example:**

```python
from codex_ml.utils.config_drift import ConfigDrift

config = {"learning_rate": 0.001, "batch_size": 32}

# Save baseline
drift = ConfigDrift(config)
drift.save_baseline("config_baseline.json")

# Validate on resume
drift2 = ConfigDrift(config)
result = drift2.validate_against_baseline("config_baseline.json", strict=True)
```

---

## Phase 3: Autonomy

### Self-Healing

#### `codex_ml.utils.self_healing`

Autonomous error recovery and self-healing framework.

```python
class SelfHealingContext:
    """Context manager for self-healing execution."""
    
    def __init__(
        self,
        batch_size: int,
        enable_oom_recovery: bool = True,
        max_retries: int = 3,
        min_batch_size: int = 1
    ):
        """Initialize self-healing context.
        
        Args:
            batch_size: Initial batch size
            enable_oom_recovery: Enable automatic OOM recovery
            max_retries: Maximum recovery attempts
            min_batch_size: Minimum batch size (stop reducing below this)
        """
        
    def __enter__(self) -> "SelfHealingContext":
        """Enter context."""
        
    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Exit context with automatic remediation.
        
        Returns:
            True if error was handled, False to propagate
        """

def auto_remediate(
    max_retries: int = 3,
    batch_size: Optional[int] = None
):
    """Decorator for auto-remediation.
    
    Args:
        max_retries: Maximum retry attempts
        batch_size: Initial batch size (for OOM recovery)
    """
```

**Example:**

```python
from codex_ml.utils.self_healing import SelfHealingContext, auto_remediate

# Context manager approach
with SelfHealingContext(batch_size=32, enable_oom_recovery=True) as healer:
    train_model(batch_size=healer.batch_size)
    # If OOM occurs: batch_size automatically reduced to 16, 8, 4...

# Decorator approach
@auto_remediate(max_retries=3, batch_size=32)
def train_with_recovery(batch_size):
    return train_model(batch_size=batch_size)
```

### Drift Detection

#### `codex_ml.monitoring.drift_detection`

Comprehensive drift monitoring for data, config, and model performance.

```python
class ComprehensiveDriftMonitor:
    """Unified drift monitoring system."""
    
    def __init__(
        self,
        data_threshold: float = 0.1,
        config_threshold: float = 0.0,
        model_threshold: float = 0.1
    ):
        """Initialize drift monitor.
        
        Args:
            data_threshold: Threshold for data drift (0-1)
            config_threshold: Threshold for config drift
            model_threshold: Threshold for model performance drift
        """
        
    def monitor_all(
        self,
        current_data_stats: Optional[Dict[str, float]] = None,
        baseline_data_stats: Optional[Dict[str, float]] = None,
        current_config: Optional[Dict] = None,
        baseline_config: Optional[Dict] = None,
        current_metrics: Optional[Dict[str, float]] = None,
        baseline_metrics: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """Monitor all drift types.
        
        Returns:
            {
                "data_drift": {...},
                "config_drift": {...},
                "model_drift": {...}
            }
        """
        
    def has_critical_drift(self) -> bool:
        """Check if any critical drift detected.
        
        Returns:
            True if any alerts with severity="critical"
        """
        
    def get_drift_summary(self) -> Dict[str, int]:
        """Get summary of drift alerts.
        
        Returns:
            {
                "total_alerts": int,
                "critical_count": int,
                "high_count": int,
                "medium_count": int,
                "low_count": int
            }
        """
        
    def save_alerts(self, output_path: Path | str):
        """Save drift alerts to JSON file."""
```

**Alert Severity Levels:**
- **Critical**: >50% metric change
- **High**: 30-50% change or config modifications
- **Medium**: 15-30% change or config additions
- **Low**: 10-15% change

**Example:**

```python
from codex_ml.monitoring.drift_detection import ComprehensiveDriftMonitor

monitor = ComprehensiveDriftMonitor(
    data_threshold=0.1,
    config_threshold=0.0,
    model_threshold=0.1
)

results = monitor.monitor_all(
    current_data_stats={"mean": 0.5, "std": 0.2},
    baseline_data_stats={"mean": 0.48, "std": 0.19},
    current_config=config,
    baseline_config=baseline_config,
    current_metrics={"loss": 0.3, "accuracy": 0.92},
    baseline_metrics={"loss": 0.25, "accuracy": 0.95}
)

if monitor.has_critical_drift():
    print("⚠️ Critical drift detected!")
    monitor.save_alerts("drift_alerts.json")
    summary = monitor.get_drift_summary()
    print(f"Total alerts: {summary['total_alerts']}")
    print(f"Critical: {summary['critical_count']}")
```

### Training

#### `codex_ml.training.early_stopping`

Auto-injected early stopping for HuggingFace trainers.

```python
def auto_inject_early_stopping_for_trainer(
    trainer_class,
    eval_dataset: Optional[Any] = None,
    callbacks: Optional[List] = None,
    patience: int = 3,
    threshold: float = 0.0
) -> List:
    """Auto-inject EarlyStopping callback.
    
    Args:
        trainer_class: HuggingFace Trainer class
        eval_dataset: Evaluation dataset (required for early stopping)
        callbacks: Existing callbacks
        patience: Number of evaluations with no improvement
        threshold: Minimum change to qualify as improvement
        
    Returns:
        Updated callbacks list with EarlyStopping added
    """
```

**Example:**

```python
from codex_ml.training.early_stopping import auto_inject_early_stopping_for_trainer
from transformers import Trainer

callbacks = auto_inject_early_stopping_for_trainer(
    trainer_class=Trainer,
    eval_dataset=eval_dataset,
    callbacks=[],
    patience=3
)

trainer = Trainer(..., callbacks=callbacks)
# EarlyStopping auto-injected with patience=3
```

#### `codex_ml.utils.wandb_logger`

Offline-first Weights & Biases logger with NDJSON fallback.

```python
def init_wandb(
    project: str,
    name: Optional[str] = None,
    config: Optional[Dict] = None,
    **kwargs
) -> "WandBLogger":
    """Initialize W&B logger (offline by default).
    
    Args:
        project: Project name
        name: Run name
        config: Configuration dictionary
        **kwargs: Additional wandb.init kwargs
        
    Returns:
        WandBLogger instance (graceful fallback to NDJSON if W&B unavailable)
    """

class WandBLogger:
    """W&B logger with graceful fallback."""
    
    def log(self, metrics: Dict[str, Any]):
        """Log metrics.
        
        Args:
            metrics: Dictionary of metric values
        """
        
    def finish(self):
        """Finish logging session."""
```

**Example:**

```python
from codex_ml.utils.wandb_logger import init_wandb

# Defaults to offline mode (WANDB_MODE=offline)
logger = init_wandb(project="my-project", name="run-1")
logger.log({"loss": 0.5, "accuracy": 0.9})
logger.finish()

# Falls back to NDJSON if W&B not available
```

---

## Phase 4: Production Excellence

### Continuous Learning

#### `codex_ml.training.continuous_learning`

Auto-retraining pipeline with drift-triggered model updates.

```python
class ContinuousLearningPipeline:
    """Continuous learning with auto-retraining."""
    
    def __init__(
        self,
        model_name: str,
        registry_path: Path | str = "models/registry.json",
        drift_threshold: float = 0.15,
        min_samples_retrain: int = 1000,
        performance_degradation_threshold: float = 0.05
    ):
        """Initialize continuous learning pipeline.
        
        Args:
            model_name: Model name
            registry_path: Path to model registry
            drift_threshold: Drift score threshold for retraining
            min_samples_retrain: Minimum samples required
            performance_degradation_threshold: Max acceptable performance drop
        """
        
    def should_retrain(
        self,
        drift_score: float,
        samples_count: int,
        current_performance: Optional[Dict[str, float]] = None
    ) -> bool:
        """Determine if retraining should be triggered.
        
        Returns:
            True if retraining criteria met
        """
        
    def retrain(
        self,
        train_fn: Callable,
        train_data: Any,
        dataset_hash: Optional[str] = None,
        drift_score: Optional[float] = None
    ) -> ModelVersion:
        """Execute retraining.
        
        Args:
            train_fn: Training function that returns (model, metrics)
            train_data: Training dataset
            dataset_hash: Hash of training dataset
            drift_score: Drift score that triggered retraining
            
        Returns:
            New ModelVersion
        """
        
    def compare_models(
        self,
        new_version: ModelVersion,
        baseline_version: Optional[ModelVersion] = None,
        primary_metric: str = "accuracy"
    ) -> Dict[str, Any]:
        """Compare model versions.
        
        Returns:
            {
                "is_better": bool,
                "improvement": float,
                "new_metric": float,
                "baseline_metric": float
            }
        """
        
    def deploy_model(self, version: ModelVersion):
        """Deploy model version to production."""
        
    def rollback(self, to_version: Optional[str] = None):
        """Rollback to previous model version."""
```

**Example:**

```python
from codex_ml.training.continuous_learning import ContinuousLearningPipeline
from codex_ml.monitoring.drift_detection import ComprehensiveDriftMonitor

pipeline = ContinuousLearningPipeline(
    model_name="my_model",
    drift_threshold=0.15,
    min_samples_retrain=1000
)

monitor = ComprehensiveDriftMonitor(...)

# Auto-retrain on drift
if monitor.has_critical_drift():
    drift_score = monitor.get_drift_summary()["max_drift"]
    
    if pipeline.should_retrain(drift_score=drift_score, samples_count=1500):
        # Retrain
        new_version = pipeline.retrain(train_fn, train_data)
        
        # Compare with production
        comparison = pipeline.compare_models(new_version)
        
        if comparison["is_better"]:
            pipeline.deploy_model(new_version)
        else:
            pipeline.rollback()
```

### A/B Testing

#### `codex_ml.training.ab_testing`

A/B testing framework for model evaluation.

```python
class ABTestManager:
    """A/B test manager for model experiments."""
    
    def __init__(self, config: ABTestConfig):
        """Initialize A/B test manager.
        
        Args:
            config: A/B test configuration
        """
        
    def record_result(self, variant_name: str, metrics: Dict[str, float]):
        """Record result for a variant.
        
        Args:
            variant_name: Name of variant (e.g., "v1.0", "v2.0")
            metrics: Dictionary of metric values
        """
        
    def is_significant(self, alpha: float = 0.05) -> bool:
        """Check if results are statistically significant.
        
        Args:
            alpha: Significance level (default: 0.05 for 95% confidence)
            
        Returns:
            True if difference is statistically significant
        """
        
    def get_winner(self) -> str:
        """Determine winning variant based on primary metric.
        
        Returns:
            Name of winning variant
        """
        
    def gradual_rollout(self, winner_variant: str, steps: int = 5):
        """Gradually rollout winning variant.
        
        Args:
            winner_variant: Variant to roll out
            steps: Number of rollout steps
        """
        
    def save_results(self, output_path: Path | str):
        """Save experiment results to file."""
```

**Example:**

```python
from codex_ml.training.ab_testing import ABTestManager, ABTestConfig

config = ABTestConfig(
    experiment_name="model_v2_test",
    control_variant="v1.0",
    treatment_variants=["v2.0"],
    traffic_split={"v1.0": 0.5, "v2.0": 0.5},
    primary_metric="accuracy"
)

manager = ABTestManager(config)

# Track performance
for i in range(100):
    variant = "v1.0" if i % 2 == 0 else "v2.0"
    metrics = get_metrics(variant)
    manager.record_result(variant, metrics)

# Determine winner
if manager.is_significant():
    winner = manager.get_winner()
    print(f"Winner: {winner}")
    manager.gradual_rollout(winner, steps=5)
    manager.save_results("ab_test_results.json")
```

### Plugin Sandbox

#### `codex_ml.plugins.plugin_sandbox`

Sandboxed plugin execution with contract validation and auto-disable.

```python
class Plugin(ABC):
    """Base class for plugins."""
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize plugin."""
        
    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Execute plugin logic."""
        
    @abstractmethod
    def cleanup(self):
        """Clean up resources."""
        
    def get_contract(self) -> PluginContract:
        """Get plugin contract specification."""

class PluginManager:
    """Plugin lifecycle manager."""
    
    def __init__(
        self,
        sandbox: Optional[PluginSandbox] = None,
        validate_contracts: bool = True
    ):
        """Initialize plugin manager.
        
        Args:
            sandbox: Plugin sandbox (creates default if None)
            validate_contracts: Enable contract validation
        """
        
    def register_plugin(self, plugin: Plugin) -> bool:
        """Register a plugin.
        
        Args:
            plugin: Plugin instance
            
        Returns:
            True if registration successful
        """
        
    def execute_plugin(
        self,
        plugin_name: str,
        *args,
        **kwargs
    ) -> Optional[Any]:
        """Execute a registered plugin."""
        
    def get_plugin_health_report(self) -> Dict[str, Any]:
        """Get health report for all plugins."""
```

**Example:**

```python
from codex_ml.plugins.plugin_sandbox import Plugin, PluginContract, PluginManager

class MyPlugin(Plugin):
    def initialize(self) -> bool:
        return True
    
    def execute(self, data):
        return {"result": "processed"}
    
    def cleanup(self):
        pass
    
    def get_contract(self) -> PluginContract:
        return PluginContract(
            required_methods=["initialize", "execute", "cleanup"],
            max_execution_time=10.0
        )

# Use plugin manager
manager = PluginManager()
manager.register_plugin(MyPlugin(config={}))

# Execute (auto-disabled on failures)
result = manager.execute_plugin("MyPlugin", data=input_data)

# Check health
health = manager.get_plugin_health_report()
# {
#   "total_plugins": 1,
#   "enabled": 1,
#   "disabled": 0,
#   "plugins": {
#     "MyPlugin": {"status": "enabled", "failure_count": 0, ...}
#   }
# }
```

---

## Integration Examples

### Complete Autonomous Training Pipeline

```python
from codex_ml.utils.deterministic import enable_deterministic_mode
from codex_ml.utils.repro import DatasetManifest
from codex_ml.utils.checkpoint_integrity_validation import CheckpointIntegrity
from codex_ml.utils.config_drift import ConfigDrift
from codex_ml.training.rng_checkpoint import RNGState
from codex_ml.utils.wandb_logger import init_wandb
from codex_ml.training.early_stopping import auto_inject_early_stopping_for_trainer
from codex_ml.utils.self_healing import SelfHealingContext
from codex_ml.monitoring.drift_detection import ComprehensiveDriftMonitor
from codex_ml.training.continuous_learning import ContinuousLearningPipeline
from codex_ml.training.ab_testing import ABTestManager

def autonomous_training_pipeline(config, train_data, eval_data):
    """Fully autonomous training with all features."""
    
    # Phase 2: Deterministic mode
    enable_deterministic_mode()
    
    # Phase 2: Dataset integrity
    manifest = DatasetManifest("data/train")
    assert not manifest.has_drift("dataset_manifest.json")
    
    # Phase 2: Config validation
    drift = ConfigDrift(config)
    drift.validate_against_baseline("config_baseline.json", strict=True)
    
    # Phase 3: Offline logging
    logger = init_wandb(project="codex")
    
    # Phase 3: Auto early stopping
    callbacks = auto_inject_early_stopping_for_trainer(
        trainer_class=Trainer,
        eval_dataset=eval_data
    )
    
    # Phase 3: Self-healing training
    with SelfHealingContext(batch_size=config["batch_size"]) as healer:
        trainer = Trainer(
            model=model,
            args=TrainingArguments(
                per_device_train_batch_size=healer.batch_size
            ),
            train_dataset=train_data,
            eval_dataset=eval_data,
            callbacks=callbacks
        )
        
        trainer.train()
        logger.log(trainer.state.log_history[-1])
    
    # Phase 2: Save with integrity
    checkpoint_path = "checkpoint.pt"
    torch.save(model.state_dict(), checkpoint_path)
    
    integrity = CheckpointIntegrity(checkpoint_path)
    integrity.save_integrity()
    
    rng_state = RNGState()
    rng_state.capture()
    rng_state.save_to_file(Path(f"{checkpoint_path}.rng.json"))
    
    logger.finish()
    
    # Phase 4: Continuous learning
    monitor = ComprehensiveDriftMonitor(...)
    if monitor.has_critical_drift():
        pipeline = ContinuousLearningPipeline(...)
        new_version = pipeline.retrain(train_fn, train_data)
        pipeline.deploy_model(new_version)

if __name__ == "__main__":
    autonomous_training_pipeline(config, train_data, eval_data)
```

---

## Next Steps

For detailed guides, see:
- [Getting Started Guide](guides/getting_started.md)
- [Continuous Learning Guide](guides/continuous_learning_guide.md)
- [A/B Testing Guide](guides/ab_testing_guide.md)
- [Plugin Development Guide](guides/plugin_development.md)
- [Production Deployment Guide](guides/production_deployment.md)

For architecture documentation, see:
- [System Overview](architecture/system_overview.md)
- [Phase 1: Foundation](architecture/phase_1_foundation.md)
- [Phase 2: Reproducibility](architecture/phase_2_reproducibility.md)
- [Phase 3: Autonomy](architecture/phase_3_autonomy.md)
- [Phase 4: Excellence](architecture/phase_4_excellence.md)
