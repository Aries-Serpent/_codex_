"""
Test Import Codex

Test module for import codex.
"""
import pytest
    import codex


def test_import_codex():

    assert codex is not None, "codex must be initialized"
