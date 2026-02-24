# PyTorch Meta Tensor Tracking

**Version**: 1.0.0
**Created**: 2026-01-29
**Last Updated**: 2026-01-29
**Maintainer**: RAG Team, AI Agent Team

---

## 📊 Current Status

### PyTorch Version Compatibility

| PyTorch Version | Status | Meta Tensor Issues | Recommended Action |
|----------------|---------|-------------------|-------------------|
| **2.0.0 - 2.1.x** | ✅ Stable | None reported | Safe to use |
| **2.2.0 - 2.5.x** | ⚠️ Caution | Intermittent issues | Pin to <2.2.0 or use careful patterns |
| **2.6.0+** | ⚠️ Caution | Strict meta device enforcement | Use default device allocation pattern |
| **3.0.0+** | 🔮 Future | Unknown | Monitor beta releases |

### Current Dependencies

```toml
# From pyproject.toml [project.optional-dependencies.rag]
torch = ">=2.0.0,<2.2.0"
sentence-transformers = ">=2.2.0,<2.8.0"
transformers = ">=4.30.0,<4.37.0"
```

**Last Validated**: 2026-01-29
**Validation Environment**: Python 3.11, Ubuntu 22.04

### Known Issues

#### PyTorch 2.2.0+
- **Issue**: Stricter meta device handling
- **Symptom**: `NotImplementedError: Cannot copy out of meta tensor`
- **Workaround**: Use default device allocation (no explicit `device=` parameter)
- **Status**: Tracked in [RAG_META_TENSOR_FIX_SUMMARY.md](../RAG_META_TENSOR_FIX_SUMMARY.md)

#### PyTorch 2.6.0+
- **Issue**: More aggressive meta tensor enforcement
- **Symptom**: Models initialized with meta tensors by default in some scenarios
- **Workaround**: Multi-layered prevention pattern (env vars + default allocation + verification)
- **Status**: Resolved with safe loading patterns

---

## 🔄 Update Checklist

### When Upgrading PyTorch

**BEFORE upgrading**, complete these steps:

#### 1. Research Phase
- [ ] Review PyTorch release notes for meta tensor changes
- [ ] Check PyTorch GitHub issues for meta device bugs
- [ ] Search for breaking changes in `torch.nn.Module` APIs
- [ ] Verify transformers/sentence-transformers compatibility

#### 2. Local Testing Phase
- [ ] Create isolated test environment with new PyTorch version
- [ ] Run RAG test suite: `pytest tests/test_rag_*.py -v`
- [ ] Check for meta tensor errors in logs
- [ ] Test model loading in all RAG modules (indexer, retriever, embeddings)
- [ ] Verify GPU/CPU device handling works correctly

#### 3. Validation Phase
- [ ] Run full test suite with new PyTorch version
- [ ] Check test coverage remains ≥90%
- [ ] Validate pre-commit hooks still detect issues
- [ ] Test on multiple Python versions (3.10, 3.11, 3.12)
- [ ] Verify Windows/macOS/Linux compatibility

#### 4. Documentation Phase
- [ ] Update this document with new version status
- [ ] Document any new workarounds or patterns
- [ ] Update `RAG_META_TENSOR_FIX_SUMMARY.md` if needed
- [ ] Add migration notes to `CHANGELOG.md`
- [ ] Update agent documentation if detection patterns change

#### 5. Deployment Phase
- [ ] Update `pyproject.toml` with new version constraint
- [ ] Regenerate requirements files if using pip-compile
- [ ] Update CI/CD workflows if needed
- [ ] Run full CI pipeline before merging
- [ ] Monitor production for 48 hours after deployment

---

## 📈 Monitoring Strategy

### Automated Monitoring

**Pre-commit Hook**: Catches issues during development
```bash
pre-commit run check-meta-tensors --all-files
```

**CI/CD**: Validates every PR
```bash
# In .github/workflows/test-suite.yml
pytest tests/test_rag_*.py -v --tb=short
```

**Manual Testing**: Periodic validation
```bash
# Quarterly check (or before major releases)
python scripts/validate_rag_models.py --check-meta-tensors
```

### Manual Monitoring

**Quarterly Review** (Every 3 months):
1. Check PyTorch release schedule
2. Review meta tensor-related GitHub issues
3. Test latest PyTorch version in isolated environment
4. Update compatibility matrix in this document

**Before Major Releases**:
1. Validate current PyTorch version still works
2. Test with next minor version (if available)
3. Update documentation with findings
4. Plan migration if needed

---

## 🛠️ Debugging Meta Tensor Issues

### Diagnostic Commands

**Check if model has meta tensors:**
```python
import torch
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

# Check parameters
meta_params = [
    name for name, param in model.named_parameters()
    if param.device.type == "meta"
]

# Check buffers
meta_buffers = [
    name for name, buf in model.named_buffers()
    if buf.device.type == "meta"
]

print(f"Meta parameters: {len(meta_params)}")
print(f"Meta buffers: {len(meta_buffers)}")

if meta_params or meta_buffers:
    print("⚠️ Model has meta tensors!")
    print(f"Params: {meta_params[:5]}")
    print(f"Buffers: {meta_buffers[:5]}")
else:
    print("✅ Model is properly materialized")
```

