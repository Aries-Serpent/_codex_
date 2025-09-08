import textwrap

from codex_ml.interfaces.registry import get_component


def test_get_component_env(monkeypatch, tmp_path):
    mod = tmp_path / "dummy_mod.py"
    mod.write_text(
        textwrap.dedent(
            """
        class DummyTokenizer:
            pass
        """
        )
    )
    monkeypatch.syspath_prepend(str(tmp_path))
    monkeypatch.setenv("CODEX_TOKENIZER_PATH", "dummy_mod:DummyTokenizer")
    inst = get_component("CODEX_TOKENIZER_PATH", "unused:Unused")
    assert inst.__class__.__name__ == "DummyTokenizer"
