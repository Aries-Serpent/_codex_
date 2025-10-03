# Connectors

Connectors provide async access to external data sources. The `LocalConnector` works with the local filesystem:

```python
from codex_ml.connectors.local import LocalConnector
```

Remote endpoints are disabled in offline runs. Use the `RemoteConnector` shim to make this explicit in tests or tooling:

```python
from codex_ml.connectors.remote import RemoteConnector, ConnectorError

remote = RemoteConnector()
files = await remote.list_files("models")  # []

try:
    await remote.read_file("weights.bin")
except ConnectorError as exc:
    print(exc)
```

Register new connectors via `codex_ml.connectors.registry.register_connector`.
