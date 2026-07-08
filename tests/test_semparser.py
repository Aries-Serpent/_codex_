"""
Test Semparser

Test module for semparser.
"""

from codex_digest.semparser import SemParser


def test_semparser_intents():
    sp = SemParser()
    text = "Please audit the repo and fix pre-commit hang; run pytest with coverage."
    pr = sp.parse(text)
    names = [i.name for i in pr.intents]
    assert "AUDIT_REPO" in names, "Condition must be true"
    assert "FIX_PRECOMMIT" in names, "Condition must be true"
    assert "TEST_COVERAGE" in names, "Condition must be true"
