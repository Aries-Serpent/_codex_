import json
import os
from pathlib import Path

from tools import catalog_db


def test_catalog_ingest(tmp_path: Path) -> None:
    db_file = tmp_path / "cat.sqlite"
    os.environ["CODEX_CATALOG_DB"] = str(db_file)
    report = tmp_path / "compare.json"
    report.write_text(
        json.dumps(
            {"summary": {"unexpected_added": 1, "unexpected_removed": 0, "changed": 2, "moves": 3}}
        )
    )
    catalog_db.record_run(
        {
            "run_id": "r1",
            "started_at": "s",
            "finished_at": "f",
            "status": "ok",
            "git_head": "h",
            "branch": "main",
        }
    )
    catalog_db.ingest_compare_report("r1", str(report))
    catalog_db.upsert_artifact("r1", "manifest", str(report))
    rows = catalog_db.query("SELECT unexpected_added FROM diffs")
    assert rows[0][0] == 1
    assert db_file.exists()
