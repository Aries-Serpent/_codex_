"""Network allowlist policy enforcement for isolated deployments.

This module provides fail-closed outbound network controls for packaged
installations. The default posture is localhost-only unless explicitly
allowlisted in a policy file.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml


class PolicyViolationError(RuntimeError):
    """Raised when a network target violates the configured allowlist policy."""


@dataclass(frozen=True)
class NetworkPolicy:
    """Represents an outbound network allowlist policy."""

    default_mode: str
    allowed_hosts: tuple[str, ...]
    allow_localhost: bool = True


_DEFAULT_LOCALHOSTS: tuple[str, ...] = (
    ("localhost", "127.0.0.1", "::1")
    if os.environ.get("CODEX_LOCAL_LOOPBACK", "true").lower() == "true"
    else ()
)
_DEFAULT_POLICY_PATH = Path(".codex/network-policy.yaml")


def _default_policy() -> NetworkPolicy:
    return NetworkPolicy(
        default_mode="fail_closed",
        allowed_hosts=_DEFAULT_LOCALHOSTS,
        allow_localhost=True,
    )


def _resolve_policy_path(policy_path: str | Path | None) -> Path:
    if policy_path is not None:
        return Path(policy_path)
    env_path = os.getenv("CODEX_NETWORK_POLICY_PATH") or os.getenv("CODEX_NETWORK_ALLOWLIST_PATH")
    if env_path:
        return Path(env_path)
    return _DEFAULT_POLICY_PATH


def load_network_policy(policy_path: str | Path | None = None) -> NetworkPolicy:
    """Load network policy from YAML or return safe localhost-only defaults."""
    resolved = _resolve_policy_path(policy_path)
    if not resolved.exists():
        return _default_policy()

    with resolved.open("r", encoding="utf-8") as handle:
        raw: Any = yaml.safe_load(handle) or {}

    allowed_hosts = raw.get("allowed_hosts") or []
    if not isinstance(allowed_hosts, list):
        raise ValueError("allowed_hosts must be a list")

    normalized_hosts: list[str] = []
    for host in allowed_hosts:
        if not isinstance(host, str):
            raise ValueError("allowed_hosts entries must be strings")
        entry = host.strip().lower()
        if entry:
            normalized_hosts.append(entry)

    default_mode = str(raw.get("default_mode", "fail_closed")).strip().lower()
    if default_mode not in {"fail_closed", "allow"}:
        raise ValueError("default_mode must be 'fail_closed' or 'allow'")

    allow_localhost = bool(raw.get("allow_localhost", True))

    return NetworkPolicy(
        default_mode=default_mode,
        allowed_hosts=tuple(normalized_hosts),
        allow_localhost=allow_localhost,
    )


def _normalized_host(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme in {"", "file", "sqlite", "sqlite3"}:
        return ""
    host = parsed.hostname
    if not host:
        raise PolicyViolationError(f"Missing host in URL: {url}")
    return host.lower()


def _is_allowed_host(host: str, policy: NetworkPolicy) -> bool:
    if not host:
        return True

    if policy.allow_localhost and host in _DEFAULT_LOCALHOSTS:
        return True

    for pattern in policy.allowed_hosts:
        if host == pattern or fnmatch(host, pattern):
            return True

    return False


def enforce_network_policy(
    url: str,
    policy_path: str | Path | None = None,
    extra_allowed_hosts: set[str] | None = None,
) -> None:
    """Raise PolicyViolationError when URL host is not allowlisted."""
    policy = load_network_policy(policy_path)
    host = _normalized_host(url)

    if not host:
        return

    if extra_allowed_hosts and host in {entry.lower() for entry in extra_allowed_hosts}:
        return

    if _is_allowed_host(host, policy):
        return

    if policy.default_mode == "allow":
        return

    raise PolicyViolationError(
        f"Outbound request blocked by network policy: host='{host}'. "
        "Add host to .codex/network-policy.yaml allowed_hosts to permit access."
    )


__all__ = [
    "NetworkPolicy",
    "PolicyViolationError",
    "enforce_network_policy",
    "load_network_policy",
]
