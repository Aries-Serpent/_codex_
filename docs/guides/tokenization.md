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

### Offline training quickstart

When working in air-gapped or resource-constrained environments you can use the
lightweight `SentencePieceAdapter` from `src/tokenization/` to bootstrap a
tokenizer without any additional infrastructure. The helper exposes a
`train_or_load` method that trains a model if the `.model` file is missing and
loads it otherwise, ensuring repeatable runs on subsequent invocations.

```python
from pathlib import Path

from src.tokenization.sentencepiece_adapter import SentencePieceAdapter

corpus = Path("artifacts/corpus.txt")
adapter = SentencePieceAdapter(Path("artifacts/offline.model"))
adapter.train_or_load(corpus, vocab_size=8000)

ids = adapter.encode("offline training ready", padding="max_length", max_length=16)
text = adapter.decode(ids)
```

Persist the corpus snapshot alongside the trained model to guarantee
reproducibility. The adapter accepts `trainer_kwargs` for advanced options (for
example `unk_surface` or `byte_fallback`) and guards optional dependencies with
clear error messages when `sentencepiece` is unavailable.
### Optional dependencies

The tokenizer workflow depends on the [🤗 `tokenizers`](https://github.com/huggingface/tokenizers)
Rust bindings for both training and encode/decode operations. Configurations that
use the SentencePiece `unigram` trainer additionally require the
[`sentencepiece`](https://github.com/google/sentencepiece) Python package. If either
dependency is missing the CLI exits with a helpful error message pointing to the
required package.

To install everything locally:

```bash
pip install tokenizers sentencepiece
```
### Validation & manifests

Running `codex tokenizer validate` reports the files resolved from the
configuration, highlights any missing shards, and records whether cached
artifacts such as `tokenizer.json`, `tokenizer.model`, and `manifest.json` exist.
When a manifest is present the CLI prints the parsed JSON so provenance hashes
and command-line overrides are visible without opening the file manually.

## Configuration reference

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
