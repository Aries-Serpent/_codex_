"""Tests for restore_pipeline.cli — argument parsing and input collection."""

from __future__ import annotations

import pytest

from restore_pipeline.cli import _collect_inputs, build_parser


# ---------------------------------------------------------------------------
# build_parser
# ---------------------------------------------------------------------------


def test_parser_requires_input():
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["--output", "/tmp/out"])


def test_parser_requires_output():
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["--input", "photo.jpg"])


def test_parser_minimal_args():
    parser = build_parser()
    args = parser.parse_args(["--input", "photo.jpg", "--output", "./out"])
    assert args.input == "photo.jpg"
    assert args.output == "./out"


def test_parser_default_algorithm():
    parser = build_parser()
    args = parser.parse_args(["--input", "x.jpg", "--output", "y"])
    assert args.algorithm == "auto"


def test_parser_algorithm_choices():
    parser = build_parser()
    for algo in ("auto", "bm3d", "nl_means", "opencv"):
        args = parser.parse_args(["--input", "x.jpg", "--output", "y", "--algorithm", algo])
        assert args.algorithm == algo


def test_parser_invalid_algorithm_raises():
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["--input", "x.jpg", "--output", "y", "--algorithm", "invalid"])


def test_parser_deblur_flag():
    parser = build_parser()
    args = parser.parse_args(["--input", "x.jpg", "--output", "y", "--deblur"])
    assert args.deblur is True


def test_parser_deblur_flag_false_by_default():
    parser = build_parser()
    args = parser.parse_args(["--input", "x.jpg", "--output", "y"])
    assert args.deblur is False


def test_parser_colorize_flag():
    parser = build_parser()
    args = parser.parse_args(["--input", "x.jpg", "--output", "y", "--colorize"])
    assert args.colorize is True


def test_parser_colorize_false_by_default():
    parser = build_parser()
    args = parser.parse_args(["--input", "x.jpg", "--output", "y"])
    assert args.colorize is False


def test_parser_verbose_flag():
    parser = build_parser()
    args = parser.parse_args(["--input", "x.jpg", "--output", "y", "--verbose"])
    assert args.verbose is True


def test_parser_verbose_false_by_default():
    parser = build_parser()
    args = parser.parse_args(["--input", "x.jpg", "--output", "y"])
    assert args.verbose is False


def test_parser_mask_optional():
    parser = build_parser()
    args = parser.parse_args(["--input", "x.jpg", "--output", "y", "--mask", "mask.png"])
    assert args.mask == "mask.png"


def test_parser_mask_default_none():
    parser = build_parser()
    args = parser.parse_args(["--input", "x.jpg", "--output", "y"])
    assert args.mask is None


def test_parser_colorize_model_dest():
    parser = build_parser()
    args = parser.parse_args(
        ["--input", "x.jpg", "--output", "y", "--colorize-model", "/models/c.onnx"]
    )
    assert args.colorize_model == "/models/c.onnx"


def test_parser_short_input_flag():
    parser = build_parser()
    args = parser.parse_args(["-i", "photo.jpg", "-o", "./out"])
    assert args.input == "photo.jpg"
    assert args.output == "./out"


# ---------------------------------------------------------------------------
# _collect_inputs
# ---------------------------------------------------------------------------


def test_collect_inputs_single_file(tmp_path):
    img = tmp_path / "photo.jpg"
    img.write_bytes(b"fake")
    inputs = _collect_inputs(img)
    assert inputs == [img]


def test_collect_inputs_directory(tmp_path):
    (tmp_path / "a.jpg").write_bytes(b"x")
    (tmp_path / "b.png").write_bytes(b"x")
    (tmp_path / "c.txt").write_bytes(b"x")  # should be excluded
    inputs = _collect_inputs(tmp_path)
    names = {p.name for p in inputs}
    assert "a.jpg" in names
    assert "b.png" in names
    assert "c.txt" not in names


def test_collect_inputs_empty_directory(tmp_path):
    inputs = _collect_inputs(tmp_path)
    assert inputs == []


def test_collect_inputs_supports_tiff(tmp_path):
    (tmp_path / "scan.tiff").write_bytes(b"x")
    inputs = _collect_inputs(tmp_path)
    assert any(p.suffix.lower() == ".tiff" for p in inputs)


def test_collect_inputs_supports_bmp(tmp_path):
    (tmp_path / "img.bmp").write_bytes(b"x")
    inputs = _collect_inputs(tmp_path)
    assert any(p.suffix.lower() == ".bmp" for p in inputs)


def test_collect_inputs_supports_webp(tmp_path):
    (tmp_path / "img.webp").write_bytes(b"x")
    inputs = _collect_inputs(tmp_path)
    assert any(p.suffix.lower() == ".webp" for p in inputs)


def test_collect_inputs_sorted(tmp_path):
    for name in ("c.jpg", "a.jpg", "b.png"):
        (tmp_path / name).write_bytes(b"x")
    inputs = _collect_inputs(tmp_path)
    names = [p.name for p in inputs]
    assert names == sorted(names)
