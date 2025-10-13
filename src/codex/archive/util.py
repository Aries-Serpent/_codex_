from __future__ import annotations

import json
import os
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_EVIDENCE_DIR = Path(".codex/evidence")
DEFAULT_ARCHIVE_URL = "sqlite:///./.codex/archive.sqlite"
DEFAULT_BACKEND = "sqlite"
DEFAULT_TABLE = "codex_archive_blobs"


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def get_archive_backend() -> str:
    return os.getenv("CODEX_ARCHIVE_BACKEND", DEFAULT_BACKEND).strip().lower() or DEFAULT_BACKEND


def get_archive_url() -> str:
    return os.getenv("CODEX_ARCHIVE_URL", DEFAULT_ARCHIVE_URL)


def get_archive_table() -> str:
    return os.getenv("CODEX_ARCHIVE_TABLE", DEFAULT_TABLE)


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def evidence_dir() -> Path:
    base = Path(os.getenv("CODEX_EVIDENCE_DIR", DEFAULT_EVIDENCE_DIR.as_posix()))
    return ensure_dir(base)


def evidence_path() -> Path:
    return evidence_dir() / "archive_ops.jsonl"


def append_evidence(record: Mapping[str, Any]) -> None:
    path = evidence_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(dict(record), sort_keys=True) + "\n")
