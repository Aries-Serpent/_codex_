"""Utilities for retrieving secrets in a controlled fashion."""

from __future__ import annotations

import os
from collections.abc import Mapping, MutableMapping
from dataclasses import dataclass
from typing import Protocol


class SecretProvider(Protocol):
    """Abstract protocol describing how to fetch secrets."""

    def get_secret(self, key: str) -> str | None:
        """Return the secret value for ``key`` or ``None`` when unavailable."""


@dataclass
class EnvironmentSecretProvider:
    """Fetch secrets from a mapping (defaults to ``os.environ``)."""

    environ: MutableMapping[str, str]

    def get_secret(self, key: str) -> str | None:
        return self.environ.get(key)


def environment_secret_provider(environ: Mapping[str, str] | None = None) -> SecretProvider:
    """Factory to create an :class:`EnvironmentSecretProvider` instance."""

    mapping: MutableMapping[str, str]
    if environ is None:
        mapping = os.environ
    else:
        mapping = dict(environ)
    return EnvironmentSecretProvider(mapping)
