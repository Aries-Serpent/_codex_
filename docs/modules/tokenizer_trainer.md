# Tokenizer Trainer

`codex_ml.tokenization.train_tokenizer` trains a SentencePiece tokenizer and exports `tokenizer.json`.

Streaming ingestion is enabled by default. Set `stream_chunk_size` in the
configuration (or supply `--stream-chunk-size` via the CLI) to tune how many
characters are buffered per read. The chunk size is captured in the generated
`manifest.json` alongside other hyperparameters.

## CLI

```bash
codex tokenizer train --config configs/tokenization/base.yaml
```

It produces a SentencePiece model, a `tokenizer.json`, and HF-compatible
artifacts that can be loaded with `interfaces.tokenizer.HFTokenizer`. Use
`codex tokenizer validate` to confirm corpus manifests and cached artifacts, or
`codex tokenizer encode`/`decode` to interactively test trained models.
