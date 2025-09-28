# Tokenizer Invariants & Canonical `max_seq_len`

This repository standardizes tokenizer usage by pinning a **canonical `max_seq_len`** per model family and explicitly configuring padding and truncation:

```python
encoded = tokenizer(
    texts,
    truncation=True,
    padding="max_length",
    max_length=CANONICAL_MAX_SEQ_LEN,  # e.g., 2048 / 4096 / 8192
    return_tensors="pt",
)
```

## Why it matters

Tokenizer defaults vary by backend and version. Setting `truncation`, `padding`, and `max_length` removes drift and ensures sequence lengths remain predictable across environments.

## Policy

- Declare `CANONICAL_MAX_SEQ_LEN` for each model family (matching or below `tokenizer.model_max_length`).
- Keep `padding_side` consistent per model (decoder-only models typically use right padding unless specified otherwise).
- Tests should enforce:
  - `len(ids) == max_length` when `padding="max_length"` and `truncation=True`.
  - `len(ids) <= max_length` when `truncation=True` and padding is disabled.

See:
- `tests/tokenization/test_padding_truncation_ext.py`
- `tests/tokenization/test_sp_fixture_roundtrip.py`
