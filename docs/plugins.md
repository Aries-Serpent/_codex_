# Plugin System

This project exposes a lightweight plugin mechanism built around two primitives:

1. **Registries** for models, datasets, and metrics.
2. **Hooks** that integrate with the training loop.

Plugins are plain Python modules that import the relevant registry or hook APIs and register entries as a side effect.

## Registries

Registries live in `common/registry.py` and expose decorator helpers.

```python
from common.registry import METRICS

@METRICS.register("nonzero_rate")
def nonzero_rate(df=None, **kwargs) -> float:
    if df is None or "value" not in df.columns:
        return float("nan")
    return float((df["value"] != 0).mean())
```

## Hooks

Hooks subclass `common.hooks.BaseHook` and can be appended to a `HookManager`.

```python
from common.hooks import BaseHook

class StepCounterHook(BaseHook):
    def on_init(self, state):
        state["plugin_steps"] = 0

    def on_step_end(self, state):
        state["plugin_steps"] += 1
```

## Loading plugins

Hydra config `conf/plugins/default.yaml` lists plugin modules. The training entrypoint automatically calls the loader when plugins are enabled.

```yaml
plugins:
  enable: true
  modules:
    - "hhg_logistics.plugins.example_plugin"
```

```python
from hhg_logistics.plugins import load_plugins

if cfg.plugins.enable:
    load_plugins(cfg.plugins.modules)
```

Plugins may also provide custom hooks; instantiate them within configuration or code as needed.

- No dynamic execution beyond `importlib.import_module` occurs.
- Failures to import plugins are logged but non-fatal.
- The system remains offline-first; plugins operate on local modules.
