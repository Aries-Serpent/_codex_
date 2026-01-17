# PyTorch Security Migration Guide

**Date**: 2025-12-22  
**Purpose**: Migrate existing `torch.load()` calls to secure wrappers

## 🚨 Security Issue

CVE-2024-XXXXX: PyTorch's `torch.load()` can execute arbitrary code when loading malicious model files. This affects all versions before 2.2.2 and requires using `weights_only=True`.

## ✅ Solution

We've created `utils/safe_torch_loader.py` which enforces secure loading practices.

## 🔄 Migration Steps

### Step 1: Update imports

**Before:**
```python
import torch

# Load model
model_dict = torch.load('model.pth')
```

**After:**
```python
from utils.safe_torch_loader import safe_load

# Load model securely
model_dict = safe_load('model.pth')
```

### Step 2: Handle map_location

**Before:**
```python
checkpoint = torch.load('checkpoint.pth', map_location='cpu')
```

**After:**
```python
from utils.safe_torch_loader import safe_load

checkpoint = safe_load('checkpoint.pth', map_location='cpu')
```

### Step 3: For model state dict loading

**Before:**
```python
model = MyModel()
model.load_state_dict(torch.load('model.pth'))
```

**After:**
```python
from utils.safe_torch_loader import safe_load

model = MyModel()
state_dict = safe_load('model.pth', map_location='cpu')
model.load_state_dict(state_dict)
```

## 📝 Files Requiring Migration

Based on grep analysis, the following files need updates:

### High Priority (Production Code)
- [ ] `src/codex_ml/utils/checkpoint.py` - Line 132
- [ ] `src/codex_ml/utils/checkpointing.py` - Multiple locations
- [ ] `src/codex_ml/utils/checkpoint_manager.py` - Lines 59, 64
- [ ] `src/codex_ml/utils/checkpoint_core.py` - Line 364
- [ ] `src/training/checkpointing.py` - Line 115 (error message)
- [ ] `src/utils/checkpoint.py` - Line 230 (error message)

### Medium Priority (Tools)
- [ ] `scripts/inference_pipeline.py`
- [ ] `src/codex_ml/serving/model_loader.py` - Line 241 (comment only)

### Low Priority (Tests)
- [ ] `tests/checkpoint/test_checkpoint_peft_state.py`
- [ ] `tests/integration/test_ml_pipeline_integration.py`
- [ ] `tests/modeling/test_decoder_only.py`
- [ ] `tests/utils/test_checkpointing_safe_load.py`
- [ ] `tests/smoke/test_checkpoint_hashing.py`
- [ ] `tests/test_checkpoint_metadata.py`
- [ ] `tests/test_checkpoint_commit_meta.py`
- [ ] `tests/space_traversal/test_peft_comprehensive/test_extended_trainer.py`
- [ ] `tests/checkpointing/test_checkpoint_comprehensive.py`
- [ ] `tests/data/test_data_cache.py`

## 🔒 Security Best Practices

### DO ✅
```python
from utils.safe_torch_loader import safe_load

# Always use weights_only=True (default)
state = safe_load('model.pth')

# With resource cleanup
from utils.torch_resource_manager import torch_resource_guard

with torch_resource_guard():
    state = safe_load('model.pth')
    model.load_state_dict(state)
```

### DON'T ❌
```python
# NEVER do this - RCE vulnerability!
state = torch.load('model.pth')

# NEVER do this - bypasses security!
state = torch.load('model.pth', weights_only=False)
```

## 🧪 Testing Your Migration

After migrating, verify with:

```python
# Test that safe_load works
from utils.safe_torch_loader import safe_load
import torch

# Create a test model
model = torch.nn.Linear(10, 5)
torch.save(model.state_dict(), '/tmp/test_model.pth')

# Load it back safely
state = safe_load('/tmp/test_model.pth')
assert isinstance(state, dict)
print("✅ Safe loading works!")
```

## 📞 Support

If you encounter issues during migration:
1. Check that torch>=2.2.2 is installed
2. Review error messages - they indicate if weights_only=False is needed
3. For legacy models that fail with weights_only=True, consider re-saving them
4. Contact security team if you have questions

## 🎯 Completion Checklist

- [x] Security wrappers created
- [x] Migration guide written
- [ ] High priority files migrated
- [ ] Medium priority files migrated
- [ ] Tests updated
- [ ] Documentation updated
- [ ] Security audit passed

## 🔗 References

- [CVE-2024-XXXXX](https://github.com/Aries-Serpent/_codex_/security)
- [PyTorch Security Advisory](https://pytorch.org/docs/stable/generated/torch.load.html)
- [utils/safe_torch_loader.py](../utils/safe_torch_loader.py)
- [SECURITY.md](./SECURITY.md)
