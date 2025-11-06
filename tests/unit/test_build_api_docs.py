"""Unit tests for tools/build_api_docs.py module filtering and list building."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add tools directory to path to import build_api_docs
tools_dir = Path(__file__).parent.parent.parent / "tools"
sys.path.insert(0, str(tools_dir))

import build_api_docs


class TestFilterModules:
    """Test the filter_modules function."""

    def test_filter_modules_returns_importable_only(self, tmp_path, monkeypatch):
        """Test that filter_modules returns only importable modules."""
        # Create a fake package structure
        package_dir = tmp_path / "test_package"
        package_dir.mkdir()
        (package_dir / "__init__.py").write_text("# dummy package")

        submodule_dir = package_dir / "submodule"
        submodule_dir.mkdir()
        (submodule_dir / "__init__.py").write_text("# dummy submodule")

        # Add tmp_path to sys.path
        monkeypatch.syspath_prepend(str(tmp_path))

        # Test with mix of importable and non-importable modules
        modules = ["test_package", "test_package.submodule", "nonexistent_module"]
        available = build_api_docs.filter_modules(modules)

        assert "test_package" in available
        assert "test_package.submodule" in available
        assert "nonexistent_module" not in available

    def test_filter_modules_handles_import_errors(self, caplog):
        """Test that filter_modules gracefully handles import errors."""
        modules = ["definitely_does_not_exist_module_12345"]

        with caplog.at_level("WARNING"):
            available = build_api_docs.filter_modules(modules)

        assert len(available) == 0
        assert "Skipping" in caplog.text

    def test_filter_modules_empty_input(self):
        """Test filter_modules with empty input."""
        result = build_api_docs.filter_modules([])
        assert result == []


class TestModuleListBuilding:
    """Test module list construction logic."""

    def test_main_includes_optional_by_default(self, monkeypatch):
        """Test that optional modules are included when not skipped."""
        # Mock filter_modules to track what it receives
        called_with = {}

        def mock_filter(modules):
            called_with["modules"] = list(modules)
            return modules

        monkeypatch.setattr(build_api_docs, "filter_modules", mock_filter)
        monkeypatch.setattr(build_api_docs, "check_pdoc_installed", lambda: True)
        monkeypatch.setattr(build_api_docs, "build_docs", lambda *args: None)

        # Simulate running main without --skip-optional
        with patch("sys.argv", ["build_api_docs.py"]):
            build_api_docs.main()

        # Should include both core and optional modules
        assert "codex.cli" in called_with["modules"]
        assert "codex.logging" in called_with["modules"]
        assert "codex_ml" in called_with["modules"]
        assert "codex_ml.peft" in called_with["modules"]
        assert "codex_ml.distributed" in called_with["modules"]

    def test_main_excludes_optional_when_skipped(self, monkeypatch):
        """Test that optional modules are excluded with --skip-optional."""
        called_with = {}

        def mock_filter(modules):
            called_with["modules"] = list(modules)
            return modules

        monkeypatch.setattr(build_api_docs, "filter_modules", mock_filter)
        monkeypatch.setattr(build_api_docs, "check_pdoc_installed", lambda: True)
        monkeypatch.setattr(build_api_docs, "build_docs", lambda *args: None)

        # Simulate running main with --skip-optional
        with patch("sys.argv", ["build_api_docs.py", "--skip-optional"]):
            build_api_docs.main()

        # Should include only core modules
        assert "codex.cli" in called_with["modules"]
        assert "codex.logging" in called_with["modules"]
        assert "codex_ml" not in called_with["modules"]
        assert "codex_ml.peft" not in called_with["modules"]
        assert "codex_ml.distributed" not in called_with["modules"]

    def test_main_respects_env_var(self, monkeypatch):
        """Test that CODEX_SKIP_OPTIONAL_IMPORTS environment variable works."""
        called_with = {}

        def mock_filter(modules):
            called_with["modules"] = list(modules)
            return modules

        monkeypatch.setattr(build_api_docs, "filter_modules", mock_filter)
        monkeypatch.setattr(build_api_docs, "check_pdoc_installed", lambda: True)
        monkeypatch.setattr(build_api_docs, "build_docs", lambda *args: None)
        monkeypatch.setenv("CODEX_SKIP_OPTIONAL_IMPORTS", "1")

        with patch("sys.argv", ["build_api_docs.py"]):
            build_api_docs.main()

        # Should exclude optional modules due to env var
        assert "codex_ml" not in called_with["modules"]

    def test_main_exits_when_no_modules_available(self, monkeypatch):
        """Test that main exits with error when no modules are importable."""
        monkeypatch.setattr(build_api_docs, "filter_modules", lambda m: [])
        monkeypatch.setattr(build_api_docs, "check_pdoc_installed", lambda: True)

        with patch("sys.argv", ["build_api_docs.py"]):
            with pytest.raises(SystemExit) as exc_info:
                build_api_docs.main()

            assert exc_info.value.code == 1


class TestLogging:
    """Test logging behavior."""

    def test_verbose_flag_enables_debug_logging(self, monkeypatch, caplog):
        """Test that --verbose enables debug-level logging."""
        monkeypatch.setattr(build_api_docs, "check_pdoc_installed", lambda: True)
        monkeypatch.setattr(build_api_docs, "filter_modules", lambda m: m)
        monkeypatch.setattr(build_api_docs, "build_docs", lambda *args: None)

        with patch("sys.argv", ["build_api_docs.py", "--verbose"]):
            with caplog.at_level("DEBUG"):
                build_api_docs.main()

        # Logger should be set to DEBUG level
        assert build_api_docs.logger.level <= 10  # DEBUG is 10

    def test_final_module_list_is_logged(self, monkeypatch, caplog):
        """Test that final module list is logged for visibility."""

        def mock_filter(modules):
            return ["codex.cli", "codex_ml"]

        monkeypatch.setattr(build_api_docs, "filter_modules", mock_filter)
        monkeypatch.setattr(build_api_docs, "check_pdoc_installed", lambda: True)
        monkeypatch.setattr(build_api_docs, "build_docs", lambda *args: None)

        with patch("sys.argv", ["build_api_docs.py"]):
            with caplog.at_level("INFO"):
                build_api_docs.main()

        # Should log the final module list
        assert "Final module list to document" in caplog.text
        assert "codex.cli" in caplog.text
        assert "codex_ml" in caplog.text
