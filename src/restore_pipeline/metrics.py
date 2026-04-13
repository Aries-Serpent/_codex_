"""PSNR and SSIM metrics (scikit-image)."""

from __future__ import annotations

import logging

import numpy as np

logger = logging.getLogger(__name__)


def psnr(reference: np.ndarray, degraded: np.ndarray) -> float:
    """Peak Signal-to-Noise Ratio between *reference* and *degraded*.

    Both arrays must be float32 in [0, 1] with identical shape.

    Returns
    -------
    float
        PSNR in dB.  Returns 100.0 for identical images (infinite / undefined).
    """
    mse = float(np.mean((reference.astype(np.float64) - degraded.astype(np.float64)) ** 2))
    if mse == 0.0:
        return 100.0  # identical images → cap at 100 dB
    from skimage.metrics import peak_signal_noise_ratio

    return float(peak_signal_noise_ratio(reference, degraded, data_range=1.0))


def ssim(reference: np.ndarray, degraded: np.ndarray) -> float:
    """Structural Similarity Index Measure.

    Parameters
    ----------
    reference, degraded:
        Float32 arrays in [0, 1], shape ``(H, W, 3)`` or ``(H, W)``.

    Returns
    -------
    float
        SSIM ∈ [−1, 1]; higher is better.
    """
    from skimage.metrics import structural_similarity

    channel_axis = 2 if reference.ndim == 3 else None
    return float(
        structural_similarity(reference, degraded, data_range=1.0, channel_axis=channel_axis)
    )


def compute_all(
    reference: np.ndarray,
    restored: np.ndarray,
    *,
    degraded: np.ndarray | None = None,
) -> dict[str, float]:
    """Compute PSNR and SSIM for both restored→reference and (optionally) degraded→reference.

    Returns a flat dict with keys like ``psnr_restored``, ``ssim_restored``,
    ``psnr_degraded``, ``ssim_degraded``.
    """
    metrics: dict[str, float] = {}

    metrics["psnr_restored"] = psnr(reference, restored)
    metrics["ssim_restored"] = ssim(reference, restored)

    if degraded is not None:
        metrics["psnr_degraded"] = psnr(reference, degraded)
        metrics["ssim_degraded"] = ssim(reference, degraded)
        metrics["psnr_improvement"] = metrics["psnr_restored"] - metrics["psnr_degraded"]
        metrics["ssim_improvement"] = metrics["ssim_restored"] - metrics["ssim_degraded"]

    for k, v in metrics.items():
        logger.info("  %-25s %+.4f", k, v)

    return metrics
