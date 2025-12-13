# Tokenization — Canonical Surfaces and Legacy Shims

This guide clarifies canonical tokenization imports and the behavior of legacy shims.

## Import Behavior (Updated 2025-12-13)

The `src/tokenization` package uses **guarded imports** for optional dependencies. When heavy dependencies (tokenizers, transformers, torch) are not installed, the module gracefully degrades:

```python
import tokenization
# Module imports successfully even without dependencies

tokenization.load_tokenizer    # None if dependencies missing
tokenization.TokenizerAdapter  # None if dependencies missing
tokenization.__all__           # ['sentencepiece_adapter', 'cli'] - only available exports
```

This pattern ensures minimal/offline installs work correctly. See `src/tokenization/__init__.py` for the implementation.

## Canonical Imports
| Use case | Import |
|----------|--------|
| API | `from codex_ml.tokenization import api` |
| SentencePiece adapter | `from codex_ml.tokenization import sentencepiece_adapter` |

These surfaces handle optional dependencies gracefully and are the preferred imports for new code and documentation.

## Legacy Shims (Deprecated)
For backward compatibility, the following legacy modules re-export the canonical implementations and emit DeprecationWarning on import:
- `tokenization.api`
- `tokenization.sentencepiece_adapter`

Example:
```python
# Emits DeprecationWarning, but works
import tokenization.api as legacy_api

# Preferred
from codex_ml.tokenization import api as canonical_api
```text

## Testing Guidance
- Deprecation warnings are expected when importing legacy shims.
- No behavior change is introduced by the shims; they only forward to canonical modules.

*End of guide*
