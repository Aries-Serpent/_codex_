# Tokenization Adapters

Codex ships with several tokenizer adapters that present a common interface to
training and evaluation pipelines. This guide focuses on the
`SentencePieceTokenizer`, which wraps the optional [`sentencepiece`][spm]
package and integrates with the `TokenizerAdapter` factory.

> **Optional dependency** — install SentencePiece support with:
>
> ```bash
> pip install sentencepiece
> ```
>
> Alternatively, install the dedicated extra: `pip install .[sentencepiece]`.

## Loading from configuration

`TokenizerAdapter.from_config` recognises configurations with
`{"type": "sentencepiece", "model_path": "path/to/model.model"}` (or a
directory containing a `.model` file) and returns a ready-to-use
`SentencePieceTokenizer`. The optional `special_tokens` entry accepts either a
sequence of strings or a mapping of token-to-id assignments that will be
persisted alongside the model.

```python
from codex_ml.tokenization.adapter import TokenizerAdapter

config = {
    "type": "sentencepiece",
    "model_path": "artifacts/spm.model",
    "special_tokens": ["<extra_pad>"]
}

tokenizer = TokenizerAdapter.from_config(config)
```

## Direct usage

The adapter can also be instantiated directly from a `.model` file (or an
existing `SentencePieceProcessor`). The encode/decode methods mirror the
behaviour of the lightweight adapter under `tokenization/` and support
single-sequence truncation modes (`only_first` and `longest_first`) that retain
leading tokens.

```python
from codex_ml.tokenization.adapter import SentencePieceTokenizer

tokenizer = SentencePieceTokenizer("artifacts/spm.model")
ids = tokenizer.encode("hello world", truncation="only_first", max_length=4)
text = tokenizer.decode(ids)
```

For batches, call `batch_encode` with shared truncation/padding arguments:

```python
encoded_batch = tokenizer.batch_encode(
    ["alpha beta", "gamma delta"],
    truncation="only_first",
    max_length=3,
)
```

## Saving and reloading

Call `save_pretrained(path)` to persist the SentencePiece model, the `.vocab`
file, and a `<prefix>.special_tokens.json` sidecar describing registered special
tokens. The resulting directory can be reloaded with
`SentencePieceTokenizer.from_pretrained(path)` or referenced directly via
`TokenizerAdapter.from_config`.

```python
save_dir = "artifacts/tokenizer"
tokenizer.save_pretrained(save_dir)
reloaded = SentencePieceTokenizer.from_pretrained(save_dir)
assert reloaded.encode("hello world") == tokenizer.encode("hello world")
```

[spm]: https://github.com/google/sentencepiece
