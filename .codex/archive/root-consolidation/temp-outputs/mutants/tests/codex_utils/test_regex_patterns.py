"""Ensure codex_utils regex patterns remain importable and valid."""

from __future__ import annotations

import re

import pytest


@pytest.mark.parametrize("pattern_name", ["ENV_ASSIGNMENT", "PEM_BLOCK"])
def test_patterns_compile(pattern_name: str) -> None:
    from codex_utils import regex_patterns

    pattern = getattr(regex_patterns, pattern_name)
    assert isinstance(pattern, (str, re.Pattern))
    compiled = re.compile(pattern) if isinstance(pattern, str) else pattern
    assert compiled.search("TEST=1") is not None or pattern_name == "PEM_BLOCK", "pattern_name must be initialized"
