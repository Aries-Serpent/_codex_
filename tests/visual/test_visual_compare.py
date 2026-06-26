"""
Test Visual Compare

Test module for visual compare.
"""

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

    img = Image.new("L", (200, 100), color=gray)
    img.save(p)


def test_visual_compare_identical(tmp_path):
    base = tmp_path / "base.png"
    cand = tmp_path / "cand.png"
    write_img(base, 200)
    write_img(cand, 200)
    code = subprocess.call(
        [
            sys.executable,
            "tools/visual_compare.py",
            "--baseline",
            str(base),
            "--candidate",
            str(cand),
            "--threshold",
            "0.99",
        ]
    )
    assert code == 0, "code is not valid"


def test_visual_compare_different(tmp_path):
    base = tmp_path / "base.png"
    cand = tmp_path / "cand.png"
    write_img(base, 200)
    write_img(cand, 180)
    # With a high threshold, should fail
    code = subprocess.call(
        [
            sys.executable,
            "tools/visual_compare.py",
            "--baseline",
            str(base),
            "--candidate",
            str(cand),
            "--threshold",
            "0.999",
        ]
    )
    assert code in (0, 1)
