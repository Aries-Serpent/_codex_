from __future__ import annotations

import warnings

import pytest

from codex_ml.tokenization import api, compat


def test_whitespace_tokenizer_roundtrip() -> None:
    tok = api.WhitespaceTokenizer()
    ids = tok.encode("hello world")
    assert len(ids) == 2
    assert tok.decode(ids)


def test_load_tokenizer_uses_hf_adapter(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = {}

    class DummyAdapter:
        @staticmethod
        def load(target, use_fast: bool = True):
            calls["args"] = (target, use_fast)
            return {"target": target, "use_fast": use_fast}

    monkeypatch.setattr(api, "_load_hf_adapter", lambda: DummyAdapter)
    adapter = api.load_tokenizer(name="demo")
    assert adapter == {"target": "demo", "use_fast": True}
    assert calls["args"] == ("demo", True)


def test_deprecated_access_emits_warning() -> None:
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        value = api.deprecated_legacy_access("PAD_TOKEN")
    assert value == api.PAD_TOKEN
    assert any("deprecated" in str(w.message) for w in captured)


def test_compat_module_proxies_and_warns(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(compat, "_warned", False)
    monkeypatch.setattr(compat, "_api", api)
    calls = {}

    def fake_get_tokenizer(*args, **kwargs):
        calls["args"] = (args, kwargs)
        return "ok"

    monkeypatch.setattr(api, "load_tokenizer", fake_get_tokenizer)
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        result = compat.load_tokenizer("demo")
    assert result == "ok"
    assert calls["args"][0][0] == "demo"
    assert any("deprecated" in str(w.message) for w in captured)
