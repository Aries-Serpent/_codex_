from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from codex.archive.api import restore
from codex.cli_archive import app as archive_app


def test_consolidation_end_to_end(tmp_path: Path, monkeypatch) -> None:
    runner = CliRunner()
    root = tmp_path
    (root / "src" / "codex" / "mod").mkdir(parents=True, exist_ok=True)
    canonical = root / "src" / "codex" / "mod" / "foo.py"
    duplicate = root / "src" / "codex" / "mod" / "foo_old.py"
    canonical.write_text("def func():\n    return 42\n", encoding="utf-8")
    original_duplicate = (
        "def func():\n"
        "    return 42  # duplicate implementation\n"
    )
    duplicate.write_text(original_duplicate, encoding="utf-8")

    (root / "artifacts").mkdir(parents=True, exist_ok=True)
    (root / ".codex" / "evidence").mkdir(parents=True, exist_ok=True)

    monkeypatch.setenv("CODEX_ARCHIVE_BACKEND", "sqlite")
    monkeypatch.setenv(
        "CODEX_ARCHIVE_URL",
        f"sqlite:///{(root / '.codex' / 'archive.sqlite').as_posix()}",
    )
    monkeypatch.setenv(
        "CODEX_EVIDENCE_DIR", (root / ".codex" / "evidence").as_posix()
    )
    monkeypatch.chdir(root)

    plan_path = root / "artifacts" / "consolidation_plan.json"
    res_plan = runner.invoke(
        archive_app,
        [
            "consolidate-plan",
            "--root",
            ".",
            "--out",
            plan_path.as_posix(),
        ],
    )
    assert res_plan.exit_code == 0, res_plan.output
    assert plan_path.exists()
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    clusters = plan.get("clusters", [])
    assert clusters, "expected consolidation clusters"
    duplicate_rel = duplicate.relative_to(root).as_posix()
    assert any(
        any(d.get("path") in {duplicate.as_posix(), duplicate_rel} for d in c.get("duplicates", []))
        for c in clusters
    ), "duplicate should be present in plan"

    res_apply = runner.invoke(
        archive_app,
        [
            "consolidate-apply",
            plan_path.as_posix(),
            "--repo",
            "_codex_",
            "--by",
            "tester",
        ],
    )
    assert res_apply.exit_code == 0, res_apply.output
    payload = json.loads(res_apply.stdout)
    applied = payload.get("applied", [])
    rec = next(
        (
            item
            for item in applied
            if item.get("path") in {duplicate.as_posix(), duplicate_rel}
        ),
        None,
    )
    assert rec is not None
    tombstone = rec["tombstone"]

    shim_text = duplicate.read_text(encoding="utf-8")
    assert "AUTO-GENERATED SHIM" in shim_text
    assert "from codex.mod.foo import *" in shim_text.replace("  ", " ")

    evidence_path = root / ".codex" / "evidence" / "archive_ops.jsonl"
    assert evidence_path.exists()
    contents = evidence_path.read_text(encoding="utf-8")
    assert "CONSOLIDATE_APPLY" in contents
    assert duplicate.as_posix() in contents or duplicate_rel in contents

    restored = restore(tombstone)
    assert restored["bytes"].decode("utf-8") == original_duplicate
