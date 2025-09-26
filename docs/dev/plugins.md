# Plugin Architecture

Codex exposes first-class registries for tokenizers, models, data loaders,
metrics and trainers.  Registries are case-insensitive and discover third-party
components via Python entry points.

## Built-in registries

```python
from codex_ml.registry import list_models, get_tokenizer

print("Models:", list_models())
tokenizer = get_tokenizer("hf", name_or_path="sshleifer/tiny-gpt2")
```
## Creating a plugin package

1. Add entry points to your package:

```toml
[project.entry-points."codex_ml.models"]
awesome = "my_pkg.models:build_model"
```
2. Ensure `build_model(cfg: dict) -> nn.Module` returns an instantiated model.
3. Distribute the package (wheel, editable install, etc.).
4. Codex will discover it on demand: `codex_ml.registry.get_model("awesome", cfg)`.

See [`examples/plugins`](../../examples/plugins/) for toy implementations.

## Handling conflicts

Duplicate registrations raise `RegistryConflictError`.  Override intentionally:

```python
from codex_ml.registry import register_trainer

register_trainer("custom", my_trainer, override=True)
```
## Debugging

* List available entries with `python -m codex_ml.registry` (future work).
* Use `Registry.temporarily_registered({...})` in tests to avoid leaking state.
* Verify entry point resolution using `importlib.metadata.entry_points()`.
