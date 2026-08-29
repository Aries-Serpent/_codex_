"""
Test Codex Evaluator

Test module for codex evaluator.
"""

import json

import pytest

import tools.codex_evaluator as ce

# Skip all tests if optional dependencies are missing
pytestmark = pytest.mark.skipif(
    bool(ce.MISSING_OPTIONALS), reason=f"Optional dependencies missing: {ce.MISSING_OPTIONALS}"
)

RULES = {
    "rubric": {
        "hard_fail": {"activated_ci": True},
        "forbidden_cues": ["\\.github/workflows/"],
        "env_guard_regex": "^PYTEST_DISABLE_PLUGIN_AUTOLOAD=1\\s+pytest\\b",
    },
    "scoring": {"penalties": {"no_env_guard_when_pytest_present": 2}},
}


def test_optional_dependencies_available():
    """Verify optional dependencies are loaded when tests run."""
    assert ce.has_all_optional() is True, "Condition must be true"
    assert "pydantic" in ce.OPTIONAL_STATUS, "Condition must be true"
    assert "typer" in ce.OPTIONAL_STATUS, "Condition must be true"


def test_hard_fail_on_ci_activation():
    text = "We will add .github/workflows/new.yml and enable github actions."
    res = ce.evaluate_text(text, RULES)
    assert res.hard_fail, "Condition must be true"
    assert any(".github/workflows/" in r for r in res.hard_fail_reasons), "Condition must be true"


def test_env_guard_penalty_when_pytest_present_without_guard():
    text = "Run pytest -q"
    res = ce.evaluate_text(text, RULES)
    assert not res.hard_fail, "Condition must be true"
    assert res.score <= -2, "score is not valid"


def test_env_guard_ok_when_present():
    text = "Use PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests -q"
    res = ce.evaluate_text(text, RULES)
    assert not res.hard_fail, "Condition must be true"
    assert res.score >= 0, "score must be greater than zero"


def test_cli_smoke(tmp_path):
    rules_path = tmp_path / "rules.json"
    with open(rules_path, "w", encoding="utf-8") as f:
        json.dump(RULES, f)

    sample = {"message_text": "No CI activation here."}
    sample_path = tmp_path / "sample.json"
    with open(sample_path, "w", encoding="utf-8") as f:
        json.dump(sample, f)

    # Call main as a function
    rc = ce.main(["--rules", str(rules_path), "--input", str(sample_path)])
    assert rc == 0, "rc is not valid"
