import json
from pathlib import Path

import pytest

from codex_ml.connectors.base import ConnectorError
from codex_ml.connectors.remote import RemoteConnector
from codex_ml.monitoring.health import HEALTH_LOG_ENV


@pytest.mark.asyncio
async def test_remote_connector_roundtrip(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    health_dir = tmp_path / "health"
    monkeypatch.setenv(HEALTH_LOG_ENV, str(health_dir))

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

    events = []
    for event_path in health_dir.glob("*.ndjson"):
        events.extend(
            json.loads(raw) for raw in event_path.read_text(encoding="utf-8").splitlines() if raw
        )
    event_names = {entry["event"] for entry in events}
    assert {"initialised", "write", "listed", "read"}.issubset(event_names)


@pytest.mark.asyncio
async def test_remote_connector_manifest_tracks_updates(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv(HEALTH_LOG_ENV, str(tmp_path / "health"))
    connector = RemoteConnector(cache_root=tmp_path)

    manifest = tmp_path / ".remote_manifest.json"
    first = json.loads(manifest.read_text(encoding="utf-8"))
    assert first["files"] == []
    assert first["readonly"] is False

    await connector.write_file("models/model.bin", b"binary")
    updated = json.loads(manifest.read_text(encoding="utf-8"))
    assert "models/model.bin" in updated["files"]
    assert updated["endpoint"].startswith("offline://")
    assert "updated_at" in updated


@pytest.mark.asyncio
async def test_remote_connector_readonly_records_health(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv(HEALTH_LOG_ENV, str(tmp_path / "health"))
    connector = RemoteConnector(cache_root=tmp_path, readonly=True)

    with pytest.raises(ConnectorError):
        await connector.write_file("blocked.txt", b"payload")

    log_path = tmp_path / "health" / "connectors.remote.ndjson"
    assert log_path.exists()
    events = [
        json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines() if line
    ]
    assert any(event["event"] == "write_blocked" for event in events)
