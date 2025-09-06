import subprocess

from tokenization.train_tokenizer import TrainTokenizerConfig, train


def test_cli_inspect_export(tmp_path):
    corpus = tmp_path / "corpus.txt"
    corpus.write_text("hello world\n" * 3)
    cfg = TrainTokenizerConfig(
        corpus_glob=str(corpus),
        vocab_size=20,
        out_dir=str(tmp_path / "artifacts"),
        name="tok",
        seed=0,
        workers=1,
    )
    out = train(cfg)
    res = subprocess.run(
        ["python", "-m", "tokenization.cli", "inspect", str(out)],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "vocab_size" in res.stdout
    export_dir = tmp_path / "export"
    subprocess.run(
        ["python", "-m", "tokenization.cli", "export", str(out), str(export_dir)],
        check=True,
    )
    assert (export_dir / "tokenizer.json").exists()
    assert (export_dir / "README.md").exists()
