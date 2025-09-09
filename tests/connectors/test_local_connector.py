import asyncio
from pathlib import Path

from codex_ml.connectors.local import LocalConnector


def test_local_connector_io(tmp_path: Path):
    conn = LocalConnector()
    file = tmp_path / "a.txt"
    asyncio.run(conn.write_file(str(file), b"hi"))
    data = asyncio.run(conn.read_file(str(file)))
    assert data == b"hi"
    files = asyncio.run(conn.list_files(str(tmp_path)))
    assert "a.txt" in files
