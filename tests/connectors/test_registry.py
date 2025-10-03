import pytest

from codex_ml.connectors.base import Connector
from codex_ml.connectors.registry import get_connector, list_connectors, register_connector


class DummyConnector(Connector):
    async def list_files(self, path):  # pragma: no cover - simple
        return []

    async def read_file(self, path):  # pragma: no cover - simple
        return b""

    async def write_file(self, path, data):  # pragma: no cover - simple
        pass


def test_registry_get_and_register():
    register_connector("dummy", DummyConnector)
    conn = get_connector("dummy")
    assert isinstance(conn, DummyConnector)
    available = list_connectors()
    assert "local" in available and "remote" in available
    with pytest.raises(KeyError):
        get_connector("missing")
