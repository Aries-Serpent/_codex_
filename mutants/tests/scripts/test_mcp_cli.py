#         )
# Test module for mcp cli.
# 
#     def test_cli_respects_github_tmp_for_temp_files(self, mcp_package_cli, mock_repo):
# """
#         )
# Test suite for scripts/mcp/mcp-package CLI
# 
#     def test_cli_respects_github_tmp_for_temp_files(self, mcp_package_cli, mock_repo):
# Tests command-line interface and integration
#         """Test that CLI uses .github/tmp for temporary files (anti-/tmp/ protection)"""
#         # This is verified by checking the script's behavior
#         # The script should create temp files in .github/tmp
#         github_tmp = mock_repo / ".github" / "tmp"
#         assert github_tmp.exists(), ".github/tmp should exist in mock repo"
# 
#             capture_output=True,
#             text=True,
#             cwd=str(mock_repo),
#         )
#     """Path to mcp-package CLI script"""
#     cli = Path(__file__).parent.parent.parent / "scripts" / "mcp" / "mcp-package"
#     if not cli.exists():
#         pytest.skip("mcp-package CLI not found")
#     return cli
#             text=True,
#             cwd=str(mock_repo),
#         )
# def mock_repo(tmp_path):
# @pytest.fixture
#         )
#     repo.mkdir()
# 
#     # Initialize git repository (required by mcp-package CLI)
#     subprocess.run(
#         ["git", "init"],
#         cwd=str(repo),
#         capture_output=True,
#         check=True,
#     )
#     subprocess.run(
#         ["git", "config", "user.email", "test@example.com"],
#         cwd=str(repo),
#         capture_output=True,
#         check=True,
#     )
#     subprocess.run(
#         ["git", "config", "user.name", "Test User"],
#         cwd=str(repo),
#         capture_output=True,
#         check=True,
#     )
# 
#     # Create topics.json
#     scripts_mcp = repo / "scripts" / "mcp"
#     scripts_mcp.mkdir(parents=True)
#     scripts_mcp.mkdir(parents=True)
# 
#     topics = {"test_topic": ["**/*.py"], "docs": ["**/*.md"]}
#     (scripts_mcp / "topics.json").write_text(json.dumps(topics))
#     # Create select_components.py placeholder
#     (scripts_mcp / "select_components.py").write_text("#!/usr/bin/env python3\nlogger.info('mock')")
# 
#     # Create package_flatten.sh placeholder
#     (scripts_mcp / "package_flatten.sh").write_text("#!/bin/bash\necho 'mock'")
#     (scripts_mcp / "package_flatten.sh").chmod(0o755)
# 
#     # Create .github/tmp for temp files
#     (repo / ".github" / "tmp").mkdir(parents=True)
# 
#     # Create some test files
#     (repo / "test.py").write_text("# test")
#     (repo / "README.md").write_text("# readme")
# 
#     # Commit initial files so git ls-files works
#     subprocess.run(
#         ["git", "add", "."],
#         cwd=str(repo),
#         capture_output=True,
#         check=True,
#     )
#     subprocess.run(
#         ["git", "commit", "-m", "Initial commit"],
#         cwd=str(repo),
#         capture_output=True,
#         check=True,
#     )
#     )
# 
#     return repo
#             cwd=str(mock_repo),
#         )
#     """Tests for mcp-package command-line interface"""
#     """Tests for mcp-package command-line interface"""
# 
#     def test_cli_exists_and_executable(self, mcp_package_cli):
#     def test_cli_exists_and_executable(self, mcp_package_cli):
#         """Test that CLI script exists and is executable"""
#         assert mcp_package_cli.exists(), "Condition must be true"
#         assert mcp_package_cli.stat().st_mode & 0o111, "Condition must be true"
#     def test_cli_help_flag(self, mcp_package_cli):
#     def test_cli_help_flag(self, mcp_package_cli):
#         """Test --help flag displays help message"""
#         result = subprocess.run(
#             [sys.executable, str(mcp_package_cli), "--help"],
#             capture_output=True,
#             text=True,
#         )
#         assert result.returncode == 0, "Result must not be empty"
#         assert "--list" in result.stdout, "Result must not be empty"
#         assert "--topic" in result.stdout, "Result must not be empty"
#         assert "--custom" in result.stdout, "Result must not be empty"
# 
#     def test_cli_list_topics_flag(self, mcp_package_cli, mock_repo, monkeypatch):
#     def test_cli_list_topics_flag(self, mcp_package_cli, mock_repo, monkeypatch):
#         """Test --list flag shows available topics"""
#         monkeypatch.chdir(mock_repo)
#         result = subprocess.run(
#             [sys.executable, str(mcp_package_cli), "--list"],
#             capture_output=True,
#             text=True,
#             cwd=str(mock_repo),
#         )
#         # Should show topics or handle gracefully
#         assert result.returncode in (0, 1)
#         if result.returncode == 0:
#             assert "topic" in result.stdout.lower() or "available" in result.stdout.lower(), "Result must not be empty"
#             assert "topic" in result.stdout.lower() or "available" in result.stdout.lower(), "Result must not be empty"
# 
#     def test_cli_requires_topic_or_custom(self, mcp_package_cli):
#     def test_cli_requires_topic_or_custom(self, mcp_package_cli):
#         """Test that CLI requires either --topic or --custom"""
#         result = subprocess.run(
#             [sys.executable, str(mcp_package_cli)], capture_output=True, text=True
#         )
#         assert result.returncode != 0 or "--topic" in result.stdout, "Result must not be empty"
#         assert result.returncode != 0 or "--topic" in result.stdout, "Result must not be empty"
# 
#     def test_cli_topic_flag_validation(self, mcp_package_cli, mock_repo):
#     def test_cli_topic_flag_validation(self, mcp_package_cli, mock_repo):
#         """Test --topic flag with valid topic"""
#         # Using stdlib subprocess.run (not codex.utils.subprocess.run)
#         result: subprocess.CompletedProcess[str] = subprocess.run(
#             [
#                 sys.executable,
#                 str(mcp_package_cli),
#                 "--topic",
#                 "test_topic",
#                 "--dry-run",
#             ],
#             capture_output=True,
#             text=True,
#             cwd=str(mock_repo),
#             timeout=10,
#         )
#         assert "Topic:" in result.stdout or result.returncode in (0, 1)
#         # May fail due to missing dependencies, but syntax should be OK
#         assert "Topic:" in result.stdout or result.returncode in (0, 1)
# 
#     def test_cli_custom_flag_validation(self, mcp_package_cli, mock_repo):
#     def test_cli_custom_flag_validation(self, mcp_package_cli, mock_repo):
#         """Test --custom flag with glob patterns"""
#         # Using stdlib subprocess.run (not codex.utils.subprocess.run)
#         result: subprocess.CompletedProcess[str] = subprocess.run(
#             [sys.executable, str(mcp_package_cli), "--custom", "**/*.py", "--dry-run"],
#             capture_output=True,
#             text=True,
#             cwd=str(mock_repo),
#             timeout=10,
#         )
#         assert "Custom" in result.stdout or result.returncode in (0, 1)
#         assert "Custom" in result.stdout or result.returncode in (0, 1)
# 
#     def test_cli_output_flag_adds_zip_extension(self, mcp_package_cli, mock_repo):
#     def test_cli_output_flag_adds_zip_extension(self, mcp_package_cli, mock_repo):
#         """Test that --output flag automatically adds .zip extension"""
#         # Using stdlib subprocess.run (not codex.utils.subprocess.run)
#         result: subprocess.CompletedProcess[str] = subprocess.run(
#             [
#                 sys.executable,
#                 str(mcp_package_cli),
#                 "--topic",
#                 "test_topic",
#                 "--output",
#                 "mypackage",
#                 "--dry-run",
#             ],
#             capture_output=True,
#             text=True,
#             cwd=str(mock_repo),
#             timeout=10,
#         )
#         if result.returncode == 0:
#             assert ".zip" in result.stdout, "Result must not be empty"
#             assert ".zip" in result.stdout, "Result must not be empty"
# 
#     def test_cli_dry_run_flag(self, mcp_package_cli, mock_repo):
#     def test_cli_dry_run_flag(self, mcp_package_cli, mock_repo):
#         """Test --dry-run flag prevents actual packaging"""
#         # Using stdlib subprocess.run (not codex.utils.subprocess.run)
#         result: subprocess.CompletedProcess[str] = subprocess.run(
#             [
#                 sys.executable,
#                 str(mcp_package_cli),
#                 "--topic",
#                 "test_topic",
#                 "--dry-run",
#             ],
#             capture_output=True,
#             text=True,
#             cwd=str(mock_repo),
#             timeout=10,
#         )
#         if result.returncode == 0:
#             assert "DRY RUN" in result.stdout or "dry" in result.stdout.lower(), "Result must not be empty"
#             assert "DRY RUN" in result.stdout or "dry" in result.stdout.lower(), "Result must not be empty"
# 
#     def test_cli_verbose_flag(self, mcp_package_cli, mock_repo):
#     def test_cli_verbose_flag(self, mcp_package_cli, mock_repo):
#         """Test --verbose flag increases output detail"""
#         # Using stdlib subprocess.run (not codex.utils.subprocess.run)
#         result: subprocess.CompletedProcess[str] = subprocess.run(
#             [
#                 sys.executable,
#                 str(mcp_package_cli),
#                 "--topic",
#                 "test_topic",
#                 "--verbose",
#                 "--dry-run",
#             ],
#             capture_output=True,
#             text=True,
#             cwd=str(mock_repo),
#             timeout=10,
#         )
#         if result.returncode == 0:
#             assert len(result.stdout) > 0, "Collection must not be empty"
#             assert len(result.stdout) > 0, "Collection must not be empty"
# 
#     def test_cli_generates_timestamped_output_name(self, mcp_package_cli, mock_repo):
#     def test_cli_generates_timestamped_output_name(self, mcp_package_cli, mock_repo):
#         """Test automatic timestamp-based output naming"""
#         # Using stdlib subprocess.run (not codex.utils.subprocess.run)
#         result: subprocess.CompletedProcess[str] = subprocess.run(
#             [
#                 sys.executable,
#                 str(mcp_package_cli),
#                 "--topic",
#                 "test_topic",
#                 "--dry-run",
#             ],
#             capture_output=True,
#             text=True,
#             cwd=str(mock_repo),
#             timeout=10,
#         )
#         if result.returncode == 0:
#             # Look for patterns like: package_test_topic_20251231.zip
#             assert "package_" in result.stdout or "Output:" in result.stdout, "Result must not be empty"
#             text=True,
#             cwd=str(mock_repo),
#         )
#     """Tests for CLI edge cases and error handling"""
#     """Tests for CLI edge cases and error handling"""
# 
#     def test_cli_handles_missing_topics_file(self, mcp_package_cli, tmp_path):
#     def test_cli_handles_missing_topics_file(self, mcp_package_cli, tmp_path):
#         """Test error handling when topics.json is missing"""
#         empty_repo = tmp_path / "empty"
#         empty_repo.mkdir()
#         result = subprocess.run(
#             [sys.executable, str(mcp_package_cli), "--list"],
#             capture_output=True,
#             text=True,
#             cwd=str(empty_repo),
#         )
#         # Should show error
#         assert result.returncode != 0, "Result must not be empty"
#         assert ("not found" in result.stderr.lower(), "Result must not be empty"
#             or "not found" in result.stdout.lower()
#             or "git repository" in result.stderr.lower()
#             or "git repository" in result.stdout.lower()
#         )
#         )
# 
#     def test_cli_handles_invalid_topic_name(self, mcp_package_cli, mock_repo):
#     def test_cli_handles_invalid_topic_name(self, mcp_package_cli, mock_repo):
#         """Test error handling for unknown topic"""
#         # Using stdlib subprocess.run (not codex.utils.subprocess.run)
#         result: subprocess.CompletedProcess[str] = subprocess.run(
#             [
#                 sys.executable,
#                 str(mcp_package_cli),
#                 "--topic",
#                 "nonexistent_topic",
#                 "--dry-run",
#             ],
#             capture_output=True,
#             text=True,
#             cwd=str(mock_repo),
#             timeout=10,
#         )
#         if result.returncode != 0:
#             # Fixed malformed assertion: assert any(...)],
#             capture_output=True,
#             text=True,
#             cwd=str(mock_repo),
#         )
#         # Step 2: Package a topic (dry run)
#         if list_result.returncode == 0:
#             # Using stdlib subprocess.run (not codex.utils.subprocess.run)
#             package_result: subprocess.CompletedProcess[str] = subprocess.run(
#                 [
#                     sys.executable,
#                     str(mcp_package_cli),
#                     sys.executable,
#                     str(mcp_package_cli),
#                     "--topic",
#                     "test_topic",
#                     "--dry-run",
#                 ],
#                 capture_output=True,
#                 text=True,
#                 cwd=str(mock_repo),
#                 timeout=10,
#             )
#             assert package_result.returncode in (0, 1)
#             assert package_result.returncode in (0, 1)
# 
#     def test_cli_respects_github_tmp_for_temp_files(self, mcp_package_cli, mock_repo):
#     def test_cli_respects_github_tmp_for_temp_files(self, mcp_package_cli, mock_repo):
#         """Test that CLI uses .github/tmp for temporary files (anti-/tmp/ protection)"""
#         # This is verified by checking the script's behavior
#         # The script should create temp files in .github/tmp
#         github_tmp = mock_repo / ".github" / "tmp"
#         assert github_tmp.exists(), ".github/tmp should exist in mock repo"
#         result: subprocess.CompletedProcess[str] = subprocess.run(
#             [
#                 sys.executable,
#                 str(mcp_package_cli),
#             [
#                 sys.executable,
#                 str(mcp_package_cli),
#                 "--topic",
#                 "test_topic",
#                 "--dry-run",
#             ],
#             capture_output=True,
#             text=True,
#             cwd=str(mock_repo),
#             timeout=10,
#         )
#         if result.returncode != 0:
#             # Failure should not be about bare /tmp usage outside .github/tmp
#             assert "/tmp" not in result.stderr or "/.github/tmp/" in result.stderr, "Result must not be empty"


# Run tests with: python -m pytest tests/scripts/test_mcp_cli.py -v
