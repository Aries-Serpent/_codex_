import json

import tools.codex_evaluator as ce

RULES = {
    "rubric": {
        "hard_fail": {"activated_ci": True},
        "forbidden_cues": ["\\.github/workflows/"],
        "env_guard_regex": "^PYTEST_DISABLE_PLUGIN_AUTOLOAD=1\\s+pytest\\b",
    },
    "scoring": {"penalties": {"no_env_guard_when_pytest_present": 2}},
}


def test_hard_fail_on_ci_activation():
    text = "We will add .github/workflows/new.yml and enable github actions."
    res = ce.evaluate_text(text, RULES)
    assert res.hard_fail
    assert any(".github/workflows/" in r for r in res.hard_fail_reasons)


def test_env_guard_penalty_when_pytest_present_without_guard():
    text = "Run pytest -q"
    res = ce.evaluate_text(text, RULES)
    assert not res.hard_fail
    assert res.score <= -2


def test_env_guard_ok_when_present():
    text = "Use PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests -q"
    res = ce.evaluate_text(text, RULES)
    assert not res.hard_fail
    assert res.score >= 0


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
    assert rc == 0
