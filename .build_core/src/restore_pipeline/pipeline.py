"""Core image-restoration pipeline.

Stages (all CPU-safe):
  1. Load / normalise to float32 [0, 1]
  2. Estimate noise level (skimage.restoration.estimate_sigma)
  3. Denoise  — BM3D → cv2 NL-means → skimage NL-means (fallback chain)
  4. Deblur   — Richardson–Lucy (opt-in)
  5. Inpaint  — cv2 INPAINT_TELEA (requires mask)
  6. Color enhancement — CLAHE on L + saturation boost + optional Reinhard
  7. Colorize — ONNX CPU (opt-in)
  8. Sharpen  — unsharp mask + clip → uint8
"""

from __future__ import annotations

import importlib.util
import logging
import time
from typing import TYPE_CHECKING, Any

import numpy as np

from restore_pipeline.config import PipelineConfig

if TYPE_CHECKING:
    pass  # Only used for type annotations below

logger = logging.getLogger(__name__)

# Module-level cache for ONNX InferenceSession objects, keyed by model path.
# Avoids reloading the model on every call to _colorize.
_ORT_SESSION_CACHE: dict[str, Any] = {}


# ── Public entry point ────────────────────────────────────────────────────────


def process(
    image: np.ndarray,
    mask: np.ndarray | None = None,
    reference: np.ndarray | None = None,
    config: PipelineConfig | None = None,
) -> tuple[np.ndarray, dict[str, float]]:
    """Run the full restoration pipeline on *image*.

    Parameters
    ----------
    image:
        Input image — float32 [0, 1] or uint8, shape (H, W, 3).
    mask:
        Optional binary mask (uint8, non-zero = region to inpaint).
    reference:
        Optional ground-truth reference for computing PSNR / SSIM improvement.
    config:
        Pipeline configuration.  Defaults to ``PipelineConfig()``.

    Returns
    -------
    restored : np.ndarray
        Restored image as uint8 (H, W, 3) RGB.
    metrics : dict[str, float]
        Metric values.  Empty when no *reference* is provided.
    """
    cfg = config or PipelineConfig()
    t0 = time.perf_counter()

    # Normalise input to float32 [0, 1]
    img = _to_float32(image)
    original = img.copy()

    # ── Stage 2: estimate noise ───────────────────────────────────────────────
    sigma = _estimate_sigma(img)
    logger.info("Estimated noise sigma: %.4f", sigma)

    # ── Stage 3: denoise ──────────────────────────────────────────────────────
    if sigma >= cfg.noise_threshold:
        img = _denoise(img, cfg, sigma)
        logger.info("Denoise stage  %.3fs", time.perf_counter() - t0)
    else:
        logger.info(
            "Noise below threshold (%.4f < %.4f) — denoising skipped", sigma, cfg.noise_threshold
        )

    # ── Stage 4: deblur ───────────────────────────────────────────────────────
    if cfg.deblur:
        img = _deblur(img, cfg)
        logger.info("Deblur stage   %.3fs", time.perf_counter() - t0)

    # ── Stage 5: inpaint ──────────────────────────────────────────────────────
    if mask is not None:
        img = _inpaint(img, mask, cfg)
        logger.info("Inpaint stage  %.3fs", time.perf_counter() - t0)

    # ── Stage 6: color enhancement ────────────────────────────────────────────
    # NOTE: reference is used only for metrics, NOT for colour transfer here.
    # Reinhard colour transfer is a separate opt-in: pass reference explicitly
    # via config.reinhard_reference or the --reference CLI flag with a separate
    # colour-transfer flag in a future update.  For now, reference is metrics-only.
    img = _color_enhance(img, reference=None, cfg=cfg)
    logger.info("Color stage    %.3fs", time.perf_counter() - t0)

    # ── Stage 7: colorization (opt-in) ────────────────────────────────────────
    if cfg.colorize:
        img = _colorize(img, cfg)
        logger.info("Colorize stage %.3fs", time.perf_counter() - t0)

    # ── Stage 8: sharpen + finalize ──────────────────────────────────────────
    if cfg.sharpen_amount > 0:
        img = _unsharp_mask(img, amount=cfg.sharpen_amount)

    img = np.clip(img, 0.0, 1.0)
    restored_f32 = img

    elapsed = time.perf_counter() - t0
    logger.info("Pipeline complete in %.3fs", elapsed)

    # ── Metrics ───────────────────────────────────────────────────────────────
    metrics: dict[str, float] = {"elapsed_seconds": elapsed}
    if reference is not None:
        from restore_pipeline.metrics import compute_all

        ref_f32 = _to_float32(reference)
        metrics.update(compute_all(ref_f32, restored_f32, degraded=original))

    restored_u8 = (restored_f32 * 255).round().astype(np.uint8)
    return restored_u8, metrics


# ── Stage implementations ─────────────────────────────────────────────────────


def _to_float32(img: np.ndarray) -> np.ndarray:
    if img.dtype == np.uint8:
        return img.astype(np.float32) / 255.0
    return img.astype(np.float32)


