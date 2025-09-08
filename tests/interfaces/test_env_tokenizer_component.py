import os
import sys

from codex_ml.interfaces import get_component


def test_get_component_env_tokenizer(tmp_path):
    module_path = tmp_path / "tok_mod.py"
    module_path.write_text("class Tok:\n    def __init__(self):\n        self.name = 'tok'\n")
    sys.path.insert(0, str(tmp_path))
    os.environ["CODEX_TOKENIZER_PATH"] = "tok_mod:Tok"
    try:
        inst = get_component("CODEX_TOKENIZER_PATH", "tok_mod:Tok")
        assert inst.name == "tok"
    finally:
        sys.path.remove(str(tmp_path))
        os.environ.pop("CODEX_TOKENIZER_PATH", None)
