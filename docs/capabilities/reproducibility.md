# Reproducibility

## Overview

The reproducibility capability ensures ML experiments and training runs can be consistently reproduced with identical results through deterministic execution, environment capture, and comprehensive state tracking.

**Keywords**: reproducibility, deterministic, seed, random, environment, snapshot, versioning, rerun, consistent, repeatable

## Purpose

Provides reproducibility through:
- **Random Seed Control**: Deterministic random number generation
- **Environment Capture**: Record all dependencies and versions
- **State Snapshots**: Save and restore complete training state
- **Configuration Tracking**: Version all hyperparameters
- **Code Versioning**: Link experiments to git commits
- **Data Versioning**: Track dataset versions and transforms

## Architecture

### Reproducibility Layers

```
┌─────────────────────────────────────┐
│   Code Version Control              │
│   (Git commit, branch, diff)        │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│   Environment Snapshot              │
│   (Python version, packages)        │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│   Configuration & Seed              │
│   (Hyperparams, random seeds)       │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│   Data Versioning                   │
│   (Dataset hash, transforms)        │
└─────────────────────────────────────┘
```

## Core Concepts

### Random Seed Management

```python
import random
import numpy as np
import torch
from typing import Optional

def set_seed(seed: int, deterministic: bool = True) -> None:
    """
    Set random seeds for reproducibility.
    
    Safeguard: Validates seed value.
    Deterministic: Enables deterministic operations.
    
    Args:
        seed: Random seed value (non-negative integer).
        deterministic: Enable fully deterministic mode.
    """
    # Validation safeguard
    if seed < 0:
        raise ValueError(f"Seed must be non-negative, got {seed}")
    
    # Python random
    random.seed(seed)
    
    # NumPy
    np.random.seed(seed)
    
    # PyTorch
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    
    # Deterministic operations
    if deterministic:
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
        
        # Enable deterministic algorithms (PyTorch 1.8+)
        if hasattr(torch, 'use_deterministic_algorithms'):
            try:
                torch.use_deterministic_algorithms(True)
            except RuntimeError:
                # Some operations don't have deterministic implementations
                pass

def get_random_state() -> dict:
    """
    Capture current random state.
    
    Returns:
        Dictionary with all random states.
    """
    return {
        "python": random.getstate(),
        "numpy": np.random.get_state(),
        "torch": torch.get_rng_state(),
        "cuda": torch.cuda.get_rng_state_all() if torch.cuda.is_available() else None,
    }

def set_random_state(state: dict) -> None:
    """
    Restore random state.
    
    Safeguard: Validates state dictionary.
    """
    if "python" not in state:
        raise ValueError("Invalid state dictionary")
    
    random.setstate(state["python"])
    np.random.set_state(state["numpy"])
    torch.set_rng_state(state["torch"])
    
    if state["cuda"] is not None and torch.cuda.is_available():
        torch.cuda.set_rng_state_all(state["cuda"])
```

### Environment Snapshot

```python
import subprocess
import sys
import json
from pathlib import Path
from typing import Dict, Any

def capture_environment() -> Dict[str, Any]:
    """
    Capture complete environment snapshot.
    
    Safeguard: Handles missing components gracefully.
    """
    env = {
        "python_version": sys.version,
        "platform": sys.platform,
    }
    
    # Installed packages
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "freeze"],
            capture_output=True,
            text=True,
            timeout=30  # Timeout safeguard
        )
        env["packages"] = result.stdout.strip().split("\n")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        env["packages"] = []
    
    # Git information
    try:
        git_hash = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL,
            timeout=5
        ).decode().strip()
        env["git_hash"] = git_hash
        
        # Check for uncommitted changes
        diff_result = subprocess.run(
            ["git", "diff", "--stat"],
            capture_output=True,
            text=True,
            timeout=5
        )
        env["git_dirty"] = bool(diff_result.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        env["git_hash"] = "unknown"
        env["git_dirty"] = None
    
    # PyTorch specific
    try:
        import torch
        env["torch_version"] = torch.__version__
        env["cuda_available"] = torch.cuda.is_available()
        if torch.cuda.is_available():
            env["cuda_version"] = torch.version.cuda
            env["cudnn_version"] = torch.backends.cudnn.version()
    except ImportError:
        pass
    
    return env

def save_environment(path: str) -> None:
    """
    Save environment snapshot to file.
    
    Safeguard: Creates parent directories.
    """
    env = capture_environment()
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(env, indent=2))

def verify_environment(expected_path: str) -> Dict[str, list]:
    """
    Verify current environment matches snapshot.
    
    Returns dictionary of mismatches.
    """
    expected_env = json.loads(Path(expected_path).read_text())
    current_env = capture_environment()
    
    mismatches = {
        "version_changes": [],
        "missing_packages": [],
        "extra_packages": [],
    }
    
    # Check Python version
    if expected_env.get("python_version") != current_env.get("python_version"):
        mismatches["version_changes"].append({
            "name": "python",
            "expected": expected_env.get("python_version"),
            "current": current_env.get("python_version"),
        })
    
    # Check packages
    expected_packages = set(expected_env.get("packages", []))
    current_packages = set(current_env.get("packages", []))
    
    mismatches["missing_packages"] = list(expected_packages - current_packages)
    mismatches["extra_packages"] = list(current_packages - expected_packages)
    
    return mismatches
```

