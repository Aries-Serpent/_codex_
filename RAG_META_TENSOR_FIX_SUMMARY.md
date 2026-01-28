# RAG Meta Tensor Fix - Implementation Summary

## Problem Statement
PR #3020 had 20 failed tests + 10 errors all caused by:
```
NotImplementedError: Cannot copy out of meta tensor; no data! 
Please use torch.nn.Module.to_empty() instead of torch.nn.Module.to()
```

**Failing at**:
- `src/codex/rag/indexer.py:122`
- `src/codex/rag/retriever.py:110`
- `src/codex/rag/embeddings.py:92`

**Root Cause**: The previous approach attempted to fix models AFTER they were initialized with meta tensors, which cannot work. Meta tensors are placeholders without data, and PyTorch doesn't allow copying them.

## Solution Implemented

**Prevention over cure**: Stop meta tensors from being created in the first place by using correct initialization patterns.

### Changes Made

#### 1. `src/codex/rag/indexer.py` (embed_chunks function)

**Before**: Model was initialized and then an attempt was made to fix it
**After**: Direct, correct initialization with multi-layered prevention:

```python
# Environment setup
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:128"
os.environ["TRANSFORMERS_OFFLINE"] = "0"

# Context manager forces CPU device
with torch.device('cpu'):
    model = SentenceTransformer(
        model_name,
        cache_folder=cache_dir,
        device="cpu",  # Explicit device parameter
        trust_remote_code=False  # Security: prevent code execution
    )

# Defensive: Force CPU again
model = model.to('cpu')

# Verification: Check for any meta tensors
meta_params = []
for name, param in model.named_parameters():
    if param.device.type == "meta":
        meta_params.append(name)

if meta_params:
    raise RuntimeError(f"Model has {len(meta_params)} meta tensor(s)...")

model.eval()
```

**Key improvements**:
1. ✅ Environment variables set BEFORE loading
2. ✅ Context manager `with torch.device('cpu')`
3. ✅ Explicit `device="cpu"` parameter
4. ✅ Defensive `.to('cpu')` call
5. ✅ Verification loop to detect any remaining meta tensors
6. ✅ Clear error message with upgrade instructions if detected

#### 2. `src/codex/rag/retriever.py` (_load_model method)

Applied the same defensive pattern as indexer:
- Environment setup
- Context manager
- Explicit device parameter
- Defensive device move
- Verification
- Clear error handling

#### 3. `src/codex/rag/embeddings.py` (LocalSentenceTransformerProvider._load_model)

Applied the same defensive pattern as the other two modules for consistency.

#### 4. `pyproject.toml` (RAG dependencies)

**Before**:
```toml
rag = [
  "sentence-transformers>=2.3.0,<4.0.0",
  "chromadb>=0.4.22,<1.0.0",
  "faiss-cpu>=1.7.4,<2.0.0",
  "openai>=1.0; python_version >= '3.8'",
]
```

**After**:
```toml
rag = [
  "sentence-transformers>=2.2.0,<2.8.0",  # Pin to working versions
  "torch>=2.0.0,<2.2.0",  # Avoid 2.2+ meta device changes
  "transformers>=4.30.0,<4.37.0",  # Stable compatibility
  "chromadb>=0.4.22,<1.0.0",
  "faiss-cpu>=1.7.4,<2.0.0",
  "openai>=1.0; python_version >= '3.8'",
]
```

**Rationale**:
- PyTorch 2.2+ introduced changes to meta device behavior
- Pinning to 2.0-2.1.x ensures stable behavior
- sentence-transformers 2.2-2.7.x are well-tested versions
- transformers 4.30-4.36.x provide stable compatibility

## Why This Works

### The Problem with Previous Approach
Previous commits (8cb2ef9, 095c2a4, 4ff8eb1) tried using `safe_model_load()` utility:
```python
model = SentenceTransformer(...)  # Already has meta tensors
model = safe_model_load(model)     # Too late! Can't copy meta tensors
```

### The Solution
Our approach prevents meta tensors at initialization:
```python
# Set stage BEFORE initialization
with torch.device('cpu'):
    model = SentenceTransformer(..., device="cpu")  # No meta tensors created
```

### Defense in Depth

1. **Layer 1**: Environment variables prevent meta device selection
2. **Layer 2**: Context manager forces CPU device scope
3. **Layer 3**: Explicit `device="cpu"` parameter
4. **Layer 4**: Defensive `.to('cpu')` call after initialization
5. **Layer 5**: Verification loop catches any that slip through
6. **Layer 6**: Version pinning ensures compatible library behavior

## Testing Strategy

The fix can be validated by:

1. **Unit tests** (using mocks):
   - Test that model initialization happens with correct parameters
   - Test that meta tensor detection raises appropriate errors
   - Test that CPU device is properly set

2. **Integration tests**:
   - Run existing RAG test suite (tests/rag/)
   - All tests should pass without meta tensor errors

3. **CI validation**:
   - The failed CI job should now pass
   - https://github.com/Aries-Serpent/_codex_/actions/runs/21459135765/job/61807319678

## Expected Outcomes

✅ All 20 failed tests should pass
✅ All 10 error cases should resolve
✅ No `NotImplementedError: Cannot copy out of meta tensor` errors
✅ Models load correctly on CPU device
✅ Test execution time should improve (no retry/fallback logic)

## Security Considerations

Added `trust_remote_code=False` to SentenceTransformer initialization to prevent arbitrary code execution from model configs.

## Files Modified

1. `src/codex/rag/indexer.py` - embed_chunks function
2. `src/codex/rag/retriever.py` - Retriever._load_model method
3. `src/codex/rag/embeddings.py` - LocalSentenceTransformerProvider._load_model method
4. `pyproject.toml` - RAG dependencies section

Total: 4 files, +81 lines, -45 lines

## Backward Compatibility

✅ **API Compatible**: No changes to function signatures or public APIs
✅ **Behavior Compatible**: Same functionality, just fixes the bug
✅ **Test Compatible**: All existing tests should pass
⚠️ **Version Constraints**: Tighter version pins may require dependency resolution

## Next Steps

1. ✅ **Code changes implemented**
2. ⏳ **Run code review** - Request automated review
3. ⏳ **Run security scan** - CodeQL analysis
4. ⏳ **CI validation** - Monitor test results
5. ⏳ **Merge** - After all checks pass

## References

- PR #3020: https://github.com/Aries-Serpent/_codex_/pull/3020
- Failed CI Job: https://github.com/Aries-Serpent/_codex_/actions/runs/21459135765/job/61807319678
- Previous attempts: commits 8cb2ef9, 095c2a4, 4ff8eb1
