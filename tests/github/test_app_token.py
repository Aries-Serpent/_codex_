"""
Test App Token

Test module for app token.
"""

from __future__ import annotations

import shutil
import subprocess
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
