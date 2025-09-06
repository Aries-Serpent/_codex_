# Plugin System

Codex ML exposes a lightweight plugin API with two discovery mechanisms:

1. **In-process registry** – register classes or factories directly using
   decorators.
2. **Optional entry-point loading** – when the environment variable
   `CODEX_PLUGINS_ENTRYPOINTS=1` is set, entry points such as
   `codex_ml.tokenizers` are discovered via `importlib.metadata`.

Plugins should declare a compatibility marker:

```python
__codex_ext_api__ = "v1"
```

## Registering a plugin locally

```python
from codex_ml.plugins import tokenizers
from codex_ml.interfaces.tokenizer import TokenizerAdapter

@tokenizers.register("toy")
class ToyTokenizer(TokenizerAdapter):
    __codex_ext_api__ = "v1"

    def encode(self, text: str, *, add_special_tokens: bool = True):
        return [1, 2, 3]

    def decode(self, ids, *, skip_special_tokens: bool = True):
        return "toy"

    @property
    def vocab_size(self) -> int:
        return 0
```

Invoke via the helper factory:

```python
from codex_ml.interfaces.tokenizer import get_tokenizer

tk = get_tokenizer("toy")
```

## Declaring an entry point

In `pyproject.toml`:

```toml
[project.entry-points."codex_ml.tokenizers"]
my_toy = "my_pkg.toy:ToyTokenizer"
```

Enable discovery:

```bash
export CODEX_PLUGINS_ENTRYPOINTS=1
python -m codex_ml.cli.plugins_cli list tokenizers
```
