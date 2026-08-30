"""
Conftest Module

This module provides functionality for conftest.

Usage:
    from multilingual.conftest import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

import pytest

pytest.importorskip("transformers")
pytest.importorskip("sentencepiece")
