# API Reference Documentation

**Last Updated:** 2026-06-22

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

## Observability

### `codex_ml.serving.health`

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

## `codex_ml.monitoring.metrics`

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

## `codex_ml.utils.repro`

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

## `codex_ml.utils.deterministic`

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

## `codex_ml.utils.checkpoint_integrity_validation`

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

## `codex_ml.utils.config_drift`

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

## Drift Detection

### `codex_ml.monitoring.drift_detection`

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

## `codex_ml.utils.wandb_logger`

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

## A/B Testing

### `codex_ml.training.ab_testing`

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

## Plugin Sandbox

### `codex_ml.plugins.plugin_sandbox`

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
# "total_plugins": 1,
# "enabled": 1,
# "disabled": 0,
# "plugins": {
# "MyPlugin": {"status": "enabled", "failure_count": 0, ...}
# }
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
- [A/B Testing Guide](guides/TESTING_GUIDE.md)
- [Plugin Development Guide](guides/plugin_development.md)
- [Production Deployment Guide](guides/production_deployment.md)

For architecture documentation, see:
- [System Overview](architecture/system_overview.md)
- [Phase 1: Foundation](architecture/phase_1_foundation.md)
- [Phase 2: Reproducibility](architecture/phase_2_reproducibility.md)
- [Phase 3: Autonomy](architecture/phase_3_autonomy.md)
- [Phase 4: Excellence](architecture/phase_4_excellence.md)


---
## 📎 Consolidated from: docs/api/API_DOCUMENTATION.md

# API Reference Documentation

> **Version**: 1.0.0
> **Generated**: 2025-12-11
> **Auto-sync**: Updates with code changes via CI

---

## Overview

This document provides comprehensive API documentation for the _codex_ repository, covering all public modules, classes, and functions.

---

## Table of Contents

