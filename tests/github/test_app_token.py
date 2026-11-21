"""
Test App Token

Test module for app token.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from tools.github.app_token import build_app_jwt

jwt = pytest.importorskip("jwt")


def _make_dummy_pem(tmp_path: Path) -> Path:
    if shutil.which("openssl") is None:
        pytest.skip("openssl not available")
    pem = tmp_path / "dummy.pem"
    with open(pem, "wb") as fh:
        subprocess.run(["openssl", "genrsa", "2048"], check=True, stdout=fh)
    return pem


def test_isolated_app_token_module_resolves_private_key_without_checkout(tmp_path: Path) -> None:
    source = Path(__file__).resolve().parents[2] / "src/tools/github/app_token.py"
    target = tmp_path / "installed/tools/github/app_token.py"
    target.parent.mkdir(parents=True)
    shutil.copyfile(source, target)
    pem = tmp_path / "app.pem"
    private_key = (
        "-----BEGIN " + "PRIVATE KEY-----\ninstalled-key-canary\n-----END PRIVATE KEY-----"
    )
    pem.write_text(private_key, encoding="utf-8")
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    for name in (
        "_GITHUB_APP_PRIVATE_KEY_PEM",
        "_GITHUB_APP_PRIVATE_KEY",
        "GITHUB_APP_PRIVATE_KEY_PEM",
        "GITHUB_APP_PRIVATE_KEY",
    ):
        environment.pop(name, None)
    environment["GITHUB_APP_PRIVATE_KEY_PATH"] = str(pem)
    proc = subprocess.run(
        [
            sys.executable,
            "-I",
            "-c",
            (
                "import sys; "
                f"sys.path.insert(0, {str(tmp_path / 'installed')!r}); "
                "from tools.github.app_token import _read_private_key; "
                "print(_read_private_key().decode())"
            ),
        ],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.strip() == private_key


def test_build_app_jwt_with_dummy_key(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    pem = _make_dummy_pem(tmp_path)
    monkeypatch.setenv("GITHUB_APP_PRIVATE_KEY_PATH", str(pem))
    token = build_app_jwt("123456", now=1_700_000_000, ttl_seconds=540)
    header = jwt.get_unverified_header(token)
    assert header.get("alg") == "RS256", "Condition must be true"
    public_key = subprocess.run(
        ["openssl", "rsa", "-in", str(pem), "-pubout"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    payload = jwt.decode(
        token,
        public_key,
        algorithms=["RS256"],
        options={"verify_exp": False, "verify_iat": False, "verify_nbf": False},
    )
    assert payload.get("iss") == "123456", "Condition must be true"
    assert payload.get("exp") > payload.get("iat"), "Value must be greater than zero"
