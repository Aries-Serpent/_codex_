import os
import sys

from codex_ml.interfaces import get_component


def test_get_component_tokenizer_env(tmp_path):
    module = tmp_path / "dummy_tok.py"
    module.write_text("class Tok:\n    def __init__(self):\n        self.ok = True\n")
    sys.path.insert(0, str(tmp_path))
    try:
        os.environ["CODEX_TOKENIZER_PATH"] = "dummy_tok:Tok"
        inst = get_component("CODEX_TOKENIZER_PATH", "dummy_tok:Tok")
        assert inst.ok
    finally:
        sys.path.remove(str(tmp_path))
        os.environ.pop("CODEX_TOKENIZER_PATH", None)
