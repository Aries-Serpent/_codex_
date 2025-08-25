import json
import os
import subprocess
import sys
from pathlib import Path


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


def _run_cli(args, env=None, check=False):
    cmd = [
        sys.executable,
        "scripts/deploy_codex_pipeline.py",
        *args,
    ]
    repo_root = Path(__file__).resolve().parents[1]
    env = {
        **os.environ,
        "CODEX_SKIP_INSTALL": "1",
        "PYTHONPATH": str(repo_root / "src"),
        **(env or {}),
    }
    return subprocess.run(cmd, check=check, env=env, capture_output=True, text=True)


def test_reproducible_run(tmp_path: Path):
    corpus = tmp_path / "corpus.txt"
    demos = tmp_path / "demos.jsonl"
    prefs = tmp_path / "prefs.jsonl"
    corpus.write_text("print('hi')\n")
    _write_jsonl(demos, [{"prompt": "p", "completion": "c"}])
    _write_jsonl(prefs, [["p", "a", "b", 1]])

    def run_once(out_dir: Path):
        _run_cli(
            [
                "--corpus",
                str(corpus),
                "--demos",
                str(demos),
                "--prefs",
                str(prefs),
                "--output-dir",
                str(out_dir),
            ],
            check=True,
        )
        return json.loads((out_dir / "summary.json").read_text())

    s1 = run_once(tmp_path / "run1")
    s2 = run_once(tmp_path / "run2")
    assert s1 == s2


def test_empty_corpus(tmp_path: Path):
    corpus = tmp_path / "corpus.jsonl"
    corpus.write_text("")
    demos = tmp_path / "demos.jsonl"
    prefs = tmp_path / "prefs.jsonl"
    _write_jsonl(demos, [{"prompt": "p", "completion": "c"}])
    _write_jsonl(prefs, [["p", "a", "b", 1]])
    result = _run_cli(
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
    assert result.returncode != 0


def test_missing_prefs(tmp_path: Path):
    corpus, demos, _ = _basic_files(tmp_path)
    missing = tmp_path / "missing.jsonl"
    result = _run_cli(
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
    assert result.returncode != 0


def test_invalid_config(tmp_path: Path):
    corpus, demos, prefs = _basic_files(tmp_path)
    result = _run_cli(
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
    assert result.returncode != 0
