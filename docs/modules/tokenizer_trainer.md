# Tokenizer Trainer

`codex_ml.tokenization.train_tokenizer` trains a SentencePiece tokenizer and exports `tokenizer.json`.

## Configuration highlights

- `streaming` disables eager loading of corpus files. Enable it when training on
  large datasets to keep memory usage flat; leave it `false` for small corpora to
  avoid the additional IO overhead of chunked reads.
- `stream_chunk_size` (default: 1 MiB when streaming is on) controls the size of
  each chunk fed to the trainer. Smaller values reduce peak memory even further
  but increase wall-clock time because SentencePiece/BPE see more iterator calls.

## CLI

```bash
codex tokenizer train --config configs/tokenization/base.yaml
```

It produces a SentencePiece model, a `tokenizer.json`, and HF-compatible
artifacts that can be loaded with `interfaces.tokenizer.HFTokenizer`. Use
`codex tokenizer validate` to confirm corpus manifests and cached artifacts, or
`codex tokenizer encode`/`decode` to interactively test trained models.
