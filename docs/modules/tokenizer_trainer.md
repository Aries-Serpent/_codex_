# Tokenizer Trainer

`codex_ml.tokenization.train_tokenizer` trains a SentencePiece tokenizer and exports `tokenizer.json`.

## Configuration highlights

- `stream_chunk_size` (default: 1 MiB) configures how much text is read at a time when
  streaming corpora into the tokenizer trainer. Leaving it unset uses the default chunk
  size so large corpora are never fully loaded into memory.

## CLI

```bash
codex tokenizer train --config configs/tokenization/base.yaml
```

It produces a SentencePiece model, a `tokenizer.json`, and HF-compatible
artifacts that can be loaded with `interfaces.tokenizer.HFTokenizer`. Use
`codex tokenizer validate` to confirm corpus manifests and cached artifacts, or
`codex tokenizer encode`/`decode` to interactively test trained models.
