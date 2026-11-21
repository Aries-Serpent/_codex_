"""Secret-redaction regressions for Codespaces auth bootstrap."""

from __future__ import annotations

import json
from typing import Any

from scripts.ci import codespace_auth_bootstrap as bootstrap


def public_key() -> dict[str, str]:
    return {"key": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=", "key_id": "key-id"}


def test_repo_secret_failure_never_returns_encryption_exception(
    monkeypatch: Any,
) -> None:
    canary = "repo-secret-canary"
    monkeypatch.setattr(bootstrap, "api_request", lambda *_args, **_kwargs: (200, public_key()))

    def fail_encryption(_public_key: str, _value: str) -> str:
        raise RuntimeError(f"failed to encrypt {canary}")

    monkeypatch.setattr(bootstrap, "encrypt_secret", fail_encryption)

    result = bootstrap.set_repo_secret("token", "owner", "repo", "NAME", canary)

    assert result == (False, "encryption-failed")
    assert canary not in repr(result)


def test_secret_write_failures_never_return_provider_message(
    monkeypatch: Any,
) -> None:
    canary = "provider-message-canary"
    responses = iter(
        [
            (200, public_key()),
            (500, {"message": f"provider echoed {canary}"}),
        ]
    )
    monkeypatch.setattr(bootstrap, "api_request", lambda *_args, **_kwargs: next(responses))
    monkeypatch.setattr(bootstrap, "encrypt_secret", lambda *_args, **_kwargs: "ciphertext")

    result = bootstrap.set_codespace_secret("token", 1, "NAME", canary)

    assert result == (False, "write-http-500")
    assert canary not in repr(result)


def test_main_report_excludes_resolved_secret_values(monkeypatch: Any, capsys: Any) -> None:
    canary_values = {
        "app_id": "123456",
        "installation_id": "654321",
        "private_key": "-----BEGIN PRIVATE KEY-----\nprivate-key-canary\n-----END PRIVATE KEY-----",
        "client_secret": "client-secret-canary",
    }
    monkeypatch.setattr(bootstrap, "get_pat", lambda: "pat-canary")
    monkeypatch.setattr(bootstrap, "resolve_app_credentials", lambda: canary_values.copy())
    monkeypatch.setattr(bootstrap, "api_request", lambda *_args, **_kwargs: (200, {"id": 7}))
    monkeypatch.setattr(bootstrap, "set_repo_secret", lambda *_args, **_kwargs: (True, "synced"))
    monkeypatch.setattr(
        bootstrap,
        "set_codespace_secret",
        lambda *_args, **_kwargs: (True, "synced"),
    )
    monkeypatch.setattr(
        "sys.argv",
        ["codespace_auth_bootstrap.py", "--sync-app-secrets", "--json"],
    )

    assert bootstrap.main() == 0

    output = capsys.readouterr().out
    report = json.loads(output)
    for canary in ("pat-canary", "private-key-canary", "client-secret-canary"):
        assert canary not in output
    assert report["app_secrets"]["_GITHUB_APP_PRIVATE_KEY"] == {
        "repo_synced": True,
        "codespace_synced": True,
    }
