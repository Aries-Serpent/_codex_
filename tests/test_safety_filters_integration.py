from __future__ import annotations

from pathlib import Path

import pytest

from codex_ml.safety import SafetyConfig, sanitize_prompt


def _aws_token() -> str:
    return "AKIA1234567890" + "ABCD" + "EF"


def _slack_token() -> str:
    return "xoxb-" + "abcdefghij" + "klm"


def _google_api_key() -> str:
    return "AIza" + "A" * 35


def _password_kv() -> str:
    return "pass" + "word=supersecret"


def _api_key_kv() -> str:
    return "api" + "_key=deadbeef"


def test_sanitize_prompt_redacts_common_tokens() -> None:
    text = f"{_password_kv()} {_aws_token()} {_slack_token()} {_google_api_key()} {_api_key_kv()}"
    result = sanitize_prompt(text, SafetyConfig())
    redacted = result["text"]
    assert "supersecret" not in redacted
    assert _aws_token() not in redacted
    assert _slack_token() not in redacted
    assert _google_api_key() not in redacted
    assert _api_key_kv() not in redacted
    assert "«REDACTED:SECRET»" in redacted


def test_policy_yaml_safe_loading_and_overrides() -> None:
    bad_yaml = "!!python/object/apply:os.system ['echo hacked']"
    safe_text = sanitize_prompt("hello", SafetyConfig(), policy_yaml=bad_yaml)
    assert safe_text["text"] == "hello"

    policy_yaml = "regex:\n  - token"
    augmented = sanitize_prompt("token here", SafetyConfig(), policy_yaml=policy_yaml)
    assert augmented["text"] == "«REDACTED:SECRET» here"


def test_training_invokes_prompt_sanitizer(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    import codex_ml.training.__init__ as training
    from codex_ml.safety.sanitizers import sanitize_prompt as sanitize_impl

    calls: list[str] = []

    def tracking_sanitize(
        text: str, cfg: SafetyConfig | None = None, *, policy_yaml: str | None = None
    ):
        result = sanitize_impl(text, cfg, policy_yaml=policy_yaml)
        calls.append(result["text"])
        return result

    monkeypatch.setattr(training, "sanitize_prompt", tracking_sanitize, raising=False)
    monkeypatch.setattr(training, "set_reproducible", lambda *_a, **_k: None, raising=False)
    monkeypatch.setattr(training, "export_environment", lambda *_a, **_k: None, raising=False)

    dataset = {
        "train_texts": [f"{_api_key_kv()} {_aws_token()}", "just text"],
        "eval_texts": [],
        "format": "text",
    }
    cfg = training.TrainingRunConfig(
        output_dir=str(tmp_path / "run"),
        checkpoint_dir=str(tmp_path / "run" / "ckpt"),
        dataset=dataset,
    )
    cfg.safety = training.SafetySettings(enabled=False)

    result = training.run_functional_training(cfg)

    assert calls, "sanitize_prompt should be invoked during training"
    assert any("«REDACTED:SECRET»" in entry for entry in calls)
    assert "metrics" in result and isinstance(result["metrics"], list)