**Check PyTorch version:**
```python
import torch
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA version: {torch.version.cuda if torch.cuda.is_available() else 'N/A'}")
```

**Test safe loading pattern:**
```python
from codex.rag.utils import safe_model_load_v2, check_for_meta_tensors

model = SentenceTransformer('all-MiniLM-L6-v2')
has_meta = check_for_meta_tensors(model)
print(f"Has meta tensors: {has_meta}")

if has_meta:
    model = safe_model_load_v2(
        model,
        device="cpu",
        model_name='all-MiniLM-L6-v2',
        cache_folder='./cache'
    )
    has_meta_after = check_for_meta_tensors(model)
    print(f"Has meta tensors after fix: {has_meta_after}")
```

### Common Error Messages

**Error 1: NotImplementedError**
```
NotImplementedError: Cannot copy out of meta tensor; no data!
Please use torch.nn.Module.to_empty() instead of torch.nn.Module.to()
```

**Solution**: Use default device allocation pattern in CONTRIBUTING.md

**Error 2: RuntimeError**
```
RuntimeError: Model has 123 meta tensor(s). This is a bug.
```

**Solution**: Model initialization failed verification. Check initialization code follows safe patterns.

**Error 3: AttributeError**
```
AttributeError: 'Tensor' object has no attribute 'data'
```

**Solution**: Attempting to access data from meta tensor. Ensure model is properly materialized first.

---

## 📚 Resources

### Internal Documentation
- **Fix Summary**: [RAG_META_TENSOR_FIX_SUMMARY.md](../RAG_META_TENSOR_FIX_SUMMARY.md)

### External Resources
- [PyTorch Meta Tensors Documentation](https://pytorch.org/docs/stable/meta.html)
- [PyTorch Release Notes](https://github.com/pytorch/pytorch/releases)
- [SentenceTransformers Documentation](https://www.sbert.net/docs/quickstart.html)
- [Transformers Model Loading](https://huggingface.co/docs/transformers/main_classes/model)

### Community Support
- PyTorch Forums: https://discuss.pytorch.org/
- PyTorch GitHub Issues: https://github.com/pytorch/pytorch/issues
- SentenceTransformers GitHub: https://github.com/UKPLab/sentence-transformers/issues

---

## 📊 Historical Tracking

### Version History

| Date | PyTorch Version | Status Change | Reason |
|------|----------------|---------------|---------|
| 2026-01-29 | 2.0.0-2.1.x | ✅ Stable | Initial tracking document created |
| 2026-01-29 | 2.2.0+ | ⚠️ Caution | Meta tensor issues reported in PR #3020 |
| 2026-01-29 | Current (2.0.x-2.1.x) | ✅ Validated | All 28 RAG tests passing with safe patterns |

### Incident Log

#### 2026-01-28: PR #3020 Meta Tensor Crisis
- **Severity**: High
- **Impact**: 28 RAG test failures
- **Root Cause**: Incorrect model initialization patterns
- **Resolution**: Implemented safe loading patterns + pre-commit validation
- **Prevention**: Meta Tensor Validator agent + documentation
- **Time to Resolution**: 2 iterations
- **Status**: ✅ Resolved

---

## 🎯 Future Roadmap

### Short Term (1-3 Months)
- [ ] Add automated PyTorch version testing in CI (test matrix)
- [ ] Create alerting system for new PyTorch releases
- [ ] Expand pre-commit hook to detect more patterns
- [ ] Add model loading benchmarks

### Medium Term (3-6 Months)
- [ ] Investigate PyTorch 2.x compilation impact on meta tensors
- [ ] Develop automatic migration tool for pattern updates
- [ ] Create comprehensive model loading test suite
- [ ] Document patterns for other ML frameworks (TensorFlow, JAX)

### Long Term (6-12 Months)
- [ ] Contribute fixes upstream to PyTorch/transformers if needed
- [ ] Build model registry with pre-validated safe models
- [ ] Develop automated version compatibility testing
- [ ] Create training materials for safe ML coding

---

## 📞 Contact & Support

### For Questions
- **Technical Issues**: Create issue with `label:meta-tensor` label
- **Pattern Questions**: Activate Meta Tensor Validator agent with `@copilot`
- **Urgent Issues**: Contact @mbaetiong or RAG team lead

### For Updates
- **Submit Updates**: Create PR updating this document
- **Report Issues**: GitHub Issues with detailed reproduction steps
- **Suggest Improvements**: Discussions or direct PR

---

**This document is actively maintained. Last review: 2026-01-29**

**Next scheduled review: 2026-04-29 (Quarterly)**
