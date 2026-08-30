"""
Test Visual Compare Config

Test module for visual compare config.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(
    subprocess.call(
        [sys.executable, "-c", "import importlib; importlib.import_module('PIL'); import numpy"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    != 0,
    reason="pillow or numpy not installed",
)


def write_img(p: Path, gray: int):
    from PIL import Image  # type: ignore

    img = Image.new("L", (100, 60), color=gray)
    img.save(p)


def test_visual_compare_config_uses_template_threshold(tmp_path):
    # Config
    cfg = {
        "default_metric": "ssim",
        "default_threshold": 0.90,
        "templates": {"report_template_themed.html": {"metric": "ssim", "threshold": 0.99}},
    }
    cfgp = tmp_path / "thresholds.json"
    cfgp.write_text(json.dumps(cfg), encoding="utf-8")

    base = tmp_path / "base.png"
    cand = tmp_path / "cand.png"
    write_img(base, 200)
    write_img(cand, 200)
    code = subprocess.call(
        [
            sys.executable,
            "tools/visual_compare_config.py",
            "--config",
            str(cfgp),
            "--template",
            "report_template_themed.html",
            "--baseline",
            str(base),
            "--candidate",
            str(cand),
        ]
    )
    assert code == 0, "code is not valid"
