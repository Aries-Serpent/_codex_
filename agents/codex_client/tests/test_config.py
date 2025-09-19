"""Unit tests for the Codex bridge client configuration."""

from __future__ import annotations

from typing import Iterator

import pytest
from codex_client.config import ClientConfig


@pytest.fixture()
def clean_env(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    for key in ["ITA_URL", "ITA_API_KEY", "ITA_CLIENT_TIMEOUT"]:
        monkeypatch.delenv(key, raising=False)
    yield


def test_from_environment_requires_settings(clean_env: None) -> None:
    with pytest.raises(RuntimeError):
        ClientConfig.from_environment()


def test_from_environment_parses_values(clean_env: None, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ITA_URL", "http://localhost:8080/")
    monkeypatch.setenv("ITA_API_KEY", "demo")
    monkeypatch.setenv("ITA_CLIENT_TIMEOUT", "45")

    config = ClientConfig.from_environment()
    assert config.ita_url == "http://localhost:8080"
    assert config.api_key == "demo"
    assert config.request_timeout == 45
