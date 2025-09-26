import os
import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa

from services.api.main import app  # noqa


client = TestClient(app)


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
    assert resp.status_code == 200
    data = resp.json()
    # Expect masked output
    assert "[SECRET]" in data["completion"], f"Secret not masked for pattern: {secret}"


def test_secret_filter_disabled(monkeypatch):
    monkeypatch.setenv("DISABLE_SECRET_FILTER", "1")
    secret = "sk-abc123NOFILTER"
    resp = client.post("/infer", json={"prompt": secret})
    assert resp.status_code == 200
    data = resp.json()
    # Raw secret should appear when filter disabled
    assert secret in data["completion"]
    monkeypatch.delenv("DISABLE_SECRET_FILTER", raising=False)