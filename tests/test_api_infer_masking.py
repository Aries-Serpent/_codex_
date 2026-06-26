"""
Test Api Infer Masking

Test module for api infer masking.
"""

import sys

import pytest

pytest.importorskip("torch", reason="PyTorch is required for API service tests")

# Check for PyTorch 2.x + Python 3.12 isinstance bug
try:
    import torch

    _TORCH_312_BUG = sys.version_info >= (3, 12) and torch.__version__.startswith("2.")
except ImportError: # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
    _TORCH_312_BUG = False

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from services.api.main import app

client = TestClient(app)


@pytest.mark.skipif(
    _TORCH_312_BUG, reason="PyTorch 2.x isinstance bug with Python 3.12 union types"
)
@pytest.mark.parametrize(
    "secret",
    [
        "sk-abc123XYZsecret",
        "AKIAABCDEFGHIJKLMNOP",
        "ASIAABCDEFGHIJKLMNOP",
        "AIzaSyDUMMYKEYVALUE123456",
        "ghp_ABCdefGHIjklMNOpqrSTUvwxYZ012345678",
        "xoxb-1234567890-ABCDEFG",
        "xoxp-1234567890-ABCDEFG",
    ],
)
def test_secret_masking(secret):
    resp = client.post("/infer", json={"prompt": f"leak: {secret}"})
    assert resp.status_code == 200, "status_code is not valid"
    data = resp.json()
    # Expect masked output
    assert "[SECRET]" in data["completion"], f"Secret not masked for pattern: {secret}"


@pytest.mark.skipif(
    _TORCH_312_BUG, reason="PyTorch 2.x isinstance bug with Python 3.12 union types"
)
def test_secret_filter_disabled(monkeypatch):
    monkeypatch.setenv("DISABLE_SECRET_FILTER", "1")
    secret = "sk-abc123NOFILTER"
    resp = client.post("/infer", json={"prompt": secret})
    assert resp.status_code == 200, "status_code is not valid"
    data = resp.json()
    # Raw secret should appear when filter disabled
    assert secret in data["completion"], "Data must not be empty"
    monkeypatch.delenv("DISABLE_SECRET_FILTER", raising=False)
