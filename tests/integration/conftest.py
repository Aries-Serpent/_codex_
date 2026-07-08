"""
Conftest for integration tests with validation gate framework.

This file imports and exposes the validation gate fixtures.
"""

import pytest
from tests.integration.conftest_validation_gates import (
    get_gate_registry,
    validation_gates as validation_gates_fixture,
    execute_validation_gates as execute_validation_gates_fixture,
)

# Re-export fixtures
pytest_plugins = ['tests.integration.conftest_validation_gates']
