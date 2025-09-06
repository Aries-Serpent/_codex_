import json

from tokenizers import Tokenizer

from tokenization.train_tokenizer import TrainTokenizerConfig, train


def test_train_tokenizer_smoke(tmp_path):
    corpus = tmp_path / "corpus.txt"
    corpus.write_text("hello world\n" * 5)
    cfg = TrainTokenizerConfig(
        corpus_glob=str(corpus),
        vocab_size=30,
        out_dir=str(tmp_path / "artifacts"),
        name="tok",
        seed=0,
        workers=1,
    )
    out = train(cfg)
    assert (out / "tokenizer.json").exists()
    assert (out / "manifest.json").exists()
    assert (out / "spm.model").exists()
    assert (out / "spm.vocab").exists()
    tok = Tokenizer.from_file(str(out / "tokenizer.json"))
    assert tok.get_vocab_size() <= cfg.vocab_size + 4
    manifest = json.loads((out / "manifest.json").read_text())
    assert manifest.get("hash")
