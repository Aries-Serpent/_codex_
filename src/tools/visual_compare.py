#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

try:
    from PIL import Image
except Exception:  # pragma: no cover
    Image = None  # type: ignore

try:
    import numpy as np
except Exception:  # pragma: no cover
    np = None  # type: ignore

# Optional SSIM from scikit-image if available
try:
    from skimage.metrics import structural_similarity as ssim  # type: ignore
except Exception:  # pragma: no cover
    ssim = None  # type: ignore

# Maximum pixel value for 8-bit grayscale images
MAX_PIXEL_VALUE = 255.0


def load_gray(path: Path):
    if Image is None:
        raise RuntimeError("Pillow not installed; pip install pillow")
    return Image.open(path).convert("L")


def to_array(img) -> "np.ndarray":
    if np is None:
        raise RuntimeError("numpy not installed; pip install numpy")
    return np.asarray(img, dtype=np.float32)


def resize_to_match(a, b) -> tuple["np.ndarray", "np.ndarray"]:
    # Resize b to a's size if different
    if a.shape == b.shape:
        return a, b
    if Image is None:
        raise RuntimeError("Pillow not installed; pip install pillow")
    h, w = a.shape
    b_img = Image.fromarray(b.astype("uint8"), mode="L").resize((w, h))
    return a, to_array(b_img)


def metric_ssim(a: "np.ndarray", b: "np.ndarray") -> float:
    if ssim is not None:
        return float(ssim(a, b, data_range=MAX_PIXEL_VALUE))
    # Fallback: 1 - normalized MSE in [0,1]; crude proxy
    mse = float(((a - b) ** 2).mean())
    nmse = min(1.0, mse / (MAX_PIXEL_VALUE**2))
    return max(0.0, 1.0 - nmse)


def compare(baseline: Path, candidate: Path, metric: str = "ssim") -> float:
    a = to_array(load_gray(baseline))
    b = to_array(load_gray(candidate))
    a, b = resize_to_match(a, b)
    if metric.lower() == "ssim":
        return metric_ssim(a, b)
    if metric.lower() == "mse":
        # Return similarity-like score from MSE
        mse = float(((a - b) ** 2).mean())
        nmse = min(1.0, mse / (MAX_PIXEL_VALUE**2))
        return max(0.0, 1.0 - nmse)
    raise ValueError(f"Unknown metric: {metric}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Compare two images and output similarity score (SSIM or MSE-based)."
    )
    ap.add_argument("--baseline", required=True, help="Path to baseline image (PNG)")
    ap.add_argument("--candidate", required=True, help="Path to candidate image (PNG)")
    ap.add_argument("--metric", default="ssim", choices=["ssim", "mse"])
    ap.add_argument("--threshold", type=float, default=0.98, help="Pass if similarity >= threshold")
    args = ap.parse_args(argv)

    sim = compare(Path(args.baseline), Path(args.candidate), args.metric)
    print(f'{{"metric":"{args.metric}","similarity":{sim:.6f},"threshold":{args.threshold}}}')
    return 0 if sim >= args.threshold else 1


if __name__ == "__main__":
    raise SystemExit(main())
