import json
from pathlib import Path

import pytest

from scripts.deploy_codex_pipeline import main


def _write_jsonl(path: Path, rows):
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")


def _basic_files(tmp_path: Path):
    corpus = tmp_path / "corpus.jsonl"
    demos = tmp_path / "demos.jsonl"
    prefs = tmp_path / "prefs.jsonl"
    _write_jsonl(corpus, ["def add(a,b): return a+b", "print('hi')"])
    _write_jsonl(demos, [{"prompt": "p1", "completion": "c1"}])
    _write_jsonl(prefs, [["p1", "good", "bad", 1]])
    return corpus, demos, prefs


def test_reproducible(tmp_path, monkeypatch):
    corpus, demos, prefs = _basic_files(tmp_path)
    out1 = tmp_path / "run1"
    out2 = tmp_path / "run2"
    monkeypatch.setenv("CODEX_SKIP_INSTALL", "1")
    main(
        [
            "--corpus",
            str(corpus),
            "--demos",
            str(demos),
            "--prefs",
            str(prefs),
            "--output-dir",
            str(out1),
        ]
    )
    # Ensure expected artefacts are produced
    for fn in ["summary.json", "metrics.json", "seeds.json"]:
        assert (out1 / fn).is_file()
    for stage in ["M0", "M1", "RM", "M2"]:
        assert (out1 / "checkpoints" / f"{stage}.json").is_file()
    main(
        [
            "--corpus",
            str(corpus),
            "--demos",
            str(demos),
            "--prefs",
            str(prefs),
            "--output-dir",
            str(out2),
        ]
    )
    with (out1 / "summary.json").open() as f:
        summary1 = json.load(f)
    with (out2 / "summary.json").open() as f:
        summary2 = json.load(f)
    assert summary1 == summary2


def test_empty_corpus(tmp_path, monkeypatch):
    corpus = tmp_path / "corpus.jsonl"
    corpus.write_text("")
    demos = tmp_path / "demos.jsonl"
    prefs = tmp_path / "prefs.jsonl"
    _write_jsonl(demos, [{"prompt": "p", "completion": "c"}])
    _write_jsonl(prefs, [["p", "a", "b", 1]])
    monkeypatch.setenv("CODEX_SKIP_INSTALL", "1")
    with pytest.raises(ValueError):
        main(
            [
                "--corpus",
                str(corpus),
                "--demos",
                str(demos),
                "--prefs",
                str(prefs),
                "--output-dir",
                str(tmp_path / "out"),
            ]
        )


def test_missing_prefs(tmp_path, monkeypatch):
    corpus, demos, _ = _basic_files(tmp_path)
    missing = tmp_path / "missing.jsonl"
    monkeypatch.setenv("CODEX_SKIP_INSTALL", "1")
    with pytest.raises(FileNotFoundError):
        main(
            [
                "--corpus",
                str(corpus),
                "--demos",
                str(demos),
                "--prefs",
                str(missing),
                "--output-dir",
                str(tmp_path / "out"),
            ]
        )


def test_invalid_config(tmp_path, monkeypatch):
    corpus, demos, prefs = _basic_files(tmp_path)
    monkeypatch.setenv("CODEX_SKIP_INSTALL", "1")
    with pytest.raises(ValueError):
        main(
            [
                "--corpus",
                str(corpus),
                "--demos",
                str(demos),
                "--prefs",
                str(prefs),
                "--output-dir",
                str(tmp_path / "out"),
                "--pretrain-epochs",
                "0",
            ]
        )
