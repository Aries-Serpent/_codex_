# Plugin Registry

The Codex ML plugin surface is intentionally small. A single registry keeps track of
`BasePlugin` instances and can populate itself from Python entry points.

## Programmatic registration

```python
from codex_ml.plugins import BasePlugin, registry

class MyPlugin(BasePlugin):
    def name(self) -> str:
        return "my-plugin"

    def version(self) -> str:
        return "0.1.0"

registry().register(MyPlugin())
```

The registry is global within the process, so repeated calls return the same instance.
Use `override=True` when you intentionally want to replace an existing plugin implementation.

## Entry-point discovery

Declare plugins under the `codex_ml.plugins` group in `pyproject.toml`:

```toml
[project.entry-points."codex_ml.plugins"]
my-plugin = "my_pkg.my_module:MyPlugin"
```

Then call discovery:

```python
from codex_ml.plugins import registry
added = registry().discover()
```

Discovery is best-effort: broken entry points are skipped so the rest of the environment can keep loading.

## Example plugin

`examples/plugins/hello_plugin.py` is bundled for smoke tests and demonstrates the minimum viable plugin implementation.
