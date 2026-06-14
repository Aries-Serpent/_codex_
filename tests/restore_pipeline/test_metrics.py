"""Tests for restore_pipeline.metrics — psnr, ssim, compute_all."""

from __future__ import annotations

import numpy as np
import pytest

from restore_pipeline.metrics import compute_all, psnr, ssim

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _rand_image(seed: int = 0, shape=(16, 16, 3)) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.random(shape).astype(np.float32)


# ---------------------------------------------------------------------------
# psnr
# ---------------------------------------------------------------------------


def test_psnr_identical_images_returns_100():
    img = _rand_image(1)
    result = psnr(img, img)
    assert result == pytest.approx(100.0)


def test_psnr_different_images_returns_finite_positive():
    ref = _rand_image(1)
    deg = _rand_image(2)
    result = psnr(ref, deg)
    assert result > 0.0
    assert result < 100.0


def test_psnr_higher_for_less_noisy():
    ref = _rand_image(1)
    slightly_noisy = ref + np.float32(0.01) * _rand_image(3)
    very_noisy = ref + np.float32(0.3) * _rand_image(4)
    np.clip(slightly_noisy, 0, 1, out=slightly_noisy)
    np.clip(very_noisy, 0, 1, out=very_noisy)
    assert psnr(ref, slightly_noisy) > psnr(ref, very_noisy)


def test_psnr_symmetric_ish():
    """PSNR is defined from reference perspective; values should be close both ways."""
    ref = _rand_image(1)
    deg = _rand_image(2)
    # Not strictly symmetric but both should be positive
    assert psnr(ref, deg) > 0
    assert psnr(deg, ref) > 0


# ---------------------------------------------------------------------------
# ssim
# ---------------------------------------------------------------------------


def test_ssim_identical_images_returns_one():
    img = _rand_image(1)
    result = ssim(img, img)
    assert result == pytest.approx(1.0, abs=1e-5)


def test_ssim_different_images_below_one():
    ref = _rand_image(1)
    deg = _rand_image(2)
    result = ssim(ref, deg)
    assert result < 1.0


def test_ssim_range_valid():
    ref = _rand_image(1)
    deg = _rand_image(2)
    result = ssim(ref, deg)
    assert -1.0 <= result <= 1.0


def test_ssim_works_on_grayscale():
    rng = np.random.default_rng(5)
    img = rng.random((16, 16)).astype(np.float32)
    result = ssim(img, img)
    assert result == pytest.approx(1.0, abs=1e-5)


# ---------------------------------------------------------------------------
# compute_all
# ---------------------------------------------------------------------------


def test_compute_all_without_degraded():
    ref = _rand_image(1)
    restored = _rand_image(2)
    metrics = compute_all(ref, restored)
    assert "psnr_restored" in metrics
    assert "ssim_restored" in metrics
    # No degraded metrics
    assert "psnr_degraded" not in metrics
    assert "ssim_degraded" not in metrics


def test_compute_all_with_degraded():
    ref = _rand_image(1)
    restored = _rand_image(2)
    degraded = _rand_image(3)
    metrics = compute_all(ref, restored, degraded=degraded)
    assert "psnr_restored" in metrics
    assert "ssim_restored" in metrics
    assert "psnr_degraded" in metrics
    assert "ssim_degraded" in metrics
    assert "psnr_improvement" in metrics
    assert "ssim_improvement" in metrics


def test_compute_all_improvement_is_positive_when_restored_better():
    ref = _rand_image(1)
    # Restored is close to reference; degraded is very different
    noise = _rand_image(5)
    restored = np.clip(ref + np.float32(0.02) * noise, 0, 1).astype(np.float32)
    degraded = np.clip(ref + np.float32(0.5) * _rand_image(6), 0, 1).astype(np.float32)
    metrics = compute_all(ref, restored, degraded=degraded)
    assert metrics["psnr_improvement"] > 0.0


def test_compute_all_identical_restored_gives_100_psnr():
    ref = _rand_image(1)
    metrics = compute_all(ref, ref)
    assert metrics["psnr_restored"] == pytest.approx(100.0)
    assert metrics["ssim_restored"] == pytest.approx(1.0, abs=1e-5)
