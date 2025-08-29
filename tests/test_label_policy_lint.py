import json
import pathlib
import subprocess
import sys

SAMPLE_OK = """
name: ok
on: [push]
jobs:
  build:
    runs-on: [self-hosted, linux, x64, codex]
    steps: []
"""

SAMPLE_BAD = """
name: bad
on: [push]
jobs:
  test:
    runs-on: [self-hosted, linux, x64, nosuchlabel]
    steps: []
"""


def _write(path: pathlib.Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def test_lint_ok(tmp_path: pathlib.Path) -> None:
    wf = tmp_path / ".github/workflows"
    wf.mkdir(parents=True)
    _write(wf / "ok.yml", SAMPLE_OK)
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools/label_policy.json").write_text(
        json.dumps(
            {
                "allowed_labels": ["self-hosted", "linux", "x64", "codex"],
                "required_base": ["self-hosted", "linux", "x64"],
                "defaults_for_string_runs_on": ["linux", "x64", "codex"],
            }
        ),
        encoding="utf-8",
    )
    src = pathlib.Path(__file__).resolve().parents[1] / "tools" / "label_policy_lint.py"
    (tmp_path / "tools/label_policy_lint.py").write_text(
        src.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, str(tmp_path / "tools/label_policy_lint.py")],
        cwd=tmp_path,
    )
    assert result.returncode == 0


def test_lint_bad(tmp_path: pathlib.Path) -> None:
    wf = tmp_path / ".github/workflows"
    wf.mkdir(parents=True)
    _write(wf / "bad.yml", SAMPLE_BAD)
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools/label_policy.json").write_text(
        json.dumps(
            {
                "allowed_labels": ["self-hosted", "linux", "x64", "codex"],
                "required_base": ["self-hosted", "linux", "x64"],
                "defaults_for_string_runs_on": ["linux", "x64", "codex"],
            }
        ),
        encoding="utf-8",
    )
    src = pathlib.Path(__file__).resolve().parents[1] / "tools" / "label_policy_lint.py"
    (tmp_path / "tools/label_policy_lint.py").write_text(
        src.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, str(tmp_path / "tools/label_policy_lint.py")],
        cwd=tmp_path,
        capture_output=True,
    )
    assert result.returncode != 0
    assert b"disallowed labels" in result.stderr
