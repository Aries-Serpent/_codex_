"""Functional tests for the Internal Tools API endpoints."""

from __future__ import annotations

from pathlib import Path
from typing import Iterator

import pytest
from app.main import app
from app.security import ApiKeyStore
from fastapi.testclient import TestClient

pytestmark = pytest.mark.filterwarnings("ignore:The 'app' shortcut is now deprecated.*")


@pytest.fixture()
def api_key(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[str]:
    store_path = tmp_path / "api_keys.json"
    monkeypatch.setenv("ITA_API_KEYS_PATH", str(store_path))
    store = ApiKeyStore(path=store_path)
    key = store.issue_key()
    yield key


@pytest.fixture()
def client(api_key: str) -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        test_client.headers.update({"X-API-Key": api_key, "X-Request-Id": "test-request"})
        yield test_client


def test_healthz(client: TestClient) -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"


def test_kb_search_returns_results(client: TestClient) -> None:
    response = client.post("/kb/search", json={"query": "Copilot"})
    assert response.status_code == 200
    data = response.json()
    assert data["results"], "Expected non-empty search results"


def test_repo_hygiene_detects_secret(client: TestClient) -> None:
    diff = """diff --git a/app.py b/app.py
@@
+API_KEY = \"AWS_SECRET_KEY=EXAMPLE\"
"""
    response = client.post("/repo/hygiene", json={"diff": diff, "checks": ["secrets"]})
    assert response.status_code == 200
    issues = response.json()["issues"]
    assert any(issue["type"] == "secrets" for issue in issues)


def test_repo_hygiene_rejects_unknown_check(client: TestClient) -> None:
    response = client.post("/repo/hygiene", json={"diff": "", "checks": ["unknown"]})
    assert response.status_code == 400


def test_tests_run_handles_failures(client: TestClient) -> None:
    response = client.post("/tests/run", json={"targets": ["tests/unit", "integration_fail_case"]})
    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"]["total"] == 2
    assert payload["summary"]["failed"] >= 1


def test_git_create_pr_requires_confirm(client: TestClient) -> None:
    body = {
        "repo": "octo/example",
        "title": "Demo",
        "body": "Example PR",
        "base": "main",
        "head": "feature/demo",
    }
    response = client.post("/git/create-pr?dry_run=false", json=body)
    assert response.status_code == 412


def test_git_create_pr_simulation(client: TestClient) -> None:
    body = {
        "repo": "octo/example",
        "title": "Demo",
        "body": "Example PR",
        "base": "main",
        "head": "feature/demo",
    }
    response = client.post("/git/create-pr", json=body)
    assert response.status_code == 200
    data = response.json()
    assert data["simulated"] is True
    assert data["pr_url"] is None
