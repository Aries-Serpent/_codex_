import json

import pytest

from scripts.ci import github_app_bootstrap as bootstrap
from scripts.ci import github_auth_preflight as preflight


@pytest.fixture
def credentials(monkeypatch):
    for name in (*preflight.CANONICAL_HIERARCHY, "CODEX_ADMIN_KEY"):
        monkeypatch.delenv(name, raising=False)
    for name in ("GITHUB_APP_ID", "GITHUB_APP_PRIVATE_KEY", "GITHUB_APP_INSTALLATION_ID"):
        monkeypatch.delenv(name, raising=False)
        monkeypatch.delenv("_" + name, raising=False)


def test_rejected_named_admin_does_not_hide_working_provider(credentials, monkeypatch):
    monkeypatch.setenv("CODEX_MASTER_KEY", "rejected-credential-fixture")
    monkeypatch.setenv("GITHUB_TOKEN", "working-credential-fixture")
    calls = []

    def request(method, path, token):
        calls.append((method, path))
        if token.startswith("rejected"):
            return 401, {}
        return 200, {"private": "must-not-be-emitted"}

    monkeypatch.setattr(preflight, "_gh", request)
    result = preflight.inspect_access("o/r", "owner-approval", "main")
    assert all(result["verified_reads"].values())
    assert result["routes"][0]["repository_http_status"] == 401
    assert result["routes"][1]["source"] == "GITHUB_TOKEN"
    assert all(method == "GET" for method, _ in calls)
    assert "unverified" in result["write_authority"]
    serialized = json.dumps(result)
    assert "credential-fixture" not in serialized
    assert "must-not-be-emitted" not in serialized


def test_admin_role_is_not_endpoint_permission(credentials, monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "fixture")

    def request(method, path, token):
        if path == "/repos/o/r":
            return 200, {"permissions": {"admin": True}}
        return 403, {"message": "Resource not accessible by integration"}

    monkeypatch.setattr(preflight, "_gh", request)
    result = preflight.inspect_access("o/r", "owner-approval", "main")
    assert not any(result["verified_reads"].values())
    assert all(probe["http_status"] == 403 for probe in result["routes"][0]["probes"])
    assert "unverified" in result["protected_approval"]


def test_no_credentials_never_reports_access(credentials):
    result = preflight.inspect_access("o/r", "owner-approval", "main")
    assert result["routes"] == []
    assert not any(result["verified_reads"].values())


def test_scope_and_transport_failures_are_explicit(credentials, monkeypatch):
    monkeypatch.setenv("GH_TOKEN", "fixture")
    monkeypatch.setattr(preflight, "_gh", lambda *args: (_ for _ in ()).throw(TimeoutError()))
    result = preflight.inspect_access("o/r", "owner-approval", "main")
    assert result["routes"][0]["transport_error"]
    assert not any(result["verified_reads"].values())
    with pytest.raises(ValueError):
        preflight.inspect_access("o/r/../../other", "owner-approval", "main")


def test_existing_app_bootstrap_uses_canonical_and_admin_fallback(credentials, monkeypatch):
    monkeypatch.setenv("CODEX_ADMIN_KEY", "admin-fixture")
    assert bootstrap._backup_token() == "admin-fixture"
    monkeypatch.setenv("CODEX_BACKUP_KEY", "backup-fixture")
    assert bootstrap._backup_token() == "backup-fixture"


def test_missing_bootstrap_credential_fails_without_values(credentials, capsys):
    with pytest.raises(SystemExit) as exc:
        bootstrap._backup_token()
    assert exc.value.code == 1
    err = capsys.readouterr().err
    assert "CODEX_BACKUP_KEY" in err and "CODEX_ADMIN_KEY" in err


