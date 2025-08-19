import pathlib
import sys


def test_import_codex():
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
    import codex

    assert codex is not None
