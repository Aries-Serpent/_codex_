# [How-to]: Tokenizer Migration & Deprecation Shim  
> Generated: 2025-10-09 20:20:37 UTC | Author: mbaetiong  
Roles: [Audit Orchestrator], [Capability Cartographer]  Energy: 5

Context
- Consolidate legacy tokenizer entry points under a stable API while warning on legacy access.

Behavior
- src/tokenization/api.py re-exports:
  - HFTokenizerAdapter
  - SentencePieceTokenizer
- Legacy alias:
  - legacy_tokenizer → emits DeprecationWarning on use.

Usage
```python
from src.tokenization.api import HFTokenizerAdapter, SentencePieceTokenizer
# Legacy (triggers DeprecationWarning):
from src.tokenization.api import legacy_tokenizer
```

Testing
- tests/tokenization/test_deprecation.py asserts a DeprecationWarning on legacy access.
- Direct adapter imports must not warn.

Operator Notes
- No behavior change besides warnings.
- Keep shim for two releases; then remove legacy alias.

*End*