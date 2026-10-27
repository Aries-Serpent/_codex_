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

    noise_threshold: float = 0.02

    nl_patch_size: int = 5
    nl_patch_distance: int = 6
    nl_h: float = 0.08

    opencv_h: int = 10
    opencv_template_window: int = 7
    opencv_search_window: int = 21

    # ── Deblur ─────────────────────────────────────────────────────────────────
    deblur: bool = False

    rl_iterations: int = 20

    psf_sigma: float = 1.5

    psf_size: int = 9

    # ── Inpaint ────────────────────────────────────────────────────────────────
    inpaint_radius: int = 3

    # ── Color enhancement ──────────────────────────────────────────────────────
    clahe_clip_limit: float = 2.0
    clahe_tile_grid_size: tuple[int, int] = field(default_factory=lambda: (8, 8))

    saturation_scale: float = 1.35

    sharpen_amount: float = 0.5

    # ── Colorization ───────────────────────────────────────────────────────────
    colorize: bool = False

    colorize_model_path: str | None = None

    colorize_model_url: str = (
        "https://github.com/richzhang/colorization/raw/caffe/demo/colorization_release_v2.caffemodel"
    )
