# Tokenization Validation Updates

Recent changes improve determinism and error handling across the tokenization stack:

- `SentencePieceAdapter.add_special_tokens` now accepts a sequence of token strings, merges with any persisted mapping, returns a `Dict[str, int]`, and writes updates back to `*.special_tokens.json` for stable IDs across runs.
- `WhitespaceTokenizer.encode` uses a deterministic BLAKE2b-based hash instead of Python's salted `hash()` so repeated runs (even in separate processes) produce identical token IDs.
- `tokenization.train_tokenizer.train` raises a `FileNotFoundError` when the configured corpus glob does not resolve to any files, providing immediate feedback about misconfigured input patterns.

## Verification

Run the focused tests below from the repository root to exercise the new behavior:

```bash
pytest -q tests/test_sentencepiece_adapter.py::test_add_special_tokens_returns_mapping
pytest -q tests/test_tokenizer.py::test_whitespace_tokenizer_deterministic
pytest -q tests/test_train_tokenizer.py::test_train_tokenizer_no_corpus_raises
```

A full sweep of the related suites can be triggered with:

```bash
pytest -q tests/test_sentencepiece_adapter.py tests/test_tokenizer.py tests/test_train_tokenizer.py
```
