"""Canonical, secret-free maintainer control-plane discovery."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts.autonomous.codespace_keepalive import read_status, runtime_dir_default

ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = ROOT / ".codex" / "maintainer_control_plane.json"


def load_catalog() -> dict[str, Any]:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    if catalog.get("owner", {}).get("human_login") != "mbaetiong":
        raise ValueError("maintainer owner invariant violated")
    if catalog.get("owner", {}).get("human_reviewers_required") != 0:
        raise ValueError("single-owner review invariant violated")
    return catalog


def maintainer_status() -> dict[str, Any]:
    catalog = load_catalog()
    return {
        "schema_version": catalog["schema_version"],
        "owner": catalog["owner"],
        "session_liveness": catalog["session_liveness"],
        "commands": catalog["commands"],
        "credential_routes": catalog["credential_routes"],
        "mcp_tools": catalog["mcp_tools"],
        "discovery": catalog["discovery"],
        "keepalive": read_status(runtime_dir_default()),
    }
