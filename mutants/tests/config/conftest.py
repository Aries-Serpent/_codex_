"""
Conftest Module

This module provides functionality for conftest.

Usage:
    from config.conftest import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

import pytest

pytest.importorskip("yaml")
pytest.importorskip("omegaconf")
