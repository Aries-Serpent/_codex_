from __future__ import annotations

import shutil
from pathlib import Path
from typing import Optional

from tools.build_sqlite_snapshot import ARTIFACT_DB, build_snapshot
from tools.codex_sqlite_align import _quote_identifier, _validate_identifier

ROOT = Path(__file__).resolve().parents[1]
PARQUET_DIR = ROOT / "parquet"

_ALLOWED_EXTENSIONS = {"httpfs", "azure"}


def _ensure_within_base(path: Path, base: Optional[Path] = None) -> Path:
    """Resolve *path* and ensure it does not escape *base* (defaults to repo root)."""

    base_dir = (base or ROOT).expanduser().resolve()
    target = Path(path).expanduser().resolve()
    if base_dir == target or base_dir in target.parents:
        return target
    raise ValueError(f"path {target} escapes base directory {base_dir}")


def export_to_parquet(
    db_path: Path = ARTIFACT_DB,
    parquet_dir: Path = PARQUET_DIR,
) -> Path:
    """Export the snapshot SQLite database to partitioned Parquet files.

    The function installs and loads DuckDB's ``httpfs`` and ``azure``
    extensions so the resulting dataset can be uploaded to object storage.
    A parquet directory containing one file per ``id`` value is produced.
    """

    try:  # local import keeps module importable when duckdb is absent
        import duckdb  # type: ignore
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("duckdb is required to export parquet snapshots") from exc

    parquet_dir = _ensure_within_base(parquet_dir)
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

        for ext in _ALLOWED_EXTENSIONS:
            try:
                con.execute(f"INSTALL {ext};")
                con.execute(f"LOAD {ext};")
            except Exception:
                # Installation may fail in offline environments; continue anyway.
                pass
        dataset_path = parquet_dir / "snippet"
        dataset_path = _ensure_within_base(dataset_path, parquet_dir)
        if dataset_path.exists():
            shutil.rmtree(dataset_path)
        safe_table = _validate_identifier(source_table)
        quoted_table = _quote_identifier(safe_table)
        copy_sql = "".join(
            [
                "COPY (SELECT * FROM ",
                quoted_table,
                ") TO ? (FORMAT PARQUET, PARTITION_BY (id))",
            ]
        )
        con.execute(copy_sql, [str(dataset_path)])
    finally:
        con.close()
    return dataset_path


if __name__ == "__main__":
    export_to_parquet()