## Configuration

### Reproducibility Configuration

```python
from dataclasses import dataclass

@dataclass
class ReproducibilityConfig:
    """
    Reproducibility settings.
    
    Safeguard: Validates configuration.
    """
    # Random seed
    seed: int = 42
    deterministic: bool = True
    
    # Environment
    save_environment: bool = True
    verify_environment: bool = False
    
    # Code versioning
    require_clean_git: bool = False
    log_git_diff: bool = True
    
    # Data versioning
    hash_datasets: bool = True
    
    def __post_init__(self):
        """Validate configuration."""
        if self.seed < 0:
            raise ValueError("Seed must be non-negative")
```

### YAML Configuration

```yaml
# config/reproducibility.yaml
reproducibility:
  seed: 42
  deterministic: true
  
  environment:
    save_snapshot: true
    verify_on_load: true
    snapshot_path: experiments/environment.json
  
  code:
    require_clean_git: false
    log_git_diff: true
    
  data:
    hash_datasets: true
    track_transforms: true
```

## Usage Examples

### Example 1: Basic Reproducible Training

```python
from reproducibility import set_seed, save_environment

# Set seed at start of training
SEED = 42
set_seed(SEED, deterministic=True)

# Save environment
save_environment("experiments/env.json")

# Training will now be reproducible
model = train_model(config)
```

### Example 2: Complete Reproducibility Context

```python
from contextlib import contextmanager
from pathlib import Path
import json

@contextmanager
def reproducible_context(
    seed: int,
    output_dir: str,
    deterministic: bool = True
):
    """
    Context manager for reproducible experiments.
    
    Safeguard: Captures and restores state.
    """
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    
    # Set seeds
    set_seed(seed, deterministic=deterministic)
    
    # Capture environment
    env = capture_environment()
    (out_path / "environment.json").write_text(json.dumps(env, indent=2))
    
    # Capture random state
    initial_state = get_random_state()
    
    try:
        yield
    finally:
        # Save final random state for continuation
        final_state = get_random_state()
        # Could save this for later restoration

# Usage
with reproducible_context(seed=42, output_dir="experiments/run1"):
    model = train_model(config)
    save_model(model, "experiments/run1/model.pt")
```

### Example 3: Data Hashing

```python
import hashlib
from typing import Union
import numpy as np

def hash_data(data: Union[np.ndarray, list, str]) -> str:
    """
    Compute deterministic hash of data.
    
    Safeguard: Handles different data types.
    Deterministic: Same data always produces same hash.
    """
    if isinstance(data, np.ndarray):
        # Convert to bytes deterministically
        data_bytes = data.tobytes()
    elif isinstance(data, list):
        data_bytes = str(data).encode()
    elif isinstance(data, str):
        data_bytes = data.encode()
    else:
        raise TypeError(f"Unsupported type: {type(data)}")
    
    return hashlib.sha256(data_bytes).hexdigest()[:16]

def verify_dataset(dataset, expected_hash: str) -> bool:
    """
    Verify dataset matches expected hash.
    
    Safeguard: Ensures data hasn't changed.
    """
    # Convert dataset to array for hashing
    if hasattr(dataset, 'data'):
        data = dataset.data
    elif hasattr(dataset, '__array__'):
        data = np.array(dataset)
    else:
        data = list(dataset)
    
    actual_hash = hash_data(data)
    return actual_hash == expected_hash

# Example: Hash dataset and log
train_hash = hash_data(train_data)
print(f"Training data hash: {train_hash}")
```

### Example 4: Checkpoint with Full State

