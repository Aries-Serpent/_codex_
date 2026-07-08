"""
Security tests for offline bootstrap tarfile extraction.

Tests verify that the tarfile extraction is protected against:
- Path traversal attacks (../../../etc/passwd)
- Absolute path extraction
- Symlink/hardlink traversal attacks
- Malicious archive contents
"""

from __future__ import annotations

import io
import json
import shutil
import sys
import tarfile # pragma: allowlist secret # pragma: allowlist secret
from pathlib import Path

import pytest

# Add scripts/deploy to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "deploy"))

from bootstrap_offline import OfflineBootstrapper


@pytest.fixture
def cleanup_bootstrapper():
    """Fixture to clean up bootstrapper extraction directories."""
    bootstrappers = []
    
    def register(bootstrapper):
        bootstrappers.append(bootstrapper)
        return bootstrapper
    
    yield register
    
    for bootstrapper in bootstrappers:
        if bootstrapper.extraction_dir:
            shutil.rmtree(bootstrapper.extraction_dir, ignore_errors=True)


class TestTarfileExtractionSecurity:
    """Test security of tarfile extraction in OfflineBootstrapper."""

    def test_safe_extraction_valid_archive(self, tmp_path, cleanup_bootstrapper):
        """Test that valid archives extract correctly."""
        # Create a valid tar.gz with normal structure
        archive_dir = tmp_path / "archive_src"
        archive_dir.mkdir()
        
        (archive_dir / "wheelhouse").mkdir()
        (archive_dir / "wheelhouse" / "test.whl").write_text("wheel content")
        (archive_dir / "wheelhouse" / "manifest.json").write_text('{"wheels": {}}')
        
        archive_path = tmp_path / "valid.tar.gz"
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(archive_dir, arcname=".")
        
        # Extract using OfflineBootstrapper
        bootstrapper = OfflineBootstrapper(
            archive_path,
            profile="core",
            dry_run=True,
        )
        cleanup_bootstrapper(bootstrapper)
        
        success = bootstrapper._extract_wheelhouse()
        
        assert success, "Extraction should succeed for valid archive"
        assert bootstrapper.wheelhouse_dir.exists()
        assert (bootstrapper.wheelhouse_dir / "test.whl").exists()

    def test_safe_extraction_blocks_path_traversal(self, tmp_path):
        """Test that path traversal attacks are blocked."""
        # Create a tar.gz with path traversal in member names
        archive_path = tmp_path / "malicious.tar.gz"
        
        with tarfile.open(archive_path, "w:gz") as tar:
            # Create a TarInfo object with path traversal
            info = tarfile.TarInfo(name="../../../etc/passwd")
            info.size = 4
            tar.addfile(info, io.BytesIO(b"evil"))
        
        bootstrapper = OfflineBootstrapper(
            archive_path,
            profile="core",
            dry_run=True,
        )
        
        # Extraction should fail due to path traversal detection
        success = bootstrapper._extract_wheelhouse()
        
        assert not success, "Extraction should fail for path traversal attack"
        
        # Verify no file was written outside extraction directory
        passwd_files = list(tmp_path.glob("**/passwd"))
        assert not passwd_files, "Path traversal should not create files"

    def test_safe_extraction_blocks_absolute_paths(self, tmp_path):
        """Test that absolute paths are blocked."""
        # Create a tar.gz with absolute path
        archive_path = tmp_path / "absolute_path.tar.gz"
        
        with tarfile.open(archive_path, "w:gz") as tar:
            info = tarfile.TarInfo(name="/etc/important_file")
            info.size = 5
            tar.addfile(info, io.BytesIO(b"hacked"))
        
        bootstrapper = OfflineBootstrapper(
            archive_path,
            profile="core",
            dry_run=True,
        )
        
        success = bootstrapper._extract_wheelhouse()
        
        assert not success, "Extraction should fail for absolute paths"

    def test_safe_extraction_blocks_symlinks(self, tmp_path):
        """Test that symlinks are blocked."""
        # Create a tar.gz with symlink
        archive_path = tmp_path / "symlink.tar.gz"
        
        with tarfile.open(archive_path, "w:gz") as tar:
            info = tarfile.TarInfo(name="malicious_link")
            info.type = tarfile.SYMTYPE
            info.linkname = "../../../etc/passwd"
            tar.addfile(info)
        
        bootstrapper = OfflineBootstrapper(
            archive_path,
            profile="core",
            dry_run=True,
        )
        
        success = bootstrapper._extract_wheelhouse()
        
        assert not success, "Extraction should fail for symlinks"

    def test_safe_extraction_blocks_hardlinks(self, tmp_path):
        """Test that hardlinks are blocked."""
        # Create a tar.gz with hardlink
        archive_path = tmp_path / "hardlink.tar.gz"
        
        with tarfile.open(archive_path, "w:gz") as tar:
            info = tarfile.TarInfo(name="malicious_hardlink")
            info.type = tarfile.LNKTYPE  # Hardlink type
            info.linkname = "/etc/passwd"
            tar.addfile(info)
        
        bootstrapper = OfflineBootstrapper(
            archive_path,
            profile="core",
            dry_run=True,
        )
        
        success = bootstrapper._extract_wheelhouse()
        
        assert not success, "Extraction should fail for hardlinks"

    def test_safe_extraction_nested_traversal(self, tmp_path):
        """Test that complex nested path traversal is blocked."""
        # Create tar with deeply nested traversal attempt
        archive_path = tmp_path / "nested_traversal.tar.gz"
        
        with tarfile.open(archive_path, "w:gz") as tar:
            info = tarfile.TarInfo(name="./subdir/../../../../../../etc/passwd")
            info.size = 6
            tar.addfile(info, io.BytesIO(b"hacked"))
        
        bootstrapper = OfflineBootstrapper(
            archive_path,
            profile="core",
            dry_run=True,
        )
        
        success = bootstrapper._extract_wheelhouse()
        
        assert not success, "Extraction should fail for nested traversal"

    def test_validate_and_extract_safely_valid_members(self, tmp_path):
        """Test _validate_and_extract_safely with valid members."""
        # Create a valid tar.gz
        archive_path = tmp_path / "valid.tar.gz"
        archive_dir = tmp_path / "src"
        archive_dir.mkdir()
        
        (archive_dir / "file1.txt").write_text("content1")
        (archive_dir / "file2.txt").write_text("content2")
        
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(archive_dir / "file1.txt", arcname="file1.txt")
            tar.add(archive_dir / "file2.txt", arcname="file2.txt")
        
        bootstrapper = OfflineBootstrapper(
            archive_path,
            profile="core",
            dry_run=True,
        )
        
        extract_dir = tmp_path / "extract"
        extract_dir.mkdir()
        
        with tarfile.open(archive_path, "r:gz") as tar:
            # Should not raise an exception
            bootstrapper._validate_and_extract_safely(tar, str(extract_dir))
        
        # Verify files were extracted
        assert (extract_dir / "file1.txt").exists()
        assert (extract_dir / "file2.txt").exists()
        assert (extract_dir / "file1.txt").read_text() == "content1"

    def test_validate_and_extract_safely_rejects_traversal(self, tmp_path):
        """Test _validate_and_extract_safely rejects traversal."""
        archive_path = tmp_path / "malicious.tar.gz"
        
        with tarfile.open(archive_path, "w:gz") as tar:
            import io
            
            info = tarfile.TarInfo(name="../../../etc/passwd")
            info.size = 4
            tar.addfile(info, io.BytesIO(b"evil"))
        
        bootstrapper = OfflineBootstrapper(
            archive_path,
            profile="core",
            dry_run=True,
        )
        
        extract_dir = tmp_path / "extract"
        extract_dir.mkdir()
        
        with tarfile.open(archive_path, "r:gz") as tar:
            with pytest.raises(ValueError, match="path traversal"):
                bootstrapper._validate_and_extract_safely(tar, str(extract_dir))

    def test_extraction_preserves_legitimate_subdirectories(self, tmp_path, cleanup_bootstrapper):
        """Test that legitimate subdirectories are preserved during extraction."""
        # Create tar with legitimate nested structure
        archive_dir = tmp_path / "archive_src"
        archive_dir.mkdir()
        
        (archive_dir / "wheelhouse").mkdir()
        (archive_dir / "wheelhouse" / "subdir").mkdir()
        (archive_dir / "wheelhouse" / "subdir" / "package.whl").write_text("wheel")
        (archive_dir / "wheelhouse" / "manifest.json").write_text('{"wheels": {}}')
        
        archive_path = tmp_path / "valid.tar.gz"
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(archive_dir, arcname=".")
        
        bootstrapper = OfflineBootstrapper(
            archive_path,
            profile="core",
            dry_run=True,
        )
        cleanup_bootstrapper(bootstrapper)
        
        success = bootstrapper._extract_wheelhouse()
        
        assert success, "Extraction should succeed"
        assert (bootstrapper.wheelhouse_dir / "subdir" / "package.whl").exists()

    def test_extraction_handles_special_characters(self, tmp_path, cleanup_bootstrapper):
        """Test extraction with special but safe characters in filenames."""
        archive_dir = tmp_path / "archive_src"
        archive_dir.mkdir()
        
        (archive_dir / "wheelhouse").mkdir()
        (archive_dir / "wheelhouse" / "package-1.0-py3-none-any.whl").write_text("wheel")
        (archive_dir / "wheelhouse" / "manifest.json").write_text('{"wheels": {}}')
        
        archive_path = tmp_path / "valid.tar.gz"
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(archive_dir, arcname=".")
        
        bootstrapper = OfflineBootstrapper(
            archive_path,
            profile="core",
            dry_run=True,
        )
        cleanup_bootstrapper(bootstrapper)
        
        success = bootstrapper._extract_wheelhouse()
        
        assert success, "Extraction should succeed with special characters"
        assert (bootstrapper.wheelhouse_dir / "package-1.0-py3-none-any.whl").exists()


