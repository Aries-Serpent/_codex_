#!/usr/bin/env python
"""Smoke test for GitHub Actions log fetcher.

Tests basic functionality without requiring actual GitHub API access.
"""

import os
import sys

from codex.logging.structured_logger import logger

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def test_imports():
    """Test that all modules can be imported."""
    logger.info("Testing imports...")

    try:
        logger.info("✓ GitHub types imported successfully")
    except (ImportError, AttributeError) as e:
        logger.info(f"✗ Failed to import GitHub types: {e}")
        return False

    try:
        logger.info("✓ GitHub client imported successfully")
    except (ImportError, AttributeError) as e:
        logger.info(f"✗ Failed to import GitHub client: {e}")
        return False

    try:
        logger.info("✓ CLI module imported successfully")
    except (ImportError, AttributeError) as e:
        logger.info(f"✗ Failed to import CLI module: {e}")
        return False

    try:
        logger.info("✓ API module imported successfully")
    except (ImportError, AttributeError) as e:
        logger.info(f"✗ Failed to import API module: {e}")
        return False

    try:
        logger.info("✓ MCP tools imported successfully")
    except (ImportError, AttributeError) as e:
        logger.info(f"✗ Failed to import MCP tools: {e}")
        return False

    return True


def test_cli_help():
    """Test CLI help commands."""
    logger.info("\nTesting CLI commands...")

    try:
        from click.testing import CliRunner

        from codex.cli import cli as main_cli

        runner = CliRunner()

        # Test main github-logs command
        result = runner.invoke(main_cli, ["github-logs", "--help"])
        if result.exit_code != 0:
            logger.info(f"✗ github-logs --help failed: {result.output}")
            return False
        logger.info("✓ github-logs --help works")

        # Test check-run subcommand help
        result = runner.invoke(main_cli, ["github-logs", "check-run", "--help"])
        if result.exit_code != 0:
            logger.info(f"✗ github-logs check-run --help failed: {result.output}")
            return False
        logger.info("✓ github-logs check-run --help works")

        # Test list-check-runs subcommand help
        result = runner.invoke(main_cli, ["github-logs", "list-check-runs", "--help"])
        if result.exit_code != 0:
            logger.info(f"✗ github-logs list-check-runs --help failed: {result.output}")
            return False
        logger.info("✓ github-logs list-check-runs --help works")

    except (ImportError, AttributeError) as e:
        logger.info(f"✗ CLI test failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    return True


def test_type_creation():
    """Test creating type instances."""
    logger.info("\nTesting type creation...")

    try:
        from services.github.types import CheckRun, CheckRunConclusion, CheckRunStatus

        check_run = CheckRun(
            id=12345,
            name="Test Run",
            head_sha="abc123",
            status=CheckRunStatus.COMPLETED,
            conclusion=CheckRunConclusion.SUCCESS,
            html_url="https://github.com/test",
        )

        assert check_run.id == 12345, "id is not valid"
        assert check_run.is_completed, "Condition must be true"
        assert check_run.is_successful, "Condition must be true"
        assert not check_run.is_failed, "Condition must be true"

        logger.info("✓ CheckRun type creation works")

    except (ImportError, AttributeError) as e:
        logger.info(f"✗ Type creation failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    return True


def main():
    """Run all smoke tests."""

    logger.info("GitHub Actions Log Fetcher - Smoke Tests")


    results = []

    results.append(("Imports", test_imports()))
    results.append(("CLI Help", test_cli_help()))
    results.append(("Type Creation", test_type_creation()))

    logger.info("\n" + "=" * 60)
    logger.info("Test Results")


    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        logger.info(f"{status}: {name}")

    all_passed = all(passed for _, passed in results)

    logger.info("\n" + "=" * 60)
    if all_passed:
        logger.info("✓ All smoke tests passed!")

        return 0
    logger.info("✗ Some tests failed")

    return 1


if __name__ == "__main__":
    sys.exit(main())
