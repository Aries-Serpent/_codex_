from __future__ import annotations

from src.tools.codeowners_validate import validate_codeowners_text, validate_repo_codeowners


def test_validate_codeowners_happy_path():
    text = """
# Sample CODEOWNERS
* @org/team
/src/ @org/team
/tests/ @user
/docs/ @org/docsteam
"""
    rep = validate_codeowners_text(text)
    assert rep.exists is True
    assert rep.errors == []
    assert rep.default_rule is True
    assert rep.owners_ok is True
    assert rep.coverage["src"] and rep.coverage["tests"] and rep.coverage["docs"]


def test_validate_codeowners_missing_default_and_bad_owner():
    text = """
/src/ user_without_at
"""
    rep = validate_codeowners_text(text)
    assert rep.exists is True
    assert rep.owners_ok is False
    assert any("Default '*'" in w for w in rep.warnings)


def test_validate_repo_codeowners_not_found(tmp_path):
    rep = validate_repo_codeowners(tmp_path)
    assert rep.exists is False
    assert rep.errors and "not found" in rep.errors[0]