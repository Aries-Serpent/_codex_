# GPU Docker Build Guide

This guide explains how to build and run the GPU-enabled Docker image for codex-ml with opt-in CUDA PyTorch installation.

## Overview

The `Dockerfile.gpu` provides an optional mechanism to install CUDA-enabled PyTorch in the container. By default, the image does NOT install GPU-specific PyTorch wheels to keep the image flexible for different deployment scenarios.

**Base Image**: `nvidia/cuda:12.2.2-cudnn8-runtime-ubuntu22.04`

**Default Torch Channel**: CUDA 12.1 (compatible with CUDA 12.2 runtime)

## Build Options

### Option 1: Default Build (No GPU PyTorch)

Build the image without GPU-specific PyTorch installation. This creates a smaller image that can install torch from requirements:

```bash
docker build -f Dockerfile.gpu -t codex-gpu:local .
```text

Or use the helper script:

```bash
./scripts/packaging/build_docker.sh codex-gpu:local
```text

### Option 2: With CUDA 12.1 PyTorch (Recommended)

Build with the default CUDA 12.1 compatible PyTorch wheels:

```bash
docker build -f Dockerfile.gpu -t codex-gpu:cu121 \
  --build-arg INSTALL_TORCH_GPU=1 \
  .
```text

Or use the helper script:

```bash
INSTALL_TORCH_GPU=1 ./scripts/packaging/build_docker.sh codex-gpu:cu121
```text

**Installed Versions**:
- `torch==2.4.0+cu121`
- `torchvision==0.19.0+cu121`

### Option 3: Custom PyTorch Wheel

Specify a custom PyTorch installation command:

```bash
docker build -f Dockerfile.gpu -t codex-gpu:custom \
  --build-arg INSTALL_TORCH_GPU=1 \
  --build-arg TORCH_WHEEL="torch==2.5.0+cu124 --extra-index-url https://download.pytorch.org/whl/cu124" \
  .
```text

Or use the helper script:

```bash
INSTALL_TORCH_GPU=1 \
TORCH_WHEEL="torch==2.5.0+cu124 --extra-index-url https://download.pytorch.org/whl/cu124" \
./scripts/packaging/build_docker.sh codex-gpu:custom
```text

## Verifying GPU Support

After building, verify CUDA availability:

```bash
docker run --rm codex-gpu:cu121 \
  python -c "import torch; print('CUDA available:', torch.cuda.is_available())"
```text

**Expected Output**:
- With GPU build args: `CUDA available: False` (no GPU in container, but library installed)
- With `--gpus all` and NVIDIA runtime: `CUDA available: True`

## Running the Container

### CPU-only Mode

```bash
docker run --rm -p 8000:8000 codex-gpu:cu121
```text

### GPU Mode (Requires NVIDIA Container Toolkit)

```bash
docker run --rm --gpus all -p 8000:8000 codex-gpu:cu121
```text

To use specific GPUs:

```bash
docker run --rm --gpus '"device=0,1"' -p 8000:8000 codex-gpu:cu121
```text

## Prerequisites

### For Building

- Docker with BuildKit support
- Sufficient disk space (~5-8 GB for GPU image)

### For GPU Runtime

1. **NVIDIA GPU** with CUDA support
2. **NVIDIA Driver** compatible with CUDA 12.1+ (recommended: 520.61.05 or newer)
3. **NVIDIA Container Toolkit** installed on the host

Install NVIDIA Container Toolkit:

```bash
# Ubuntu/Debian
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```text

Verify installation:

```bash
docker run --rm --gpus all nvidia/cuda:12.2.2-base-ubuntu22.04 nvidia-smi
```text

## Smoke Test

Quick verification that the image works:

```bash
# Check Python and package imports
docker run --rm codex-gpu:cu121 python -c "
import torch
import transformers
import peft
print('✓ All imports successful')
print(f'PyTorch version: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'CUDA version: {torch.version.cuda}')
    print(f'GPU count: {torch.cuda.device_count()}')
"
```text