def test_preflight_supports_documented_app_aliases(credentials, monkeypatch):
    monkeypatch.delenv("REPO", raising=False)
    monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)
    monkeypatch.setenv("_GITHUB_APP_ID", "1")
    monkeypatch.setenv("_GITHUB_APP_PRIVATE_KEY", "-----BEGIN FIXTURE-----")
    monkeypatch.setenv("_GITHUB_APP_INSTALLATION_ID", "2")
    calls = []

    def mint(*args, **kwargs):
        calls.append((args, kwargs))
        return "temporary-fixture"

    requests = []

    def request(method, path, token):
        requests.append((method, path, token))
        return (204, {}) if method == "DELETE" else (200, {})

    monkeypatch.setattr(preflight, "_mint_app_token", mint)
    monkeypatch.setattr(preflight, "_gh", request)
    result = preflight.inspect_access("o/r", "owner-approval", "main")
    assert calls == [
        (
            ("1", "-----BEGIN FIXTURE-----", "2"),
            {"repo": "o/r", "permissions": preflight.READ_ONLY_APP_PERMISSIONS},
        )
    ]
    assert set(preflight.READ_ONLY_APP_PERMISSIONS.values()) == {"read"}
    assert requests[-1] == ("DELETE", "/installation/token", "temporary-fixture")
    assert all(method == "GET" for method, _, _ in requests[:-1])
    assert result["app_route"] == "verified-installation"
    assert result["routes"][0]["source"] == "cognitive-brain-app"
    assert "temporary-fixture" not in json.dumps(result)


def test_preflight_rejects_conflicting_ambient_repository(credentials, monkeypatch):
    monkeypatch.setenv("REPO", "other/repository")
    monkeypatch.setenv("_GITHUB_APP_ID", "1")
    monkeypatch.setenv("_GITHUB_APP_PRIVATE_KEY", "-----BEGIN FIXTURE-----")
    monkeypatch.setenv("_GITHUB_APP_INSTALLATION_ID", "2")
    monkeypatch.setattr(
        preflight, "_mint_app_token", lambda *args, **kwargs: pytest.fail("must not mint")
    )

    result = preflight.inspect_access("o/r", "owner-approval", "main")

    assert result["app_route"] == "repository-scope-mismatch"


def test_bad_app_key_fails_before_mint(credentials, monkeypatch):
    monkeypatch.setenv("_GITHUB_APP_ID", "1")
    monkeypatch.setenv("_GITHUB_APP_PRIVATE_KEY", "not-a-key")
    monkeypatch.setenv("_GITHUB_APP_INSTALLATION_ID", "2")
    monkeypatch.setattr(preflight, "_mint_app_token", lambda *args: pytest.fail("must not mint"))
    result = preflight.inspect_access("o/r", "owner-approval", "main")
    assert result["app_route"] == "private-key-not-pem"


def test_app_token_revocation_failure_is_reported(credentials, monkeypatch):
    monkeypatch.delenv("REPO", raising=False)
    monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)
    monkeypatch.setenv("_GITHUB_APP_ID", "1")
    monkeypatch.setenv("_GITHUB_APP_PRIVATE_KEY", "-----BEGIN FIXTURE-----")
    monkeypatch.setenv("_GITHUB_APP_INSTALLATION_ID", "2")
    monkeypatch.setattr(preflight, "_mint_app_token", lambda *args, **kwargs: "fixture")
    monkeypatch.setattr(
        preflight, "_gh", lambda method, *args: (500, {}) if method == "DELETE" else (200, {})
    )
    result = preflight.inspect_access("o/r", "owner-approval", "main")
    assert result["app_route"] == "verified-installation-revoke-failed"


@pytest.mark.parametrize(
    ("granted", "expected"),
    [
        ({"actions": "read", "administration": "read", "metadata": "read"}, "read-fixture"),
        ({"actions": "write", "administration": "read"}, None),
        ({"actions": "read"}, None),
    ],
)
def test_read_only_app_mint_requests_and_requires_read_scopes(monkeypatch, granted, expected):
    import sys
    from datetime import datetime, timedelta, timezone
    from types import SimpleNamespace

    from scripts.ci import approve_pending_runs as approval

    monkeypatch.setitem(
        sys.modules, "jwt", SimpleNamespace(encode=lambda *args, **kwargs: "jwt-fixture")
    )
    bodies = []

    def request(method, path, token, body=None):
        if path == "/app":
            return 200, {"id": 1, "slug": "codex-maintainer"}
        if path == "/app/installations/2":
            return 200, {"id": 2, "app_id": 1, "account": {"login": "o"}}
        bodies.append((method, path, body))
        if method == "DELETE":
            return 204, {}
        return 201, {
            "token": "read-fixture",
            "expires_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
            "permissions": granted,
        }

    monkeypatch.setattr(approval, "_gh", request)
    requested = {"actions": "read", "administration": "read"}
    token = approval._mint_app_token("1", "fixture", "2", repo="o/r", permissions=requested)
    assert token == expected
    mint_request = ("POST", "/app/installations/2/access_tokens")
    assert bodies[0] == (*mint_request, {"repositories": ["r"], "permissions": requested})
    revocations = [("DELETE", "/installation/token", None)] if expected is None else []
    assert bodies[1:] == revocations


