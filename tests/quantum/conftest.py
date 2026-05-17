"""Shared pytest configuration for quantum tests.

This conftest module exposes fixtures and helpers from
``tests.utils.quantum_helpers`` so they are available across the quantum
test suite without per-test imports.

``pytest_plugins`` declarations are not allowed in non-root conftest files
in modern pytest; the fixture is therefore imported and re-exposed directly.
"""

from tests.utils.quantum_helpers import quantum_plugin_fixture  # noqa: F401
