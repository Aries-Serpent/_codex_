# [Guide]: Tokenizer Adapter Consolidation — Canonical HF Adapter


## Summary
- Canonical import: `from codex_ml.tokenization.hf_adapter import HFTokenizerAdapter`
- Deprecated shim: `from codex_ml.interfaces.tokenizer_hf import HFTokenizerAdapter` (emits DeprecationWarning)

## Rationale
Prevents alias drift and clarifies a single adapter surface. The shim remains for BC until the next major release.

## Testing
- See tests/tokenization/test_hf_adapter_canonical.py to verify import identity.

*End*