@pytest.mark.parametrize("requested", [{}, {"actions": "write"}])
def test_explicit_mint_rejects_empty_or_write_scopes_before_request(monkeypatch, requested):
    import sys
    from types import SimpleNamespace

    from scripts.ci import approve_pending_runs as approval

    monkeypatch.setitem(
        sys.modules, "jwt", SimpleNamespace(encode=lambda *args, **kwargs: "jwt-fixture")
    )
    monkeypatch.setattr(approval, "_gh", lambda *args, **kwargs: pytest.fail("must not call"))
    assert approval._mint_app_token("1", "fixture", "2", repo="o/r", permissions=requested) is None


def test_cli_fails_closed_when_app_token_revocation_fails(monkeypatch, capsys):
    reads = {"workflow_runs": True}
    monkeypatch.setattr(
        preflight,
        "inspect_access",
        lambda *args: {"app_route": "verified-installation-revoke-failed", "verified_reads": reads},
    )
    monkeypatch.setattr("sys.argv", ["github_auth_preflight", "--repo", "o/r"])
    assert preflight.main() == 1
    assert "revoke-failed" in capsys.readouterr().out


@pytest.mark.parametrize("revoke", [(403, {}), OSError("offline")])
def test_rejected_token_unsuccessful_revocation_is_reported(monkeypatch, capsys, revoke):
    import sys
    from datetime import datetime, timedelta, timezone
    from types import SimpleNamespace

    from scripts.ci import approve_pending_runs as approval

    monkeypatch.setitem(
        sys.modules, "jwt", SimpleNamespace(encode=lambda *args, **kwargs: "jwt-fixture")
    )

    def request(method, path, token, body=None):
        if path == "/app":
            return 200, {"id": 1, "slug": "codex-maintainer"}
        if path == "/app/installations/2":
            return 200, {"id": 2, "app_id": 1, "account": {"login": "o"}}
        if method == "DELETE":
            if isinstance(revoke, Exception):
                raise revoke
            return revoke
        return 201, {
            "token": "broad-fixture",
            "expires_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
            "permissions": {"actions": "write"},
        }

    monkeypatch.setattr(approval, "_gh", request)
    requested = {"actions": "read"}
    with pytest.raises(approval.AppTokenRevocationError):
        approval._mint_app_token("1", "fixture", "2", repo="o/r", permissions=requested)
    assert "Rejected app token revocation failed" in capsys.readouterr().err


def test_rejected_token_revocation_failure_never_falls_back(credentials, monkeypatch, capsys):
    monkeypatch.delenv("REPO", raising=False)
    monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)
    monkeypatch.setenv("GITHUB_TOKEN", "working-credential-fixture")
    monkeypatch.setenv("_GITHUB_APP_ID", "1")
    monkeypatch.setenv("_GITHUB_APP_PRIVATE_KEY", "-----BEGIN FIXTURE-----")
    monkeypatch.setenv("_GITHUB_APP_INSTALLATION_ID", "2")

    def mint(*args, **kwargs):
        raise preflight.AppTokenRevocationError("not limited to read scopes")

    monkeypatch.setattr(preflight, "_mint_app_token", mint)
    monkeypatch.setattr(preflight, "_gh", lambda *args: pytest.fail("must not probe"))
    result = preflight.inspect_access("o/r", "owner-approval", "main")
    assert result["app_route"] == "rejected-token-revoke-failed"
    assert result["routes"] == []
    assert not any(result["verified_reads"].values())

    monkeypatch.setattr("sys.argv", ["github_auth_preflight", "--repo", "o/r"])
    assert preflight.main() == 1
    assert "working-credential-fixture" not in capsys.readouterr().out


def test_bootstrap_manifest_grants_preflight_read_permissions():
    granted = bootstrap.APP_MANIFEST["default_permissions"]
    for permission in preflight.READ_ONLY_APP_PERMISSIONS:
        assert granted.get(permission) in {"read", "write"}
