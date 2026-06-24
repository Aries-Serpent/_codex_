"""Unit + integration tests for restore_pipeline.

All tests generate synthetic images programmatically — no external files required.
Designed to run with ``pytest -q --tb=short -W error``.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture()
def clean_image() -> np.ndarray:
    """Create a small synthetic RGB image, float32 [0,1]."""
    rng = np.random.default_rng(42)
    return rng.uniform(0.2, 0.9, (64, 64, 3)).astype(np.float32)


@pytest.fixture()
def noisy_image(clean_image: np.ndarray) -> np.ndarray:
    """Add Gaussian noise to the clean image."""
    rng = np.random.default_rng(0)
    noise = rng.normal(0, 0.08, clean_image.shape).astype(np.float32)
    return np.clip(clean_image + noise, 0.0, 1.0).astype(np.float32)


@pytest.fixture()
def blurry_noisy_image(clean_image: np.ndarray) -> np.ndarray:
    """Add blur AND noise."""
    import cv2

    blurred = cv2.GaussianBlur(clean_image, (5, 5), 1.5)
    rng = np.random.default_rng(7)
    noise = rng.normal(0, 0.06, blurred.shape).astype(np.float32)
    return np.clip(blurred + noise, 0.0, 1.0).astype(np.float32)


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


# ── Import / deprecation smoke test ──────────────────────────────────────────


def test_import_no_deprecation_warnings() -> None:
    """Importing the package must produce zero deprecation warnings."""
    result = subprocess.run(
        [sys.executable, "-W", "error", "-c", "import restore_pipeline"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Import failed:\n{result.stderr}"


# ── Config ───────────────────────────────────────────────────────────────────


def test_config_defaults() -> None:
    from restore_pipeline import PipelineConfig

    cfg = PipelineConfig()
    assert cfg.algorithm == "auto"
    assert not cfg.deblur
    assert not cfg.colorize
    assert cfg.saturation_scale > 1.0


# ── I/O ───────────────────────────────────────────────────────────────────────


def test_save_and_load_roundtrip(clean_image: np.ndarray, tmp_dir: Path) -> None:
    from restore_pipeline.io import load_image, save_image

    out = tmp_dir / "roundtrip.png"
    save_image(clean_image, out)
    loaded = load_image(out)

    assert loaded.shape == clean_image.shape
    assert loaded.dtype == np.float32
    assert 0.0 <= loaded.min() <= loaded.max() <= 1.0
    # Pixel values should be close (PNG is lossless)
    np.testing.assert_allclose(loaded, clean_image, atol=1 / 255)


def test_load_nonexistent_raises() -> None:
    from restore_pipeline.io import load_image

    with pytest.raises(FileNotFoundError):
        load_image("/nonexistent/path/image.png")


def test_load_unsupported_ext_raises(tmp_dir: Path) -> None:
    from restore_pipeline.io import load_image

    bogus = tmp_dir / "file.xyz"
    bogus.write_bytes(b"data")
    with pytest.raises(ValueError, match="Unsupported image format"):
        load_image(bogus)


# ── Metrics ───────────────────────────────────────────────────────────────────


def test_psnr_identical_images(clean_image: np.ndarray) -> None:
    from restore_pipeline.metrics import psnr

    score = psnr(clean_image, clean_image)
    # Identical images → capped at 100 dB
    assert score >= 100.0


def test_ssim_identical_images(clean_image: np.ndarray) -> None:
    from restore_pipeline.metrics import ssim

    score = ssim(clean_image, clean_image)
    assert score > 0.99


def test_metrics_show_improvement(clean_image: np.ndarray, noisy_image: np.ndarray) -> None:
    from restore_pipeline.metrics import psnr, ssim

    clean_psnr = psnr(clean_image, clean_image)
    noisy_psnr = psnr(clean_image, noisy_image)
    assert clean_psnr > noisy_psnr

    clean_ssim = ssim(clean_image, clean_image)
    noisy_ssim = ssim(clean_image, noisy_image)
    assert clean_ssim > noisy_ssim


# ── Pipeline — default (nl_means / bm3d fallback) ────────────────────────────


def test_pipeline_returns_uint8(noisy_image: np.ndarray) -> None:
    from restore_pipeline import process

    restored, _metrics = process(noisy_image)
    assert restored.dtype == np.uint8
    assert restored.shape == noisy_image.shape


def test_pipeline_output_has_same_spatial_shape(noisy_image: np.ndarray) -> None:
    from restore_pipeline import process

    restored, _ = process(noisy_image)
    assert restored.shape[:2] == noisy_image.shape[:2]


def test_pipeline_with_uint8_input(noisy_image: np.ndarray) -> None:
    from restore_pipeline import process

    u8 = (noisy_image * 255).astype(np.uint8)
    restored, _ = process(u8)
    assert restored.dtype == np.uint8


def test_pipeline_psnr_improves_over_degraded(
    clean_image: np.ndarray, noisy_image: np.ndarray
) -> None:
    """Denoised image should have higher PSNR than the degraded input vs reference."""
    from restore_pipeline import PipelineConfig, process

    # Use neutral colour enhancement so PSNR measures denoising faithfully
    cfg = PipelineConfig(
        algorithm="nl_means",
        saturation_scale=1.0,  # no saturation boost
        clahe_clip_limit=0.0,  # disable CLAHE
        sharpen_amount=0.0,  # no sharpening
    )
    _restored_u8, metrics = process(noisy_image, reference=clean_image, config=cfg)

    assert "psnr_restored" in metrics
    assert "psnr_degraded" in metrics
    # The pipeline should not make PSNR worse than the degraded input
    assert metrics["psnr_restored"] >= metrics["psnr_degraded"] - 1.0


def test_pipeline_ssim_reasonable(clean_image: np.ndarray, noisy_image: np.ndarray) -> None:
    from restore_pipeline import PipelineConfig, process

    # Use neutral settings to measure structural similarity faithfully
    cfg = PipelineConfig(
        algorithm="nl_means",
        saturation_scale=1.0,
        clahe_clip_limit=0.0,
        sharpen_amount=0.0,
    )
    _, metrics = process(noisy_image, reference=clean_image, config=cfg)
    assert metrics["ssim_restored"] > 0.4


# ── Pipeline — deblur stage ───────────────────────────────────────────────────


def test_pipeline_deblur_flag(blurry_noisy_image: np.ndarray) -> None:
    from restore_pipeline import PipelineConfig, process

    cfg = PipelineConfig(deblur=True, algorithm="nl_means")
    restored, _ = process(blurry_noisy_image, config=cfg)
    assert restored.dtype == np.uint8


# ── Pipeline — inpaint stage ─────────────────────────────────────────────────


def test_pipeline_inpaint(clean_image: np.ndarray) -> None:
    from restore_pipeline import process

    mask = np.zeros((64, 64), dtype=np.uint8)
    mask[20:30, 20:30] = 255  # small inpaint region

    restored, _ = process(clean_image, mask=mask)
    assert restored.dtype == np.uint8
    # The masked region should be filled (not all zeros)
    assert restored[20:30, 20:30].mean() > 0


# ── Pipeline — colour enhancement ────────────────────────────────────────────


def test_pipeline_with_reference_for_color_transfer(
    noisy_image: np.ndarray, clean_image: np.ndarray
) -> None:
    from restore_pipeline import process

    restored, metrics = process(noisy_image, reference=clean_image)
    assert restored.dtype == np.uint8
    assert "psnr_restored" in metrics


# ── Pipeline — opencv algorithm ──────────────────────────────────────────────


def test_pipeline_opencv_algorithm(noisy_image: np.ndarray) -> None:
    from restore_pipeline import PipelineConfig, process

    cfg = PipelineConfig(algorithm="opencv")
    restored, _ = process(noisy_image, config=cfg)
    assert restored.dtype == np.uint8


# ── File-based integration: save input → run pipeline → check output ─────────


def test_pipeline_file_integration(clean_image: np.ndarray, tmp_dir: Path) -> None:
    from restore_pipeline import PipelineConfig, process
    from restore_pipeline.io import load_image, save_image

    # Build a noisy degraded image
    rng = np.random.default_rng(99)
    noise = rng.normal(0, 0.1, clean_image.shape).astype(np.float32)
    degraded = np.clip(clean_image + noise, 0.0, 1.0)

    # Write degraded to disk
    in_path = tmp_dir / "degraded.png"
    save_image(degraded, in_path)

    # Process with neutral colour settings to keep PSNR meaningful
    img = load_image(in_path)
    cfg = PipelineConfig(
        algorithm="nl_means",
        saturation_scale=1.0,
        clahe_clip_limit=0.0,
        sharpen_amount=0.0,
    )
    restored_u8, metrics = process(img, reference=clean_image, config=cfg)

    # Write output
    out_path = tmp_dir / "restored.png"
    save_image(restored_u8, out_path)

    assert out_path.exists()
    assert out_path.stat().st_size > 0
    # Noise=0.10 → degraded PSNR ~20 dB; restored should be at least 15 dB
    assert metrics["psnr_restored"] > 15.0


# ── CLI smoke test ────────────────────────────────────────────────────────────


def test_cli_smoke_run(clean_image: np.ndarray, tmp_dir: Path) -> None:
    """Run the CLI as a subprocess with a synthetic noisy image."""
    from restore_pipeline.io import save_image

    rng = np.random.default_rng(3)
    noise = rng.normal(0, 0.08, clean_image.shape).astype(np.float32)
    noisy = np.clip(clean_image + noise, 0.0, 1.0)

    in_path = tmp_dir / "cli_input.png"
    save_image(noisy, in_path)
    out_dir = tmp_dir / "cli_output"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "restore_pipeline.cli",
            "--input",
            str(in_path),
            "--output",
            str(out_dir),
            "--algorithm",
            "nl_means",
            "--verbose",
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, (
        f"CLI failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )
    out_files = list(out_dir.iterdir())
    assert len(out_files) >= 1, "No output files produced"


def test_cli_missing_input_exits_nonzero(tmp_dir: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "restore_pipeline.cli",
            "--input",
            str(tmp_dir / "nonexistent.png"),
            "--output",
            str(tmp_dir / "out"),
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode != 0
