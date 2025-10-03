from pathlib import Path

import pytest

from codex_ml.connectors.remote import RemoteConnector


@pytest.mark.asyncio
async def test_remote_connector_roundtrip(tmp_path: Path) -> None:
    connector = RemoteConnector(cache_root=tmp_path)
    await connector.write_file("samples/data.txt", b"payload")
    files = await connector.list_files(".")
    assert "samples/data.txt" in files
    data = await connector.read_file("samples/data.txt")
    assert data == b"payload"

    manifest = tmp_path / ".remote_manifest.json"
    assert manifest.exists()
    payload = manifest.read_text(encoding="utf-8")
    assert "samples/data.txt" in payload
