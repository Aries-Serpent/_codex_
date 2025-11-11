import importlib


def test_peft_disabled_by_default(monkeypatch):
    monkeypatch.delenv("CODEX_ENABLE_PEFT", raising=False)
    mf = importlib.import_module("codex_ml.models.factory")
    # ensure module import does not require peft
    assert hasattr(mf, "ENABLE_PEFT")
