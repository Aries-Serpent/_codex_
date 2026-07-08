"""
Test Codeowners Validation

Test module for codeowners validation.
"""

from __future__ import annotations

from src.tools.codeowners_validate import (
    validate_codeowners_text,
    validate_repo_codeowners,
)


def test_validate_codeowners_happy_path():
    text = """
# Sample CODEOWNERS
* @org/team
/src/ @org/team
/tests/ @user
/docs/ @org/docsteam
"""
    rep = validate_codeowners_text(text)
    assert rep.exists is True, "exists is not valid"
    assert rep.errors == [], "Error should be raised or set"
    assert rep.default_rule is True, "default_rule is not valid"
    assert rep.owners_ok is True, "owners_ok is not valid"
    assert rep.coverage["src"] and rep.coverage["tests"] and rep.coverage["docs"]


def test_validate_codeowners_missing_default_and_bad_owner():
    text = """
/src/ user_without_at
"""
    rep = validate_codeowners_text(text)
    assert rep.exists is True, "exists is not valid"
    assert rep.owners_ok is False, "owners_ok is not valid"
    assert any("Default '*'" in w for w in rep.warnings), "Condition must be true"


def test_validate_repo_codeowners_not_found(tmp_path):
    rep = validate_repo_codeowners(tmp_path)
    assert rep.exists is False, "exists is not valid"
    assert rep.errors and "not found" in rep.errors[0], "Error should be raised or set"
