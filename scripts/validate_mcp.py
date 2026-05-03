"""Validation helper for MCP scaffolding.

Usage examples:
- python scripts/validate_mcp.py --check-capability-map
- python scripts/validate_mcp.py --run-http-smoke
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Iterable
from pathlib import Path

import yaml
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from mcp.server.http import ContextItem, ContextUpsertRequest, QueryRequest, app

REQUIRED_FILES: list[Path] = [
    ROOT / ".copilot-space" / "mcp.example.json",
    ROOT / "codex_capability_map.yaml",
    ROOT / "docs" / "mcp" / "api_schema.md",
    ROOT / "docs" / "mcp" / "authentication.md",
    ROOT / "docs" / "mcp" / "rate_limiting.md",
    ROOT / "docs" / "mcp" / "server_deployment.md",
    ROOT / "scripts" / "validate_mcp.py",
    ROOT / "tests" / "mcp" / "test_http_server.py",
]


def _load_json(path: Path) -> None:
    with path.open() as fp:
        json.load(fp)


def _load_yaml(path: Path) -> dict:
    with path.open() as fp:
        return yaml.safe_load(fp)


def check_required_files(paths: Iterable[Path]) -> list[Path]:
    missing = [p for p in paths if not p.exists()]
    if missing:
        raise SystemExit(f"Missing required files: {missing}")
    return []


def check_capability_map_has_mcp(path: Path) -> None:
    data = _load_yaml(path)
    capabilities = data.get("capabilities", {})
    expected_keys = {
        "mcp-protocol-surface",
        "mcp-tooling-registry",
        "mcp-authentication",
        "mcp-rate-limiting",
        "mcp-observability",
        "mcp-versioning",
    }
    missing = expected_keys - set(capabilities.keys())
    if missing:
        raise SystemExit(f"Capability map missing entries: {sorted(missing)}")


def run_http_smoke() -> None:
    client = TestClient(app)
    headers = {"X-MCP-API-Key": os.environ.get("MCP_API_KEY", "dev-key")}

    health = client.get("/mcp/v1/health")
    if health.status_code != 200:
        raise SystemExit(f"Health failed: {health.status_code} {health.text}")

    query_resp = client.post(
        "/mcp/v1/query",
        headers=headers,
        json=QueryRequest(query="codex", top_k=2).dict(),
    )
    if query_resp.status_code != 200:
        raise SystemExit(f"Query failed: {query_resp.status_code} {query_resp.text}")

    upsert_resp = client.post(
        "/mcp/v1/context",
        headers=headers,
        json=ContextUpsertRequest(
            items=[ContextItem(id="smoke", content="smoke test", metadata={"scope": "test"})]
        ).dict(),
    )
    if upsert_resp.status_code != 200:
        raise SystemExit(f"Context failed: {upsert_resp.status_code} {upsert_resp.text}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate MCP scaffolding")
    parser.add_argument("--check-capability-map", action="store_true", help="Ensure MCP keys exist in capability map")
    parser.add_argument("--run-http-smoke", action="store_true", help="Run lightweight HTTP smoke tests")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    check_required_files(REQUIRED_FILES)
    _load_json(ROOT / ".copilot-space" / "mcp.example.json")

    if args.check_capability_map:
        check_capability_map_has_mcp(ROOT / "codex_capability_map.yaml")

    if args.run_http_smoke:
        run_http_smoke()

    print("MCP validation completed")


if __name__ == "__main__":
    main()
