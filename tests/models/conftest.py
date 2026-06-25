"""
Conftest Module

This module provides functionality for conftest.

Usage:
    from models.conftest import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

import pytest

# NOTE: HF_REVISION is intentionally set per-function via the autouse fixture
# below, NOT at module scope. Module-level os.environ assignment leaks across
# the entire test session (root cause of S105/S106/S107 failures — Pattern P-042).
# See: .codex/permanent_facts.md § HF_REVISION Leak Pattern


@pytest.fixture(autouse=True, scope="function")
def _isolate_hf_revision(monkeypatch):
    """Isolate HF_REVISION to the current test function.

    Prevents the env-var from leaking into tests that do not belong to
    tests/models/ (e.g. tests/space_traversal/test_peft_comprehensive/).
    """
    monkeypatch.setenv("HF_REVISION", "abcdef0")


pytest.importorskip("torch")
pytest.importorskip("transformers")
