# AST Standardization - Dependency Requirements

**Generated**: 2025-11-09  
**Purpose**: Complete dependency specification for AST standardization project  
**Status**: PLANNING - Not yet installed

---

## Core Dependencies

### Primary AST Libraries

| Package | Version | Purpose | Priority | Installation |
|---------|---------|---------|----------|--------------|
| **libcst** | >=1.0.0 | Universal Python parser with CST preservation | CRITICAL | `pip install libcst>=1.0.0` |
| **radon** | >=6.0.0 | Cyclomatic complexity and maintainability metrics | CRITICAL | `pip install radon>=6.0.0` |
| **parso** | >=0.8.0 | Fallback parser for graceful degradation | HIGH | `pip install parso>=0.8.0` |
| **tree-sitter** | >=0.20.0 | Multi-language parsing (optional) | MEDIUM | `pip install tree-sitter>=0.20.0` |
| **tree-sitter-python** | >=0.20.0 | Python grammar for tree-sitter | MEDIUM | `pip install tree-sitter-python>=0.20.0` |

### Proposed pyproject.toml Changes

```toml
[project]
dependencies = [
    # Existing dependencies...
    "omegaconf>=2.3",
    "hydra-core==1.3.2",
    
    # AST Core Dependencies (NEW)
    "libcst>=1.0.0",         # Universal Python parser
    "radon>=6.0.0",          # Code metrics
    "parso>=0.8.0",          # Graceful degradation
]

[project.optional-dependencies]
ast = [
    "tree-sitter>=0.20.0",
    "tree-sitter-python>=0.20.0",
    "tree-sitter-yaml>=0.20.0",
    "sqlparse>=0.4.0",       # SQL parsing (optional)
]
```text

---

## Dependency Conflicts Analysis

### Known Conflicts

| Conflict | Packages | Resolution Strategy |
|----------|----------|---------------------|
| **None identified** | N/A | Initial analysis shows no conflicts |

### Compatibility Matrix

| Dependency | Python 3.8 | Python 3.9 | Python 3.10 | Python 3.11 | Python 3.12 |
|------------|------------|------------|-------------|-------------|-------------|
| libcst>=1.0.0 | ✅ | ✅ | ✅ | ✅ | ✅ |
| radon>=6.0.0 | ✅ | ✅ | ✅ | ✅ | ✅ |
| parso>=0.8.0 | ✅ | ✅ | ✅ | ✅ | ✅ |
| tree-sitter>=0.20.0 | ✅ | ✅ | ✅ | ✅ | ⚠️ (test) |

---

## Installation Order

### Phase 1: Core Dependencies (Required)

```bash
# Install core AST dependencies
pip install libcst>=1.0.0 radon>=6.0.0 parso>=0.8.0

# Verify installation
python -c "import libcst, radon, parso; print('✅ Core AST deps installed')"
```text

### Phase 2: Optional Dependencies

```bash
# Install optional multi-language support
pip install tree-sitter>=0.20.0 tree-sitter-python>=0.20.0

# Verify installation
python -c "import tree_sitter; print('✅ tree-sitter installed')"
```text

### Phase 3: Validation

```bash
# Run full test suite with new dependencies
pytest tests/ -v

# Check for dependency conflicts
pip check

# Verify no security vulnerabilities
pip-audit || echo "Install pip-audit: pip install pip-audit"
```text

---

## Offline Operation Requirements

### Bundled Dependencies

For offline environments, pre-download:

```bash
# Download all dependencies
pip download libcst radon parso tree-sitter tree-sitter-python   -d /tmp/ast_deps/

# Install from local cache
pip install --no-index --find-links=/tmp/ast_deps/   libcst radon parso tree-sitter tree-sitter-python
```text

### Grammar Files

tree-sitter requires pre-compiled grammar files:

```bash
# Download grammar repositories
git clone https://github.com/tree-sitter/tree-sitter-python
git clone https://github.com/tree-sitter/tree-sitter-yaml

# Build grammars (requires C compiler)
# This should be done during package build, not at runtime
```text

---

## Validation Commands

### Post-Installation Verification

```bash
# Test each library individually
python << 'EOF'
import sys

# Test libcst
try:
    import libcst as cst
    code = "def hello(): pass"
    tree = cst.parse_module(code)
    print(f"✅ libcst: {cst.__version__}")
except Exception as e:
    print(f"❌ libcst failed: {e}")
    sys.exit(1)

# Test radon
try:
    from radon.complexity import cc_visit
    code = "def hello():\n    pass"
    result = cc_visit(code)
    print(f"✅ radon: works")
except Exception as e:
    print(f"❌ radon failed: {e}")
    sys.exit(1)

# Test parso
try:
    import parso
    code = "def hello(): pass"
    tree = parso.parse(code)
    print(f"✅ parso: {parso.__version__}")
except Exception as e:
    print(f"❌ parso failed: {e}")
    sys.exit(1)

print("\n✅ All AST dependencies validated")
EOF
```text

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Version conflicts with torch/transformers | LOW | MEDIUM | Test in isolated venv first |
| Grammar file downloads in offline mode | MEDIUM | HIGH | Bundle grammars in package |
| Performance impact on startup | LOW | LOW | Lazy loading of heavy parsers |
| Security vulnerabilities in deps | LOW | HIGH | Regular pip-audit scans |

---

## Next Steps

1. ✅ AI Assistant autonomous document review
2. ⏳ Create test environment for validation
3. ⏳ Test dependency installation
4. ⏳ Update pyproject.toml
5. ⏳ Run full test suite
6. ⏳ Document any issues discovered
7. ⏳ Get sign-off from Tech Lead

**Status**: PLANNING COMPLETE - Awaiting implementation approval  
**Owner**: DevOps Lead  
**Timeline**: 1-2 days once approved
