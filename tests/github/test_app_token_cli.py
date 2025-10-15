from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

pytest.importorskip("jwt")


def _generate_pem(tmp_path: Path) -> Path:
    if shutil.which("openssl") is None:
        pytest.skip("openssl not available")
    pem = tmp_path / "dummy_cli.pem"
    with open(pem, "wb") as fh:
        subprocess.run(["openssl", "genrsa", "2048"], check=True, stdout=fh)
    return pem


def test_cli_print_jwt(tmp_path: Path) -> None:
    pem = _generate_pem(tmp_path)
    env = os.environ.copy()
    env["GITHUB_APP_ID"] = "123456"
    env["GITHUB_APP_PRIVATE_KEY_PATH"] = str(pem)
    repo_root = Path(__file__).resolve().parents[2]
    cmd = [sys.executable, "tools/github/app_token.py", "--print-jwt"]
    proc = subprocess.run(cmd, env=env, capture_output=True, text=True, cwd=repo_root)
    assert proc.returncode == 0
    token = proc.stdout.strip()
    assert token.count(".") == 2


def test_cli_help(tmp_path: Path) -> None:
    pem = _generate_pem(tmp_path)
    env = os.environ.copy()
    env["GITHUB_APP_ID"] = "123456"
    env["GITHUB_APP_PRIVATE_KEY_PATH"] = str(pem)
    repo_root = Path(__file__).resolve().parents[2]
    proc = subprocess.run(
        [sys.executable, "tools/github/app_token.py", "--help"],
        env=env,
        capture_output=True,
        text=True,
        cwd=repo_root,
    )
    assert proc.returncode == 0
    assert "GitHub App token helper" in proc.stdout
