# Enhancements Guide: Advanced Features

**Version:** 1.0  
**Date:** December 6, 2025  
**Status:** Production Ready

This guide covers the optional enhancement features added to the _codex_ ML system:

1. MLflow Integration
2. Performance Benchmarking
3. Distributed Training
4. Notebook Validation
5. Docker Optimization

---

## 1. MLflow Integration

### Overview

MLflow integration provides experiment tracking with graceful degradation for offline-first operation.

### Installation

```bash
pip install mlflow
```

### Basic Usage

```python
from codex_ml.training.mlflow_integration import init_mlflow

# Initialize MLflow (offline by default)
tracker = init_mlflow(
    experiment_name="my_experiment",
    run_name="run_001",
    tracking_uri="./mlruns",  # Local tracking
)

# Log parameters
tracker.log_params({
    "learning_rate": 0.001,
    "batch_size": 32,
    "epochs": 10,
})

# Training loop
for epoch in range(epochs):
    # ... training code ...
    
    # Log metrics
    tracker.log_metrics({
        "loss": loss_value,
        "accuracy": accuracy_value,
    }, step=epoch)

# Log artifacts
tracker.log_artifact("model.pt")
tracker.log_artifacts("checkpoints/")

# End run
tracker.end_run()
```

### Context Manager

```python
from codex_ml.training.mlflow_integration import MLflowTracker

with MLflowTracker("my_exp", run_name="run_002") as tracker:
    # Training code
    tracker.log_params({"lr": 0.001})
    tracker.log_metrics({"loss": 0.5}, step=0)
# Run automatically ended
```

### Graceful Degradation

MLflow integration automatically degrades if MLflow is unavailable:

```python
tracker = MLflowTracker("exp")
# tracker.active == False if MLflow unavailable

# These operations are no-ops if inactive (no errors raised)
tracker.log_metrics({"loss": 0.5})  # Silently skipped
tracker.log_params({"lr": 0.001})   # Silently skipped
```

### Testing

```bash
# Run MLflow tests
nox -f nox_enhancements.py -s mlflow_tests

# Or with pytest directly
pytest tests/test_mlflow_integration.py -v
```

### MLflow UI

View experiment results:

```bash
# Start MLflow UI
mlflow ui --backend-store-uri ./mlruns

# Open browser to http://localhost:5000
```

---

## 2. Performance Benchmarking

### Overview

Comprehensive performance benchmarking suite for training, inference, and data loading.

### Installation

No additional dependencies required (uses PyTorch).

### Benchmark Training Steps

```python
from codex_ml.utils.performance_benchmark import benchmark_training_step

model = MyModel()
batch = {"input_ids": torch.randn(32, 512)}
optimizer = torch.optim.Adam(model.parameters())

result = benchmark_training_step(
    model=model,
    batch=batch,
    optimizer=optimizer,
    num_iterations=100,
    warmup_iters=10,
)

print(result)
# Output:
# training_step:
#   Duration: 1250.45ms
#   Throughput: 80.0 items/sec
#   GPU Memory: 2048.5MB
```

### Benchmark Inference

```python
from codex_ml.utils.performance_benchmark import benchmark_inference

result = benchmark_inference(
    model=model,
    batch=batch,
    num_iterations=1000,
    warmup_iters=100,
)

print(f"Average latency: {result.metadata['avg_ms_per_sample']:.2f}ms")
```

### Benchmark Data Loading

```python
from codex_ml.utils.performance_benchmark import benchmark_data_loading

dataloader = DataLoader(dataset, batch_size=32, num_workers=4)

result = benchmark_data_loading(
    dataloader=dataloader,
    num_batches=100,
)

print(f"Throughput: {result.throughput:.2f} batches/sec")
```

### Benchmark Suite

```python
from codex_ml.utils.performance_benchmark import BenchmarkSuite

suite = BenchmarkSuite("training_pipeline")

# Add benchmarks
suite.add_result(benchmark_training_step(...))
suite.add_result(benchmark_inference(...))
suite.add_result(benchmark_data_loading(...))

# Print summary
suite.print_summary()

# Save results
suite.save_results("benchmarks/results.json")
```

