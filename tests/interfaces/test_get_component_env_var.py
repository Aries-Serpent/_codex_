from codex_ml.interfaces.registry import get_component


def test_get_component_from_env(monkeypatch, tmp_path):
    module_path = tmp_path / "dummy_mod.py"
    module_path.write_text("class Dummy:\n    pass\n")
    monkeypatch.syspath_prepend(tmp_path)
    monkeypatch.setenv("CODEX_TOKENIZER_PATH", "dummy_mod:Dummy")
    inst = get_component("CODEX_TOKENIZER_PATH", "dummy_mod:Dummy")
    assert inst.__class__.__name__ == "Dummy"
