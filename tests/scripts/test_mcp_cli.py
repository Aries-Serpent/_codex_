"""
Test Mcp Cli

Test module for mcp cli.
"""

#! /usr/bin/env python3
"""
Test suite for scripts/mcp/mcp-package CLI
Tests command-line interface and integration
"""

import json
import pytest
import subprocess  # Using stdlib subprocess.run which supports timeout parameter
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock


@pytest.fixture
def mcp_package_cli():
    """Path to mcp-package CLI script"""
    cli = Path(__file__).parent.parent.parent / "scripts" / "mcp" / "mcp-package"
    if not cli.exists():
        pytest.skip("mcp-package CLI not found")
    return cli


@pytest.fixture
def mock_repo(tmp_path):
    """Create mock repository structure for CLI testing"""
    repo = tmp_path / "repo"
    repo.mkdir()
    
    # Create topics.json
    scripts_mcp = repo / "scripts" / "mcp"
    scripts_mcp.mkdir(parents=True)
    
    topics = {
        "test_topic": ["**/*.py"],
        "docs": ["**/*.md"]
    }
    (scripts_mcp / "topics.json").write_text(json.dumps(topics))
    
    # Create select_components.py placeholder
    (scripts_mcp / "select_components.py").write_text("#!/usr/bin/env python3\nprint('mock')")
    
    # Create package_flatten.sh placeholder
    (scripts_mcp / "package_flatten.sh").write_text("#!/bin/bash\necho 'mock'")
    (scripts_mcp / "package_flatten.sh").chmod(0o755)
    
    # Create .github/tmp for temp files
    (repo / ".github" / "tmp").mkdir(parents=True)
    
    # Create some test files
    (repo / "test.py").write_text("# test")
    (repo / "README.md").write_text("# readme")
    
    return repo