def _estimate_sigma(img: np.ndarray) -> float:
    from skimage.restoration import estimate_sigma

    sigmas = estimate_sigma(img, channel_axis=2)
    return float(np.mean(sigmas))


def _denoise(img: np.ndarray, cfg: PipelineConfig, sigma: float = 0.1) -> np.ndarray:
    algo = cfg.algorithm
    if algo == "auto":
        algo = _pick_algorithm()

    if algo == "bm3d":
        return _denoise_bm3d(img, sigma)
    if algo == "opencv":
        return _denoise_opencv(img, cfg)
    return _denoise_nlmeans(img, cfg, sigma)


def _pick_algorithm() -> str:
    """Return the best available denoising algorithm."""
    if importlib.util.find_spec("bm3d") is not None:
        return "bm3d"
    return "nl_means"


def _denoise_bm3d(img: np.ndarray, sigma: float = 0.1) -> np.ndarray:
    try:
        import bm3d

        # Use the estimated noise sigma as sigma_psd for adaptive denoising.
        # Cap at 0.15 so that wavelet-estimator overestimation on textured
        # images does not cause destructive over-smoothing.
        sigma_psd = float(np.clip(sigma, 0.01, 0.15))
        return np.clip(
            bm3d.bm3d(img, sigma_psd=sigma_psd, stage_arg=bm3d.BM3DStages.ALL_STAGES), 0.0, 1.0
        ).astype(np.float32)
    except (ImportError, AttributeError) as exc:
        logger.warning("BM3D denoising failed (%s); falling back to NL-means.", exc)
        from skimage.restoration import denoise_nl_means

        h = float(np.clip(sigma, 0.04, 0.10))
        return denoise_nl_means(
            img, h=h, fast_mode=True, patch_size=5, patch_distance=6, channel_axis=2
        ).astype(np.float32)


def _denoise_opencv(img: np.ndarray, cfg: PipelineConfig) -> np.ndarray:
    import cv2

    u8 = (img * 255).round().astype(np.uint8)
    # cv2 works in BGR
    bgr = cv2.cvtColor(u8, cv2.COLOR_RGB2BGR)
    denoised = cv2.fastNlMeansDenoisingColored(
        bgr,
        None,
        cfg.opencv_h,
        cfg.opencv_h,
        cfg.opencv_template_window,
        cfg.opencv_search_window,
    )
    rgb = cv2.cvtColor(denoised, cv2.COLOR_BGR2RGB)
    return rgb.astype(np.float32) / 255.0


def _denoise_nlmeans(img: np.ndarray, cfg: PipelineConfig, sigma: float = 0.08) -> np.ndarray:
    from skimage.restoration import denoise_nl_means

    # h scales proportionally to the estimated noise sigma; cfg.nl_h acts as
    # the upper bound to guard against overestimation by the wavelet estimator
    # on small or highly-textured images (common practice: h ∝ σ, bounded).
    h = float(np.clip(sigma, cfg.nl_h * 0.5, cfg.nl_h))
    return denoise_nl_means(
        img,
        h=h,
        fast_mode=True,
        patch_size=cfg.nl_patch_size,
        patch_distance=cfg.nl_patch_distance,
        channel_axis=2,
    ).astype(np.float32)


def _deblur(img: np.ndarray, cfg: PipelineConfig) -> np.ndarray:
    from skimage.restoration import richardson_lucy

    psf = _gaussian_psf(cfg.psf_size, cfg.psf_sigma)
    # Process each channel independently
    channels = [
        richardson_lucy(img[..., c], psf, num_iter=cfg.rl_iterations, clip=True) for c in range(3)
    ]
    return np.stack(channels, axis=-1).astype(np.float32)


def _gaussian_psf(size: int, sigma: float) -> np.ndarray:
    """Create a normalised 2-D Gaussian PSF kernel."""
    import cv2

    k = cv2.getGaussianKernel(size, sigma)
    psf = k @ k.T
    return (psf / psf.sum()).astype(np.float64)


def _inpaint(img: np.ndarray, mask: np.ndarray, cfg: PipelineConfig) -> np.ndarray:
    import cv2

    u8 = (img * 255).round().astype(np.uint8)
    bgr = cv2.cvtColor(u8, cv2.COLOR_RGB2BGR)
    result = cv2.inpaint(bgr, mask, cfg.inpaint_radius, cv2.INPAINT_TELEA)
    rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
    return rgb.astype(np.float32) / 255.0