```python
def save_reproducible_checkpoint(
    path: str,
    model,
    optimizer,
    epoch: int,
    config: dict,
) -> None:
    """
    Save checkpoint with complete reproducibility info.
    
    Safeguard: Captures all necessary state.
    """
    checkpoint = {
        # Model state
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        
        # Training progress
        "epoch": epoch,
        
        # Configuration
        "config": config,
        
        # Reproducibility
        "random_state": get_random_state(),
        "environment": capture_environment(),
    }
    
    torch.save(checkpoint, path)

def load_reproducible_checkpoint(path: str, model, optimizer):
    """
    Load checkpoint and restore reproducibility state.
    
    Safeguard: Validates checkpoint structure.
    """
    checkpoint = torch.load(path)
    
    # Restore model
    model.load_state_dict(checkpoint["model_state_dict"])
    optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
    
    # Restore random state
    if "random_state" in checkpoint:
        set_random_state(checkpoint["random_state"])
    
    # Verify environment
    if "environment" in checkpoint:
        expected_env = checkpoint["environment"]
        current_env = capture_environment()
        
        if expected_env.get("torch_version") != current_env.get("torch_version"):
            print(f"Warning: PyTorch version mismatch")
    
    return checkpoint["epoch"], checkpoint.get("config", {})
```

### Example 5: Reproducibility Report

```python
def generate_reproducibility_report(output_dir: str) -> str:
    """
    Generate comprehensive reproducibility report.
    
    Safeguard: Validates all paths exist.
    """
    out_path = Path(output_dir)
    report = []
    
    report.append("# Reproducibility Report\n")
    report.append(f"Generated: {datetime.datetime.now().isoformat()}\n")
    
    # Environment
    env_file = out_path / "environment.json"
    if env_file.exists():
        env = json.loads(env_file.read_text())
        report.append("\n## Environment\n")
        report.append(f"- Python: {env.get('python_version', 'unknown')}")
        report.append(f"- PyTorch: {env.get('torch_version', 'unknown')}")
        report.append(f"- Git Hash: {env.get('git_hash', 'unknown')}")
        report.append(f"- Git Dirty: {env.get('git_dirty', 'unknown')}")
    
    # Configuration
    config_file = out_path / "config.yaml"
    if config_file.exists():
        report.append("\n## Configuration\n")
        report.append("```yaml")
        report.append(config_file.read_text())
        report.append("```")
    
    # Instructions to reproduce
    report.append("\n## How to Reproduce\n")
    report.append("```bash")
    report.append("# Clone repository at specific commit")
    if env_file.exists():
        env = json.loads(env_file.read_text())
        report.append(f"git checkout {env.get('git_hash', 'main')}")
    report.append("")
    report.append("# Install dependencies")
    report.append("pip install -r requirements.txt")
    report.append("")
    report.append("# Run training with same seed")
    report.append("python train.py --seed 42 --config config.yaml")
    report.append("```")
    
    return "\n".join(report)
```

## Safeguards

### Determinism Validation

```python
def validate_determinism(fn, *args, num_runs: int = 3) -> bool:
    """
    Validate function produces deterministic results.
    
    Safeguard: Tests multiple runs for consistency.
    """
    results = []
    
    for _ in range(num_runs):
        set_seed(42)
        result = fn(*args)
        
        if isinstance(result, torch.Tensor):
            result = result.detach().cpu().numpy().tolist()
        
        results.append(result)
    
    # All results should be identical
    return all(r == results[0] for r in results)
```

### Git State Validation

```python
def require_clean_git() -> None:
    """
    Require clean git state for reproducibility.
    
    Safeguard: Prevents experiments with uncommitted changes.
    """
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.stdout.strip():
            raise RuntimeError(
                "Uncommitted changes detected. "
                "Commit or stash changes before running experiments."
            )
    except FileNotFoundError:
        raise RuntimeError("Git not found. Cannot verify clean state.")
```

## Best Practices

1. **Set Seed Early**: Set random seed before any random operations
2. **Use Deterministic Mode**: Enable PyTorch deterministic mode
3. **Version Everything**: Code, data, environment, config
4. **Document Dependencies**: Use requirements.txt or pyproject.toml
5. **Hash Data**: Compute and log dataset hashes
6. **Save Full State**: Include random state in checkpoints
7. **Test Reproducibility**: Run experiments twice to verify
8. **Clean Git**: Commit before experiments

## Troubleshooting

### Non-deterministic Results

```python
# Check CUDA determinism
print(f"cudnn.deterministic: {torch.backends.cudnn.deterministic}")
print(f"cudnn.benchmark: {torch.backends.cudnn.benchmark}")

# Force deterministic
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False
```

### Missing Dependencies

```bash
# Generate requirements
pip freeze > requirements.txt

# Or with exact versions
pip freeze --all > requirements-exact.txt
```

## Related Capabilities

- [Experiment Management](experiment_management.md) - Track experiments
- [Checkpointing](checkpointing.md) - Save training state
- [Configuration](configuration.md) - Manage configs

## References

- PyTorch Reproducibility: https://pytorch.org/docs/stable/notes/randomness.html
- NumPy Random: https://numpy.org/doc/stable/reference/random/index.html
