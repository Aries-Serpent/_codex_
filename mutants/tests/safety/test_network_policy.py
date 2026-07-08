from __future__ import annotations

from pathlib import Path

import pytest

from safety.network_policy import PolicyViolationError, enforce_network_policy, load_network_policy


def test_load_network_policy_defaults_when_file_missing(tmp_path: Path) -> None:
    policy = load_network_policy(tmp_path / "missing.yaml")
    assert policy.default_mode == "fail_closed", "default_mode should be fail_closed"
    assert "localhost" in policy.allowed_hosts, "localhost should be allowlisted"


def test_enforce_network_policy_allows_localhost_without_policy_file() -> None:
    enforce_network_policy("http://localhost:8765")


def test_enforce_network_policy_blocks_unapproved_host(tmp_path: Path) -> None:
    policy_file = tmp_path / "network-policy.yaml"
    policy_file.write_text(
        "version: 1\n"
        "default_mode: fail_closed\n"
        "allow_localhost: true\n"
        "allowed_hosts:\n"
        "  - localhost\n",
        encoding="utf-8",
    )

    with pytest.raises(PolicyViolationError):
        enforce_network_policy("https://example.com", policy_file)


def test_enforce_network_policy_allows_wildcard_allowlist(tmp_path: Path) -> None:
    policy_file = tmp_path / "network-policy.yaml"
    policy_file.write_text(
        "version: 1\n"
        "default_mode: fail_closed\n"
        "allow_localhost: true\n"
        "allowed_hosts:\n"
        "  - '*.github.com'\n",
        encoding="utf-8",
    )

    enforce_network_policy("https://api.github.com/repos/org/repo", policy_file)
