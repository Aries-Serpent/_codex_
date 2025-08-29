import importlib.util
from pathlib import Path


def _load_adapter():
    root = Path(__file__).resolve().parents[2]
    spec = importlib.util.spec_from_file_location(
        "sentencepiece_adapter", root / "src/codex_ml/tokenization/sentencepiece_adapter.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    import types, sys

    sys.modules.setdefault(
        "sentencepiece",
        types.SimpleNamespace(SentencePieceTrainer=object, SentencePieceProcessor=object),
    )
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return module.SentencePieceAdapter


def test_model_prefix_setter(tmp_path):
    SentencePieceAdapter = _load_adapter()
    model = tmp_path / "m.model"
    sp = SentencePieceAdapter(model)
    assert sp.model_prefix == model.with_suffix("")
    new_prefix = tmp_path / "new"
    sp.model_prefix = new_prefix
    assert sp.model_prefix == new_prefix
    assert sp.model_path == new_prefix.with_suffix(".model")
