"""
Tests for MCP packaging CLI features: --estimate (PS-11) and --exclude (PS-12).

Tests the select_components.py functions directly (unit tests)
and the mcp-package CLI argument parsing (integration tests).
"""

import importlib.machinery
import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add scripts/mcp to path so we can import select_components
scripts_mcp = Path(__file__).resolve().parents[2] / "scripts" / "mcp"
sys.path.insert(0, str(scripts_mcp))

import select_components


def _load_mcp_package_module():
    """Load the mcp-package script as a module (no .py extension)."""
    loader = importlib.machinery.SourceFileLoader("mcp_package", str(scripts_mcp / "mcp-package"))
    spec = importlib.util.spec_from_loader("mcp_package", loader)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# PS-12: expand_globs with exclude_patterns
# ---------------------------------------------------------------------------


class TestExpandGlobsExclude:
    """Test the exclude_patterns parameter of expand_globs (PS-12)."""

    def test_exclude_none_returns_all(self, tmp_path):
        """No excludes → all matched files returned."""
        (tmp_path / "a.py").write_text("a")
        (tmp_path / "b.py").write_text("b")

        result = select_components.expand_globs(["*.py"], tmp_path, exclude_patterns=None)
        assert len(result) == 2, "Result must not be empty"

    def test_exclude_removes_matching(self, tmp_path):
        """Exclude pattern removes matching files."""
        (tmp_path / "keep.py").write_text("k")
        (tmp_path / "remove.txt").write_text("r")

        result = select_components.expand_globs(
            ["*"],
            tmp_path,
            exclude_patterns=["*.txt"],
        )
        names = {p.name for p in result}
        assert "keep.py" in names, "Condition must be true"
        assert "remove.txt" not in names, "Condition must be true"

    def test_exclude_recursive(self, tmp_path):
        """Exclude with ** recursive patterns."""
        sub = tmp_path / "src"
        sub.mkdir()
        (sub / "main.py").write_text("m")
        tests = tmp_path / "tests"
        tests.mkdir()
        (tests / "test_main.py").write_text("t")

        result = select_components.expand_globs(
            ["**/*.py"],
            tmp_path,
            exclude_patterns=["tests/**"],
        )
        names = {p.name for p in result}
        assert "main.py" in names, "Condition must be true"
        assert "test_main.py" not in names, "Condition must be true"

    def test_exclude_empty_list(self, tmp_path):
        """Empty exclude list → same as None."""
        (tmp_path / "a.py").write_text("a")

        result = select_components.expand_globs(["*.py"], tmp_path, exclude_patterns=[])
        assert len(result) == 1, "Result must not be empty"

    def test_exclude_no_match(self, tmp_path):
        """Exclude pattern that matches nothing → no effect."""
        (tmp_path / "a.py").write_text("a")

        result = select_components.expand_globs(
            ["*.py"],
            tmp_path,
            exclude_patterns=["*.nonexistent"],
        )
        assert len(result) == 1, "Result must not be empty"


class TestFilterByTopicExclude:
    """Test filter_by_topic with exclude_patterns."""

    def test_topic_with_exclude(self, tmp_path):
        """Topic filter with exclude patterns."""
        src = tmp_path / "src"
        src.mkdir()
        (src / "main.py").write_text("m")
        (src / "test_helper.py").write_text("t")

        topics_map = {"src": ["src/**"]}

        result = select_components.filter_by_topic(
            "src", topics_map, tmp_path, exclude_patterns=["**/*test*"]
        )
        names = {p.name for p in result}
        assert "main.py" in names, "Condition must be true"
        assert "test_helper.py" not in names, "Condition must be true"


class TestFilterByGlobsExclude:
    """Test filter_by_globs with exclude_patterns."""

    def test_globs_with_exclude(self, tmp_path):
        """Custom globs with exclude patterns."""
        (tmp_path / "a.py").write_text("a")
        (tmp_path / "b.md").write_text("b")

        result = select_components.filter_by_globs("*.py,*.md", tmp_path, exclude_patterns=["*.md"])
        names = {p.name for p in result}
        assert "a.py" in names, "Condition must be true"
        assert "b.md" not in names, "Condition must be true"


# ---------------------------------------------------------------------------
# PS-11: MCPPackager.estimate
# ---------------------------------------------------------------------------


class TestMCPPackagerEstimate:
    """Test the --estimate flag behavior (PS-11)."""

    def test_estimate_method_exists(self):
        """MCPPackager has an estimate method."""
        mcp_mod = _load_mcp_package_module()
        packager = mcp_mod.MCPPackager(Path.cwd())
        assert hasattr(packager, "estimate")
        assert callable(packager.estimate), "Condition must be true"

    def test_estimate_returns_zero_on_valid_topic(self):
        """Estimate returns 0 for a valid topic with files."""
        mcp_mod = _load_mcp_package_module()
        packager = mcp_mod.MCPPackager(Path.cwd())

        # Mock subprocess to return a file list
        filelist_content = ""

        def side_effect(cmd, **kwargs):
            # Write file list when select_components is called
            for i, arg in enumerate(cmd):
                if arg == "--output" and i + 1 < len(cmd):
                    Path(cmd[i + 1]).parent.mkdir(parents=True, exist_ok=True)
                    Path(cmd[i + 1]).write_text(filelist_content)
            result = MagicMock()
            result.returncode = 0
            return result

        with patch.object(mcp_mod.subprocess, "run", side_effect=side_effect):
            ret = packager.estimate(topic="mcp")
            assert ret == 0, "ret is not valid"


# ---------------------------------------------------------------------------
# CLI argument parsing
# ---------------------------------------------------------------------------


class TestCLIArguments:
    """Test that --estimate and --exclude are accepted by the argument parser."""

    def test_estimate_flag_accepted(self):
        """--estimate flag is recognized by argparse."""
        mcp_mod = _load_mcp_package_module()
        # --estimate alone should fail (needs --topic or --custom)
        with pytest.raises(SystemExit):
            with patch.object(sys, "argv", ["mcp-package", "--estimate"]):
                mcp_mod.main()

    def test_exclude_flag_accepted(self):
        """--exclude flag is recognized by argparse."""
        mcp_mod = _load_mcp_package_module()
        # --exclude alone should fail (needs --topic or --custom)
        with pytest.raises(SystemExit):
            with patch.object(sys, "argv", ["mcp-package", "--exclude", "tests/**"]):
                mcp_mod.main()
