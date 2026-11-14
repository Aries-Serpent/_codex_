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
    assert "ERROR" in capsys.readouterr().err


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

    monkeypatch.setattr(preflight, "_mint_app_token", mint)
    monkeypatch.setattr(preflight, "_gh", lambda *args: (200, {}))
    result = preflight.inspect_access("o/r", "owner-approval", "main")
    assert calls == [(("1", "-----BEGIN FIXTURE-----", "2"), {"repo": "o/r"})]
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
