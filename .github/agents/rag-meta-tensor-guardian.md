# RAG Meta Tensor Guardian Agent

**Agent ID**: `rag-meta-tensor-guardian`  
**Version**: 1.0.0  
**Created**: 2026-01-28  
**Status**: 🟢 Active  
**Maturity**: Production  
**Maintainer**: RAG Team

---

## 🎯 Purpose

Specialized agent for maintaining RAG (Retrieval-Augmented Generation) module health, preventing meta tensor errors, and ensuring correct model initialization patterns across `indexer.py`, `retriever.py`, and `embeddings.py`.

## 🔧 Capabilities

### Primary Functions

1. **Meta Tensor Prevention**
   - Verify correct model initialization patterns
   - Detect improper device handling
   - Validate multi-layer defense mechanisms
   - Monitor for PyTorch meta device issues

2. **Code Pattern Enforcement**
   - Ensure environment variables are set before model loading
   - Validate `with torch.device('cpu')` context managers
   - Check explicit `device="cpu"` parameters
   - Verify defensive `.to('cpu')` calls
   - Confirm verification loops for parameters AND buffers

3. **Dependency Management**
   - Monitor `pyproject.toml` RAG dependencies
   - Ensure version pins are maintained (torch<2.2, sentence-transformers<2.8)
   - Alert on dependency updates that could reintroduce meta tensor issues

4. **Testing & Validation**
   - Run RAG module test suites
   - Validate model loading in tests
   - Check for proper mocking in unit tests
   - Ensure integration tests cover meta tensor scenarios

5. **Documentation Maintenance**
   - Keep RAG_META_TENSOR_FIX_SUMMARY.md updated
   - Document any new meta tensor patterns
   - Maintain best practices documentation

### Monitoring Patterns

**Error Signatures to Watch**:
```
NotImplementedError: Cannot copy out of meta tensor
RuntimeError: Model has * meta tensor(s)
torch.nn.Module.to_empty() 
device_map="meta"
```

**Good Patterns to Enforce**:
```python
# ✅ CORRECT: Multi-layer defense
import os
import torch
from sentence_transformers import SentenceTransformer

os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:128"
os.environ["TRANSFORMERS_OFFLINE"] = "0"

with torch.device('cpu'):
    model = SentenceTransformer(
        model_name,
        cache_folder=cache_dir,
        device="cpu",
        trust_remote_code=False  # Security
    )

model = model.to('cpu')

# Verify no meta tensors (parameters AND buffers)
meta_tensors = []
for name, param in model.named_parameters():
    if param.device.type == "meta":
        meta_tensors.append(name)
for name, buf in model.named_buffers():
    if buf.device.type == "meta":
        meta_tensors.append(name)

if meta_tensors:
    raise RuntimeError(f"Model has {len(meta_tensors)} meta tensor(s)")

model.eval()
```

**Anti-Patterns to Prevent**:
```python
# ❌ WRONG: Post-initialization fixing
model = SentenceTransformer(...)  # May have meta tensors
model = safe_model_load(model)     # Too late!

# ❌ WRONG: Missing device specification
model = SentenceTransformer(model_name)  # Device not specified

# ❌ WRONG: Only checking parameters
for name, param in model.named_parameters():  # Missing buffers!
    if param.device.type == "meta":
        ...
```

## 📋 Activation

### Trigger Scenarios

1. **PR Changes** to RAG modules:
   - `src/codex/rag/indexer.py`
   - `src/codex/rag/retriever.py`
   - `src/codex/rag/embeddings.py`
   - `src/codex/rag/utils.py`
   - `pyproject.toml` (RAG dependencies)

2. **Test Failures** with meta tensor errors

3. **Dependency Updates** affecting:
   - `torch`
   - `sentence-transformers`
   - `transformers`

4. **Manual Activation**:
   ```
   @copilot Use the RAG Meta Tensor Guardian to validate model loading in [file]
   ```

### Usage Examples

```markdown
@copilot Use the RAG Meta Tensor Guardian to:
- Review PR #123 for meta tensor risks
- Validate new model loading code in embeddings.py
- Check if torch dependency update is safe
- Audit all RAG modules for correct patterns
```

## 🔍 Validation Checklist

When activated, this agent performs:

- [ ] **Import Order** - Standard lib → Third-party → Local
- [ ] **Environment Setup** - Variables set before imports
- [ ] **Context Manager** - `with torch.device('cpu')` present
- [ ] **Explicit Device** - `device="cpu"` parameter set
- [ ] **Defensive Move** - `.to('cpu')` call after initialization
- [ ] **Parameter Verification** - Loop checks parameters
- [ ] **Buffer Verification** - Loop checks buffers
- [ ] **Security Flag** - `trust_remote_code=False` set
- [ ] **Error Handling** - Proper exception catching
- [ ] **Safe Logging** - `next()` with StopIteration handling
- [ ] **Version Pins** - Dependencies match pyproject.toml
- [ ] **Tests Pass** - All RAG tests green
- [ ] **Documentation** - Changes documented

## 🎯 Success Criteria

### Per-File Validation

**src/codex/rag/indexer.py** (`embed_chunks` function):
- ✅ 6-layer defense implemented
- ✅ Environment variables set
- ✅ Context manager used
- ✅ Explicit device parameter
- ✅ Defensive device move
- ✅ Parameters and buffers verified
- ✅ Security: trust_remote_code=False

