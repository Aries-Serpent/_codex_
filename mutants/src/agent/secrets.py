"""Secrets management stubs for admin automation integration tests."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class GitHubSecretsManager:
    owner: str | None = None
    repo: str | None = None
    token: str | None = None

    def setup_phase10_secrets(self, *args: Any, **kwargs: Any) -> dict[str, str]:
        return {}
