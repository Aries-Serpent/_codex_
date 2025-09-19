"""Contract regression tests for the OpenAPI specification."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pytest
import yaml
from app.main import app
from fastapi.testclient import TestClient

pytestmark = pytest.mark.filterwarnings("ignore:The 'app' shortcut is now deprecated.*")

SPEC_PATH = Path(__file__).resolve().parents[1] / "openapi.yaml"


@pytest.fixture()
def auth_headers(monkeypatch: pytest.MonkeyPatch) -> dict[str, str]:
    monkeypatch.setenv("ITA_API_KEY", "contract-key")
    return {"X-API-Key": "contract-key", "X-Request-Id": "contract-test"}


def _load_contract() -> dict:
    with SPEC_PATH.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _extract_paths(contract: dict) -> Iterable[str]:
    return contract.get("paths", {}).keys()


def test_contract_exposes_expected_paths() -> None:
    contract_paths = set(_extract_paths(_load_contract()))
    expected = {"/healthz", "/kb/search", "/repo/hygiene", "/tests/run", "/git/create-pr"}
    assert expected.issubset(contract_paths)


def test_openapi_matches_fastapi_schema(auth_headers: dict[str, str]) -> None:
    contract = _load_contract()
    with TestClient(app) as client:
        response = client.get("/openapi.json", headers=auth_headers)
        assert response.status_code == 200
        live_schema = response.json()
    for path, methods in contract["paths"].items():
        assert path in live_schema["paths"], f"Path {path} missing from generated schema"
        for method in methods:
            assert method in live_schema["paths"][path], f"Method {method} missing for {path}"


# Placeholder: in CI, use schemathesis to fuzz test against openapi.yaml
