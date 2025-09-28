# Tokenizer Invariants & Canonical `max_seq_len`

This repository standardizes tokenizer behavior across model families by pinning a **canonical `max_seq_len`** and using explicit padding/truncation:

```python
encoded = tokenizer(
    texts,
    truncation=True,
    padding="max_length",
    max_length=CANONICAL_MAX_SEQ_LEN,  # e.g., 2048 / 4096 / 8192
    return_tensors="pt",
)
```

## Why this matters

Tokenizer padding/truncation depends on tokenizer configuration and library defaults. Explicitly setting `truncation`, `padding`, and `max_length` avoids silent drift across tokenizers, library versions, and SentencePiece models.

## Policy

- Declare `CANONICAL_MAX_SEQ_LEN` for each model family (match or be <= `tokenizer.model_max_length`).
- Keep `padding_side` consistent for the model (e.g., right for decoder-only unless specified otherwise).
- Tests assert:
  - `len(ids) == max_length` when `padding='max_length'` and `truncation=True`.
  - `len(ids) <= max_length` when `truncation=True` and `pad=False`.

See `tests/tokenization/test_padding_truncation_ext.py` and the SentencePiece fixture round-trip test for enforcement examples.
