"""
Test Evidence Parity

Test module for evidence parity.
"""

from __future__ import annotations

import json
from pathlib import Path

from codex.evidence.core import evidence_append


def test_zendesk_evidence_parity(tmp_path: Path, monkeypatch):
    evdir = tmp_path / ".codex" / "evidence"
    evdir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("CODEX_EVIDENCE_DIR", evdir.as_posix())
    monkeypatch.setenv("CODEX_ACTOR", "tester")
    evidence_append(
        action="ZENDESK_PLAN",
        actor="tester",
        tool="zendesk",
        repo="_codex_",
        context={"args": ["plan", "--brand", "acme"], "commit": "HEAD"},
    )
    evidence_append(
        action="ZENDESK_APPLY",
        actor="tester",
        tool="zendesk",
        repo="_codex_",
        context={
            "args": ["apply", "--brand", "acme"],
            "commit": "HEAD",
            "dry_run": True,
        },
    )
    lines = (evdir / "archive_ops.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2, "Lines must not be empty"
    recs = [json.loads(line) for line in lines]
    for rec in recs:
        for key in ("action", "actor", "tool", "repo", "context"):
            assert key in rec, "Condition must be true"
        assert rec["repo"] == "_codex_", "Condition must be true"
        assert "python" in rec["context"] and "os" in rec["context"], "Condition must be true"