def _color_enhance(
    img: np.ndarray,
    *,
    reference: np.ndarray | None = None,
    cfg: PipelineConfig,
) -> np.ndarray:
    import cv2

    u8 = (img * 255).round().astype(np.uint8)
    bgr = cv2.cvtColor(u8, cv2.COLOR_RGB2BGR)

    # ── CLAHE on L channel ─────────────────────────────────────────────────
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2Lab)
    l_ch, a_ch, b_ch = cv2.split(lab)

    if cfg.clahe_clip_limit > 0.0:
        clahe = cv2.createCLAHE(
            clipLimit=cfg.clahe_clip_limit,
            tileGridSize=cfg.clahe_tile_grid_size,
        )
        l_ch = clahe.apply(l_ch)

    # ── Saturation (AB) boost ─────────────────────────────────────────────
    a_f = a_ch.astype(np.float32) - 128.0
    b_f = b_ch.astype(np.float32) - 128.0
    a_f = np.clip(a_f * cfg.saturation_scale + 128.0, 0, 255).astype(np.uint8)
    b_f = np.clip(b_f * cfg.saturation_scale + 128.0, 0, 255).astype(np.uint8)

    lab_enhanced = cv2.merge([l_ch, a_f, b_f])
    bgr_out = cv2.cvtColor(lab_enhanced, cv2.COLOR_Lab2BGR)

    # ── Optional Reinhard color transfer ──────────────────────────────────
    if reference is not None:
        ref_u8 = (np.clip(_to_float32(reference), 0, 1) * 255).round().astype(np.uint8)
        ref_bgr = cv2.cvtColor(ref_u8, cv2.COLOR_RGB2BGR)
        bgr_out = _reinhard_transfer(bgr_out, ref_bgr)

    rgb = cv2.cvtColor(bgr_out, cv2.COLOR_BGR2RGB)
    return rgb.astype(np.float32) / 255.0


def _reinhard_transfer(source: np.ndarray, target: np.ndarray) -> np.ndarray:
    """Simple Reinhard (2001) colour transfer in LAB space."""
    import cv2

    src_lab = cv2.cvtColor(source, cv2.COLOR_BGR2Lab).astype(np.float32)
    tgt_lab = cv2.cvtColor(target, cv2.COLOR_BGR2Lab).astype(np.float32)

    result = src_lab.copy()
    for ch in range(3):
        src_mean, src_std = src_lab[..., ch].mean(), src_lab[..., ch].std() + 1e-6
        tgt_mean, tgt_std = tgt_lab[..., ch].mean(), tgt_lab[..., ch].std() + 1e-6
        result[..., ch] = (src_lab[..., ch] - src_mean) * (tgt_std / src_std) + tgt_mean

    result = np.clip(result, 0, 255).astype(np.uint8)
    return cv2.cvtColor(result, cv2.COLOR_Lab2BGR)


def _colorize(img: np.ndarray, cfg: PipelineConfig) -> np.ndarray:
    """Optional ONNX-based colorization (CPU only).

    The model must be downloaded separately — see README for instructions.
    If no model path is set, or the model file is missing, this stage is skipped
    with a warning.
    """
    if not cfg.colorize_model_path:
        logger.warning("colorize=True but no model_path set; skipping colorization stage.")
        return img

    import pathlib

    if not pathlib.Path(cfg.colorize_model_path).exists():
        logger.warning(
            "Colorization model not found at '%s'; skipping. Download from: %s",
            cfg.colorize_model_path,
            cfg.colorize_model_url,
        )
        return img

    try:
        import cv2
        import onnxruntime as ort

        # Reuse a cached session to avoid reloading the model for every image.
        model_path = cfg.colorize_model_path
        if model_path not in _ORT_SESSION_CACHE:
            _ORT_SESSION_CACHE[model_path] = ort.InferenceSession(
                model_path,
                providers=["CPUExecutionProvider"],
            )
        session = _ORT_SESSION_CACHE[model_path]
        # Convert to grayscale L channel (LAB) and resize to model input
        u8 = (img * 255).round().astype(np.uint8)
        bgr = cv2.cvtColor(u8, cv2.COLOR_RGB2BGR)
        lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2Lab)
        l_ch = lab[..., 0:1].astype(np.float32)  # (H, W, 1)

        h_orig, w_orig = l_ch.shape[:2]
        input_name = session.get_inputs()[0].name
        # Typical colorization model expects (1, 1, 224, 224)
        l_resized = cv2.resize(l_ch[..., 0], (224, 224)).astype(np.float32)
        inp = l_resized[np.newaxis, np.newaxis, :, :]  # (1,1,H,W)

        ab_pred = session.run(None, {input_name: inp})[0]  # (1,2,H,W)
        ab_resized = np.stack(
            [
                cv2.resize(ab_pred[0, 0], (w_orig, h_orig)),
                cv2.resize(ab_pred[0, 1], (w_orig, h_orig)),
            ],
            axis=-1,
        )
        # Recombine with original L
        lab_out = np.concatenate([l_ch, ab_resized + 128.0], axis=-1).clip(0, 255).astype(np.uint8)
        rgb_out = cv2.cvtColor(lab_out, cv2.COLOR_Lab2RGB)
        return rgb_out.astype(np.float32) / 255.0

    except (ImportError, AttributeError) as exc:
        logger.warning("Colorization failed (%s); returning image without colorization.", exc)
        return img


def _unsharp_mask(img: np.ndarray, amount: float = 0.5) -> np.ndarray:
    """Apply unsharp masking for final sharpening."""
    from skimage.filters import unsharp_mask as skimage_unsharp

    return skimage_unsharp(img, radius=1.0, amount=amount, channel_axis=2).astype(np.float32)
