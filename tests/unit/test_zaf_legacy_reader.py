"""Tests for the legacy ZAF bundle reader."""

from __future__ import annotations

from pathlib import Path
from zipfile import ZipFile

import pytest

from codex_crm.zaf_legacy.reader import extract_legacy_app
from tests.fixtures.zaf_legacy import SAMPLE_ZAF_BUNDLE


@pytest.fixture()
def legacy_bundle_zip(tmp_path: Path) -> Path:
    archive = tmp_path / "legacy_bundle.zip"
    with ZipFile(archive, "w") as zf:
        for relative_path, payload in SAMPLE_ZAF_BUNDLE.items():
            zf.writestr(relative_path, payload)
    return archive


def test_extract_writes_into_src_tree(tmp_path: Path, legacy_bundle_zip: Path) -> None:
    output_dir = tmp_path / "output"
    written = extract_legacy_app(legacy_bundle_zip, output_dir)

    expected_root = output_dir / "src"
    assert expected_root.exists()

    written_relative = {path.relative_to(expected_root) for path in written}
    assert written_relative == {Path(rel) for rel in SAMPLE_ZAF_BUNDLE}

    for relative_path, payload in SAMPLE_ZAF_BUNDLE.items():
        destination = expected_root / relative_path
        assert destination.exists()
        if isinstance(payload, bytes):
            assert destination.read_bytes() == payload
        else:
            assert destination.read_text(encoding="utf-8") == payload


def test_nested_directories_remain_distinct(tmp_path: Path, legacy_bundle_zip: Path) -> None:
    output_dir = tmp_path / "roundtrip"
    extract_legacy_app(legacy_bundle_zip, output_dir)

    src_root = output_dir / "src"
    nested = src_root / "translations" / "subdir" / "duplicate.txt"
    root_level = src_root / "subdir" / "duplicate.txt"

    assert nested.read_text(encoding="utf-8") == "nested\n"
    assert root_level.read_text(encoding="utf-8") == "root\n"


def test_binary_assets_are_written_in_binary_mode(tmp_path: Path, legacy_bundle_zip: Path) -> None:
    output_dir = tmp_path / "binary"
    extract_legacy_app(legacy_bundle_zip, output_dir)

    src_root = output_dir / "src"
    primary_logo = src_root / "assets" / "images" / "logo.png"
    nested_logo = src_root / "assets" / "images" / "icons" / "logo.png"

    assert primary_logo.read_bytes() == SAMPLE_ZAF_BUNDLE["assets/images/logo.png"]
    assert nested_logo.read_bytes() == SAMPLE_ZAF_BUNDLE["assets/images/icons/logo.png"]
