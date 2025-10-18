# Tokenization — Canonical Surfaces and Legacy Shims

This guide clarifies canonical tokenization imports and the behavior of legacy shims.

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
```

## Testing Guidance
- Deprecation warnings are expected when importing legacy shims.
- No behavior change is introduced by the shims; they only forward to canonical modules.

*End of guide*
