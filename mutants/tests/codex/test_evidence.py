"""Smoke tests for :mod:`codex.evidence`."""

from __future__ import annotations

import json
from pathlib import Path

import pytest


def test_append_evidence_writes_record(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from codex import evidence

    monkeypatch.setenv("CODEX_EVIDENCE_DIR", str(tmp_path))
    evidence.append_evidence("record.ndjson", {"foo": "bar"})

    out_file = tmp_path / "record.ndjson"
    assert out_file.exists(), "Condition must be true"
    payload = json.loads(out_file.read_text().strip())
    assert payload.get("meta"), "Condition must be true"
    assert payload.get("foo") == "bar", "Condition must be true"


def test_utc_now_format() -> None:
    from codex.evidence import utc_now

    stamp = utc_now()
    assert stamp.endswith("Z"), "Condition must be true"
    assert "T" in stamp, "Condition must be true"
