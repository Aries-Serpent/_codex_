# Examples: Atomic Patch Diff Style (v1.2)
> Generated: 2025-11-02 15:10:07 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Diff Coach], [Secondary: Reviewer] ⚡ Energy: 5

Example — Add parity test
```diff
*** Begin Patch
*** Add File: tests/tokenization/test_tokenizer_parity.py
+import pytest
+...
*** End Patch
```

Validation Checklist
- Lint/typecheck pass
- Tests updated and green
- Security scans reviewed
- Schema validation unaffected (configs untouched)
