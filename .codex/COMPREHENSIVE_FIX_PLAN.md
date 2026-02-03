# 🔧 Comprehensive Fix Plan - PR #3140 Failures

> **Generated During**: Workflow monitoring wait time  
> **Based On**: CI failure analysis + workflow monitoring results  
> **Status**: Ready to apply after all workflows complete

---

## 📊 Current Situation

**Workflow Status (Latest Check):**
- ⏳ In Progress: 63 workflows
- ✅ Successful: 25 workflows
- ❌ Failed: 8 workflows
- **Action**: Waiting for all to complete before applying fixes

---

## 🎯 Fix Strategy

### Phase 1: Critical Infrastructure Fixes (Must Fix First)

#### Fix 1.1: PyTorch Checkpoint Serialization
```python
# File: src/codex_ml/utils/checkpoint.py
# Location: _dump_payload function

# CURRENT CODE (causing pickle errors):
def _dump_payload(path, payload):
    save_fn(payload, path)

# FIXED CODE:
def _dump_payload(path, payload):
    import torch
    # Use PyTorch 2.x compatible serialization
    torch.save(
        payload,
        path,
        pickle_protocol=4,
        _use_new_zipfile_serialization=True
    )
```

**Rationale**: PyTorch 2.x storage types require specific serialization flags

---

#### Fix 1.2: Packaging Metadata
```toml
# File: pyproject.toml

# ADD after [project] section:
[project.license-files]
paths = ["LICENSE"]

# CHANGE license line:
# FROM: license = {text = "MIT"}
# TO:   license = "MIT"
```

**Rationale**: PEP 621 compliance for LICENSE files

---

#### Fix 1.3: CLI Argument Structure
```python
# File: tests/cli/test_dataset_cli.py
# Line ~45

# FROM:
subprocess.run([sys.executable, "-m", "src.codex_ml.data.cli", "validate", str(data)])

# TO:
subprocess.run([sys.executable, "-m", "src.codex_ml.data.cli", "validate", "--paths", str(data)])
```

**Rationale**: CLI requires --paths flag for validate command

---

### Phase 2: Dependency Management

#### Fix 2.1: RAG Optional Dependencies
```python
# File: tests/rag/conftest.py (or tests/conftest.py)

import pytest

# Add at module level:
sentence_transformers = pytest.importorskip(
    "sentence_transformers",
    reason="sentence-transformers is an optional RAG dependency"
)
```

**Alternative**: Add to requirements.txt if needed as core dependency

---

#### Fix 2.2: Docker Volume Configuration
```yaml
# File: docker-compose.yml

services:
  app:
    volumes:
      - ./:/workspace
      - ./data:/data  # ADD THIS LINE
```

**Rationale**: Tests expect /data mount for data files

---

### Phase 3: Type Safety & Python 3.12 Compatibility

#### Fix 3.1: isinstance with Union Types
```python
# Pattern to find:
grep -r "isinstance.*\|" src/ tests/

# Example fix:
# FROM: isinstance(model, ModelType | None)
# TO:   isinstance(model, (ModelType, type(None)))

# OR better:
# TO:   model is None or isinstance(model, ModelType)
```

**Rationale**: Python 3.12 requires tuple syntax for isinstance with unions

---

### Phase 4: Test Infrastructure

#### Fix 4.1: Audit Artifacts Directory
```python
# File: tests/specs/test_audit_meta_in_report.py

def test_meta_propagates_and_renders(tmp_path):
    # ADD at start:
    artifacts = Path.cwd() / "audit_artifacts"
    artifacts.mkdir(parents=True, exist_ok=True)
    
    # ... rest of test
```

**Rationale**: Test requires audit_artifacts directory to exist

---

#### Fix 4.2: Deterministic Seeding
```python
# File: src/codex_ml/utils/seed.py or wherever seeding occurs

def set_seed(seed: int) -> None:
    import random
    import numpy as np
    import torch
    
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    
    # ADD these critical lines for determinism:
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    
    # For PyTorch 2.x:
    try:
        torch.use_deterministic_algorithms(True, warn_only=True)
    except AttributeError:
        pass  # Older PyTorch versions
```

**Rationale**: Ensures reproducible test results

---

### Phase 5: SARIF Chunking Verification

#### Action 5.1: Verify Chunking Worked
```bash
# Check workflow artifacts for:
1. Multiple SARIF chunks uploaded (not just one)
2. No "exceeded 5000 limit" warning
3. All results successfully uploaded

# Check GitHub Security tab:
# - Should see results from multiple categories (semgrep-chunk-001, etc.)
```

---

## 🔄 Application Order

**After all workflows complete:**

1. **Apply all fixes in single comprehensive commit**
2. **Run local test suite**: `pytest tests/ -v --maxfail=25`
3. **Verify fixes work**
4. **Commit with detailed message**
5. **Push and monitor new workflow run**

---

## 📝 Commit Message Template

```
fix: Resolve all CI/CD failures and workflow issues

Critical Fixes:
- PyTorch checkpoint serialization (pickle_protocol=4)
- Packaging metadata (PEP 621 compliance)
- CLI argument parsing (--paths flag)

Dependency Fixes:
- RAG optional dependencies (sentence-transformers)
- Docker volume configuration (/data mount)

Type Safety:
- isinstance() calls for Python 3.12 (union → tuple)
- Type hints updated for compatibility

Test Infrastructure:
- Audit artifacts directory creation
- Deterministic seeding (cudnn flags)

Verification:
- SARIF chunking validated (no limit warnings)
- All 20 test failures addressed
- Full test suite passing

Resolves: 20 test failures
Addresses: 8 workflow failures
Policy: AI Codebase Agency Policy compliant
```

---

## ✅ Success Criteria

Before finalizing:
- [ ] All workflows completed (in_progress = 0)
- [ ] All fixes applied
- [ ] Local tests passing
- [ ] No new failures introduced
- [ ] SARIF chunking verified
- [ ] Comprehensive commit message
- [ ] Documentation updated

---

**Status**: Prepared and ready to apply after workflow completion
