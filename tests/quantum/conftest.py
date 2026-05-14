"""Shared pytest configuration for quantum tests.

This conftest module enables fixtures and helpers from
``tests.utils.quantum_helpers`` so they are available across the quantum
test suite without per-test imports.
"""

pytest_plugins = ("tests.utils.quantum_helpers",)