1. [Agent APIs](#agent-apis)
2. [ML Core APIs](#ml-core-apis)
3. [Integration APIs](#integration-apis)
4. [Utility APIs](#utility-apis)

---

## Agent APIs

### AgentMemorySystem

**Module**: `agents.agent_memory`

SQLite-backed persistent memory system for AI agents.

```python
from agents.agent_memory import AgentMemorySystem

# Initialize
memory = AgentMemorySystem(agent_id="my_agent", db_path=Path("memory.db"))

# Start a task
frame = memory.start_task("Fix security vulnerability")

# Store a decision
memory_id = memory.store_decision(
    task_id="task_001",  # pragma: allowlist secret
    decision="Use input validation",
    rationale="Prevents injection attacks",
    context={"file": "auth.py"}
)

# Retrieve similar contexts
contexts = memory.retrieve_similar_context(
    task_description="security input validation",  # pragma: allowlist secret
    limit=5
)

# Get pattern library
patterns = memory.get_pattern_library()

# Invalidate old contexts
count = memory.invalidate_stale_contexts(age_days=30)

# Complete task
memory.complete_task(success=True, summary="Fixed vulnerability")
```

## Methods

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `start_task` | `task_description: str` | `ContextFrame` | Start a new task context | <!-- pragma: allowlist secret -->
| `store_decision` | `task_id, decision, rationale, context` | `str` | Store decision, returns memory ID | <!-- pragma: allowlist secret -->
| `retrieve_similar_context` | `task_description, limit=5` | `List[Dict]` | Find relevant past contexts | <!-- pragma: allowlist secret -->
| `get_pattern_library` | None | `List[Dict]` | Get all decision patterns |
| `invalidate_stale_contexts` | `age_days=30` | `int` | Clean old contexts, returns count |
| `record_decision` | `decision, alternatives, confidence, reasoning` | `MemoryEntry` | Record decision with alternatives |
| `record_lesson` | `lesson, success` | `MemoryEntry` | Record lesson learned |
| `get_guidance` | `situation: str` | `Dict` | Get guidance for situation |
| `complete_task` | `success, summary` | None | Complete current task |
| `get_stats` | None | `Dict` | Get memory statistics |

---

### SelfHealingEngine

**Module**: `agents.self_healing`

Automated issue detection and remediation engine.

```python
from agents.self_healing import SelfHealingEngine

# Initialize
engine = SelfHealingEngine(repo_path=".")

# Run health check
report = engine.run_health_check()
print(f"Health Score: {report.health_score}/100")

# Get issues
for issue in report.issues:
    print(f"- {issue.issue_type}: {issue.description}")
    print(f"  Fix: {issue.suggested_fix}")

# Apply fixes (dry run)
results = engine.apply_fixes(dry_run=True)
```

## Methods

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `run_health_check` | None | `HealthReport` | Analyze repository health |
| `detect_issues` | None | `List[Issue]` | Detect all issues |
| `suggest_fixes` | `issues: List[Issue]` | `List[Fix]` | Generate fix suggestions |
| `apply_fixes` | `dry_run=True` | `Dict` | Apply fixes to codebase |

---

### QuantumGameTheory

**Module**: `agents.quantum_game_theory`

Physics-inspired game theory for Blue/Red team simulations.

```python
from agents.quantum_game_theory import (
    ClassicalGameEngine,
    QuantumInspiredGameEngine,
    BlueRedTeamSimulator
)

# Classical game
classical = ClassicalGameEngine(
    strategy_sizes=(3, 3),
    payoff_a=[[3, 0, 5], [1, 2, 1], [0, 1, 4]],
    payoff_b=[[3, 1, 0], [0, 2, 1], [5, 1, 4]]
)
eq = classical.find_nash_equilibrium()

# Quantum-inspired game
quantum = QuantumInspiredGameEngine(
    strategy_sizes=(3, 3),
    payoff_a=payoff_a,
    payoff_b=payoff_b
)
quantum.apply_entanglement(strength=0.5)
result = quantum.measure_strategy()

# Blue/Red team simulation
simulator = BlueRedTeamSimulator()
results = simulator.run_simulation(rounds=100)
```

---

## ML Core APIs

### PluginSandbox

**Module**: `src.codex_ml.plugins.plugin_sandbox`

Secure plugin execution environment.

```python
from codex_ml.plugins.plugin_sandbox import PluginSandbox, PluginMetadata

# Create sandbox
sandbox = PluginSandbox(
    max_memory_mb=512,
    max_execution_time=30.0,
    allowed_imports=["numpy", "pandas"]
)

# Register plugin
sandbox.register_plugin(
    name="my_plugin",
    module_path="plugins/my_plugin.py"
)

# Execute plugin
result = sandbox.execute_plugin(
    name="my_plugin",
    method="process",
    args={"data": input_data}
)

# Check quarantine status
metadata = sandbox.get_plugin_metadata("my_plugin")
if metadata.is_quarantine_expired(quarantine_duration=3600):
    sandbox.restore_plugin("my_plugin")
```

---

## HARIntegration

**Module**: `src.codex_ml.integrations.har_integration`

HTTP Archive (HAR) recording and replay.

```python
from codex_ml.integrations.har_integration import (
    HARRecorder,
    HARCache,
    HARReplayer
)

# Record HTTP transactions
recorder = HARRecorder()
recorder.start_recording()
# ... make HTTP requests ...
har_log = recorder.stop_recording()
recorder.save("transactions.har")

# Cache responses
cache = HARCache(cache_dir=".har_cache")
cache.cache_response(request, response)
cached = cache.get_cached_response(request)

# Replay transactions
replayer = HARReplayer("transactions.har")
for entry in replayer.entries:
    response = replayer.replay_entry(entry)
```

---

## Scalability Utilities

**Module**: `src.codex_ml.utils.scalability`

Performance and scalability utilities.

```python
from codex_ml.utils.scalability import (
    LRUCache,
    RateLimiter,
    CircuitBreaker,
    LoadBalancer,
    ResourcePool,
    PerformanceMonitor
)

# LRU Cache
cache = LRUCache(max_size=1000)
cache.put("key", "value")
value = cache.get("key")

# Rate Limiter
limiter = RateLimiter(rate=100, per_seconds=1)
if limiter.acquire():
    # Process request
    pass

# Circuit Breaker
breaker = CircuitBreaker(failure_threshold=5, reset_timeout=30)
with breaker:
    # Protected operation
    result = risky_operation()

# Load Balancer
balancer = LoadBalancer(
    endpoints=["server1", "server2", "server3"],
    strategy="round_robin"
)
endpoint = balancer.get_endpoint()

# Resource Pool
pool = ResourcePool(factory=create_connection, max_size=10)
with pool.acquire() as conn:
    conn.execute(query)

# Performance Monitor
monitor = PerformanceMonitor()

@monitor.timed("operation_name")
def my_operation():
    pass

stats = monitor.get_stats("operation_name")
```

---

## Integration APIs

### Event System

**Module**: `src.codex_ml.events.base`

Event publishing and subscription.

```python
from codex_ml.events import EventPublisher, Event

# Create publisher
publisher = EventPublisher()

# Subscribe to events
def on_model_trained(event: Event):
    print(f"Model trained: {event.data}")

publisher.subscribe("model.trained", on_model_trained)

# Publish events
publisher.publish(Event(
    type="model.trained",
    data={"model_id": "model_001", "accuracy": 0.95}
))
```

---

## Utility APIs

### Stub Cleanup

**Module**: `scripts.stub_cleanup`

AST-based stub detection and cleanup.

```python
from scripts.stub_cleanup import (
    analyze_file,
    analyze_directory,
    generate_report,
    StubDetector
)

# Analyze single file
result = analyze_file(Path("src/module.py"))
print(f"Found {result.total_stubs} stubs")

# Analyze directory
result = analyze_directory(
    Path("src/"),
    exclude_abstract=True,
    exclude_patterns=["**/test_*.py"]
)

# Generate report
report = generate_report(result, format="markdown")
print(report)
```

---

## Error Handling

All APIs use consistent error handling:

```python
from codex_ml.exceptions import (
    CodexError,          # Base exception
    PluginError,         # Plugin-related errors
    ValidationError,     # Input validation errors
    ConfigurationError,  # Configuration errors
    ResourceError,       # Resource allocation errors
)

try:
    result = api_call()
except ValidationError as e:
    logger.error(f"Invalid input: {e}")
except PluginError as e:
    logger.error(f"Plugin failed: {e}")
except CodexError as e:
    logger.error(f"Operation failed: {e}")
```

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CODEX_SESSION_ID` | Session identifier | Auto-generated |
| `CODEX_LOG_DB_PATH` | SQLite database path | `.codex/logs.db` |
| `CODEX_FORCE_CPU` | Disable GPU | `0` |
| `CODEX_BATCH_SIZE` | Default batch size | `32` |
| `CODEX_MAX_MEMORY_MB` | Memory limit | `4096` |

---

## Versioning

APIs follow semantic versioning:
- **Major**: Breaking changes
- **Minor**: New features, backward compatible
- **Patch**: Bug fixes

---

## See Also

- [Architecture Blueprint](ARCHITECTURE_BLUEPRINT.md)
- [Contributing Guide](../CONTRIBUTING.md)
- [Deployment Guide](guides/production_deployment.md)
- [Agent Documentation](agent/INDEX.md)
- [Quick Start](mcp/QUICK_START.md)



---
## 📎 Consolidated from: docs/INGESTION_API_REFERENCE.md

# Ingestion Pipeline API Reference

## Overview

The ingestion pipeline provides a unified interface for processing multiple file formats (CSV, JSON, JSONL, TXT, MD) with comprehensive validation, transformation, and streaming support.

**Module**: `src.ingestion.pipeline`
**Version**: 1.0
**Status**: Production Ready

## Core Components

### 1. PipelineConfig

Configuration dataclass for the ingestion pipeline.

```python
from src.ingestion.pipeline import PipelineConfig

config = PipelineConfig(
    encoding='auto',           # File encoding detection
    batch_size=1000,          # Records per batch
    max_file_size_mb=100,     # Maximum file size
    shuffle=False,            # Shuffle records
    shuffle_seed=42,          # Random seed
    lowercase=False,          # Lowercase text
    strip_whitespace=True,    # Strip whitespace
    skip_empty=True,          # Skip empty records
    timeout_seconds=300,      # Operation timeout
    validate_utf8=True        # Validate UTF-8
)
```

**Attributes:**
- `encoding` (str): File encoding. Use 'auto' for auto-detection
- `batch_size` (int): Records per batch for streaming (default: 1000)
- `max_file_size_mb` (int): Maximum file size in MB (default: 100)
- `shuffle` (bool): Whether to shuffle records (default: False)
- `shuffle_seed` (int): Random seed for reproducibility (default: 42)
- `lowercase` (bool): Convert text to lowercase (default: False)
- `strip_whitespace` (bool): Strip leading/trailing whitespace (default: True)
- `skip_empty` (bool): Skip empty records (default: True)
- `timeout_seconds` (int): Operation timeout in seconds (default: 300)
- `validate_utf8` (bool): Validate UTF-8 encoding (default: True)

### 2. PipelineResult

Result of a pipeline operation.

```python
from src.ingestion.pipeline import PipelineResult

result = pipeline.ingest_file('data.csv')

# Access results
print(result.success)               # bool
print(result.records_processed)     # int
print(result.records_skipped)       # int
print(result.errors)                # List[str]
print(result.duration_seconds)      # float
print(result.output_path)           # str
print(result.metadata)              # dict
```

**Attributes:**
- `success` (bool): Whether operation succeeded
- `records_processed` (int): Number of records processed
- `records_skipped` (int): Number of records skipped
- `errors` (List[str]): List of error messages
- `duration_seconds` (float): Operation duration
- `output_path` (str): Output file path (if applicable)
- `metadata` (dict): Additional metadata

## 3. IngestionPipeline

Main pipeline class for data ingestion.

```python
from src.ingestion.pipeline import IngestionPipeline, PipelineConfig

config = PipelineConfig(batch_size=500)
pipeline = IngestionPipeline(config)
```

### Methods

#### `ingest_file()`

Process a single file.

```python
result = pipeline.ingest_file(
    input_path='data/input.csv',
    output_path='data/output.jsonl',
    transform_fn=None
)
```

**Parameters:**
- `input_path` (str|Path): Path to input file
- `output_path` (str|Path, optional): Path to output file
- `transform_fn` (Callable, optional): Custom transformation function

**Returns:** `PipelineResult`

**Raises:** 
- `FileNotFoundError`: If input file not found
- `ValueError`: If file exceeds max size
- `TimeoutError`: If operation exceeds timeout

**Example:**

```python
# Process with transformation
def transform(record):
    return {
        'text': record.get('text', '').lower(),
        'label': int(record.get('label', 0))
    }

result = pipeline.ingest_file(
    'raw_data.csv',
    'processed_data.jsonl',
    transform_fn=transform
)

if result.success:
    print(f"Processed {result.records_processed} records")
else:
    print(f"Errors: {result.errors}")
```

## `ingest_directory()`

Process all files in a directory.

```python
result = pipeline.ingest_directory(
    input_dir='data/raw',
    output_dir='data/processed',
    pattern='*.csv'
)
```

**Parameters:**
- `input_dir` (str|Path): Input directory path
- `output_dir` (str|Path): Output directory path
- `pattern` (str): File pattern to match (default: '*')

**Returns:** `PipelineResult` (aggregated)

**Example:**

```python
result = pipeline.ingest_directory(
    'data/raw',
    'data/processed',
    pattern='*.{csv,json}'
)

print(f"Total: {result.records_processed}")
print(f"Failed: {len(result.errors)}")
```

### `stream_records()`

Stream records from a file (memory-efficient).

```python
for batch in pipeline.stream_records('data/large_file.csv'):
    # Process batch (list of dicts)
    process_batch(batch)
```

**Parameters:**
- `input_path` (str|Path): Path to input file

**Returns:** Iterator of record batches

**Example:**

```python
# Process large file in batches
batch_count = 0
for batch in pipeline.stream_records('data/large_file.csv'):
    batch_count += 1
    process_batch(batch)
    print(f"Processed batch {batch_count}")
```

## File Format Support

### CSV Format

Comma-separated values with headers.

```python
# Input: data.csv
id,text,label
1,Sample text,0
2,Another example,1

# Usage
result = pipeline.ingest_file('data.csv', 'data.jsonl')

# Output: data.jsonl
{"id": "1", "text": "Sample text", "label": "0"}
{"id": "2", "text": "Another example", "label": "1"}
```

## JSON Format

Single JSON object or array.

```python
# Input: data.json
{
  "data": [
    {"id": 1, "text": "Sample text", "label": 0},
    {"id": 2, "text": "Another example", "label": 1}
  ]
}

# Usage
result = pipeline.ingest_file('data.json', 'data.jsonl')
```

## JSONL Format

Newline-delimited JSON (one object per line).

```
# Input: data.jsonl
{"id": 1, "text": "Sample text", "label": 0}
{"id": 2, "text": "Another example", "label": 1}
```

## Text Format

Plain text, one record per line.

```
# Input: data.txt
Sample text
Another example

# Usage with transformation
def text_to_record(line):
    return {"text": line}

result = pipeline.ingest_file('data.txt')
```

## Custom Ingestors

### CSV Ingestor

```python
from src.ingestion.csv_ingestor import CSVIngestor

ingestor = CSVIngestor(
    encoding='utf-8',
    delimiter=',',
    quotechar='"'
)

records = ingestor.ingest('data.csv')
```

### JSON Ingestor

```python
from src.ingestion.json_ingestor import JSONIngestor

ingestor = JSONIngestor(encoding='utf-8')
records = ingestor.ingest('data.json')
```

### File Ingestor

```python
from src.ingestion.file_ingestor import FileIngestor

ingestor = FileIngestor(encoding='utf-8')
records = ingestor.ingest('data.txt')
```

## Error Handling

### Common Errors

**FileNotFoundError:**
```python
try:
    result = pipeline.ingest_file('nonexistent.csv')
except FileNotFoundError:
    print("Input file not found")
```

**EncodingError:**
```python
config = PipelineConfig(encoding='utf-8', validate_utf8=True)
pipeline = IngestionPipeline(config)
result = pipeline.ingest_file('data_with_encoding_issues.csv')
```

**SizeError:**
```python
config = PipelineConfig(max_file_size_mb=50)
pipeline = IngestionPipeline(config)
result = pipeline.ingest_file('large_file.csv')  # Will fail if > 50MB
```

**TimeoutError:**
```python
config = PipelineConfig(timeout_seconds=60)
pipeline = IngestionPipeline(config)
try:
    result = pipeline.ingest_file('data.csv')
except TimeoutError:
    print("Operation exceeded 60 second timeout")
```

## Performance Considerations

1. **Batch Size**: Larger batches = faster processing but higher memory
   ```python
   config = PipelineConfig(batch_size=5000)  # Larger batches
   ```

2. **Streaming**: Use `stream_records()` for large files to save memory
   ```python
   for batch in pipeline.stream_records('large_file.csv'):
       process_batch(batch)
   ```

3. **Parallel Processing**: Process multiple files simultaneously
   ```python
   from concurrent.futures import ProcessPoolExecutor

   files = ['file1.csv', 'file2.csv', 'file3.csv']
   with ProcessPoolExecutor(max_workers=4) as executor:
       results = executor.map(pipeline.ingest_file, files)
   ```

4. **Encoding Detection**: Auto-detection is slower than specifying encoding
   ```python
   config = PipelineConfig(encoding='utf-8')  # Faster
   ```

## Best Practices

1. **Always validate input files**
   ```python
   from pathlib import Path
   input_file = Path('data.csv')
   assert input_file.exists(), f"{input_file} not found"
   ```

2. **Use deterministic shuffling for reproducibility**
   ```python
   config = PipelineConfig(shuffle=True, shuffle_seed=42)
   ```

3. **Log pipeline results**
   ```python
   result = pipeline.ingest_file('data.csv', 'output.jsonl')
   logging.info(f"Processed: {result.records_processed}, "
                f"Skipped: {result.records_skipped}")
   ```

4. **Handle errors gracefully**
   ```python
   if not result.success:
       logging.error(f"Pipeline errors: {result.errors}")
       # Implement fallback or retry logic
   ```

## See Also

- [RAG Pipeline API Reference](./RAG_API_REFERENCE.md)
- [Configuration Guide](./CONFIGURATION_GUIDE.md)
- [Quickstart Guide](./QUICKSTART.md)

