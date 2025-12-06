# Getting Started with Codex ML

Welcome to Codex ML! This guide will help you get started with the autonomous machine learning system.

## Table of Contents

- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Install from Source](#install-from-source)
  - [Optional Dependencies](#optional-dependencies)
- [Quick Start](#quick-start)
  - [Basic Training with Determinism](#1-basic-training-with-determinism)
  - [Health Monitoring](#2-health-monitoring)
- [Core Features](#core-features)
- [CLI Usage](#cli-usage)
- [Configuration](#configuration)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
## Table of Contents

- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Install from Source](#install-from-source)
  - [Optional Dependencies](#optional-dependencies)
- [Quick Start](#quick-start)
  - [Basic Training with Determinism](#1-basic-training-with-determinism)
  - [Health Monitoring](#2-health-monitoring)
  - [Experiment Tracking (Offline-First)](#3-experiment-tracking-offline-first)
  - [Safe Prompt Handling](#4-safe-prompt-handling)
- [Core Features](#core-features)
  - [Reproducibility (Phase 2)](#reproducibility-phase-2)
  - [Autonomy (Phase 3)](#autonomy-phase-3)
  - [Production Excellence (Phase 4)](#production-excellence-phase-4)
- [Complete Training Pipeline](#complete-training-pipeline)
- [CLI Usage](#cli-usage)
  - [Training with Strict Resume](#training-with-strict-resume)
  - [Prompt Sanitization](#prompt-sanitization)
  - [SBOM Generation](#sbom-generation)
  - [Stub Analysis](#stub-analysis)
- [Configuration](#configuration)
  - [Environment Variables](#environment-variables)
  - [Configuration Files](#configuration-files)
- [Testing Your Setup](#testing-your-setup)
  - [Run Tests](#run-tests)
  - [Run Nox Sessions](#run-nox-sessions)
  - [Security Scans](#security-scans)
- [Troubleshooting](#troubleshooting)
  - [Common Issues](#common-issues)
- [Next Steps](#next-steps)
- [Support](#support)

## Installation

### Prerequisites

- Python 3.9+
- pip or conda

### Install from Source

```bash
git clone https://github.com/Aries-Serpent/_codex_.git
cd _codex_
pip install -e .
```

### Optional Dependencies

```bash
# For PyTorch support
pip install torch

# For MLOps features
pip install wandb prometheus-client

# For development
pip install -e ".[dev]"
```

## Quick Start

### 1. Basic Training with Determinism

```python
from codex_ml.utils.deterministic import enable_deterministic_mode

# Enable bit-exact reproducibility
enable_deterministic_mode()

# Your training code here
model = YourModel()
trainer = YourTrainer(model)
trainer.train()
```

### 2. Health Monitoring

Set up health checks for production deployments:

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

### 3. Experiment Tracking (Offline-First)

```python
from codex_ml.utils.wandb_logger import init_wandb

# Defaults to offline mode (no network calls)
logger = init_wandb(project="my-project", name="experiment-1")

for epoch in range(10):
    # Training step
    loss = train_step()
    logger.log({"epoch": epoch, "loss": loss})

logger.finish()
```

### 4. Safe Prompt Handling

```python
from codex_ml.safety.prompt_sanitizer import PromptSanitizer

sanitizer = PromptSanitizer(strict_mode=True)

user_prompt = input("Enter your prompt: ")

try:
    safe_prompt = sanitizer.sanitize(user_prompt)
    # Use safe_prompt for model inference
    result = model.generate(safe_prompt)
except ValueError as e:
    print(f"Unsafe prompt detected: {e}")
```

## Core Features

### Reproducibility (Phase 2)

**Deterministic Training:**
```python
from codex_ml.utils.deterministic import enable_deterministic_mode

enable_deterministic_mode()
# All operations are now deterministic
```

**RNG State Management:**
```python
from codex_ml.training.rng_checkpoint import RNGState
from pathlib import Path

# Save RNG state with checkpoint
rng_state = RNGState()
rng_state.capture()
rng_state.save_to_file(Path("checkpoint.pt.rng.json"))

# Restore RNG state on resume
rng_state = RNGState.load_from_file(Path("checkpoint.pt.rng.json"))
rng_state.restore()
```

**Dataset Integrity:**
```python
from codex_ml.utils.repro import DatasetManifest

# Generate manifest
manifest = DatasetManifest("data/train")
manifest.generate().save("data/train_manifest.json")

# Verify integrity
if manifest.has_drift("data/train_manifest.json"):
    print("⚠️ Dataset has changed!")
```

### Autonomy (Phase 3)

**Self-Healing Training:**
```python
from codex_ml.utils.self_healing import SelfHealingContext

# Automatic OOM recovery
with SelfHealingContext(batch_size=32, enable_oom_recovery=True) as healer:
    trainer = Trainer(
        model=model,
        args=TrainingArguments(
            per_device_train_batch_size=healer.batch_size
        )
    )
    trainer.train()
    # If OOM occurs, batch_size automatically reduced
```

**Drift Detection:**
```python
from codex_ml.monitoring.drift_detection import ComprehensiveDriftMonitor

monitor = ComprehensiveDriftMonitor(
    data_threshold=0.1,
    model_threshold=0.1
)

results = monitor.monitor_all(
    current_data_stats=current_stats,
    baseline_data_stats=baseline_stats,
    current_metrics=current_metrics,
    baseline_metrics=baseline_metrics
)

if monitor.has_critical_drift():
    print("⚠️ Critical drift detected!")
    # Trigger retraining
```

**Early Stopping:**
```python
from codex_ml.training.early_stopping import auto_inject_early_stopping_for_trainer

callbacks = auto_inject_early_stopping_for_trainer(
    trainer_class=Trainer,
    eval_dataset=eval_dataset,
    patience=3
)

trainer = Trainer(..., callbacks=callbacks)
# Training will stop early if no improvement for 3 evaluations
```

### Production Excellence (Phase 4)

**Continuous Learning:**
```python
from codex_ml.training.continuous_learning import ContinuousLearningPipeline

pipeline = ContinuousLearningPipeline(
    model_name="my_model",
    drift_threshold=0.15,
    min_samples_retrain=1000
)

if pipeline.should_retrain(drift_score=0.2, samples_count=1500):
    new_version = pipeline.retrain(train_fn, train_data)
    if pipeline.compare_models(new_version)["is_better"]:
        pipeline.deploy_model(new_version)
```

**A/B Testing:**
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

# Record results
manager.record_result("v1.0", {"accuracy": 0.91})
manager.record_result("v2.0", {"accuracy": 0.94})

# Determine winner
if manager.is_significant():
    winner = manager.get_winner()
    manager.gradual_rollout(winner, steps=5)
```

**Plugin Sandbox:**
```python
from codex_ml.plugins.plugin_sandbox import Plugin, PluginManager

class MyPlugin(Plugin):
    def initialize(self) -> bool:
        return True
    
    def execute(self, data):
        return {"processed": data}
    
    def cleanup(self):
        pass

manager = PluginManager()
manager.register_plugin(MyPlugin())

result = manager.execute_plugin("MyPlugin", data="test")
```

## Complete Training Pipeline

Here's a complete example combining all features:

```python
from pathlib import Path
from codex_ml.utils.deterministic import enable_deterministic_mode
from codex_ml.utils.repro import DatasetManifest
from codex_ml.utils.checkpoint_integrity_validation import CheckpointIntegrity
from codex_ml.utils.config_drift import ConfigDrift
from codex_ml.training.rng_checkpoint import RNGState
from codex_ml.utils.wandb_logger import init_wandb
from codex_ml.training.early_stopping import auto_inject_early_stopping_for_trainer
from codex_ml.utils.self_healing import SelfHealingContext
from codex_ml.monitoring.drift_detection import ComprehensiveDriftMonitor

def autonomous_training(config, train_data, eval_data):
    """Fully autonomous training pipeline."""
    
    # 1. Enable determinism
    enable_deterministic_mode()
    
    # 2. Validate dataset integrity
    manifest = DatasetManifest("data/train")
    if manifest.has_drift("data/train_manifest.json"):
        raise ValueError("Dataset drift detected!")
    
    # 3. Validate config
    drift = ConfigDrift(config)
    drift.validate_against_baseline("config_baseline.json", strict=True)
    
    # 4. Initialize logging (offline)
    logger = init_wandb(project="my-project", config=config)
    
    # 5. Setup early stopping
    callbacks = auto_inject_early_stopping_for_trainer(
        trainer_class=Trainer,
        eval_dataset=eval_data,
        patience=3
    )
    
    # 6. Train with self-healing
    with SelfHealingContext(batch_size=config["batch_size"]) as healer:
        trainer = Trainer(
            model=model,
            args=TrainingArguments(
                per_device_train_batch_size=healer.batch_size,
                evaluation_strategy="epoch"
            ),
            train_dataset=train_data,
            eval_dataset=eval_data,
            callbacks=callbacks
        )
        
        trainer.train()
        
        # Log final metrics
        logger.log(trainer.state.log_history[-1])
    
    # 7. Save checkpoint with integrity
    checkpoint_path = Path("checkpoint.pt")
    torch.save(model.state_dict(), checkpoint_path)
    
    # Save integrity metadata
    integrity = CheckpointIntegrity(checkpoint_path)
    integrity.save_integrity(metadata={"config": config})
    
    # Save RNG state for deterministic resume
    rng_state = RNGState()
    rng_state.capture()
    rng_state.save_to_file(checkpoint_path.with_suffix(".pt.rng.json"))
    
    logger.finish()
    
    return model

if __name__ == "__main__":
    config = {
        "learning_rate": 0.001,
        "batch_size": 32,
        "epochs": 10
    }
    
    model = autonomous_training(config, train_data, eval_data)
```

## CLI Usage

### Training with Strict Resume

```bash
# Initial training
python cli/train_codex.py \
    --train-file data/train.txt \
    --model-name my_model \
    --output-dir checkpoints/

# Resume with strict RNG validation (deterministic)
python cli/train_codex.py \
    --codex-resume-checkpoint checkpoints/checkpoint.pt \
    --strict-resume
```

### Prompt Sanitization

```bash
# Safe prompt
python cli/inference.py --prompt "What is machine learning?"

# Unsafe prompt (blocked in strict mode)
python cli/inference.py --prompt "<script>alert('xss')</script>"
# Error: Unsafe prompt detected

# Unsafe prompt (redacted in non-strict mode)
python cli/inference.py --prompt "<script>alert('xss')</script>" --non-strict
# Output: [REDACTED]...
```

### SBOM Generation

```bash
# Generate Software Bill of Materials
python scripts/generate_sbom.py --output dist/sbom.json
```

### Stub Analysis

```bash
# Analyze code for stubs
python scripts/analyze_stubs.py
# Output: reports/stub_analysis.md
```

## Configuration

### Environment Variables

Key environment variables for Codex ML:

```bash
# Determinism
export PYTHONHASHSEED=0
export CUBLAS_WORKSPACE_CONFIG=:4096:8

# Offline mode (default)
export WANDB_MODE=offline
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

# Logging
export CODEX_SESSION_ID=my-session
export CODEX_SESSION_LOG_DIR=.codex/sessions
export CODEX_LOG_DB_PATH=.codex/logs.db

# Testing
export CODEX_TEST_SEED=42
```

### Configuration Files

Create a `config.yaml`:

```yaml
model:
  name: my_model
  architecture: transformer
  
training:
  learning_rate: 0.001
  batch_size: 32
  epochs: 10
  
reproducibility:
  enable_determinism: true
  save_rng_state: true
  validate_dataset: true
  
autonomy:
  enable_self_healing: true
  enable_early_stopping: true
  early_stopping_patience: 3
  
continuous_learning:
  drift_threshold: 0.15
  min_samples_retrain: 1000
  
observability:
  enable_health_probes: true
  enable_metrics: true
  log_offline: true
```

## Testing Your Setup

### Run Tests

```bash
# All tests
pytest tests/

# With coverage
pytest tests/ --cov=src --cov=training --cov-report=term-missing

# Specific test file
pytest tests/test_sanitize.py -v
```

### Run Nox Sessions

```bash
# Test session with coverage
nox -s tests

# All sessions
nox
```

### Security Scans

```bash
# Python SAST
bandit -r src/ training/ cli/ -ll

# Dependency vulnerabilities
pip-audit

# Credential leak detection
detect-secrets scan --baseline .secrets.baseline
```

## Troubleshooting

### Common Issues

**1. Import Errors**
```bash
# Ensure package is installed
pip install -e .

# Check Python path
python -c "import sys; print(sys.path)"
```

**2. Determinism Not Working**
```python
# Ensure deterministic mode is enabled BEFORE any operations
from codex_ml.utils.deterministic import enable_deterministic_mode
enable_deterministic_mode()  # Must be called first
```

**3. Health Checks Failing**
```python
from codex_ml.serving.health import readiness_check

# Check what's failing
status = readiness_check(
    required_dirs=[Path("data"), Path("models")],
    min_disk_space_gb=1.0
)
print(status["checks"])
```

**4. Plugin Auto-Disabled**
```python
from codex_ml.plugins.plugin_sandbox import PluginManager

manager = PluginManager()
health = manager.get_plugin_health_report()

# Check failure count
for plugin_name, info in health["plugins"].items():
    if info["status"] == "disabled":
        print(f"{plugin_name} disabled: {info['last_error']}")
        
# Manually re-enable
manager.sandbox.enable_plugin(plugin_name)
```

## Next Steps

- **Continuous Learning:** See [Continuous Learning Guide](continuous_learning_guide.md)
- **A/B Testing:** See [A/B Testing Guide](ab_testing_guide.md)
- **Plugin Development:** See [Plugin Development Guide](plugin_development.md)
- **Production Deployment:** See [Production Deployment Guide](production_deployment.md)
- **API Reference:** See [API Reference](../API_REFERENCE.md)

## Support

- **Documentation:** [docs/](../README.md)
- **Issues:** [GitHub Issues](https://github.com/Aries-Serpent/_codex_/issues)
- **Architecture:** [Architecture Docs](../architecture/)

---

**Level 4 MLOps**: Autonomous, reproducible, self-healing machine learning at scale.
