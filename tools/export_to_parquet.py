from __future__ import annotations

import shutil
from pathlib import Path

import duckdb

from tools.build_sqlite_snapshot import ARTIFACT_DB, build_snapshot

ROOT = Path(__file__).resolve().parents[1]
PARQUET_DIR = ROOT / "parquet"


def export_to_parquet(
    db_path: Path = ARTIFACT_DB,
    parquet_dir: Path = PARQUET_DIR,
) -> Path:
    """Export the snapshot SQLite database to partitioned Parquet files.

    The function installs and loads DuckDB's ``httpfs`` and ``azure``
    extensions so the resulting dataset can be uploaded to object storage.
    A parquet directory containing one file per ``id`` value is produced.
    """

    parquet_dir.mkdir(parents=True, exist_ok=True)
    if not db_path.exists():
        build_snapshot(db_path)

    con = duckdb.connect()
    try:
        source_table = "snap.snippet"
        db_path_sql = str(db_path).replace("'", "''")
        try:
            con.execute(f"ATTACH DATABASE '{db_path_sql}' AS snap (TYPE SQLITE)")
        except duckdb.IOException:
            import sqlite3

            sqlite_con = sqlite3.connect(db_path)
            try:
                rows = sqlite_con.execute("SELECT id, body FROM snippet").fetchall()
            finally:
                sqlite_con.close()
            con.execute("CREATE TEMP TABLE snippet(id INTEGER, body TEXT)")
            con.executemany("INSERT INTO snippet VALUES (?, ?)", rows)
            source_table = "snippet"

        for ext in ("httpfs", "azure"):
            try:
                con.execute(f"INSTALL {ext};")
                con.execute(f"LOAD {ext};")
            except Exception:
                # Installation may fail in offline environments; continue anyway.
                pass
        dataset_path = parquet_dir / "snippet"
        if dataset_path.exists():
            shutil.rmtree(dataset_path)
        dataset_sql = str(dataset_path).replace("'", "''")
        con.execute(
            f"COPY (SELECT * FROM {source_table}) TO '{dataset_sql}' "
            "(FORMAT PARQUET, PARTITION_BY (id))"
        )
    finally:
        con.close()
    return dataset_path


if __name__ == "__main__":
    export_to_parquet()
