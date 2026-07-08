"""ML Module Pytest Configuration and Fixtures.

Provides fixtures and configuration for ensuring ML test stability,
reproducibility, and isolation.
"""

import random
import pytest


@pytest.fixture(autouse=True)
def seed_control():
    """Reset random seed before each test for reproducibility.
    
    This fixture ensures that each test starts with a clean random state
    (seed=42) to prevent state leakage between tests. This is critical for
    ML reproducibility tests which rely on deterministic behavior.
    
    Scope: function (runs before/after each test)
    Auto-use: True (automatically applied to all tests)
    """
    # Reset seed before test
    random.seed(42)
    yield
    # Note: No cleanup needed as next test resets to seed=42


@pytest.fixture(autouse=True)
def clear_random_state():
    """Ensure random module state is clean between tests.
    
    Additional safety measure to prevent any state leakage from
    previous tests that might use random operations.
    """
    yield
    # Reset after each test
    random.seed(42)
    _ = random.random()  # Consume one value to advance state


# Custom markers for test categorization
def pytest_configure(config):
    """Register custom pytest markers."""
    config.addinivalue_line(
        "markers",
        "isolation: mark test as requiring isolation (not run with pytest-randomly)"
    )
    config.addinivalue_line(
        "markers",
        "ml_reproducibility: mark test as ML reproducibility test"
    )
    config.addinivalue_line(
        "markers",
        "threading: mark test as involving threading operations"
    )
    config.addinivalue_line(
        "markers",
        "concurrent: mark test as involving concurrent operations"
    )


# Pytest hook to handle test isolation
def pytest_runtest_setup(item):
    """Configure test setup for ML module tests."""
    # Ensure seed is reset at test start
    random.seed(42)
    
    # Mark all ML tests with ml_reproducibility if they use random
    if "random" in item.fspath.basename:
        item.add_marker(pytest.mark.ml_reproducibility)
