# Tokenizer Invariants & Canonical `max_seq_len`

This repo standardizes tokenizer behavior across models by pinning a **canonical `max_seq_len`** per model family and using explicit padding/truncation:

```python
encoded = tokenizer(
    texts,
    truncation=True,
    padding="max_length",
    max_length=CANONICAL_MAX_SEQ_LEN,  # e.g., 2048 / 4096 / 8192
    return_tensors="pt",
)
```

**Why:** Transformers padding/truncation depends on parameters and tokenizer configuration. Explicitly setting `truncation`, `padding`, and `max_length` avoids silent drift across tokenizers and versions.

**Policy**
- Declare `CANONICAL_MAX_SEQ_LEN` for each model family (match or be <= `tokenizer.model_max_length`).
- Keep `padding_side` consistent for the model (e.g., right for decoder-only unless specified otherwise).
- Tests verify:
  - `len(ids) == max_length` when `padding='max_length'` & `truncation=True`
  - `len(ids) <= max_length` when `truncation=True` & `pad=False`

See also: `tests/tokenization/test_padding_truncation_ext.py` and the SP fixture test for invariants.
