import json
import sys
import importlib
import pathlib
import pytest

pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")


def _write_corpus(tmp_path):
    p = tmp_path / "tiny.txt"
    p.write_text("hello world\nhello codex\n", encoding="utf-8")
    return p


def test_train_and_reload_roundtrip(tmp_path):
    pytest.importorskip("sentencepiece", reason="sentencepiece not installed")
    from codex_ml.tokenization.sentencepiece_adapter import SentencePieceAdapter

    corpus = _write_corpus(tmp_path)
    model_prefix = tmp_path / "spm_model"
    model_path = model_prefix.with_suffix(".model")
    adapter = SentencePieceAdapter(model_path)
    adapter.train_or_load(
        input_path=str(corpus), vocab_size=14, character_coverage=1.0
    )

    adapter2 = SentencePieceAdapter(model_path)
    adapter2.load()
    if hasattr(adapter2, "encode") and hasattr(adapter2, "decode"):
        ids = adapter2.encode("hello codex")
        assert isinstance(ids, (list, tuple))
        assert "hello" in adapter2.decode(ids)


def test_missing_sentencepiece_branch(monkeypatch):
    monkeypatch.setitem(sys.modules, "sentencepiece", None)
    with pytest.raises(ImportError):
        importlib.reload(
            importlib.import_module("codex_ml.tokenization.sentencepiece_adapter")
        )


def test_add_special_tokens_sidecar(tmp_path):
    pytest.importorskip("sentencepiece", reason="sentencepiece not installed")
    from codex_ml.tokenization.sentencepiece_adapter import SentencePieceAdapter

    corpus = _write_corpus(tmp_path)
    model_prefix = tmp_path / "spm_model"
    model_path = model_prefix.with_suffix(".model")
    adapter = SentencePieceAdapter(model_path)
    adapter.train_or_load(str(corpus), vocab_size=14, character_coverage=1.0)

    specials = {"pad_token": "<pad>", "eos_token": "</s>"}
    adapter.add_special_tokens(specials)

    sidecar = pathlib.Path(str(model_prefix) + ".special_tokens.json")
    assert sidecar.exists()
    data = json.loads(sidecar.read_text(encoding="utf-8"))
    assert data.get("pad_token") == "<pad>"


def test_assert_vocab_size(tmp_path):
    pytest.importorskip("sentencepiece", reason="sentencepiece not installed")
    from codex_ml.tokenization.sentencepiece_adapter import SentencePieceAdapter

    corpus = _write_corpus(tmp_path)
    model_prefix = tmp_path / "spm_model"
    model_path = model_prefix.with_suffix(".model")
    adapter = SentencePieceAdapter(model_path)
    adapter.train_or_load(str(corpus), vocab_size=14, character_coverage=1.0)
    adapter.assert_vocab_size(min_size=8)  # should not raise
    with pytest.raises(AssertionError):
        adapter.assert_vocab_size(min_size=10_000)

