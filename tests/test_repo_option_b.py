import duckdb

from tools.build_sqlite_snapshot import build_snapshot
from tools.export_to_parquet import export_to_parquet


def test_export_and_query_parquet():
    build_snapshot()
    dataset_path = export_to_parquet()
    con = duckdb.connect()
    try:
        rows = con.execute(
            "SELECT body FROM read_parquet(?)",
            [str(dataset_path / "*/*.parquet")],
        ).fetchall()
    finally:
        con.close()
    assert ("hello world",) in rows
