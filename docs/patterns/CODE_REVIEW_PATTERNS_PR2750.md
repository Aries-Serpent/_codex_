# Code Review Patterns and Best Practices (PR #2750)

This document captures reusable patterns discovered during the code review and self-healing process for PR #2750.

## Security Patterns

### 1. Shell Variable Injection Prevention

**Pattern**: Pass shell variables to Python heredocs as environment variables, not via string interpolation.

**Example**:
```bash
# ❌ VULNERABLE - Direct interpolation
python3 <<PYEOF
path = '${USER_INPUT}'
PYEOF

# ✅ SECURE - Environment variables with quoted heredoc
export BUILD_PATH="${USER_INPUT}"
python3 <<'PYEOF'
import os
path = os.environ.get('BUILD_PATH')
PYEOF
```

**Location**: `scripts/local/build_faiss.sh:59-66, 132-139`

**Rationale**: Prevents arbitrary code execution via crafted CLI arguments or environment variables. Critical for scripts accepting external input.

---

## PyTorch/ML Patterns

### 2. Meta Device Model Loading

**Pattern**: Use `device.type` attribute instead of `str(device)` for meta device detection.

**Example**:
```python
# ❌ FRAGILE - String comparison
if str(model.device) == "meta":
    model = model.to("cpu")

# ✅ ROBUST - Type attribute comparison
if hasattr(model, "device"):
    device_type = getattr(model.device, "type", None)
    if device_type == "meta":
        model = model.to_empty("cpu")
```

**Location**: `src/codex/rag/utils.py:34-36`

**Rationale**: Ensures compatibility across PyTorch versions. Handles test environments where models may be on meta devices.

---

## Testing Patterns

### 3. Optional Test Dependencies

**Pattern**: Mark tests requiring optional packages with `@pytest.mark.skipif` and conditional imports.

**Example**:
```python
# Check for optional package
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Skip tests when not available
@pytest.mark.skipif(not OPENAI_AVAILABLE, reason="OpenAI package not installed")
class TestOpenAIFeatures:
    def test_api_call(self):
        ...
```

**Location**: `tests/test_rag_embeddings.py:14-20`, `tests/test_rag_error_handling.py:18-37`

**Rationale**: Allows graceful skipping when optional dependencies are unavailable while maintaining full test coverage with core dependencies.

---

## Code Organization

### 4. Shared RAG Utilities

**Pattern**: Share common utilities in `src/codex/rag/utils.py` and export through `__init__.py`.

**Structure**:
```
src/codex/rag/
├── __init__.py          # Export public API
├── utils.py             # Shared utilities (NEW)
├── embeddings.py        # Import from utils
├── retriever.py         # Import from utils
└── indexer.py
```

**Location**: `src/codex/rag/utils.py:1-48`, `src/codex/rag/__init__.py:22-56`

**Rationale**: Prevents code duplication, provides clear organization for helper functions used across multiple RAG components.

---

## Code Quality

### 5. Documented Exception Handling

**Pattern**: Add explanatory comments to empty except clauses explaining why errors are being silently caught.

**Example**:
```python
# ❌ UNCLEAR - Silent error swallowing
try:
    data = json.load(f)
except (json.JSONDecodeError, OSError):
    pass

# ✅ CLEAR - Documented intent
try:
    data = json.load(f)
except (json.JSONDecodeError, OSError):
    # Intentionally ignore errors reading the cache file.
    # If the cache is corrupted or unreadable, we'll fall back to a full sync.
    pass
```

**Location**: `scripts/expanded_context_audit.py:104-107`, `src/services/crawler/zendesk_sync.py:392-395`

**Rationale**: Makes intentional error handling explicit, prevents accidental bug hiding, aids future maintenance.

---

## RAG Implementation Guidelines

### Using Local Embeddings (sentence-transformers)

The repository has **two RAG implementations**:

1. ✅ **Primary**: `src/codex/rag/` - Uses sentence-transformers (local, no API key)
2. ⚠️ **Legacy**: `src/rag/pipelines/` - Original implementation

**Preference**: Use sentence-transformers for new RAG features. OpenAI integration is optional for development.

**Key Benefits**:
- No API key required
- Works offline
- Deterministic for testing
- Lower latency for small-scale usage

---

## Related Documentation

- Security exceptions: `.security-exceptions.md`
- RAG module documentation: `docs/RAG_GUIDE.md` (if exists)
- Testing guidelines: `tests/README.md`

---

## Commit History (PR #2750)

1. `fa4d967` - Remove unused imports/variables and fix code injection vulnerability
2. `5367b80` - Add safe_model_load helper and make OpenAI tests optional
3. `9e60305` - Refactor: move safe_model_load to shared utils module
4. `38ead42` - Security: fix code injection in NDJSON path of build_faiss.sh
5. `d2dcf0e` - Improve safe_model_load device comparison for PyTorch compatibility

---

**Maintained by**: GitHub Copilot Agent  
**Last Updated**: 2026-01-08  
**PR**: #2750 (copilot/sub-pr-2750 branch)