class TestExtractWhelhouseIntegration:
    """Integration tests for full extraction workflow."""

    def test_full_bootstrap_workflow_valid_archive(self, tmp_path, cleanup_bootstrapper):
        """Test complete bootstrap workflow with valid archive."""
        # Create a complete valid archive
        archive_dir = tmp_path / "archive_src"
        archive_dir.mkdir()
        
        (archive_dir / "wheelhouse").mkdir()
        (archive_dir / "wheelhouse" / "test-1.0-py3-none-any.whl").write_text("wheel1")
        (archive_dir / "wheelhouse" / "test2-2.0-py3-none-any.whl").write_text("wheel2")
        
        manifest = {
            "metadata": {"wheel_count": 2},
            "wheels": {
                "test-1.0-py3-none-any.whl": {
                    "sha256": "aabbccdd1234567890abcdef1234567890abcdef1234567890abcdef12345678"
                },
                "test2-2.0-py3-none-any.whl": {
                    "sha256": "eeffaabbccdd1234567890abcdef1234567890abcdef1234567890abcdef1234"
                },
            },
        }
        
        (archive_dir / "wheelhouse" / "manifest.json").write_text(json.dumps(manifest))
        
        archive_path = tmp_path / "wheelhouse.tar.gz"
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(archive_dir, arcname=".")
        
        bootstrapper = OfflineBootstrapper(
            archive_path,
            profile="core",
            dry_run=True,
        )
        cleanup_bootstrapper(bootstrapper)
        
        success = bootstrapper._extract_wheelhouse()
        
        assert success, "Extraction should succeed"
        assert len(list(bootstrapper.wheelhouse_dir.glob("*.whl"))) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