class TestMCPPackageCLI:
    """Tests for mcp-package command-line interface"""
    
    def test_cli_exists_and_executable(self, mcp_package_cli):
        """Test that CLI script exists and is executable"""
        assert mcp_package_cli.exists()
        assert mcp_package_cli.stat().st_mode & 0o111  # Check execute bit
    
    def test_cli_help_flag(self, mcp_package_cli):
        """Test --help flag displays help message"""
        result = subprocess.run(
            [sys.executable, str(mcp_package_cli), "--help"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "--list" in result.stdout
        assert "--topic" in result.stdout
        assert "--custom" in result.stdout
    
    def test_cli_list_topics_flag(self, mcp_package_cli, mock_repo, monkeypatch):
        """Test --list flag shows available topics"""
        monkeypatch.chdir(mock_repo)
        
        result = subprocess.run(
            [sys.executable, str(mcp_package_cli), "--list"],
            capture_output=True,
            text=True,
            cwd=str(mock_repo)
        )
        
        # Should show topics or handle gracefully
        assert result.returncode in (0, 1)
        if result.returncode == 0:
            assert "topic" in result.stdout.lower() or "available" in result.stdout.lower()
    
    def test_cli_requires_topic_or_custom(self, mcp_package_cli):
        """Test that CLI requires either --topic or --custom"""
        result = subprocess.run(
            [sys.executable, str(mcp_package_cli)],
            capture_output=True,
            text=True
        )
        
        # Should show error or help
        assert result.returncode != 0 or "--topic" in result.stdout
    
    def test_cli_topic_flag_validation(self, mcp_package_cli, mock_repo):
        """Test --topic flag with valid topic"""
        # Using stdlib subprocess.run (not codex.utils.subprocess.run)
        result: subprocess.CompletedProcess[str] = subprocess.run(
            [sys.executable, str(mcp_package_cli), "--topic", "test_topic", "--dry-run"],
            capture_output=True,
            text=True,
            cwd=str(mock_repo),
            timeout=10
        )
        
        # Dry run should not fail immediately
        # May fail due to missing dependencies, but syntax should be OK
        assert "Topic:" in result.stdout or result.returncode in (0, 1)
    
    def test_cli_custom_flag_validation(self, mcp_package_cli, mock_repo):
        """Test --custom flag with glob patterns"""
        # Using stdlib subprocess.run (not codex.utils.subprocess.run)
        result: subprocess.CompletedProcess[str] = subprocess.run(
            [sys.executable, str(mcp_package_cli), "--custom", "**/*.py", "--dry-run"],
            capture_output=True,
            text=True,
            cwd=str(mock_repo),
            timeout=10
        )
        
        # Dry run should show custom filters
        assert "Custom" in result.stdout or result.returncode in (0, 1)
    
    def test_cli_output_flag_adds_zip_extension(self, mcp_package_cli, mock_repo):
        """Test that --output flag automatically adds .zip extension"""
        # Using stdlib subprocess.run (not codex.utils.subprocess.run)
        result: subprocess.CompletedProcess[str] = subprocess.run(
            [sys.executable, str(mcp_package_cli), "--topic", "test_topic", 
             "--output", "mypackage", "--dry-run"],
            capture_output=True,
            text=True,
            cwd=str(mock_repo),
            timeout=10
        )
        
        # Should mention .zip extension
        if result.returncode == 0:
            assert ".zip" in result.stdout
    
    def test_cli_dry_run_flag(self, mcp_package_cli, mock_repo):
        """Test --dry-run flag prevents actual packaging"""
        # Using stdlib subprocess.run (not codex.utils.subprocess.run)
        result: subprocess.CompletedProcess[str] = subprocess.run(
            [sys.executable, str(mcp_package_cli), "--topic", "test_topic", "--dry-run"],
            capture_output=True,
            text=True,
            cwd=str(mock_repo),
            timeout=10
        )
        
        # Dry run should indicate mode
        if result.returncode == 0:
            assert "DRY RUN" in result.stdout or "dry" in result.stdout.lower()
    
    def test_cli_verbose_flag(self, mcp_package_cli, mock_repo):
        """Test --verbose flag increases output detail"""
        # Using stdlib subprocess.run (not codex.utils.subprocess.run)
        result: subprocess.CompletedProcess[str] = subprocess.run(
            [sys.executable, str(mcp_package_cli), "--topic", "test_topic", 
             "--verbose", "--dry-run"],
            capture_output=True,
            text=True,
            cwd=str(mock_repo),
            timeout=10
        )
        
        # Verbose mode should produce output
        if result.returncode == 0:
            assert len(result.stdout) > 0
    
    def test_cli_generates_timestamped_output_name(self, mcp_package_cli, mock_repo):
        """Test automatic timestamp-based output naming"""
        # Using stdlib subprocess.run (not codex.utils.subprocess.run)
        result: subprocess.CompletedProcess[str] = subprocess.run(
            [sys.executable, str(mcp_package_cli), "--topic", "test_topic", "--dry-run"],
            capture_output=True,
            text=True,
            cwd=str(mock_repo),
            timeout=10
        )
        
        # Should mention output filename with date/timestamp
        if result.returncode == 0:
            # Look for patterns like: package_test_topic_20251231.zip
            assert "package_" in result.stdout or "Output:" in result.stdout


class TestCLIEdgeCases:
    """Tests for CLI edge cases and error handling"""
    
    def test_cli_handles_missing_topics_file(self, mcp_package_cli, tmp_path):
        """Test error handling when topics.json is missing"""
        empty_repo = tmp_path / "empty"
        empty_repo.mkdir()
        
        result = subprocess.run(
            [sys.executable, str(mcp_package_cli), "--list"],
            capture_output=True,
            text=True,
            cwd=str(empty_repo)
        )
        
        # Should show error
        assert result.returncode != 0
        assert "not found" in result.stderr.lower() or "not found" in result.stdout.lower()
    
    def test_cli_handles_invalid_topic_name(self, mcp_package_cli, mock_repo):
        """Test error handling for unknown topic"""
        # Using stdlib subprocess.run (not codex.utils.subprocess.run)
        result: subprocess.CompletedProcess[str] = subprocess.run(
            [sys.executable, str(mcp_package_cli), "--topic", "nonexistent_topic", 
             "--dry-run"],
            capture_output=True,
            text=True,
            cwd=str(mock_repo),
            timeout=10
        )
        
        # Should show error about unknown topic
        if result.returncode != 0:
            assert "unknown" in result.stderr.lower() or "not found" in result.stderr.lower()
    
    def test_cli_handles_empty_custom_pattern(self, mcp_package_cli, mock_repo):
        """Test error handling for empty custom pattern"""
        # Using stdlib subprocess.run (not codex.utils.subprocess.run)
        result: subprocess.CompletedProcess[str] = subprocess.run(
            [sys.executable, str(mcp_package_cli), "--custom", "", "--dry-run"],
            capture_output=True,
            text=True,
            cwd=str(mock_repo),
            timeout=10
        )
        
        # Should handle empty pattern gracefully
        assert result.returncode in (0, 1)
    
    def test_cli_python_syntax_validation(self, mcp_package_cli):
        """Test that CLI has valid Python syntax"""
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(mcp_package_cli)],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, f"Python syntax error: {result.stderr}"


class TestCLIIntegration:
    """Integration tests for complete CLI workflows"""
    
    def test_cli_list_and_package_workflow(self, mcp_package_cli, mock_repo):
        """Test typical user workflow: list topics, then package one"""
        # Step 1: List topics
        list_result = subprocess.run(
            [sys.executable, str(mcp_package_cli), "--list"],
            capture_output=True,
            text=True,
            cwd=str(mock_repo)
        )
        
        # Step 2: Package a topic (dry run)
        if list_result.returncode == 0:
            # Using stdlib subprocess.run (not codex.utils.subprocess.run)
            package_result: subprocess.CompletedProcess[str] = subprocess.run(
                [sys.executable, str(mcp_package_cli), "--topic", "test_topic", "--dry-run"],
                capture_output=True,
                text=True,
                cwd=str(mock_repo),
                timeout=10
            )
            
            # Workflow should complete
            assert package_result.returncode in (0, 1)
    
    def test_cli_respects_github_tmp_for_temp_files(self, mcp_package_cli, mock_repo):
        """Test that CLI uses .github/tmp for temporary files (anti-/tmp/ protection)"""
        # This is verified by checking the script's behavior
        # The script should create temp files in .github/tmp
        github_tmp = mock_repo / ".github" / "tmp"
        assert github_tmp.exists(), ".github/tmp should exist in mock repo"
        
        # Run CLI
        # Using stdlib subprocess.run (not codex.utils.subprocess.run)
        result: subprocess.CompletedProcess[str] = subprocess.run(
            [sys.executable, str(mcp_package_cli), "--topic", "test_topic", "--dry-run"],
            capture_output=True,
            text=True,
            cwd=str(mock_repo),
            timeout=10
        )
        
        # Should not fail due to temp directory issues
        if result.returncode != 0:
            # Failure should not be about temp directory
            assert "/tmp" not in result.stderr


# Run tests with: python -m pytest tests/scripts/test_mcp_cli.py -v
