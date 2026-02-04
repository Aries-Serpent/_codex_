"""
Conftest Module

This module provides functionality for conftest.

Usage:
    from pipeline.conftest import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

import pytest

pytest.importorskip("yaml")
pytest.importorskip("omegaconf")
pytest.importorskip("torch")
pytest.importorskip("transformers")
pytest.importorskip("hydra")
