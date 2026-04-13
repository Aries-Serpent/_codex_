#!/usr/bin/env bash
# examples/run_demo.sh — quick smoke-test of the restore_pipeline CLI
#
# Usage: bash examples/run_demo.sh
# Requirements: restore_pipeline and its dependencies must be installed.
#   pip install scikit-image opencv-python bm3d imageio Pillow onnxruntime numpy

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

export PYTHONPATH="$REPO_ROOT/src:${PYTHONPATH:-}"

INPUT_PATH="/tmp/restore_demo_input.png"
OUTPUT_DIR="/tmp/restore_demo_output"

echo "── restore_pipeline demo ─────────────────────────────────────"
echo "Repo root: $REPO_ROOT"

# ── Create a synthetic noisy test image with Python/skimage ──────────────────
python3 - <<'EOF'
import numpy as np
from skimage.util import random_noise
import imageio.v3 as iio
from pathlib import Path

rng = np.random.default_rng(42)
# Create a simple synthetic colour image (64x64 gradient + shapes)
img = np.zeros((128, 128, 3), dtype=np.float32)
img[..., 0] = np.linspace(0.1, 0.9, 128).reshape(1, -1)   # Red gradient
img[..., 1] = np.linspace(0.2, 0.8, 128).reshape(-1, 1)   # Green gradient
img[..., 2] = 0.5

# Add Gaussian noise
noisy = random_noise(img, mode="gaussian", var=0.01**2, rng=42).astype(np.float32)
noisy_u8 = (np.clip(noisy, 0, 1) * 255).astype("uint8")

Path("/tmp/restore_demo_input.png").parent.mkdir(parents=True, exist_ok=True)
iio.imwrite("/tmp/restore_demo_input.png", noisy_u8)
print(f"Synthetic noisy image written → /tmp/restore_demo_input.png  shape={noisy_u8.shape}")
EOF

echo ""
echo "── Running restore pipeline CLI ─────────────────────────────"
python3 -m restore_pipeline.cli \
    --input  "$INPUT_PATH" \
    --output "$OUTPUT_DIR" \
    --algorithm nl_means \
    --verbose

echo ""
echo "── Output files ─────────────────────────────────────────────"
ls -lh "$OUTPUT_DIR"

echo ""
echo "Done! ✅  Restored image is at $OUTPUT_DIR"
