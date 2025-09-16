from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest


def _install_runtime_stubs(module, monkeypatch: pytest.MonkeyPatch, output_text: str) -> None:
    class DummyTokenizer:
        vocab_size = 10
        eos_token_id = 0
        pad_token_id = 0

        def encode(self, text: str, return_tensors: str | None = None):
            self.last_prompt = text
            return "prompt-ids"

        def decode(self, tokens, skip_special_tokens: bool = True) -> str:
            return tokens

    class Module:
        class AutoTokenizer:  # pragma: no cover - simple stub
            @classmethod
            def from_pretrained(cls, name: str):
                return DummyTokenizer()

    monkeypatch.setattr(module, "optional_import", lambda name: (Module, True))
    monkeypatch.setattr(module, "load_model_with_optional_lora", lambda *a, **k: object())
    monkeypatch.setattr(module, "generate", lambda *a, **k: [output_text])


def _load_generate_module(monkeypatch: pytest.MonkeyPatch, output_text: str):
    fake_models = SimpleNamespace(generate=lambda *a, **k: [output_text])
    monkeypatch.setitem(sys.modules, "codex_ml.models.generate", fake_models)
    sys.modules.pop("codex_ml.cli.generate", None)
    module = importlib.import_module("codex_ml.cli.generate")
    module = importlib.reload(module)
    _install_runtime_stubs(module, monkeypatch, output_text)
    return module


def _write_policy(tmp_path: Path) -> Path:
    policy = tmp_path / "policy.yaml"
    log_file = tmp_path / "events.ndjson"
    policy.write_text(
        (
            "version: 1\n"
            f"log_path: {log_file}\n"
            "rules:\n"
            "  - id: block-forbidden\n"
            "    action: block\n"
            "    severity: high\n"
            "    match:\n"
            '      literals: ["forbidden"]\n'
            "  - id: redact-secret\n"
            "    action: redact\n"
            "    severity: high\n"
            '    replacement: "{REDACTED}"\n'
            "    match:\n"
            '      patterns: ["SECRET[0-9]+"]\n'
        ),
        encoding="utf-8",
    )
    return policy


def test_generate_blocks_disallowed_prompt(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    policy = _write_policy(tmp_path)
    module = _load_generate_module(monkeypatch, "clean output")
    with pytest.raises(SystemExit) as excinfo:
        module.main(["--prompt", "forbidden prompt", "--safety-policy", str(policy)])
    assert "Safety violation (prompt)" in str(excinfo.value)
    log_file = tmp_path / "events.ndjson"
    entries = [json.loads(line) for line in log_file.read_text().splitlines()]
    assert any(entry["rule_id"] == "block-forbidden" for entry in entries)


def test_generate_bypass_outputs_redacted(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys):
    policy = _write_policy(tmp_path)
    module = _load_generate_module(monkeypatch, "unsafe SECRET999 output")
    module.main(
        [
            "--prompt",
            "forbidden prompt",
            "--safety-policy",
            str(policy),
            "--safety-bypass",
        ]
    )
    captured = capsys.readouterr().out.strip()
    assert "«REDACTED" in captured or "{REDACTED}" in captured
    log_file = tmp_path / "events.ndjson"
    entries = [json.loads(line) for line in log_file.read_text().splitlines()]
    assert any(entry["action"] in {"bypass", "redact"} for entry in entries)
