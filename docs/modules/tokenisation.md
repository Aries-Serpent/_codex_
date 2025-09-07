# Tokenisation

This module introduces a small `TokenizerAdapter` abstraction with concrete
implementations for HuggingFace models and a whitespace fallback.  The
`HFTokenizerAdapter` wraps any pretrained tokenizer from the
`transformers` library.  `WhitespaceTokenizer` provides a minimal adapter
useful for tests where no external models are required.

Example usage:

```python
from codex_ml.tokenization.adapter import TokenizerAdapter
cfg = {"type": "hf", "pretrained_model_name_or_path": "gpt2"}
Tok = TokenizerAdapter.from_config(cfg)
```
