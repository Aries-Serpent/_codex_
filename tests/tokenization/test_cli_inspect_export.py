import json

from tests.utils.cli_runner import run_module


def test_cli_inspect_export(tmp_path):
    out = tmp_path / "artifacts"
    out.mkdir()
    tokenizer_json = {
        "model": {"type": "Unigram", "vocab": [["hello", 1], ["world", 2]]},
        "added_tokens": [
            {"id": 0, "content": "[PAD]", "special": True},
            {"id": 1, "content": "[UNK]", "special": True},
        ],
    }
    manifest = {
        "config": {
            "padding": {"direction": "left"},
            "truncation": {"max_length": 4},
            "max_length": 4,
        }
    }
    (out / "tokenizer.json").write_text(json.dumps(tokenizer_json), encoding="utf-8")
    (out / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    res = run_module("tokenization.cli", "inspect", str(out))
    assert "vocab_size" in res.stdout
    export_dir = tmp_path / "export"
    run_module("tokenization.cli", "export", str(out), str(export_dir))
    assert (export_dir / "tokenizer.json").exists()
    assert (export_dir / "README.md").exists()
