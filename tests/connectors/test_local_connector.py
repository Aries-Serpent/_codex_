import pytest

from codex_ml.connectors.base import ConnectorError, LocalConnector


@pytest.mark.asyncio
async def test_local_connector_roundtrip(tmp_path):
    conn = LocalConnector(tmp_path)
    await conn.write_file("subdir/file.txt", b"hello")
    files = await conn.list_files("subdir")
    assert files == ["subdir/file.txt"]
    data = await conn.read_file("subdir/file.txt")
    assert data == b"hello"


@pytest.mark.asyncio
async def test_local_connector_security(tmp_path):
    conn = LocalConnector(tmp_path)
    with pytest.raises(ConnectorError):
        await conn.read_file("../secret.txt")


@pytest.mark.asyncio
async def test_list_empty(tmp_path):
    conn = LocalConnector(tmp_path)
    assert await conn.list_files("does-not-exist") == []
