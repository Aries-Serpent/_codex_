# Dependency Version Constraints

This document explains critical version constraints in the _codex_ project dependencies.

## Pandas & MLflow Compatibility

### Current Constraints
- **pandas:** `>=3.0.3,<4`
- **mlflow:** `>=2.22.4,<4`

### Rationale

**Why pandas 3.x?**

This project has been upgraded to use pandas 3.x to take advantage of performance improvements and modern APIs. The constraint `>=3.0.3,<4` ensures compatibility with the latest pandas releases while maintaining stability:

- ✅ pandas 3.0.3+ is stable and production-ready
- ✅ All MLflow 3.x+ versions support pandas 3.x
- ✅ Codebase has been updated to use pandas 3.x-compatible APIs
- ✅ Performance improvements with pandas 3.x

**Issue Reference:**
- Resolved pip ResolutionImpossible conflicts by aligning to pandas 3.x-compatible dependency stack
- Affects: API Documentation, MkDocs, CI caching, code quality, security scanning, authentication tests, agent registry validation, workflow docs, actionlint, CI health monitor, pre-flight validation, RAG tests, CI checkpoint validation, and secrets baseline enforcement

### Upgrade Path

To manage pandas versions:

1. **Monitor pandas releases** - Track new patch/minor releases
2. **Test compatibility** - Run full test suite before updating
3. **Update constraints** - Change pandas pin to new version range
4. **Verify CI** - Ensure all workflows pass with new version
5. **Update documentation** - Document any API adjustments required

### Maintenance Notes

- This constraint was introduced after extensive testing confirming pandas 3.x API compatibility
- Monitor MLflow releases for continued pandas 3.x support
- Ensure all downstream dependencies remain compatible with pandas 3.x

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
