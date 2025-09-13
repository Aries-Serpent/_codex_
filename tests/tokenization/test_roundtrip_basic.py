import pytest

pytest.importorskip("sentencepiece")

from codex_ml.interfaces.tokenizer import HFTokenizer  # noqa: E402
from tokenization.train_tokenizer import TrainTokenizerConfig, train  # noqa: E402


def test_roundtrip_basic(tmp_path):
    corpus = tmp_path / "corpus.txt"
    corpus.write_text("hello world\n" * 2)
    cfg = TrainTokenizerConfig(
        corpus_glob=str(corpus),
        vocab_size=20,
        out_dir=str(tmp_path / "artifacts"),
        name="tok",
        seed=123,
        workers=1,
    )
    try:
        out = train(cfg)
    except OSError as exc:  # pragma: no cover - env missing sentencepiece
        pytest.skip(str(exc))
    tk = HFTokenizer(
        name_or_path=None,
        artifacts_dir=str(out),
        padding="max_length",
        truncation=True,
        max_length=4,
    )
    ids = tk.encode("hello world")
    assert len(ids) == 4
    assert tk.decode(ids).startswith("hello")
