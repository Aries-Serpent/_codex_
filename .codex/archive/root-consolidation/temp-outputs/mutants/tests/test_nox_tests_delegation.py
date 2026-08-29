"""
Test Nox Tests Delegation

Test module for nox tests delegation.
"""

import importlib
from unittest.mock import MagicMock

import pytest

pytest.importorskip("nox")


def test_tests_session_delegates_to_coverage():
    """Test that tests session runs pytest with coverage directly (no delegation)."""
    # Import user noxfile; the decorated function remains callable.
    noxfile = importlib.import_module("noxfile")

    # Create a mock session with all required methods
    sess = MagicMock()
    sess.python = None
    sess.posargs = []

    # Call the session function
    noxfile.tests(sess)

    # Verify pytest was called with coverage (not delegated to separate session)
    # The session should call run() with pytest and --cov flags
    run_calls = [call for call in sess.run.call_args_list]
    pytest_calls = [call for call in run_calls if "pytest" in str(call)]

    # Should have at least one pytest call with coverage flags
    assert len(pytest_calls) > 0, "tests session must run pytest"

    # Check that coverage flags are present
    all_args = str(sess.run.call_args_list)
    assert "--cov" in all_args, "tests session must run pytest with coverage"