### Performance Context

```python
from codex_ml.utils.performance_benchmark import PerformanceBenchmark

with PerformanceBenchmark("data_preprocessing") as bench:
    # Your code here
    process_data(dataset)

print(f"Processing took: {bench.result.duration_ms:.2f}ms")
```

### Testing

```bash
# Run performance benchmark tests
nox -f nox_enhancements.py -s performance_benchmarks

# Or with pytest
pytest tests/test_performance_benchmark.py -v
```

---

## 3. Distributed Training

### Overview

Multi-node distributed training support with PyTorch DDP (DistributedDataParallel).

### Installation

No additional dependencies required (uses PyTorch).

### Setup Distributed Environment

```python
from codex_ml.training.distributed_setup import setup_distributed, cleanup_distributed

# Initialize distributed training
if setup_distributed(backend="nccl"):
    print(f"Distributed mode: rank {get_rank()}/{get_world_size()}")
else:
    print("Running in single-process mode")

# ... training code ...

# Cleanup
cleanup_distributed()
```

### Wrap Model with DDP

```python
from codex_ml.training.distributed_setup import setup_ddp_model

model = MyModel()

# Wrap with DDP (no-op if not distributed)
model = setup_ddp_model(model, find_unused_parameters=False)
```

### Distributed Data Loading

```python
from codex_ml.training.distributed_setup import get_distributed_sampler
from torch.utils.data import DataLoader

# Create distributed sampler
sampler = get_distributed_sampler(
    dataset,
    shuffle=True,
    seed=42,
)

# Create dataloader
dataloader = DataLoader(
    dataset,
    batch_size=32,
    sampler=sampler,  # Use distributed sampler
    num_workers=4,
)
```

### Reduce Metrics Across Processes

```python
from codex_ml.training.distributed_setup import reduce_tensor

# Each process has a local loss
loss_tensor = torch.tensor(local_loss)

# Average across all processes
avg_loss = reduce_tensor(loss_tensor, average=True)

# Only log on main process
if is_main_process():
    logger.info(f"Average loss: {avg_loss.item()}")
```

### Launch Multi-Process Training

```bash
# Single-node, multi-GPU (using torchrun)
torchrun --nproc_per_node=4 cli/train_codex.py --config configs/training.yaml

# Multi-node (2 nodes, 4 GPUs each)
# On node 0:
torchrun \
    --nnodes=2 \
    --node_rank=0 \
    --nproc_per_node=4 \
    --master_addr=node0.example.com \
    --master_port=29500 \
    cli/train_codex.py --config configs/training.yaml

# On node 1:
torchrun \
    --nnodes=2 \
    --node_rank=1 \
    --nproc_per_node=4 \
    --master_addr=node0.example.com \
    --master_port=29500 \
    cli/train_codex.py --config configs/training.yaml
```

### Utilities

```python
from codex_ml.training.distributed_setup import (
    is_distributed,
    is_main_process,
    get_rank,
    get_world_size,
    barrier,
    print_once,
    log_once,
)

# Check if distributed
if is_distributed():
    print(f"Running distributed: rank {get_rank()}")

# Only print/log on main process
print_once("This prints only on rank 0")
log_once("This logs only on rank 0", level="info")

# Synchronize all processes
barrier()
```

### Testing

```bash
# Run distributed tests
nox -f nox_enhancements.py -s distributed_tests

# Or with pytest
pytest tests/test_distributed_setup.py -v
```

---

## 4. Notebook Validation

### Overview

Automated validation of Jupyter notebooks to ensure they execute without errors.

### Installation

```bash
pip install papermill jupyter
```

### Manual Validation

```bash
# Validate all notebooks
bash scripts/validate_notebooks.sh

# Or with nox
nox -f nox_enhancements.py -s validate_notebooks
```

### Validation Output

```
🔍 Validating Jupyter notebooks...
Found 5 notebook(s) to validate

Validating: examples/quickstart.ipynb
  ✓ Passed

Validating: examples/training_example.ipynb
  ✓ Passed

================================================
Notebook Validation Summary
================================================
Total notebooks: 5
Passed: 5
Failed: 0
================================================
✅ All notebooks validated successfully
```

