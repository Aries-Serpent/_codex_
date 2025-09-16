# Extension registries

Codex ML exposes pluggable extension points for the critical components of the
training stack.  The registries live under :mod:`codex_ml.registry` and provide
a unified interface for both in-process registration and third-party discovery
via Python entry points.

## Available registries

Each component type is backed by a dedicated :class:`~codex_ml.registry.base.Registry`.
The table below summarises the public handles and the corresponding entry-point
groups that third-party packages may target:

| Component     | Registry symbol                             | Entry-point group            |
| ------------- | -------------------------------------------- | ---------------------------- |
| Tokenizers    | ``codex_ml.registry.tokenizer_registry``     | ``codex_ml.tokenizers``      |
| Models        | ``codex_ml.registry.model_registry``         | ``codex_ml.models``          |
| Metrics       | ``codex_ml.registry.metric_registry``        | ``codex_ml.metrics``         |
| Data loaders  | ``codex_ml.registry.data_loader_registry``   | ``codex_ml.data_loaders``    |
| Trainers      | ``codex_ml.registry.trainer_registry``       | ``codex_ml.trainers``        |

All registries normalise keys to lower case, detect collisions and surface
helpful diagnostics when registrations conflict.

## Programmatic registration

Registries support both decorator-style and direct registrations.  The example
below defines an in-process tokenizer factory.  The same pattern is applicable
to models, metrics, data loaders and trainers::

    from codex_ml.registry import register_tokenizer

    @register_tokenizer("toy")
    def build_toy_tokenizer(**kwargs):
        return {"vocab": kwargs.get("vocab", {})}

Alternatively call :func:`register_tokenizer` with an object directly::

    def build_toy_tokenizer(**kwargs):
        return {"vocab": kwargs.get("vocab", {})}

    register_tokenizer("toy", build_toy_tokenizer)

Use the ``get_*`` helpers to instantiate components lazily:

```python
from codex_ml.registry import get_tokenizer

tokenizer = get_tokenizer("toy", vocab={"a": 0, "b": 1})
```

## Entry-point discovery

Third-party packages can expose components without importing Codex ML at install
time.  Declare an entry point in the package's ``pyproject.toml`` that maps to a
callable or class:

```toml
[project.entry-points."codex_ml.metrics"]
toy_metric = "my_extension.metric:build"
```

Registries load entry points on first use.  When a component is requested the
registry imports the entry point, registers the resulting object, and caches the
outcome for future lookups.  Broken entry points are reported through
``RegistryLoadError`` with the original exception attached to aid debugging.

## Example plugins

Self-contained examples live in ``examples/plugins/``.  They demonstrate the
expected factory signatures and provide artefacts for tests:

- ``toy_tokenizer`` implements a minimal ``encode``/``decode`` interface.
- ``toy_metric`` exposes a callable returning deterministic scores.
- ``toy_model``, ``toy_data_loader`` and ``toy_trainer`` showcase other
  component types and can be used as templates for experimentation.

Install the repository in editable mode (``pip install -e .``) and run
``pytest tests/test_registry.py`` to validate that custom registrations behave
as expected.

## Contribution guidelines

When publishing a third-party plugin:

1. Target the appropriate entry-point group from the table above and include a
   unique, lower-case name.
2. Provide a stable factory function that returns the component instance when
   invoked.  The registry preserves provenance metadata so debugging is easy.
3. Add automated coverage for the component to ensure behaviour remains
   deterministic across releases.
4. Document configuration knobs and dependencies so downstream users understand
   how to consume the plugin.

Following these guidelines keeps the ecosystem consistent and ensures Codex ML
can safely load community extensions.

