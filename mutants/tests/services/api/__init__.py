"""Service API test package with optional dependency guards."""

import pytest

pytest.importorskip(
    "torch",
    reason="PyTorch is required for services API tests",
)