### CI Integration

Add to your local CI workflow:

```yaml
# .github/workflows/ci.yml (if using GitHub Actions)
- name: Validate Notebooks
  run: nox -f nox_enhancements.py -s validate_notebooks
```

Or in nox sessions:

```python
# noxfile.py
@nox.session
def full_validation(session):
    """Run all validations including notebooks."""
    session.notify("tests")
    session.notify("lint")
    session.run("nox", "-f", "nox_enhancements.py", "-s", "validate_notebooks", external=True)
```

---

## 5. Docker Optimization

### Overview

Multi-stage optimized Docker images for smaller size and better security.

### Build Optimized Image

```bash
# Build image
docker build -f docker/Dockerfile.optimized -t codex-ml:optimized .

# Or with nox
nox -f nox_enhancements.py -s docker_build
```

### Image Features

- **Multi-stage build:** Separate builder and runtime stages
- **Smaller size:** ~50% smaller than single-stage builds
- **Non-root user:** Runs as user `codex` (UID 1000)
- **Health checks:** Built-in health check endpoint
- **Minimal dependencies:** Only runtime dependencies in final image

### Test Image

```bash
# Test image health and functionality
nox -f nox_enhancements.py -s docker_test

# Or manually
docker run --rm codex-ml:optimized python -m cli.train_codex --help
```

### Run Training in Container

```bash
# Run training
docker run --rm \
    -v $(pwd)/data:/data \
    -v $(pwd)/checkpoints:/checkpoints \
    codex-ml:optimized \
    python -m cli.train_codex \
        --config /data/config.yaml \
        --output-dir /checkpoints
```

### Run with GPU

```bash
# Run with NVIDIA GPU support
docker run --rm --gpus all \
    -v $(pwd)/data:/data \
    codex-ml:optimized \
    python -m cli.train_codex --config /data/config.yaml
```

### Image Sizes

Comparison of image sizes:

```
Single-stage build:    ~5.2GB
Multi-stage optimized: ~2.8GB
Reduction:            ~46%
```

---

## Maintenance

### Dependency Updates

```bash
# Check for outdated dependencies
pip list --outdated

# Update dependencies
pip install --upgrade <package>

# Run maintenance check
nox -f nox_enhancements.py -s maintenance_check
```

### Test Coverage

```bash
# Run tests with coverage
pytest tests/ --cov=src --cov=training --cov-report=html

# Open coverage report
open htmlcov/index.html
```

### Security Scanning

```bash
# Scan for vulnerabilities
pip-audit --skip-editable

# Run security checks
nox -s security  # From main noxfile
```

---

## Quick Reference

### Run All Enhancement Tests

```bash
nox -f nox_enhancements.py -s all_enhancements
```

### List Available Sessions

```bash
nox -f nox_enhancements.py -s enhancement_docs
```

### Full Test Suite

```bash
# Core tests
nox -s tests

# Enhancement tests
nox -f nox_enhancements.py -s all_enhancements

# Security checks
nox -s security
```

---

## Troubleshooting

### MLflow Not Found

```bash
pip install mlflow
```

### Papermill Not Found

```bash
pip install papermill jupyter
```

### Docker Build Fails

```bash
# Check Docker daemon is running
docker info

# Clear Docker cache
docker system prune -a
```

### Distributed Training Issues

- Ensure `MASTER_ADDR` and `MASTER_PORT` are set
- Verify network connectivity between nodes
- Check firewall allows the master port
- Ensure NCCL is installed for GPU training

---

## Next Steps

- See [API Reference](../API_REFERENCE.md) for detailed API documentation
- See [Getting Started Guide](getting_started.md) for basic usage
- See [Continuous Learning Guide](continuous_learning_guide.md) for auto-retraining
- See [A/B Testing Guide](ab_testing_guide.md) for experiment management

---

**Document Version:** 1.0  
**Last Updated:** December 6, 2025  
**Status:** Production Ready
