from __future__ import annotations

from pathlib import Path

from codex.archive.api import restore, store
from codex.archive.plan import build_plan


def test_build_plan_and_store(tmp_path: Path, monkeypatch) -> None:
    f_old = tmp_path / "old.py"
    f_old.write_text("# DEPRECATED\nprint('x')\n", encoding="utf-8")
    f_new = tmp_path / "new.py"
    f_new.write_text("print('new')\n", encoding="utf-8")

    import os
    import time

    os.utime(f_old.as_posix(), (time.time() - 200 * 86400, time.time() - 200 * 86400))

    plan = build_plan(tmp_path, analyze_sha="HEAD", excludes=[], age_days_threshold=180)
    assert plan["entries"], "expected at least one entry in auto-plan"
    entry = plan["entries"][0]
    assert entry["path"].endswith("old.py")
    assert entry["score"] >= 0.7

    monkeypatch.setenv("CODEX_ARCHIVE_BACKEND", "sqlite")
    monkeypatch.setenv("CODEX_ARCHIVE_URL", "sqlite:///./.codex/archive_test.sqlite")
    monkeypatch.setenv("CODEX_EVIDENCE_DIR", ".codex/evidence")
    Path(".codex/evidence").mkdir(parents=True, exist_ok=True)

    payload = (tmp_path / entry["path"].split("/")[-1]).read_bytes()
    out = store(
        repo="_codex_",
        path=entry["path"],
        by="tester",
        reason=entry["reason"],
        commit_sha="HEAD",
        bytes_in=payload,
        mime=entry["mime"],
        lang=entry["lang"],
    )
    assert "tombstone" in out and "sha256" in out

    restored = restore(out["tombstone"])
    assert restored["bytes"] == payload
