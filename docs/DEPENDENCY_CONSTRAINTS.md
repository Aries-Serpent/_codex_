# Dependency Version Constraints

This document explains critical version constraints in the _codex_ project dependencies.

## Pandas & MLflow Compatibility

### Current Constraints
- **pandas:** `>=2.0.0,<3`
- **mlflow:** `>=2.22.4,<4`

### Rationale

**Why pandas 2.x instead of 3.x?**

All MLflow versions from 2.22.4 through 3.14.0 depend on `pandas<3`, making pandas 3.x incompatible with the MLflow versions currently supported by this project. Downgrading to pandas 2.x resolves this conflict while maintaining full compatibility with both libraries:

- ✅ pandas 2.3.3+ is stable and feature-complete
- ✅ All MLflow 3.x versions work with pandas 2.x
- ✅ Codebase uses only pandas 2.x-compatible APIs (no ArrowDtype, StringDtype, or other 3.x-specific features)
- ✅ No performance regression observed with pandas 2.x

**Issue Reference:**
- Resolved 16 failing workflows caused by ResolutionImpossible pip error
- Affects: API Documentation, MkDocs, CI caching, code quality, security scanning, authentication tests, agent registry validation, workflow docs, actionlint, CI health monitor, pre-flight validation, RAG tests, CI checkpoint validation, and secrets baseline enforcement

### Upgrade Path

To migrate to pandas 3.x in the future:

1. **Check MLflow compatibility** - Verify MLflow has released versions that support pandas 3.x
2. **Update constraints** - Change pandas to `>=3.0.0,<4` and mlflow to compatible version
3. **Test thoroughly** - Run full test suite to verify no API changes affect downstream code
4. **Update documentation** - Document any API adjustments required

### Maintenance Notes

- This constraint was introduced after extensive testing confirming pandas 2.x API compatibility
- Monitor MLflow releases for pandas 3.x support
- Consider alternative ML tracking tools if MLflow doesn't support pandas 3.x within 12 months

## Other Critical Constraints

### PyTorch
- **torch:** `>=2.6.1,<3.0.0` (except Windows)
- Enforces CPU/GPU compatibility; Windows support varies by torch version

### Transformers
- **transformers:** `>=5.12.1,<6`
- Provides HuggingFace model integration

### Project Python Version
- **Requires Python:** `>=3.12`
- Aligns with modern Python features and security updates

## Verification

To verify dependency resolution before installation:

```bash
# Dry run (no actual installation)
pip install --dry-run -e .

# Install and verify
pip install -e .
python -c "import pandas; import mlflow; print(f'pandas={pandas.__version__}, mlflow={mlflow.__version__}')"
```

## Questions?

For dependency-related issues or upgrade planning, refer to the package's `pyproject.toml` file or open an issue on the repository.
