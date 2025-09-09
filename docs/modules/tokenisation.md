# Tokenisation

`_codex_` uses a small adapter layer to provide a consistent interface across
different tokeniser back‑ends.  All tokenisers implement the abstract
`TokenizerAdapter` interface with four core methods: `encode`, `decode`,
`batch_encode`, and `save_pretrained`.

Two concrete adapters are available:

- **HFTokenizerAdapter** – wraps a Hugging Face `PreTrainedTokenizer`.  Select a
  model via `pretrained_model_name_or_path` and optionally supply
  `special_tokens` (BOS/EOS/PAD/UNK) in the Hydra config.
- **WhitespaceTokenizer** – a minimal whitespace splitter used for quick tests
  and smoke runs.

Tokeniser selection is configured through Hydra.  The base config lives in
`configs/tokenizer/multilingual.yaml` or `configs/tokenizer/base.yaml` (when
added) and exposes the following keys:

```yaml
type: hf            # or "whitespace"
pretrained_model_name_or_path: gpt2
special_tokens: {}
```

To override from the command line:

```bash
python -m codex_ml.cli.main tokenizer.type=whitespace
```

To add a new tokeniser backend, subclass `TokenizerAdapter` and register it in
`TokenizerAdapter.from_config`.

Multilingual tokenisation remains available via the Hugging Face
`bert-base-multilingual-cased` model using `configs/tokenizer/multilingual.yaml`.
