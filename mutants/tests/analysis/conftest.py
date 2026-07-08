"""Conftest for analysis tests - disables torch fixtures."""

import pytest


@pytest.fixture(scope="function", autouse=False)
def ensure_cpu_device():
    """Override parent conftest fixture to disable torch requirement."""
    yield


# Mark all tests in this directory to skip torch setup
def pytest_collection_modifyitems(items):
    """Modify test items to skip torch-related fixtures."""
    for item in items:
        # Remove the ensure_cpu_device fixture if it's auto-used
        if hasattr(item, "fixturenames") and "ensure_cpu_device" in item.fixturenames:
            item.fixturenames.remove("ensure_cpu_device")
