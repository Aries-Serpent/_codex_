"""Tests for restore_pipeline.config — PipelineConfig dataclass."""

from __future__ import annotations

import pytest

from restore_pipeline.config import PipelineConfig


# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------


def test_default_algorithm():
    cfg = PipelineConfig()
    assert cfg.algorithm == "auto"


def test_default_noise_threshold():
    cfg = PipelineConfig()
    assert cfg.noise_threshold == pytest.approx(0.02)


def test_default_deblur_disabled():
    cfg = PipelineConfig()
    assert cfg.deblur is False


def test_default_colorize_disabled():
    cfg = PipelineConfig()
    assert cfg.colorize is False


def test_default_colorize_model_path_is_none():
    cfg = PipelineConfig()
    assert cfg.colorize_model_path is None


def test_default_sharpen_amount():
    cfg = PipelineConfig()
    assert cfg.sharpen_amount == pytest.approx(0.5)


def test_default_clahe_clip_limit():
    cfg = PipelineConfig()
    assert cfg.clahe_clip_limit == pytest.approx(2.0)


def test_default_clahe_tile_grid_size():
    cfg = PipelineConfig()
    assert cfg.clahe_tile_grid_size == (8, 8)


def test_default_saturation_scale():
    cfg = PipelineConfig()
    assert cfg.saturation_scale == pytest.approx(1.35)


def test_default_nl_patch_size():
    cfg = PipelineConfig()
    assert cfg.nl_patch_size == 5


def test_default_nl_patch_distance():
    cfg = PipelineConfig()
    assert cfg.nl_patch_distance == 6


def test_default_rl_iterations():
    cfg = PipelineConfig()
    assert cfg.rl_iterations == 20


def test_default_inpaint_radius():
    cfg = PipelineConfig()
    assert cfg.inpaint_radius == 3


# ---------------------------------------------------------------------------
# Override values
# ---------------------------------------------------------------------------


def test_override_algorithm():
    cfg = PipelineConfig(algorithm="bm3d")
    assert cfg.algorithm == "bm3d"


def test_override_deblur():
    cfg = PipelineConfig(deblur=True)
    assert cfg.deblur is True


def test_override_colorize():
    cfg = PipelineConfig(colorize=True)
    assert cfg.colorize is True


def test_override_colorize_model_path():
    cfg = PipelineConfig(colorize_model_path="/models/color.onnx")
    assert cfg.colorize_model_path == "/models/color.onnx"


def test_override_sharpen_amount_zero():
    cfg = PipelineConfig(sharpen_amount=0.0)
    assert cfg.sharpen_amount == 0.0


def test_override_noise_threshold():
    cfg = PipelineConfig(noise_threshold=0.05)
    assert cfg.noise_threshold == pytest.approx(0.05)


def test_clahe_disabled_when_clip_limit_zero():
    cfg = PipelineConfig(clahe_clip_limit=0.0)
    assert cfg.clahe_clip_limit == 0.0


def test_override_psf_params():
    cfg = PipelineConfig(psf_size=5, psf_sigma=1.0)
    assert cfg.psf_size == 5
    assert cfg.psf_sigma == pytest.approx(1.0)


def test_opencv_defaults():
    cfg = PipelineConfig()
    assert cfg.opencv_h == 10
    assert cfg.opencv_template_window == 7
    assert cfg.opencv_search_window == 21


def test_algorithm_choices():
    for algo in ("auto", "bm3d", "nl_means", "opencv"):
        cfg = PipelineConfig(algorithm=algo)
        assert cfg.algorithm == algo
