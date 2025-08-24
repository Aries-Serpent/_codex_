import json
import subprocess
from pathlib import Path


def test_reproducible_run(tmp_path: Path) -> None:
    """Ensure pipeline produces identical summaries given the same inputs."""
    # Prepare toy data
    corpus = tmp_path / "corpus.txt"
    demos = tmp_path / "demos.jsonl"
    prefs = tmp_path / "prefs.jsonl"
    corpus.write_text("print('hi')\n")
    demos.write_text('{"prompt":"p","completion":"c"}\n')
    prefs.write_text('["p","a","b",1]\n')

    def run_once(out_dir: Path) -> dict[str, object]:
        subprocess.run(
            [
                "python",
                "scripts/deploy_codex_pipeline.py",
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
