"""Environment-driven configuration for the Codex bridge client."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ClientConfig:
    ita_url: str
    api_key: str
    request_timeout: float = 30.0

    @classmethod
    def from_environment(cls) -> "ClientConfig":
        ita_url = os.environ.get("ITA_URL")
        api_key = os.environ.get("ITA_API_KEY")
        if not ita_url or not api_key:
            raise RuntimeError("ITA_URL and ITA_API_KEY environment variables must be set")
        timeout = float(os.environ.get("ITA_CLIENT_TIMEOUT", 30))
        return cls(ita_url=ita_url.rstrip("/"), api_key=api_key, request_timeout=timeout)


DEFAULT_CONFIG = ClientConfig

__all__ = ["ClientConfig", "DEFAULT_CONFIG"]
