# Contributing Guide

Thank you for improving `_codex_`. This document highlights the workflow for using the operational templates and the expectations for role-gated execution.

## 📚 Documentation Hub

**New to the project?** Start here:
- **[Newcomer Guide](docs/NEWCOMER_GUIDE.md)** - Get started quickly
- **[Documentation Index](docs/MASTER_INDEX.md)** - Find all documentation
- **[Cognitive Map](docs/system/CODEBASE_COGNITIVE_MAP.md)** - Understand architecture
- **[Code Style Guide](docs/dev/CODE_STYLE_GUIDE.md)** - Coding standards

**For AI Agents**:
- **[Agent Continuation Protocol](docs/workflows/AGENT_CONTINUATION_PROTOCOL.md)** - Session handoff
- **[Cognitive Brain](docs/system/)** - Context & navigation
- **[Roadmap](docs/ROADMAP.md)** - Current and planned work

## Testing Requirements

All contributions must include appropriate tests and maintain code coverage standards.

### Pre-commit Hooks (Automated Quality Gates)

This repository uses pre-commit hooks to catch issues before they reach CI. Install and enable them:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

**Quality Gates Enforced**:
- **Meta Tensor Validator**: Prevents PyTorch meta tensor issues in ML model loading code
- **Test Pattern Guardian**: Detects mock exhaustion and serialization issues in tests
- **Test File Naming**: Prevents `test_*.py` naming for utility modules (pytest collection risk)
- **Config Validator**: Ensures all Hydra configs referenced in tests exist
- **Security Checks**: Command injection, unsafe XML, weak hashing detection
- **Code Quality**: Trailing whitespace, YAML validation, large file checks
- **Windows Compatibility**: Filename validation for cross-platform support

**Pre-commit hooks automatically run on every commit.** If they fail:
1. Fix the reported issues
2. Stage the fixes: `git add <files>`
3. Commit again: `git commit`

**Bypassing hooks** (only in emergencies): `git commit --no-verify`

### Test File Naming Conventions

**Critical Rule**: pytest collects **ANY** file matching `test_*.py` pattern for test execution.

**✅ Correct Naming**:
- `tests/test_feature.py` - Actual test file
- `tests/framework/generator.py` - Utility module (no `test_` prefix)
- `tests/helpers/utils.py` - Helper module (no `test_` prefix)
- `conftest.py` - Pytest configuration (special name)

**❌ Incorrect Naming** (causes pytest collection errors):
- `tests/framework/test_generator.py` - Utility module with `test_` prefix ❌
- `tests/helpers/test_utils.py` - Helper module with `test_` prefix ❌

**Why This Matters**:
- pytest attempts to collect and run ALL `test_*.py` files
- Utility modules aren't designed to be test files
- Causes collection errors (exit code 2) and blocks CI
- Can lead to import errors and circular dependencies

**If You Need to Rename**:
```bash
# Rename the file
mv tests/framework/test_generator.py tests/framework/generator.py

# Update imports in all files that reference it
# Search for: from tests.framework.test_generator import
# Replace with: from tests.framework.generator import
```

**Optional Dependencies in Tests**:
For tests requiring optional dependencies (numpy, torch, etc.), use `pytest.importorskip()`:

```python
import pytest

# Skip entire module if dependency missing
numpy = pytest.importorskip("numpy")
torch = pytest.importorskip("torch")

def test_with_numpy():
    """This test only runs if numpy is installed."""
    arr = numpy.array([1, 2, 3])
    assert len(arr) == 3
```

Or skip individual tests:
```python
@pytest.mark.skipif(not has_numpy, reason="requires numpy")
def test_numpy_feature():
    import numpy as np
    # ...
```

### Running Tests Locally

**Quick test run:**
```bash
pytest
```

**With coverage:**
```bash
pytest --cov=src --cov-report=html --cov-report=xml --cov-report=term
```

**Run specific test categories:**
```bash
pytest -m smoke              # Smoke tests only
pytest -m "not slow"         # Skip slow tests
pytest -m integration        # Integration tests
```

See `tests/README.md` for comprehensive testing instructions.

### CI/CD Testing

All pull requests are automatically tested via GitHub Actions (`.github/workflows/ci-pytest.yml`):
- Tests run on Python 3.12+ (ubuntu-latest)
- Coverage must meet 90% threshold (configurable)
- Coverage reports are uploaded as artifacts
- Automatic PR comment with coverage summary and artifact links

### Coverage Requirements

- **Minimum threshold**: 90% (enforced in CI)
- **Local validation**: `pytest --cov=src --cov-fail-under=90`
- **Coverage reports**: Available as CI artifacts (HTML, XML, JSON formats)
- **Viewing reports**: Download `coverage-html-report` artifact from workflow run

### Before Submitting a PR

1. Run tests locally: `pytest -v`
2. Check coverage: `pytest --cov=src --cov-report=term-missing`
3. Ensure no test failures
4. Add tests for new functionality
5. Update documentation if needed
6. **🚨 CRITICAL: Verify no /tmp/ violations** - See [.github/TEMPORARY_FILES_POLICY.md](.github/TEMPORARY_FILES_POLICY.md)
   ```bash
   # Check for /tmp/ references
   git diff --cached | grep -i "/tmp/"
   # Verify no important files in /tmp/
   ls -la /tmp/ | grep -E "\.(md|txt|json|yaml|py)$"
   ```

## Safe Model Loading (PyTorch/ML)

When working with PyTorch, SentenceTransformers, or other ML models, follow these guidelines to prevent **meta tensor issues** (`NotImplementedError: Cannot copy out of meta tensor`).

