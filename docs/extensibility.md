# Extending Codex ML via entry points

Codex ML exposes a lightweight plugin surface that lets external packages add
optional metrics and tokenizers without modifying the core repository.  Plugin
loading is entirely offline and best-effort: discovery failures are swallowed so
that first-party workflows keep running in constrained environments.

## Discovery lifecycle

Two convenience helpers trigger plugin discovery:

- `codex_ml.metrics.registry.init_metric_plugins()`
- `codex_ml.registry.tokenizers.init_tokenizer_plugins()`

Call one (or both) during application start-up before looking up components via
`get_metric()` / `list_metrics()` or `get_tokenizer()` / `list_tokenizers()`.
The helpers ensure discovery only happens once per process unless `force=True`
is passed—useful in tests.

The loader looks for Python entry points named after the component group.  For
metrics the group is `codex_ml.metrics`; for tokenizers it is
`codex_ml.tokenizers`.

## Writing a plugin

Entry points can target either a callable or a module.  In both cases the
plugin receives a `register` function from the core registry and should call it
for every component it wishes to expose.

```python
# my_pkg/codex_plugins.py
from __future__ import annotations

from codex_ml.metrics.registry import register_metric


def register(register_fn=register_metric):
    # Register a metric using the core helper
    register_fn("weighted_accuracy", weighted_accuracy)


def weighted_accuracy(predictions, targets, weights=None):
    ...
```

The same pattern works for tokenizers using
`codex_ml.registry.tokenizers.register_tokenizer`:

```python
from codex_ml.registry.tokenizers import register_tokenizer


def register_tokenizers(register_fn=register_tokenizer):
    register_fn("custom", build_custom_tokenizer)


def build_custom_tokenizer(**kwargs):
    ...
```

### pyproject.toml

```toml
[project.entry-points."codex_ml.metrics"]
weighted = "my_pkg.codex_plugins:register"

[project.entry-points."codex_ml.tokenizers"]
my_tokenizer = "my_pkg.codex_plugins:register_tokenizers"
```

Each plugin entry point is invoked once.  Implementations can contribute more
than one component by calling `register_fn` multiple times.

## Troubleshooting

- Discovery is silent-by-default: broken plugins are skipped.  Set
  `force=True` when calling `init_*_plugins()` in tests to re-trigger discovery
  after adjusting mocks.
- Registrations are last-write wins.  If two plugins register the same name the
  most recent registration replaces the earlier one.