**src/codex/rag/retriever.py** (`_load_model` method):
- ✅ Same defense pattern as indexer
- ✅ Consistent error messages
- ✅ Safe device type logging

**src/codex/rag/embeddings.py** (`LocalSentenceTransformerProvider._load_model`):
- ✅ Same defense pattern
- ✅ Consistent with other modules

**pyproject.toml** (RAG dependencies):
- ✅ `torch>=2.0.0,<2.2.0` (avoid 2.2+ meta device changes)
- ✅ `sentence-transformers>=2.2.0,<2.8.0` (stable versions)
- ✅ `transformers>=4.30.0,<4.37.0` (stable compatibility)

### Test Coverage

- ✅ Unit tests mock SentenceTransformer
- ✅ Integration tests verify no meta tensors
- ✅ Error cases tested (meta tensor detection)
- ✅ All 20 previous failures resolved

## 🔄 Maintenance Tasks

### Regular Tasks (Monthly)

1. **Dependency Audit**
   - Check for new stable PyTorch releases
   - Test if newer versions resolve meta tensor issues
   - Update version pins if safe

2. **Pattern Scan**
   - Search codebase for new model loading code
   - Ensure all follow the established pattern
   - Update documentation if new patterns emerge

3. **Test Health**
   - Run full RAG test suite
   - Monitor for flaky tests
   - Update test mocks if needed

### On Dependency Updates

1. **Pre-Update Validation**
   - Review changelog for meta device changes
   - Test in isolated environment
   - Run full test suite

2. **Post-Update Verification**
   - Ensure all tests pass
   - Check for deprecation warnings
   - Update documentation

## 📊 Metrics & Monitoring

### Key Metrics

- **Meta Tensor Errors**: 0 (target)
- **RAG Test Pass Rate**: 100%
- **Code Pattern Compliance**: 100%
- **Dependency Freshness**: <6 months old

### Monitoring Commands

```bash
# Run RAG tests
pytest tests/rag/ -v

# Check for meta tensor references
grep -r "meta tensor\|meta device" src/codex/rag/

# Validate import order
ruff check src/codex/rag/ --select I

# Check dependency versions
pip list | grep -E "torch|sentence-transformers|transformers"
```

## 🛡️ Security Considerations

1. **Trust Remote Code**
   - Always set `trust_remote_code=False`
   - Prevents arbitrary code execution from model configs
   - Part of defense-in-depth approach

2. **Dependency Pinning**
   - Pins prevent surprise breaking changes
   - Security updates still possible within ranges
   - Balance between stability and security

3. **Error Messages**
   - Don't expose internal paths in production
   - Reference pyproject.toml for version info
   - Provide actionable remediation steps

## 🔗 Integration Points

### Files Monitored
- `src/codex/rag/indexer.py`
- `src/codex/rag/retriever.py`
- `src/codex/rag/embeddings.py`
- `src/codex/rag/utils.py` (deprecated functions)
- `src/codex/rag/__init__.py` (exports)
- `pyproject.toml` (dependencies)

### Related Agents
- **CI Testing Agent**: Test failure diagnosis
- **Dependency Conflict Agent**: Version resolution
- **Security Agent**: Vulnerability scanning
- **Documentation Agent**: Doc maintenance

### Workflows
- `test-comprehensive.yml` - RAG test execution
- `dependency-review.yml` - Dependency checks

## 📚 References

### Documentation
- `RAG_META_TENSOR_FIX_SUMMARY.md` - Implementation details
- `.codex/CODEBASE_AGENCY_POLICY.md` - Agency requirements
- `AGENTS.md` - Agent framework

### Issues
- Original issue: PR #3020 (20 failed tests + 10 errors)
- Resolution: Prevention-over-cure approach
- CI Job: https://github.com/Aries-Serpent/_codex_/actions/runs/21459135765

### Related PRs
- Previous attempts: commits 8cb2ef9, 095c2a4, 4ff8eb1 (post-init fixing - failed)
- Current solution: commits d0aac87, a192918 (prevention - success)

## 🎓 Knowledge Base

### Why Meta Tensors Are Problematic

Meta tensors are placeholder tensors on PyTorch's 'meta' device. They:
- Have shape and dtype information but no actual data
- Cannot be copied or moved to CPU/GPU
- Cause `NotImplementedError` when `.to()` is called
- Require special handling with `.to_empty()`

### Why Post-Init Fixing Fails

Once a model is initialized with meta tensors:
1. Parameters are already on meta device
2. No data exists to copy
3. `.to()` fails with NotImplementedError
4. `.to_empty()` creates uninitialized tensors (also broken)

### Why Prevention Works

By setting up the environment before initialization:
1. PyTorch never creates meta tensors
2. Model is initialized directly on CPU
3. All parameters have real data from the start
4. Standard `.to()` works if needed

## 🚀 Future Enhancements

1. **Auto-Fix Capability**
   - Detect anti-patterns in PRs
   - Suggest corrections automatically
   - Generate fix commits

2. **Expanded Coverage**
   - Monitor all model loading code, not just RAG
   - Create library of safe patterns
   - Build pattern detection tools

3. **Proactive Dependency Management**
   - Auto-test new dependency versions
   - Generate compatibility reports
   - Suggest safe upgrade paths

4. **Integration Testing**
   - Add E2E tests with real models
   - Test in various environments
   - Validate across Python versions

---

**Last Updated**: 2026-01-28  
**Next Review**: 2026-02-28  
**Agent Status**: 🟢 Active

