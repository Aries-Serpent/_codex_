import os
import sys

from codex_ml.interfaces import get_component


def test_get_component_uses_env(tmp_path):
    mod = tmp_path / "dummy_tok.py"
    mod.write_text("class DummyTok:\n    def __init__(self):\n        self.ok = True\n")
    sys.path.insert(0, str(tmp_path))
    try:
        os.environ["CODEX_TOKENIZER_PATH"] = "dummy_tok:DummyTok"
        inst = get_component("CODEX_TOKENIZER_PATH", "dummy_tok:DummyTok")
        assert getattr(inst, "ok", False)
    finally:
        sys.path.remove(str(tmp_path))
        os.environ.pop("CODEX_TOKENIZER_PATH", None)