### ✅ Correct Pattern

**Always use default device allocation** (no explicit `device=` parameter):

```python
import os
import torch
from sentence_transformers import SentenceTransformer

def load_model_safely(model_name: str, cache_dir: str = "./cache"):
    """Safe model loading with multi-layered prevention."""

    # Layer 1: Environment setup
    os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:128"
    os.environ["TRANSFORMERS_OFFLINE"] = "0"

    # Layer 2: Initialize with default device allocation
    model = SentenceTransformer(
        model_name,
        cache_folder=cache_dir,
        trust_remote_code=False  # Security: prevent code execution
    )

    # Layer 3: Verification - Check for meta tensors
    meta_tensors = []
    for name, param in model.named_parameters():
        if param.device.type == "meta":
            meta_tensors.append(name)
    for name, buf in model.named_buffers():
        if buf.device.type == "meta":
            meta_tensors.append(name)

    if meta_tensors:
        raise RuntimeError(
            f"Model has {len(meta_tensors)} meta tensor(s). "
            f"This is a bug. Please report to: "
            f"https://github.com/Aries-Serpent/_codex_/issues"
        )

    model.eval()
    return model
```

### ❌ Anti-Patterns to Avoid

**1. Explicit device parameter (causes meta tensors in some PyTorch versions):**
```python
# WRONG: Can create meta tensors
model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
```

**2. Attempting to fix meta tensors after creation:**
```python
# WRONG: Cannot fix meta tensors after they exist
model = SentenceTransformer('all-MiniLM-L6-v2')
if check_for_meta_tensors(model):
    model = safe_model_load(model, 'cpu')  # Doesn't work!
```

**3. Missing meta tensor verification:**
```python
# WRONG: No verification that model is safe
model = SentenceTransformer('all-MiniLM-L6-v2')
return model  # What if it has meta tensors?
```

**4. Using deprecated utilities:**
```python
# WRONG: Deprecated function
from codex.rag.utils import safe_model_load
model = safe_model_load(model, device='cpu')  # Don't use this!
```

### Best Practices

1. **Always set `trust_remote_code=False`** for security (prevents arbitrary code execution)
2. **Use default device allocation** (omit `device=` parameter in most cases)
3. **Add verification loops** to check for meta tensors after loading
4. **Handle errors gracefully** with clear upgrade instructions
5. **Pin PyTorch versions** in dependencies to avoid breaking changes

### Pre-commit Hook

The **Meta Tensor Validator** pre-commit hook automatically checks your code:

```bash
# Run manually on changed files
pre-commit run check-meta-tensors --files src/codex/rag/my_module.py

# Run on all files
pre-commit run check-meta-tensors --all-files
```

### Resources

- **Agent Documentation**: [.github/agents/meta-tensor-validator.md](.github/agents/meta-tensor-validator.md)
- **Utility Registry**: [.codex/AI_AGENT_UTILITIES_REGISTRY.md](.codex/AI_AGENT_UTILITIES_REGISTRY.md) - See `safe_model_load_v2()`
- **Fix Summary**: [RAG_META_TENSOR_FIX_SUMMARY.md](.codex/RAG_META_TENSOR_FIX_SUMMARY.md) - Historical context

### Troubleshooting

**Issue**: `NotImplementedError: Cannot copy out of meta tensor`

**Solution**:
1. Remove explicit `device=` parameters from model constructors
2. Add meta tensor verification loops
3. Use utility functions from `codex.rag.utils` if available
4. Pin PyTorch version (e.g., `torch>=2.0.0,<2.2.0`) if issues persist

**Need Help?** Activate the Meta Tensor Validator agent:
```markdown
@copilot Use Meta Tensor Validator to check my model loading code
```

## Using Operational Templates

We maintain reusable templates under `docs/templates/` to streamline migrations, CLI hardening, and planning work.

| Scenario | Template | Primary Author | Reviewer |
| --- | --- | --- | --- |
| Moving Python modules while keeping imports stable | [Migration – Python File Relocation](docs/templates/Migration_PythonFileRelocation.md) | Developer | Maintainer |
| Increasing CLI robustness and coverage | [Migration – CLI Hardening](docs/templates/Migration_CLIHardening.md) | Developer | Maintainer |
| Capturing intent, risks, and validation before implementation | [Planning – Intent Validation](docs/templates/Planning_IntentValidation.md) | Developer | Maintainer |

### Workflow

1. **Developer drafts** the relevant template, replacing each `[PLACEHOLDER: ...]` marker with project context.
2. **Maintainer reviews** the draft, confirms validation gates, and approves the plan.
3. **Developer executes** the agreed steps, committing code and documentation changes.
4. **Maintainer validates** results, ensuring coverage thresholds and documentation updates are met.
5. **Team archives** the completed template with the associated pull request for future reference.

### Customization Example

```markdown
Intent: Replace legacy CLI auth flow with token refresh
Assumptions: `[PLACEHOLDER:experiment_flag]` toggles rollout in staging only
Validation Gates:
- `pytest tests/cli/test_token_refresh.py -q`
- `pytest --cov=src/cli --cov-fail-under=90`
Rollback Signal: `[PLACEHOLDER:rollback_signal]` crossing threshold
```

### Additional Expectations

- Update `docs/CHANGELOG.md` when template-guided work lands.
- Run `pytest -q` for the affected paths before committing.
- Ensure coverage doesn't decrease with your changes.
- Keep placeholder markers intact until you supply concrete values.
- Reference the filled template in pull requests for reviewer context.

For questions, mention `@maintainer` in the Architecture Review forum or open a discussion thread.