## CUDA Version Compatibility

| Base Image CUDA | Compatible PyTorch CUDA | Notes |
|-----------------|------------------------|-------|
| 12.2.2 | 12.1 | Recommended (backward compatible) |
| 12.2.2 | 12.2 | Phase 5 require newer wheels |
| 12.2.2 | 11.8 | Not recommended (older CUDA) |

PyTorch CUDA wheels are forward-compatible with newer CUDA runtimes, so CUDA 12.1 wheels work with CUDA 12.2 runtime.

## Image Size Considerations

- **Base image**: ~2.5 GB (nvidia/cuda:12.2.2-cudnn8-runtime)
- **With PyTorch+CUDA**: +2-3 GB
- **Total GPU image**: ~5-8 GB

To reduce size:
- Use multi-stage builds (already implemented)
- Avoid installing development headers (runtime image only)
- Clean package manager caches (already done with `rm -rf /var/lib/apt/lists/*`)

## Troubleshooting

### "CUDA available: False" in Container

**Possible causes**:
1. NVIDIA Container Toolkit not installed on host
2. Container not started with `--gpus all` flag
3. GPU drivers not compatible with CUDA version

**Solution**:
```bash
# Verify host can see GPU
nvidia-smi

# Verify Docker can access GPU
docker run --rm --gpus all nvidia/cuda:12.2.2-base-ubuntu22.04 nvidia-smi

# Run container with GPU access
docker run --rm --gpus all codex-gpu:cu121 python -c "import torch; print(torch.cuda.is_available())"
```text

### Torch Import Errors

**Error**: `ImportError: cannot import name '_C' from 'torch'`

**Cause**: Mismatched torch versions or incomplete installation

**Solution**: Rebuild with clean cache:
```bash
docker build --no-cache -f Dockerfile.gpu \
  --build-arg INSTALL_TORCH_GPU=1 \
  -t codex-gpu:cu121 .
```text

### Wheel Compatibility Issues

**Error**: `Could not find a version that satisfies the requirement torch==...`

**Cause**: Requested torch version not available for specified CUDA version

**Solution**: Check available wheels at https://download.pytorch.org/whl/torch/

Example for CUDA 12.1:
```bash
# List available wheels
curl -s https://download.pytorch.org/whl/cu121/torch/ | grep -o 'torch-[0-9.]*+cu121'
```text

## Build Args Reference

| Argument | Default | Description |
|----------|---------|-------------|
| `VERSION` | `0.0.0` | Package version for OCI labels |
| `VCS_REF` | `unknown` | Git commit SHA for OCI labels |
| `BUILD_DATE` | `unknown` | Build timestamp for OCI labels |
| `VCS_URL` | `https://github.com/Aries-Serpent/_codex_` | Repository URL |
| `INSTALL_TORCH_GPU` | `0` | Set to `1` to install CUDA PyTorch |
| `TORCH_WHEEL` | `""` | Custom torch install command (requires `INSTALL_TORCH_GPU=1`) |

## Advanced Usage

### Custom Torch Installation

For specific torch configuration:

```dockerfile
# Example: Installing specific torch with custom flags
--build-arg INSTALL_TORCH_GPU=1 \
--build-arg TORCH_WHEEL="torch==2.4.1+cu121 torchvision==0.19.1+cu121 --extra-index-url https://download.pytorch.org/whl/cu121"
```text

### Multi-Architecture Builds

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -f Dockerfile.gpu \
  --build-arg INSTALL_TORCH_GPU=1 \
  -t codex-gpu:cu121 \
  --push \
  .
```text

Note: GPU images are typically amd64 only due to NVIDIA CUDA requirements.

## See Also

- [Docker Guide](../docker.md) - General Docker documentation
- [Packaging Guide](packaging.md) - Python wheel packaging
- [Deployment Checklist](deployment_checklist.md) - Pre-deployment validation
- [NVIDIA Container Toolkit Docs](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)
