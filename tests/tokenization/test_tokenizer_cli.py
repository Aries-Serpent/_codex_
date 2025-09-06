import types
from pathlib import Path

import codex_ml.tokenization.cli as cli


def test_train_cli(tmp_path, monkeypatch):
    corpus = tmp_path / "c.txt"
    corpus.write_text("hello", encoding="utf-8")

    sp_stub = types.SimpleNamespace(
        SentencePieceTrainer=types.SimpleNamespace(
            train=lambda **kw: Path(kw["model_prefix"] + ".model").write_text(
                "m", encoding="utf-8"
            ),
        ),
        SentencePieceProcessor=type(
            "P",
            (),
            {
                "__init__": lambda self, model_file: None,
                "encode": lambda self, text, out_type=int: [1, 2, 3],
                "decode": lambda self, ids: "ok",
                "vocab_size": lambda self: 3,
            },
        ),
    )
    monkeypatch.setattr(cli.sentencepiece_adapter, "spm", sp_stub)

    cli.main(["train", str(corpus), str(tmp_path / "tok"), "--vocab-size", "10"])

    assert (tmp_path / "tok.model").exists()
    assert (tmp_path / "tok.tokenizer.json").exists()


def test_encode_cli_padding(monkeypatch, capsys):
    class DummyAdapter:
        def __init__(self, model):
            pass

        def load(self):
            return self

        def encode(self, text, padding=None, truncation=None, max_length=None):
            assert padding == "max_length"
            assert truncation == "only_first"
            assert max_length == 4
            return [1, 2, 0, 0]

    monkeypatch.setattr(cli, "SentencePieceAdapter", DummyAdapter)

    cli.main(
        [
            "encode",
            "m.model",
            "hi",
            "--max-length",
            "4",
            "--padding",
            "max_length",
            "--truncation",
            "only_first",
        ]
    )
    out = capsys.readouterr().out.strip()
    assert out == "1 2 0 0"


def test_stats_cli(monkeypatch, capsys):
    class DummyAdapter:
        def __init__(self, model):
            self.sp = types.SimpleNamespace(vocab_size=lambda: 5)

        def load(self):
            return self

    monkeypatch.setattr(cli, "SentencePieceAdapter", DummyAdapter)

    cli.main(["stats", "m.model"])
    assert capsys.readouterr().out.strip() == "5"
