# Tokenizer Trainer

`codex_ml.tokenization.train_tokenizer` trains a SentencePiece tokenizer and exports `tokenizer.json`.

## Configuration highlights

- `stream_chunk_size` (default: 1 MiB) configures how much text is read at a time when
  streaming corpora into the tokenizer trainer. Leaving it unset uses the default chunk
  size so large corpora are never fully loaded into memory.

## CLI

```bash
python -m codex_ml.tokenization.train_tokenizer --input-file corpus.txt --output-dir runs/tokenizer --vocab-size 8000
```

It produces a `tokenizer.model` and HF-compatible artifacts that can be loaded with `interfaces.tokenizer.HFTokenizer`.
