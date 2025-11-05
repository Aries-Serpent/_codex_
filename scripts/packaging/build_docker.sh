#!/usr/bin/env bash
# Build Docker image with optional GPU support
# Usage:
#   ./build_docker.sh [image_tag]
#   INSTALL_TORCH_GPU=1 ./build_docker.sh codex-gpu:cu121
#   TORCH_WHEEL="torch==2.4.0+cu121 --extra-index-url https://download.pytorch.org/whl/cu121" ./build_docker.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Default values
IMAGE_TAG="${1:-codex-gpu:local}"
INSTALL_TORCH_GPU="${INSTALL_TORCH_GPU:-0}"
TORCH_WHEEL="${TORCH_WHEEL:-}"

echo "==> Building Docker image"
echo "Image tag: ${IMAGE_TAG}"
echo "Install GPU PyTorch: ${INSTALL_TORCH_GPU}"
echo "Custom torch wheel: ${TORCH_WHEEL:-<none>}"

cd "${REPO_ROOT}"

# Build command
BUILD_CMD="docker build -f Dockerfile.gpu -t ${IMAGE_TAG}"

# Add build args
BUILD_CMD="${BUILD_CMD} --build-arg INSTALL_TORCH_GPU=${INSTALL_TORCH_GPU}"

if [ -n "${TORCH_WHEEL}" ]; then
    BUILD_CMD="${BUILD_CMD} --build-arg TORCH_WHEEL=${TORCH_WHEEL}"
fi

# Add metadata build args
if command -v git &> /dev/null; then
    VERSION="$(git describe --tags --always --dirty=+ 2>/dev/null || echo 'unknown')"
    VCS_REF="$(git rev-parse --short=12 HEAD 2>/dev/null || echo 'unknown')"
    BUILD_CMD="${BUILD_CMD} --build-arg VERSION=${VERSION}"
    BUILD_CMD="${BUILD_CMD} --build-arg VCS_REF=${VCS_REF}"
fi

BUILD_DATE="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
BUILD_CMD="${BUILD_CMD} --build-arg BUILD_DATE=${BUILD_DATE}"

# Add repo root context
BUILD_CMD="${BUILD_CMD} ."

echo "==> Running: ${BUILD_CMD}"
eval "${BUILD_CMD}"

echo ""
echo "==> Build complete: ${IMAGE_TAG}"
echo ""
echo "Verify GPU support with:"
echo "  docker run --rm ${IMAGE_TAG} python -c \"import torch; print('CUDA available:', torch.cuda.is_available())\""
echo ""
echo "Run container with:"
echo "  docker run --rm -p 8000:8000 ${IMAGE_TAG}"
echo "  # Or with GPU:"
echo "  docker run --rm --gpus all -p 8000:8000 ${IMAGE_TAG}"
