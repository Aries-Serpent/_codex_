import os
import sys

from codex_ml.interfaces import get_component, load_component


def test_load_and_get_component(tmp_path):
    module_path = tmp_path / "tmp_mod.py"
    module_path.write_text(
        "class Dummy:\n    def __init__(self):\n        self.flag = True\n"
    )
    sys.path.insert(0, str(tmp_path))
    try:
        cls = load_component("tmp_mod:Dummy")
        assert cls.__name__ == "Dummy"
        os.environ["CODEX_DUMMY_PATH"] = "tmp_mod:Dummy"
        inst = get_component("CODEX_DUMMY_PATH", "tmp_mod:Dummy")
        assert isinstance(inst, cls) and inst.flag
    finally:
        sys.path.remove(str(tmp_path))
        os.environ.pop("CODEX_DUMMY_PATH", None)
