from __future__ import annotations

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "db" / "schema.sql"
ARTIFACT_DB = ROOT / ".artifacts" / "snippets.db"

SNIPPETS = [
    {"body": "hello world"},
    {"body": "goodbye world"},
    {"body": "lorem ipsum"},
]


def build_snapshot(
    db_path: Path = ARTIFACT_DB,
    schema_path: Path = SCHEMA_PATH,
    snippets: list[dict[str, str]] = SNIPPETS,
) -> Path:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()
    con = sqlite3.connect(db_path)
    try:
        con.executescript(schema_path.read_text())
        con.executemany(
            "INSERT INTO snippet(body) VALUES (?)",
            [(s["body"],) for s in snippets],
        )
        con.commit()
    finally:
        con.close()
    return db_path


if __name__ == "__main__":
    build_snapshot()
