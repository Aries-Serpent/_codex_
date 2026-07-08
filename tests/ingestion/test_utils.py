"""Regression coverage for ingestion.utils helpers."""

from __future__ import annotations

from ingestion import utils


def test_deterministic_shuffle_reproducible():
    first = utils.deterministic_shuffle([1, 2, 3, 4], seed=42)
    second = utils.deterministic_shuffle([1, 2, 3, 4], seed=42)
    assert first == second, "first is not valid"
    assert first != [1, 2, 3, 4]


def test_detect_encoding_and_manual_read(tmp_path, monkeypatch):
    sample = tmp_path / "sample.txt"
    sample.write_text("hello world", encoding="utf-8")

    monkeypatch.setattr(utils, "_repo_detect_encoding", None)
    monkeypatch.setattr(utils, "_io_read_text", None)

    detected = utils._detect_encoding(sample)
    assert detected == "utf-8", "detected is not valid"

    text = utils.read_text(sample)
    assert text.strip() == "hello world", "Condition must be true"
