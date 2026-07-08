"""Tests for Skills compression utilities."""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest
import yaml

from codex.skills.compression import CompressionResult, compress_skill, install_skill


def _make_skill_dir(root: Path, skill_id: str, version: str = "1.0.0") -> Path:
    """Create a minimal skill directory for testing."""
    slug = skill_id.replace(".", "_")
    skill_dir = root / slug
    skill_dir.mkdir(parents=True)
    manifest = {
        "id": skill_id,
        "version": version,
        "name": "Test Skill",
        "entrypoint": "handler:run",
        "capability_tags": ["test"],
    }
    (skill_dir / "manifest.yaml").write_text(yaml.safe_dump(manifest), encoding="utf-8")
    (skill_dir / "handler.py").write_text("def run(payload):\n    return {}\n", encoding="utf-8")
    schema_dir = skill_dir / "schema"
    schema_dir.mkdir()
    (schema_dir / "input.json").write_text('{"type":"object"}', encoding="utf-8")
    (schema_dir / "output.json").write_text('{"type":"object"}', encoding="utf-8")
    return skill_dir


class TestCompressSkill:
    def test_compress_creates_zip_fallback(self, tmp_path):
        skill_dir = _make_skill_dir(tmp_path / "skills", "test.compress.skill")
        out_dir = tmp_path / "dist"

        # Patch _find_skill_dir to return our temp dir
        from unittest.mock import patch

        with patch("codex.skills.compression._find_skill_dir", return_value=skill_dir):
            with patch("codex.skills.compression._7Z_BIN", None):  # force zip fallback
                result = compress_skill("test.compress.skill", out_dir=out_dir)

        assert isinstance(result, CompressionResult)
        assert Path(result.archive_path).exists(), "Result must not be empty"
        assert result.size_before > 0, "size_before must be greater than zero"
        assert result.size_after > 0, "size_after must be greater than zero"
        assert result.compression_ratio > 0, "compression_ratio must be greater than zero"

    def test_compress_result_has_correct_skill_id(self, tmp_path):
        skill_dir = _make_skill_dir(tmp_path / "skills", "my.test.skill")
        out_dir = tmp_path / "dist"

        from unittest.mock import patch

        with patch("codex.skills.compression._find_skill_dir", return_value=skill_dir):
            with patch("codex.skills.compression._7Z_BIN", None):
                result = compress_skill("my.test.skill", out_dir=out_dir)

        assert result.skill_id == "my.test.skill", "Result must not be empty"
        assert result.version == "1.0.0", "Result must not be empty"

    def test_compress_missing_skill_raises(self, tmp_path):
        from unittest.mock import patch

        with patch("codex.skills.compression._find_skill_dir", return_value=None):
            with pytest.raises(FileNotFoundError, match="Skill directory not found"):
                compress_skill("nonexistent.skill", out_dir=tmp_path)

    def test_compress_updates_manifest(self, tmp_path):
        skill_dir = _make_skill_dir(tmp_path / "skills", "test.manifest.update")
        out_dir = tmp_path / "dist"

        from unittest.mock import patch

        with patch("codex.skills.compression._find_skill_dir", return_value=skill_dir):
            with patch("codex.skills.compression._7Z_BIN", None):
                result = compress_skill(
                    "test.manifest.update", out_dir=out_dir, record_metrics=True
                )

        manifest_data = yaml.safe_load((skill_dir / "manifest.yaml").read_text())
        assert manifest_data["compression"]["size_before"] == result.size_before, "Result must not be empty"
        assert manifest_data["compression"]["size_after"] == result.size_after, "Result must not be empty"


class TestInstallSkill:
    def test_install_zip_archive(self, tmp_path):
        skill_dir = _make_skill_dir(tmp_path / "skills", "test.install.skill")

        # Create a zip archive manually
        archive_path = tmp_path / "test_install_skill-1.0.0.zip"
        with zipfile.ZipFile(archive_path, "w") as zf:
            for f in skill_dir.rglob("*"):
                if f.is_file():
                    zf.write(f, skill_dir.name + "/" + str(f.relative_to(skill_dir)))

        install_root = tmp_path / "installed"
        install_root.mkdir()
        dest = install_skill(archive_path, install_root=install_root)
        assert dest.exists(), "Condition must be true"
        assert (dest / "manifest.yaml").exists(), "Condition must be true"

    def test_install_missing_archive_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            install_skill(tmp_path / "nonexistent.zip")

    def test_install_unsupported_format_raises(self, tmp_path):
        fake = tmp_path / "archive.tar.gz"
        fake.write_text("fake")
        with pytest.raises(ValueError, match="Unsupported archive format"):
            install_skill(fake)
