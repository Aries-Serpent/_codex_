#!/usr/bin/env python
"""Smoke test for GitHub Actions log fetcher.

Tests basic functionality without requiring actual GitHub API access.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from services.github.types import CheckRun, CheckRunStatus, CheckRunConclusion
        print("✓ GitHub types imported successfully")
    except Exception as e:
        print(f"✗ Failed to import GitHub types: {e}")
        return False
    
    try:
        from services.github.client import GitHubClient, GitHubClientSync
        print("✓ GitHub client imported successfully")
    except Exception as e:
        print(f"✗ Failed to import GitHub client: {e}")
        return False
    
    try:
        from codex.cli_github_logs import cli
        print("✓ CLI module imported successfully")
    except Exception as e:
        print(f"✗ Failed to import CLI module: {e}")
        return False
    
    try:
        from codex.api.github_logs import router
        print("✓ API module imported successfully")
    except Exception as e:
        print(f"✗ Failed to import API module: {e}")
        return False
    
    try:
        from mcp.tools.github_logs import fetch_check_run_logs, GITHUB_LOGS_TOOLS
        print("✓ MCP tools imported successfully")
    except Exception as e:
        print(f"✗ Failed to import MCP tools: {e}")
        return False
    
    return True


def test_cli_help():
    """Test CLI help commands."""
    print("\nTesting CLI commands...")
    
    try:
        from click.testing import CliRunner
        from codex.cli import cli as main_cli
        
        runner = CliRunner()
        
        # Test main github-logs command
        result = runner.invoke(main_cli, ['github-logs', '--help'])
        if result.exit_code != 0:
            print(f"✗ github-logs --help failed: {result.output}")
            return False
        print("✓ github-logs --help works")
        
        # Test check-run subcommand help
        result = runner.invoke(main_cli, ['github-logs', 'check-run', '--help'])
        if result.exit_code != 0:
            print(f"✗ github-logs check-run --help failed: {result.output}")
            return False
        print("✓ github-logs check-run --help works")
        
        # Test list-check-runs subcommand help
        result = runner.invoke(main_cli, ['github-logs', 'list-check-runs', '--help'])
        if result.exit_code != 0:
            print(f"✗ github-logs list-check-runs --help failed: {result.output}")
            return False
        print("✓ github-logs list-check-runs --help works")
        
    except Exception as e:
        print(f"✗ CLI test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def test_type_creation():
    """Test creating type instances."""
    print("\nTesting type creation...")
    
    try:
        from services.github.types import CheckRun, CheckRunStatus, CheckRunConclusion
        
        check_run = CheckRun(
            id=12345,
            name="Test Run",
            head_sha="abc123",
            status=CheckRunStatus.COMPLETED,
            conclusion=CheckRunConclusion.SUCCESS,
            html_url="https://github.com/test"
        )
        
        assert check_run.id == 12345
        assert check_run.is_completed
        assert check_run.is_successful
        assert not check_run.is_failed
        
        print("✓ CheckRun type creation works")
        
    except Exception as e:
        print(f"✗ Type creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def main():
    """Run all smoke tests."""
    print("=" * 60)
    print("GitHub Actions Log Fetcher - Smoke Tests")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("CLI Help", test_cli_help()))
    results.append(("Type Creation", test_type_creation()))
    
    print("\n" + "=" * 60)
    print("Test Results")
    print("=" * 60)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(passed for _, passed in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All smoke tests passed!")
        print("=" * 60)
        return 0
    else:
        print("✗ Some tests failed")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
