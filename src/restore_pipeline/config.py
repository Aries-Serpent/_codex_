"""Default hyperparameters for the restoration pipeline."""

from dataclasses import dataclass, field


@dataclass
class PipelineConfig:
    """All tunable knobs in one place.

    All values are sensible defaults for general-purpose photo restoration on a
    modern CPU.  Override per-call or persist to JSON / TOML as needed.
    """

    # ── Denoise ────────────────────────────────────────────────────────────────
    algorithm: str = "auto"
    """Denoising algorithm: ``auto`` | ``bm3d`` | ``nl_means`` | ``opencv``."""

    noise_threshold: float = 0.02
    """Minimum estimated-sigma before denoising is applied (float32 scale)."""

    nl_patch_size: int = 5
    nl_patch_distance: int = 6
    nl_h: float = 0.08
    """Fast non-local means parameters."""

    opencv_h: int = 10
    opencv_template_window: int = 7
    opencv_search_window: int = 21
    """``cv2.fastNlMeansDenoisingColored`` parameters."""

    # ── Deblur ─────────────────────────────────────────────────────────────────
    deblur: bool = False
    """Enable Richardson–Lucy deblurring."""

    rl_iterations: int = 20
    """Number of Richardson–Lucy iterations."""

    psf_sigma: float = 1.5
    """Gaussian PSF sigma used when no external PSF is supplied."""

    psf_size: int = 9
    """Size of the auto-generated Gaussian PSF kernel (odd)."""

    # ── Inpaint ────────────────────────────────────────────────────────────────
    inpaint_radius: int = 3
    """Neighbourhood radius for ``cv2.inpaint`` (INPAINT_TELEA)."""

    # ── Color enhancement ──────────────────────────────────────────────────────
    clahe_clip_limit: float = 2.0
    clahe_tile_grid_size: tuple[int, int] = field(default_factory=lambda: (8, 8))
    """CLAHE parameters for the L channel (LAB colour space)."""

    saturation_scale: float = 1.35
    """Multiplier applied to the A and B channels for vibrance boost."""

    sharpen_amount: float = 0.5
    """Unsharp-mask strength (0 = disabled)."""

    # ── Colorization ───────────────────────────────────────────────────────────
    colorize: bool = False
    """Enable ONNX-based colorization (CPU only)."""

    colorize_model_path: str | None = None
    """Path to a colorization ONNX model.  See README for download instructions."""

    colorize_model_url: str = "https://github.com/richzhang/colorization/raw/caffe/demo/colorization_release_v2.caffemodel"
    """Reference URL for the original Caffe model (not ONNX).  The pipeline expects
    an ONNX export at ``colorize_model_path``; this URL is used only in warning
    messages to point users to the upstream source.  See README for ONNX download
    instructions."""
