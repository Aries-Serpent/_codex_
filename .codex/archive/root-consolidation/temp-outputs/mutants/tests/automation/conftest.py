"""Conftest for automation tests."""

from __future__ import annotations

import pytest

# Skip tests if optional dependencies are missing
pytest.importorskip("omegaconf", reason="omegaconf required for automation tests")
pytest.importorskip("hydra", reason="hydra required for automation tests")
