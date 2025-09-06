# Tokenizer Trainer

`codex_ml.tokenization.train_tokenizer` trains a SentencePiece tokenizer and exports `tokenizer.json`.

## CLI

```bash
python -m codex_ml.tokenization.train_tokenizer --input-file corpus.txt --output-dir runs/tokenizer --vocab-size 8000
```

It produces a `tokenizer.model` and HF-compatible artifacts that can be loaded with `interfaces.tokenizer.HFTokenizer`.
