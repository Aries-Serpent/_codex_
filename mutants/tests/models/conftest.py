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

import os

import pytest

# Set HF_REVISION to avoid validation errors when loading HuggingFace models
os.environ.setdefault("HF_REVISION", "abcdef0")

pytest.importorskip("torch")
pytest.importorskip("transformers")
